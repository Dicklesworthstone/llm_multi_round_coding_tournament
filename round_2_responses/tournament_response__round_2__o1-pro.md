Below is one unified “best of all worlds” solution that draws on good ideas from all four responses. It carefully merges multi‑line cells, checks if a table is already valid, and if not, fixes it by:

• Detecting multi‑line cells and merging them.  
• Splitting rows into cells, counting columns, and inserting/fixing an alignment row.  
• Preserving leading/trailing pipe style from the first row.  
• Minimally skipping extra alignment lines.  
• Leaving valid tables untouched.  
• Ignoring non‑table content.  

Paste this code into your project as is:

```python
import re

def fix_invalid_markdown_tables(markdown_text):
    def merge_continuation_lines(block):
        merged = []
        for line in block:
            stripped = line.strip()
            if '|' in line:
                # Start a new row
                merged.append(line)
            else:
                # If this line doesn't contain '|', treat it as continuation
                if merged:
                    merged[-1] += ' ' + stripped
                else:
                    merged.append(line)
        return merged

    def split_into_cells(line):
        # Split on '|' but ignore leading/trailing
        parts = line.split('|')
        if parts and not parts[0].strip():
            parts = parts[1:]
        if parts and not parts[-1].strip():
            parts = parts[:-1]
        return [p.strip() for p in parts]

    def is_alignment_row(cells):
        # True if all cells match :?-{3,}:?
        return all(re.fullmatch(r':?-{3,}:?', c.strip()) for c in cells)

    def reassemble_row(cells, style):
        # style is a tuple (leading_pipe, trailing_pipe) from the first row
        row_text = " | ".join(cells)
        if style[0]:
            row_text = "|" + row_text
        if style[1]:
            row_text = row_text + "|"
        return row_text

    def detect_style(line):
        # Return (leading_pipe, trailing_pipe) from this line
        s = line.strip()
        return (s.startswith("|"), s.endswith("|"))

    def is_table_block_valid(block):
        # A block is valid if at least 2 lines,
        # second line is alignment row, and all rows have same number of cells
        if len(block) < 2:
            return False
        rows = [split_into_cells(ln) for ln in block]
        col_count = len(rows[0])
        # Check second row must be alignment row
        if len(rows[1]) != col_count or not is_alignment_row(rows[1]):
            return False
        # Check all rows must have col_count columns
        for r in rows[2:]:
            if len(r) != col_count:
                return False
        return True

    def fix_table_block(block):
        # Merge continuation lines first
        merged = merge_continuation_lines(block)
        if len(merged) < 2:
            return merged  # Not enough lines to form a table

        # If it's already valid, do nothing
        if is_table_block_valid(merged):
            return merged

        # Split into rows of cells
        rows = [split_into_cells(ln) for ln in merged]
        # Determine leading/trailing pipe style from the first line
        style = detect_style(merged[0]) if merged else (True, True)

        # Compute the max number of columns
        max_cols = max(len(r) for r in rows)

        # Normalize each row to max_cols by padding or merging overflow
        for i, r in enumerate(rows):
            if len(r) < max_cols:
                rows[i] = r + [""] * (max_cols - len(r))
            elif len(r) > max_cols:
                # Merge overflow cells into the last cell
                overflow = r[max_cols-1:]
                rows[i] = r[:max_cols-1] + [" ".join(overflow)]

        # Construct the "fixed" set of rows
        fixed = []
        # 1) Header is rows[0]
        fixed.append(rows[0])
        idx = 1
        # 2) If second row is alignment, use it; else insert one
        if len(rows) > 1 and is_alignment_row(rows[1]):
            fixed.append(rows[1])
            idx = 2
        else:
            fixed.append(["---"] * max_cols)
        # 3) Append remaining rows, skipping any alignment rows
        for r in rows[idx:]:
            if not is_alignment_row(r):
                fixed.append(r)

        # Reassemble into lines
        return [reassemble_row(r, style) for r in fixed]

    lines = markdown_text.splitlines()
    output = []
    table_block = []
    in_table = False

    def flush_table():
        if not table_block:
            return
        fixed = fix_table_block(table_block)
        output.extend(fixed)

    for line in lines:
        if '|' in line:
            # Accumulate table lines
            table_block.append(line)
            in_table = True
        else:
            # If we were in a table, flush it first
            if in_table:
                flush_table()
                table_block = []
                in_table = False
            # Then just add this non-table line
            output.append(line)

    # If there's a leftover table block at the end
    if table_block:
        flush_table()

    return "\n".join(output)
```

Explanation of key steps:
1. **merge_continuation_lines** handles lines without `|` and appends them to the last cell of the previous row.  
2. **split_into_cells** splits a row into cells, ignoring leading/trailing pipes.  
3. **is_alignment_row** checks if each cell is something like `---`, `:---`, `---:`, or `:---:`.  
4. **is_table_block_valid** checks that we have at least two lines, the second is an alignment row with the correct number of columns, and all rows share the same column count.  
5. **fix_table_block** merges lines, checks if already valid, else:  
   - Finds the max number of columns and pads rows to match.  
   - Ensures exactly one alignment row after the header (inserts one if needed, discards additional).  
   - Preserves the first row’s leading/trailing pipe style.  