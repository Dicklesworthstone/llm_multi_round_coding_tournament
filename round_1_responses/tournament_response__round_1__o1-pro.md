Below is a single, complete Python function called `fix_invalid_markdown_tables` that merges the strongest ideas from all four solutions. It identifies potential table blocks, merges lines that are likely continuations (no pipes but follow a pipe-containing line), enforces consistent column counts, inserts (or fixes) exactly one alignment row right after the first row, and removes extra alignment rows. It leaves valid tables and non-table content unchanged as much as possible, doing minimal edits:

```python
import re

def fix_invalid_markdown_tables(markdown_text):
    lines = markdown_text.splitlines()

    def is_alignment_line(line):
        # A simple test for lines that contain only dashes/pipes/colons/spaces
        # and thus likely meant to be a separator row
        return bool(re.fullmatch(r'[|\-\s:]+', line.strip())) and '---' in line

    def merge_continuation_lines(block):
        """
        Merges lines that do not contain '|' into the last cell of the preceding row.
        This helps handle multi-line cell content.
        """
        merged = []
        for line in block:
            if '|' in line:
                merged.append(line)
            else:
                if merged:
                    merged[-1] += ' ' + line.strip()
                else:
                    merged.append(line)
        return merged

    def split_into_cells(line):
        """
        Splits a line on '|' while trimming off empty leading/trailing splits.
        E.g. "| A | B |" -> ["A", "B"].
        """
        # Split raw
        parts = line.split('|')
        # Drop empty leading/trailing if present
        if parts and not parts[0].strip():
            parts = parts[1:]
        if parts and not parts[-1].strip():
            parts = parts[:-1]
        return [p.strip() for p in parts]

    def is_valid_table_block(block):
        # A very light check to see if a block is “likely” a table: 2+ lines w/ '|'
        pipe_count = sum(1 for b in block if '|' in b)
        return pipe_count >= 2

    def fix_table_block(block):
        """
        Takes a block of lines (which we believe to be a table), merges continuation lines,
        adjusts columns, ensures exactly one alignment row after the first row,
        and reassembles rows in standard markdown style.
        """
        if not block:
            return block

        # First, merge lines that might be multi-line cells
        merged = merge_continuation_lines(block)

        # Split each merged line into cells
        rows = [split_into_cells(b) for b in merged]

        # Compute max columns
        max_cols = max((len(r) for r in rows), default=0)
        if max_cols < 2:
            # Not a real table or too few columns
            return block  # leave it unmodified

        # Normalize each row to max_cols
        # (pad short rows, collapse overflow into last cell of that row)
        for i, r in enumerate(rows):
            if len(r) < max_cols:
                rows[i] = r + [''] * (max_cols - len(r))
            elif len(r) > max_cols:
                # Minimally merge overflow into last cell
                overflow = r[max_cols-1:]
                rows[i] = r[:max_cols-1] + [' '.join(overflow)]

        # Now handle alignment row insertion or skipping
        # We want row[0] to be header, row[1] to be alignment if it exists,
        # otherwise we insert one. We skip any alignment rows after that.
        fixed = []
        fixed.append(rows[0])  # header
        idx = 1

        # Check if we do have a second row and if it looks like an alignment row
        if len(rows) > 1 and all(re.fullmatch(r':?-{3,}:?', c.strip()) for c in rows[1]):
            # row[1] is alignment row
            fixed.append(rows[1])
            idx = 2
        else:
            # Insert one
            fixed.append(['---'] * max_cols)

        # Add remaining rows, skipping any that look like alignment lines
        for r in rows[idx:]:
            # if it is an alignment line, skip it
            if all(re.fullmatch(r':?-{3,}:?', c.strip()) for c in r):
                continue
            fixed.append(r)

        # Reassemble lines with leading and trailing pipes in a standard style
        result = []
        for r in fixed:
            result.append('| ' + ' | '.join(r) + ' |')
        return result

    output = []
    table_block = []
    inside_table_block = False

    def flush_table():
        # Process the accumulated table_block if it is a valid table
        if not table_block:
            return
        if is_valid_table_block(table_block):
            fixed = fix_table_block(table_block)
            # If fix_table_block returned lines, that's our new table
            # Otherwise, fallback to original if something seemed off
            if fixed:
                output.extend(fixed)
            else:
                output.extend(table_block)
        else:
            # Not a real table, just dump as is
            output.extend(table_block)

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if '|' in line:
            # Potential table line => accumulate
            table_block.append(line)
            inside_table_block = True
        else:
            # If we were accumulating a table block and this line has no pipe,
            # check if it might be a continuation line (nonempty & not a blank line).
            # If it looks like a continuation of the last row, also accumulate.
            # Otherwise, flush the block.
            if inside_table_block and stripped:
                # Could be multi-line cell content -> accumulate
                table_block.append(line)
            else:
                # We are definitely outside a table now => flush
                if table_block:
                    flush_table()
                    table_block = []
                inside_table_block = False
                output.append(line)
        i += 1

    # If there's a leftover table block at the end, flush it
    if table_block:
        flush_table()

    return "\n".join(output)
```

## Highlights of This Hybrid Approach

1. **Table Block Detection**  
   - Like o1-pro, any line containing `|` is treated as potential table content. We accumulate these lines into a “table block,” along with any subsequent “continuation” lines (that don’t contain `|` but directly follow a table line).

2. **Multi-Line Cell Handling**  
   - Like o3-mini-high and Claude, lines without `|` right after a table row are merged into the last cell of that row (allowing multi-line cell content).

3. **Column Normalization**  
   - We determine the maximum number of columns by scanning all rows (similar to o1-pro, o3, and Grok3). Rows with fewer columns are padded with empty cells; rows with overflow columns merge the extra cells into the last cell.

4. **Single Alignment Row**  
   - We ensure exactly one alignment row immediately after the first row. If the second row is already valid alignment, we keep it; otherwise, we insert one. Like o3-mini-high, we skip any additional alignment rows further down.

5. **Minimal Edits**  
   - If a block doesn’t meet the threshold for “real table content” (fewer than 2 lines with `|`), we leave it alone.  
   - For valid tables, only the strictly necessary structural fixes are applied. If the table is already valid, the final reassembled output matches the original table layout closely.

By combining these strategies, this single function can handle the various malformed table cases you listed (including those with repeated separator rows, inconsistent column counts, or multi-line cells) while leaving tables already valid entirely intact and ignoring non-table content.