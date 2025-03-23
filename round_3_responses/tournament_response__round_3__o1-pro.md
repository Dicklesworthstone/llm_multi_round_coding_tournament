Below is a single, self-contained implementation that combines the best ideas from all four solutions. It:

• Accumulates table lines, merging multi-line cells.  
• Checks if a table is already valid; if so, leaves it as-is.  
• Otherwise tries to fix it in a minimally invasive way, preserving style (leading/trailing pipes) and detecting if there's a “separator after every row” pattern.  
• Maintains consistent column counts by padding or merging.  

Paste this code into your project as-is:

```python
import re

def fix_invalid_markdown_tables(markdown_text):
    lines = markdown_text.splitlines()
    output = []
    table_block = []
    in_table = False

    def parse_row(line):
        s = line.strip()
        parts = line.split('|')
        if s.startswith('|'):
            parts = parts[1:]
        if s.endswith('|'):
            parts = parts[:-1]
        return [p.strip() for p in parts]

    def is_separator_cell(cell):
        return re.fullmatch(r':?-{3,}:?', cell.strip()) is not None

    def is_separator_row(cells):
        if not cells: return False
        # Each non-empty cell should match the alignment pattern
        return all(is_separator_cell(c) for c in cells if c.strip())

    def merge_continuation_lines(block):
        merged = []
        for line in block:
            if '|' in line:
                merged.append(line)
            else:
                if merged and line.strip():
                    merged[-1] += ' ' + line.strip()
                else:
                    merged.append(line)
        return merged

    def has_valid_structure(rows):
        # Must have at least 2 rows and second row a separator, consistent col counts
        if len(rows) < 2:
            return False
        if not is_separator_row(rows[1]):
            return False
        col_count = len(rows[0])
        return all(len(r) == col_count for r in rows)

    def is_valid_table(lines):
        if len(lines) < 2:
            return False
        parsed = [parse_row(ln) for ln in lines]
        return has_valid_structure(parsed)

    def detect_table_style(line):
        s = line.strip()
        return (s.startswith('|'), s.endswith('|'))

    def rebuild_row(cells, style):
        row = ' | '.join(cells)
        if style[0]: row = '|' + row
        if style[1]: row += '|'
        return row

    def detect_separator_pattern(rows):
        # Return True if it seems we have a separator after nearly every data row
        # (like the first example with repeated '---|---|---' lines).
        # We'll say it's that pattern if more than half the rows at odd indices are separators.
        if len(rows) < 3: 
            return False
        total_odds = (len(rows) - 1) // 2
        sep_odds = sum(is_separator_row(rows[i]) for i in range(1, len(rows), 2))
        return sep_odds >= total_odds

    def fix_table_block(block):
        merged = merge_continuation_lines(block)
        if len(merged) < 2:
            return merged
        if is_valid_table(merged):
            return block  # Already valid; use original

        # Parse into cells
        parsed = [parse_row(ln) for ln in merged]
        # Determine overall style from the first line
        style = detect_table_style(merged[0])
        # Find max columns
        max_cols = max(len(r) for r in parsed)

        # Identify which rows are separators
        sep_flags = [is_separator_row(r) for r in parsed]

        # Decide if we have "separator after each row" pattern
        repeated_sep = detect_separator_pattern(parsed)

        # Normalize each row to max_cols
        def normalize(row):
            if len(row) < max_cols:
                return row + [''] * (max_cols - len(row))
            elif len(row) > max_cols:
                return row[:max_cols-1] + [' '.join(row[max_cols-1:])]
            else:
                return row

        parsed = [normalize(r) for r in parsed]

        # Build the fixed table
        fixed = []
        fixed.append(parsed[0])  # treat first line as header
        # Insert a standard separator row after the header
        fixed.append(['---'] * max_cols)

        if repeated_sep:
            # Step through the remaining rows: if a row is not a separator, add it, then insert a separator
            idx = 1
            while idx < len(parsed):
                if sep_flags[idx]:
                    idx += 1
                    continue
                fixed.append(parsed[idx])
                fixed.append(['---'] * max_cols)
                idx += 1
        else:
            # Standard approach: skip any extra separator rows, just add data rows
            for i in range(2, len(parsed)):
                if not sep_flags[i]:
                    fixed.append(parsed[i])

        # Convert rows back to lines
        return [rebuild_row(row, style) for row in fixed]

    def flush_table():
        if not table_block:
            return
        fixed = fix_table_block(table_block)
        output.extend(fixed)

    for line in lines:
        if '|' in line:
            table_block.append(line)
            in_table = True
        else:
            if in_table:
                flush_table()
                table_block.clear()
                in_table = False
            output.append(line)
    if table_block:
        flush_table()

    return "\n".join(output)
```

Explanation highlights:
• We detect table blocks by the presence of `|`.  
• We merge non-pipe lines into the last cell.  
• We check if the table is valid; if so, return it as is.  
• Otherwise, we fix the table by:  
  – Normalizing column counts.  
  – Inserting or unifying separator rows.  
  – Preserving any “separator after each row” pattern (seen in some examples).  
• We preserve the leading and trailing pipe style.  

This should fix the sorts of invalid tables you showed, while leaving valid ones untouched and ignoring non-table content.