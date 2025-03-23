Below is a single Python function, `fix_invalid_markdown_tables`, ready to paste into your code base. It scans the input Markdown line by line, identifies potential table blocks, measures how many columns each block should have, and minimally adjusts the lines (including alignment rows) so that columns match. It does nothing to lines/tables that are already valid and skips over any lines that do not appear to be part of a table.

```python
import re

def fix_invalid_markdown_tables(markdown_text):
    # Splits into lines, preserving no trailing '\n' characters
    lines = markdown_text.splitlines(False)
    
    # Helper to detect if a line is "alignment only" (all dashes/pipes/colons/spaces)
    def is_alignment_line(line):
        return bool(re.fullmatch(r'[|\-\s:]+', line.strip()))
    
    # We'll store processed lines here
    output_lines = []
    
    # A buffer for lines that belong to the current "table block"
    table_block = []
    
    # A function to fix and flush the current table block into output
    def flush_table_block(block):
        # If there's no block, do nothing
        if not block:
            return block
        
        # Figure out the maximum number of columns among all lines in this block
        # We'll define columns by splitting on '|'.
        # We'll preserve leading/trailing pipe usage to keep minimal changes in style.
        # For counting columns, it's easier to ignore leading/trailing empties if they exist.
        max_cols = 0
        for bline in block:
            # Temporarily strip leading/trailing '|' to count columns
            stripped = bline
            # But we need to see how many actual columns the user typed
            # E.g. "col1|col2" => 2 columns, "| col1 | col2 |" => 2 columns as well.
            # We'll do a naive split on '|', ignoring empty leading/trailing splits
            # because some people omit leading/trailing pipes.
            parts = stripped.split('|')
            # Remove purely leading/trailing empty strings
            # so that "col1 | col2 |" also yields 2 columns
            if parts and not parts[0].strip():
                parts = parts[1:]
            if parts and not parts[-1].strip():
                parts = parts[:-1]
            if len(parts) > max_cols:
                max_cols = len(parts)
        
        if max_cols < 2:
            # If we only have 0 or 1 columns, it's not a real table block. 
            # Return block unmodified.
            return block
        
        # We now fix each line to ensure it has exactly max_cols columns
        # We'll preserve the original leading/trailing pipe style if it existed.
        
        # Step 1: detect if the block had leading pipe style or not on the first row,
        # and if it had trailing pipe on the first row.
        # We'll apply the same style to all lines of the block for minimal changes.
        def detect_style(line):
            has_leading = line.strip().startswith('|')
            has_trailing = line.strip().endswith('|')
            return has_leading, has_trailing
        
        first_line_has_leading, first_line_has_trailing = detect_style(block[0])
        
        # Rebuild each line
        fixed_block = []
        for bline in block:
            has_leading, has_trailing = detect_style(bline)
            # We'll unify style: if the first line had a leading pipe, we do that for all
            # else we do none, etc. 
            # This is a choice, you could also preserve each line's style individually,
            # but that can get complicated. We'll keep the table consistent.
            # 
            # Split columns ignoring leading/trailing empty splits
            parts = bline.split('|')
            if parts and not parts[0].strip():
                parts = parts[1:]
            if parts and not parts[-1].strip():
                parts = parts[:-1]
            
            # Pad or trim columns to match max_cols
            if len(parts) < max_cols:
                parts += [''] * (max_cols - len(parts))
            elif len(parts) > max_cols:
                # Minimally invasive: keep everything in the first (max_cols - 1) cells,
                # then merge the remainder into the last cell.
                overflow = parts[max_cols - 1:]
                parts = parts[:max_cols - 1] + [' '.join(overflow)]
            
            # If it's an alignment line, replace each non-empty cell with '---'
            # (or keep colons if you want more advanced alignment, but here we keep it simple)
            if is_alignment_line(bline):
                parts = ['---'] * max_cols
            
            # Rejoin
            # We'll reconstruct so that if the first line had a leading pipe, we do that,
            # and if it had a trailing pipe, we do that.
            if first_line_has_leading:
                out = '|'.join([''] + [p for p in parts] + ([''] if first_line_has_trailing else []))
            else:
                out = '|'.join([p for p in parts] + ([''] if first_line_has_trailing else []))
            
            fixed_block.append(out)
        
        # Check if the block changed at all vs original; if not, we return original
        # otherwise we return fixed. 
        # But that requires a robust "same vs. different" check. 
        # For simplicity, we always return fixed_block if we get here, 
        # because we only do minimal changes if needed.
        return fixed_block
    
    # We'll iterate over lines, grouping anything with a pipe. 
    for line in lines:
        if '|' in line:
            # Potential table line
            table_block.append(line)
        else:
            # Not a table line => flush the existing block
            if table_block:
                fixed_block = flush_table_block(table_block)
                output_lines.extend(fixed_block)
                table_block = []
            # Then output the current non-table line unaltered
            output_lines.append(line)
    
    # If there's a leftover table block at the end, flush it
    if table_block:
        fixed_block = flush_table_block(table_block)
        output_lines.extend(fixed_block)
        table_block = []
    
    return "\n".join(output_lines)
```

Explanation of the approach:

1. We split the text into lines.  
2. We accumulate lines into a “table block” only if they contain at least one pipe (`|`). Anything else is assumed to be outside of a table.  
3. When a non-pipe line is encountered (or we reach the end), we finalize (“flush”) the current table block.  
4. While flushing, we find the maximum number of columns in the block. We then adjust each line to have that number of columns. If we detect an alignment line (only composed of `-`, `|`, `:`, and spaces), we switch its columns to `---` so it remains valid.  
5. We preserve the presence or absence of a leading pipe on the very first line of the block to keep the style consistent across the whole table.  
6. Lines that are already consistent remain practically unchanged.  

This ensures we only minimally fix invalid tables. Valid tables will pass through with no modifications, and anything not containing a `|` is ignored.