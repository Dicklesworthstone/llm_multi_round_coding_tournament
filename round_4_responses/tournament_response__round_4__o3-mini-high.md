Below is a “best‐of‐all‐worlds” solution that combines robust detection and merging of multi‐line cells, preservation of valid tables (including their “pipe style”), normalization of rows, and even special handling for tables that use a “separator after every row” pattern. It processes the markdown text line‐by‐line so that non‐table content remains untouched. Test it on your examples!

```python
import re

def fix_invalid_markdown_tables(markdown_text):
    lines = markdown_text.splitlines()
    output = []
    table_block = []
    in_table = False
    for line in lines:
        if '|' in line:
            table_block.append(line)
            in_table = True
        else:
            if in_table:
                output.extend(process_table_block(table_block))
                table_block = []
                in_table = False
            output.append(line)
    if table_block:
        output.extend(process_table_block(table_block))
    return "\n".join(output)

def process_table_block(block_lines):
    merged = merge_continuation_lines(block_lines)
    if len(merged) < 2 or not any('|' in ln for ln in merged):
        return block_lines
    if is_valid_table(merged):
        return block_lines  # already valid
    return fix_table_block(merged, block_lines[0])

def merge_continuation_lines(lines):
    merged = []
    current = None
    for line in lines:
        if '|' in line:
            if current is not None:
                merged.append(current)
            current = line.rstrip()
        elif line.strip():
            if current is not None:
                current += " " + line.strip()
            else:
                current = line.rstrip()
        else:
            if current is not None:
                merged.append(current)
                current = None
            merged.append(line)
    if current is not None:
        merged.append(current)
    return merged

def parse_row(line):
    s = line.strip()
    if s.startswith('|'):
        s = s[1:]
    if s.endswith('|'):
        s = s[:-1]
    return [cell.strip() for cell in s.split('|')]

def is_separator_cell(cell):
    return re.fullmatch(r':?-{3,}:?', cell.strip()) is not None

def is_separator_row(cells):
    return all(is_separator_cell(cell) for cell in cells if cell.strip())

def is_valid_table(lines):
    if len(lines) < 2:
        return False
    rows = [parse_row(ln) for ln in lines if '|' in ln]
    if len(rows) < 2:
        return False
    if not is_separator_row(rows[1]):
        return False
    col_count = len(rows[0])
    return all(len(row) == col_count for row in rows)

def detect_table_style(line):
    s = line.strip()
    return (s.startswith('|'), s.endswith('|'))

def rebuild_row(cells, style):
    row = " | ".join(cells)
    if style[0]:
        row = "|" + row
    if style[1]:
        row = row + "|"
    return row

def normalize_row(row, target_cols):
    if len(row) < target_cols:
        return row + [''] * (target_cols - len(row))
    elif len(row) > target_cols:
        return row[:target_cols-1] + [" ".join(row[target_cols-1:])]
    return row

def detect_separator_pattern(parsed_rows):
    if len(parsed_rows) < 3:
        return False
    sep_indices = [i for i, row in enumerate(parsed_rows) if is_separator_row(row)]
    total_odds = (len(parsed_rows) - 1) // 2
    return len(sep_indices) >= total_odds and all(i % 2 == 1 for i in sep_indices)

def fix_table_block(merged_lines, first_line):
    parsed = [parse_row(ln) for ln in merged_lines]
    style = detect_table_style(first_line)
    max_cols = max(len(r) for r in parsed)
    parsed = [normalize_row(r, max_cols) for r in parsed]
    fixed = []
    if detect_separator_pattern(parsed):
        # Use header then add a separator after each data row.
        fixed.append(parsed[0])
        fixed.append(['---'] * max_cols)
        idx = 1
        while idx < len(parsed):
            if is_separator_row(parsed[idx]):
                idx += 1
                continue
            fixed.append(parsed[idx])
            fixed.append(['---'] * max_cols)
            idx += 1
    else:
        # Standard table: header, one separator, then data rows.
        fixed.append(parsed[0])
        fixed.append(['---'] * max_cols)
        for row in parsed[2:]:
            if is_separator_row(row):
                continue
            fixed.append(row)
    return [rebuild_row(r, style) for r in fixed]

# Example usage:
if __name__ == "__main__":
    test_md = (
        "| ●| we have a limited customer base and limited sales and relationships with\n"
        "international customers;\n"
        "---|---|---  \n"
        "| ●| difficulty in managing multinational operations;\n"
        "---|---|---"
    )
    print(fix_invalid_markdown_tables(test_md))
```

### How It Works

1. **Collecting Table Blocks:**  
   The main function iterates over lines. Lines containing the pipe character are accumulated as part of a table block. When a non‑table line is reached, the current block is processed.

2. **Merging Continuation Lines:**  
   Lines without a pipe (but with content) are merged into the previous row—ensuring that multi‑line cell content is combined.

3. **Validation & Parsing:**  
   A table is deemed valid if it has at least two rows, the second row is a valid separator (using a regex that allows optional colons for alignment), and all rows have the same number of columns.  
   Each row is parsed by removing any extra leading or trailing pipes.

4. **Normalization & Fixing:**  
   If the table is invalid, rows are normalized (padded if too short or merged if too long) and the original table “style” (whether rows begin or end with a pipe) is preserved.  
   In cases where the table uses repeated separators (as in your examples), each data row is followed by an inserted standard separator.

5. **Rebuilding the Table:**  
   Finally, the rows are rebuilt into strings with consistent pipe formatting.

This hybrid implementation incorporates the best ideas from all four solutions and should correctly fix the kinds of invalid markdown tables you described while leaving valid ones untouched.