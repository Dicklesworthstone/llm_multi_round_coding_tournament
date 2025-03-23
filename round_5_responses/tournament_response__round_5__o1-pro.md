```python
import re

def fix_invalid_markdown_tables(markdown_text):
    lines = markdown_text.splitlines()
    out = []
    table_block = []
    in_table = False

    for line in lines:
        # Check if the line likely belongs to a table (contains '|')
        if '|' in line:
            table_block.append(line)
            in_table = True
        else:
            # If we were accumulating a table block, process it
            if in_table:
                out.extend(_process_table_block(table_block))
                table_block = []
                in_table = False
            # Add the non-table line
            out.append(line)

    # Handle any leftover table block at the end
    if table_block:
        out.extend(_process_table_block(table_block))

    return "\n".join(out)

def _process_table_block(block_lines):
    # Merge multi-line cells
    merged = _merge_continuation_lines(block_lines)
    # If it's already a valid table, leave it as is
    if _is_valid_table(merged):
        return block_lines
    # Otherwise, fix the invalid table
    fixed = _fix_invalid_table(merged)
    return fixed

def _merge_continuation_lines(lines):
    # Merges lines that don't contain '|' into the previous row's last cell
    merged = []
    current = None
    for ln in lines:
        if '|' in ln:
            # If we have a partial row accumulated, push it
            if current is not None:
                merged.append(current)
            current = ln
        else:
            # This line doesn't have '|', so treat it as continuation if there's a current row
            if ln.strip():
                if current is not None:
                    current += " " + ln.strip()
                else:
                    # If for some reason there's no current row, just start a new one
                    current = ln
            else:
                # Blank line: finalize current row, then keep blank line
                if current is not None:
                    merged.append(current)
                    current = None
                merged.append(ln)
    if current is not None:
        merged.append(current)
    return merged

def _is_valid_table(lines):
    # A valid table must have at least 2 lines, a separator row as line 2,
    # and consistent column counts across all rows
    if len(lines) < 2:
        return False
    rows = [_parse_row(ln) for ln in lines if '|' in ln]
    if len(rows) < 2:
        return False
    # Check if second row is a valid separator row
    if not _is_separator_row(rows[1]):
        return False
    # Check column count consistency
    col_count = len(rows[0])
    return all(len(r) == col_count for r in rows)

def _parse_row(line):
    s = line.strip()
    has_lead = s.startswith('|')
    has_tail = s.endswith('|')
    if has_lead:
        s = s[1:]
    if has_tail:
        s = s[:-1]
    return [c.strip() for c in s.split('|')]

def _is_separator_row(cells):
    # A separator row has cells that match :?-{3,}:?
    return all(_is_separator_cell(c) for c in cells if c.strip())

def _is_separator_cell(cell):
    return re.fullmatch(r':?-{3,}:?', cell.strip()) is not None

def _fix_invalid_table(lines):
    # Parse rows
    parsed_rows = [_parse_row(ln) for ln in lines if '|' in ln]
    if not parsed_rows:
        return lines  # Nothing to fix

    # Get style from the first line (leading/trailing pipes)
    first_line = lines[0]
    style = (first_line.strip().startswith('|'), first_line.strip().endswith('|'))

    # Determine max columns
    max_cols = max(len(r) for r in parsed_rows)

    # Check for repeated-separator pattern
    repeated_sep = _detect_repeated_separators(parsed_rows)

    # Normalize rows to have consistent column count
    parsed_rows = [_normalize_row(r, max_cols) for r in parsed_rows]

    # We'll build the fixed table depending on repeated-separator usage
    fixed = []

    # Always treat the first row as header
    fixed.append(_rebuild_row(parsed_rows[0], style))
    # Then insert a single separator row right after the header
    fixed.append(_rebuild_row(['---'] * max_cols, style))

    if repeated_sep:
        # If repeated separators are detected, we place a separator after every data row
        i = 1
        while i < len(parsed_rows):
            # Skip original separator rows
            if _is_separator_row(parsed_rows[i]):
                i += 1
                continue
            fixed.append(_rebuild_row(parsed_rows[i], style))
            fixed.append(_rebuild_row(['---'] * max_cols, style))
            i += 1
    else:
        # Otherwise, just copy data rows, skipping any original separator lines
        for r in parsed_rows[1:]:
            if not _is_separator_row(r):
                fixed.append(_rebuild_row(r, style))

    return fixed

def _detect_repeated_separators(rows):
    # Returns True if more than half of the "odd" rows are separator rows
    # i.e., a pattern: header row (index 0), separator row (index 1), then
    # for index 2, 3, 4, ... we see if there's a repeating pattern
    if len(rows) < 3:
        return False
    # We'll look at rows from index 1 onwards (some solutions skip index 1 because that's
    # the standard separator row). Let's see if there's a consistent pattern at odd indices.
    odd_sep_count = 0
    total_odd = 0
    for i in range(1, len(rows), 2):
        total_odd += 1
        if _is_separator_row(rows[i]):
            odd_sep_count += 1
    return odd_sep_count >= total_odd / 2.0

def _normalize_row(row, target_cols):
    if len(row) < target_cols:
        return row + [''] * (target_cols - len(row))
    elif len(row) > target_cols:
        # merge excess into the last cell
        return row[:target_cols-1] + [' '.join(row[target_cols-1:])]
    return row

def _rebuild_row(cells, style):
    # Rebuild a row from cells, respecting leading/trailing pipe style
    row_str = " | ".join(cells)
    if style[0]:
        row_str = "| " + row_str
    if style[1]:
        row_str += " |"
    return row_str
```

Explanation of the unified “best-of-all-worlds” approach:

• **Block detection**: Like the majority of solutions, it looks for lines that contain a pipe character, treating them as potential table lines. Consecutive lines with pipes are grouped into a single table block, and everything else is passed through unmodified.

• **Merging multi-line cells**: Borrowing from several solutions (e.g., O1-pro, o3-mini-high), `_merge_continuation_lines` attaches lines without pipes to the previous line’s cell content. This allows partial lines in multi-line cells to be combined properly.

• **Validation check**: Uses `_is_valid_table` logic to detect if the table is already correctly structured (≥ 2 rows, second row is a separator, and all rows have the same column count). If valid, leaves the block alone.

• **Fixing invalid tables**: 
  1. `_parse_row` strips leading/trailing pipes, then splits by `|`. 
  2. `_detect_repeated_separators` uses a similar technique as O1-pro to see if the table has a repeated-separator format after each row. 
  3. `_normalize_row` unifies columns across the table by either padding short rows or merging extra columns into the last cell. 
  4. The final rebuild inserts either a single separator row under the header or repeated separators after each data row if the repeated-separator pattern is detected.

• **Minimal invasion**: If a table is valid, we don’t touch it. Otherwise, we only adjust columns, add or remove redundant separators, and preserve leading/trailing pipe style from the very first line of the table.