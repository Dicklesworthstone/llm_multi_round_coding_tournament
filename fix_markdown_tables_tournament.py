import re


class Claude37_round_1:
    """
    Implementation based on Claude3.7's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        """
        Fix invalid markdown tables in a minimally invasive way.
        
        This function analyzes markdown text for tables, identifies if they are invalid,
        diagnoses the issues, and fixes them while preserving as much of the original 
        structure as possible. Valid tables and non-table content remain unchanged.
        
        Args:
            markdown_text (str): The markdown text containing potential tables to fix
            
        Returns:
            str: The markdown text with fixed tables
        """
        # Split the text into blocks (potential tables and other content)
        blocks = re.split(r'\n\s*\n', markdown_text)
        fixed_blocks = []
        
        for block in blocks:
            # Check if the block might be a table (contains pipe characters)
            if '|' in block and any(re.search(r'[-]+', line) for line in block.split('\n') if '|' in line):
                fixed_block = Claude37_round_1.fix_table(block)
                fixed_blocks.append(fixed_block)
            else:
                # Not a table, keep as is
                fixed_blocks.append(block)
        
        # Rejoin all blocks with appropriate spacing
        return '\n\n'.join(fixed_blocks)

    @staticmethod
    def fix_table(table_text):
        """
        Fix an individual markdown table.
        
        Args:
            table_text (str): The text of a potential markdown table
            
        Returns:
            str: The fixed table text
        """
        # Split the table into lines
        lines = [line for line in table_text.split('\n') if line.strip()]
        
        # Identify all separator rows (lines containing only |, -, :, and spaces)
        separator_indices = [
            i for i, line in enumerate(lines) 
            if i > 0 and re.match(r'^[\s|:-]+$', line) and '---' in line
        ]
        
        # If no separator rows, this may not be a table or it's too malformed
        if not separator_indices:
            return table_text
        
        # First, let's analyze the table structure
        max_columns = 0
        for line in lines:
            cell_count = len(line.split('|')) - 1  # -1 because split creates an extra item
            max_columns = max(max_columns, cell_count)
        
        # Detect if this is a table with repeated separators
        repeated_separators = len(separator_indices) > 1 and separator_indices[0] + 1 != separator_indices[1]
        
        if repeated_separators:
            # This is a table with a separator row after each data row
            # We'll fix by removing all but the first separator
            header_row = lines[0]
            first_separator = lines[separator_indices[0]]
            data_rows = []
            
            # Collect all data rows, skipping separator rows
            current_index = 0
            for i, line in enumerate(lines):
                # Skip all separator rows except the first one
                if i in separator_indices and i != separator_indices[0]:
                    continue
                # Include all non-separator rows
                if i not in separator_indices:
                    data_rows.append(line)
            
            # Reconstruct the table with a single separator row
            fixed_lines = [data_rows[0], first_separator] + data_rows[1:]
        else:
            # This is a table with a structure issue but not repeated separators
            # Normalize column count
            fixed_lines = []
            for i, line in enumerate(lines):
                cells = line.split('|')
                
                # Add cells if needed
                while len(cells) - 1 < max_columns:
                    cells.append('')
                
                # Trim excess cells
                cells = cells[:max_columns + 1]
                
                # If this is a separator row, ensure it has proper format
                if i in separator_indices:
                    separator_cells = []
                    for cell in cells[1:]:  # Skip the first empty cell
                        # Create a proper separator cell with at least 3 dashes
                        separator_cells.append('---')
                    
                    separator_line = '|' + '|'.join(separator_cells) + '|'
                    fixed_lines.append(separator_line)
                else:
                    # For regular rows, just join the cells
                    fixed_line = '|' + '|'.join(cells[1:]) + '|'
                    fixed_lines.append(fixed_line)
        
        # Handle specific case for multi-line content within cells
        fixed_table = '\n'.join(fixed_lines)
        
        # Check if we still have an invalid table (e.g., multi-line content in cells)
        # If so, try advanced fixing
        if Claude37_round_1.is_table_valid(fixed_table):
            return fixed_table
        else:
            return Claude37_round_1.fix_complex_table(table_text)

    @staticmethod
    def is_table_valid(table_text):
        """
        Check if a markdown table is valid.
        
        Args:
            table_text (str): The table text to check
            
        Returns:
            bool: True if the table is valid, False otherwise
        """
        lines = [line for line in table_text.split('\n') if line.strip()]
        
        # A valid table needs at least 2 rows (header and data)
        if len(lines) < 2:
            return False
        
        # Check for separator row
        separator_line = lines[1]
        if not all(c in '|:- ' for c in separator_line):
            return False
        
        # Count columns in header
        header_columns = len(lines[0].split('|')) - 1
        
        # Count columns in separator
        separator_columns = len(separator_line.split('|')) - 1
        
        # All rows should have the same number of columns
        if header_columns != separator_columns:
            return False
        
        for line in lines[2:]:
            if len(line.split('|')) - 1 != header_columns:
                return False
        
        return True

    @staticmethod
    def fix_complex_table(table_text):
        """
        Fix complex tables with multi-line content and other issues.
        
        Args:
            table_text (str): The text of a complex markdown table
            
        Returns:
            str: The fixed table text
        """
        # Split into lines
        lines = [line for line in table_text.split('\n') if line.strip()]
        
        # Identify all separator rows (lines containing only |, -, :, and spaces)
        separator_indices = [
            i for i, line in enumerate(lines) 
            if re.match(r'^[\s|:-]+$', line) and '---' in line
        ]
        
        # If the table has multiple separator rows or irregular structure
        if len(separator_indices) > 1:
            # Process each section as a separate mini-table
            rows = []
            current_row = []
            
            # First, join multi-line content within cells
            i = 0
            while i < len(lines):
                line = lines[i]
                
                # If this is a separator row, add it as is
                if i in separator_indices:
                    if current_row:
                        rows.append(current_row)
                        current_row = []
                    rows.append([line])
                    i += 1
                    continue
                
                # Start a new row
                current_row = [line]
                
                # Look ahead to see if the next line is part of this row
                # (not a separator and doesn't start with a pipe)
                j = i + 1
                while j < len(lines) and j not in separator_indices and not lines[j].strip().startswith('|'):
                    current_row[-1] += ' ' + lines[j].strip()
                    j += 1
                
                i = j
                
                # If we've reached the end or a separator, add the current row
                if i >= len(lines) or i in separator_indices:
                    if current_row:
                        rows.append(current_row)
                        current_row = []
            
            # Add any remaining rows
            if current_row:
                rows.append(current_row)
            
            # Now construct a proper table from the collected rows
            header_row = rows[0][0] if rows else ''
            
            # Find the first separator row
            first_separator_idx = next((i for i, row in enumerate(rows) if '---' in row[0]), -1)
            
            if first_separator_idx == -1:
                # No separator found, create one
                cell_count = len(header_row.split('|')) - 1
                separator_row = '|' + '|'.join(['---'] * cell_count) + '|'
                new_rows = [header_row, separator_row]
            else:
                separator_row = rows[first_separator_idx][0]
                new_rows = [header_row, separator_row]
                
                # Add all non-separator rows
                for i, row in enumerate(rows):
                    if i != 0 and i != first_separator_idx:
                        new_rows.append(row[0])
            
            # Normalize column count for all rows
            max_columns = max(len(row.split('|')) - 1 for row in new_rows)
            
            for i, row in enumerate(new_rows):
                cells = row.split('|')
                # Add cells if needed
                while len(cells) - 1 < max_columns:
                    cells.append('')
                # Trim excess cells
                cells = cells[:max_columns + 1]
                
                # If this is the separator row, ensure proper format
                if i == 1:
                    separator_cells = []
                    for cell in cells[1:]:
                        separator_cells.append('---')
                    new_rows[i] = '|' + '|'.join(separator_cells) + '|'
                else:
                    # For regular rows, just join the cells
                    new_rows[i] = '|' + '|'.join(cells[1:]) + '|'
            
            return '\n'.join(new_rows)
        else:
            # Handle tables with irregular alignment or structure but single separator
            if separator_indices:
                # Extract header, separator, and data rows
                header = lines[0]
                separator = lines[separator_indices[0]]
                data_rows = [line for i, line in enumerate(lines) if i != 0 and i != separator_indices[0]]
                
                # Normalize column count
                max_columns = max(
                    len(header.split('|')) - 1,
                    len(separator.split('|')) - 1,
                    max((len(row.split('|')) - 1 for row in data_rows), default=0)
                )
                
                # Fix header
                header_cells = header.split('|')[1:-1]  # Remove first and last empty cells
                while len(header_cells) < max_columns:
                    header_cells.append('')
                header = '|' + '|'.join(header_cells) + '|'
                
                # Fix separator
                separator_cells = ['---'] * max_columns
                separator = '|' + '|'.join(separator_cells) + '|'
                
                # Fix data rows
                fixed_data_rows = []
                for row in data_rows:
                    cells = row.split('|')[1:-1]  # Remove first and last empty cells
                    while len(cells) < max_columns:
                        cells.append('')
                    fixed_data_rows.append('|' + '|'.join(cells) + '|')
                
                # Combine all rows
                return '\n'.join([header, separator] + fixed_data_rows)
            
            return table_text  # No valid structure found, return as is


class Grok3_round_1:
    """
    Implementation based on Grok3's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
    def split_row(row):
        """Splits a markdown row into cells, stripping whitespace."""
        return [part.strip() for part in row.split('|')]

    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        """
        Fixes invalid markdown tables in the input text while leaving valid tables and non-table content unchanged.
        
        Args:
            markdown_text (str): The markdown text containing potential tables.
        
        Returns:
            str: The markdown text with invalid tables fixed.
        """
        # Split text into lines
        lines = markdown_text.splitlines()
        
        # Group lines into blocks separated by empty lines
        blocks = []
        current_block = []
        for line in lines:
            if line.strip():
                current_block.append(line)
            else:
                if current_block:
                    blocks.append(current_block)
                    current_block = []
        if current_block:
            blocks.append(current_block)
        
        # Process each block
        fixed_blocks = []
        for block in blocks:
            # Count lines with pipes to determine if it's a potential table
            pipe_lines = sum(1 for line in block if '|' in line)
            if pipe_lines < 3:
                # Not a table (fewer than 3 lines with '|'), leave unchanged
                fixed_blocks.append('\n'.join(block))
                continue
            
            # Split each line into cells and find the maximum number of cells
            cell_lists = [Grok3_round_1.split_row(line) for line in block]
            num_columns = max(len(cells) for cells in cell_lists)
            
            # Reconstruct the table: header, separator, content rows
            fixed_lines = []
            # Header (first line)
            header_cells = Grok3_round_1.split_row(block[0])
            if len(header_cells) < num_columns:
                header_cells += [''] * (num_columns - len(header_cells))
            fixed_lines.append('| ' + ' | '.join(header_cells) + ' |')
            
            # Separator
            separator = '| ' + ' | '.join(['---' for _ in range(num_columns)]) + ' |'
            fixed_lines.append(separator)
            
            # Content rows (remaining lines)
            for line in block[1:]:
                cells = Grok3_round_1.split_row(line)
                if len(cells) < num_columns:
                    cells += [''] * (num_columns - len(cells))
                fixed_line = '| ' + ' | '.join(cells) + ' |'
                fixed_lines.append(fixed_line)
            
            fixed_blocks.append('\n'.join(fixed_lines))
        
        # Join blocks with double newlines
        return '\n\n'.join(fixed_blocks)


class O1_pro_round_1:
    """
    Implementation based on O1-pro's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
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


class O3_mini_high_round_1:
    """
    Implementation based on O3-mini-high's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(text):
        def is_divider_row(cells):
            pat = re.compile(r'^\s*:?-{3,}:?\s*$')
            return all(pat.match(cell) for cell in cells if cell.strip() != '')
        
        def merge_block(block):
            merged = []
            for line in block:
                if '|' in line:
                    merged.append(line.rstrip())
                elif merged and line.strip():
                    merged[-1] += ' ' + line.strip()
            return merged
        
        def process_table_block(block):
            merged = merge_block(block)
            rows = []
            for line in merged:
                s = line.strip()
                if s.startswith('|'): s = s[1:]
                if s.endswith('|'): s = s[:-1]
                cells = [c.strip() for c in s.split('|')]
                rows.append(cells)
            max_cols = max(len(r) for r in rows) if rows else 0
            fixed_rows = []
            for r in rows:
                if len(r) < max_cols:
                    r += ['']*(max_cols-len(r))
                elif len(r) > max_cols:
                    r = r[:max_cols]
                fixed_rows.append(r)
            out = []
            if fixed_rows:
                header = fixed_rows[0]
                out.append(header)
                idx = 1
                # if second row exists and is a valid divider row, use it; otherwise insert one.
                if len(fixed_rows) > 1 and is_divider_row(fixed_rows[1]):
                    out.append(fixed_rows[1])
                    idx = 2
                else:
                    out.append(['---'] * max_cols)
                # add remaining rows that are not divider rows
                for r in fixed_rows[idx:]:
                    if not is_divider_row(r):
                        out.append(r)
            return [f"| {' | '.join(r)} |" for r in out]
        
        def is_table_line(line):
            return '|' in line
        
        lines = text.splitlines()
        out_lines = []
        i = 0
        while i < len(lines):
            if is_table_line(lines[i]):
                block = []
                # gather contiguous lines that are table or continuation lines
                while i < len(lines) and (is_table_line(lines[i]) or (block and lines[i].strip() and '|' not in lines[i])):
                    block.append(lines[i])
                    i += 1
                fixed_block = process_table_block(block)
                out_lines.extend(fixed_block)
            else:
                out_lines.append(lines[i])
                i += 1
        return "\n".join(out_lines)

class Claude37_round_2:
    """
    Implementation based on Claude3.7's solution for fixing invalid markdown tables.
    Early version with basic table identification and repair.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        """
        Fix invalid markdown tables in the input text while preserving valid tables
        and non-table content completely unchanged.
        
        Args:
            markdown_text (str): Input markdown text
            
        Returns:
            str: Markdown text with fixed tables
        """
        lines = markdown_text.splitlines()
        result_lines = []
        table_lines = []
        in_table = False
        
        # Process each line
        for line in lines:
            if '|' in line:
                # Potential table line
                if not in_table:
                    in_table = True
                table_lines.append(line)
            else:
                # Non-table line
                if in_table:
                    # End of table, process it
                    fixed_table = Claude37_round_2.fix_table(table_lines)
                    result_lines.extend(fixed_table)
                    table_lines = []
                    in_table = False
                
                # Add the non-table line
                result_lines.append(line)
        
        # Handle any remaining table at the end
        if in_table:
            fixed_table = Claude37_round_2.fix_table(table_lines)
            result_lines.extend(fixed_table)
        
        return '\n'.join(result_lines)
    
    @staticmethod
    def fix_table(lines):
        """
        Fix a table represented by a list of lines.
        
        Args:
            lines (list): Table lines
            
        Returns:
            list: Fixed table lines
        """
        if len(lines) < 2:
            return lines  # Not enough lines to be a valid table
        
        # Extract table styling (leading/trailing pipes)
        first_line = lines[0].strip()
        has_leading = first_line.startswith('|')
        has_trailing = first_line.endswith('|')
        
        # Parse rows
        rows = [Claude37_round_2.parse_row(line) for line in lines]
        
        # Find max column count
        max_cols = max(len(row) for row in rows)
        
        # Check if second row is a separator
        is_separator = Claude37_round_2.is_separator_row(rows[1]) if len(rows) > 1 else False
        
        # Build fixed table
        fixed_lines = []
        
        # Add header row
        header = Claude37_round_2.normalize_row(rows[0], max_cols)
        fixed_lines.append(Claude37_round_2.rebuild_row(header, has_leading, has_trailing))
        
        # Add separator row if missing
        if not is_separator:
            separator = ['---'] * max_cols
            fixed_lines.append(Claude37_round_2.rebuild_row(separator, True, True))
        else:
            fixed_lines.append(lines[1])  # Keep original separator
        
        # Add data rows
        for i in range(1 if not is_separator else 2, len(rows)):
            if not Claude37_round_2.is_separator_row(rows[i]):  # Skip additional separators
                data_row = Claude37_round_2.normalize_row(rows[i], max_cols)
                fixed_lines.append(Claude37_round_2.rebuild_row(data_row, has_leading, has_trailing))
        
        return fixed_lines
    
    @staticmethod
    def parse_row(line):
        """
        Parse a table row into cells.
        """
        parts = line.split('|')
        if line.strip().startswith('|'):
            parts = parts[1:]
        if line.strip().endswith('|'):
            parts = parts[:-1]
        return [p.strip() for p in parts]
    
    @staticmethod
    def is_separator_row(cells):
        """
        Check if cells represent a separator row.
        """
        if not cells:
            return False
        return all(re.fullmatch(r':?-{3,}:?', cell.strip()) for cell in cells if cell.strip())
    
    @staticmethod
    def normalize_row(row, target_cols):
        """
        Normalize a row to have the target number of columns.
        """
        if len(row) < target_cols:
            return row + [''] * (target_cols - len(row))
        elif len(row) > target_cols:
            return row[:target_cols-1] + [' '.join(row[target_cols-1:])]
        return row
    
    @staticmethod
    def rebuild_row(cells, has_leading, has_trailing):
        """
        Rebuild a table row from its cells.
        """
        row = ' | '.join(cells)
        if has_leading:
            row = '| ' + row
        if has_trailing:
            row = row + ' |'
        return row


class Grok3_round_2:
    """
    Implementation based on Grok3's solution for fixing invalid markdown tables.
    Early version with basic functionality.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        """
        Fixes invalid Markdown tables in the input text while leaving valid tables and non-table content unchanged.
        """
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
                    fixed_table = Grok3_round_2.process_table(table_block)
                    output.extend(fixed_table)
                    table_block = []
                    in_table = False
                output.append(line)
                
        if table_block:
            fixed_table = Grok3_round_2.process_table(table_block)
            output.extend(fixed_table)
            
        return '\n'.join(output)
    
    @staticmethod
    def process_table(block):
        """
        Process a potential table block, fixing it if invalid.
        """
        if len(block) < 2:
            return block  # Not enough lines to be a table
            
        # Check if table is valid
        if Grok3_round_2.is_valid_table(block):
            return block
            
        # Fix the table
        rows = [Grok3_round_2.split_row(line) for line in block]
        max_cols = max(len(row) for row in rows)
        
        # Determine style from first row
        style = Grok3_round_2.get_table_style(block[0])
        
        # Fix rows
        fixed = []
        
        # Add header
        header = Grok3_round_2.pad_row(rows[0], max_cols)
        fixed.append(Grok3_round_2.format_row(header, style))
        
        # Add separator
        if len(rows) > 1 and Grok3_round_2.is_separator_row(rows[1]):
            # If second row is a separator, use it
            fixed.append(block[1])
            data_start = 2
        else:
            # Otherwise, add a standard separator
            separator = ['---'] * max_cols
            fixed.append(Grok3_round_2.format_row(separator, style))
            data_start = 1
            
        # Add data rows
        for i in range(data_start, len(rows)):
            if not Grok3_round_2.is_separator_row(rows[i]):
                fixed_row = Grok3_round_2.pad_row(rows[i], max_cols)
                fixed.append(Grok3_round_2.format_row(fixed_row, style))
                
        return fixed
    
    @staticmethod
    def is_valid_table(lines):
        """
        Check if a table is valid.
        """
        if len(lines) < 2:
            return False
            
        rows = [Grok3_round_2.split_row(line) for line in lines]
        
        # Second row must be separator
        if not Grok3_round_2.is_separator_row(rows[1]):
            return False
            
        # All rows must have same number of columns
        col_count = len(rows[0])
        return all(len(row) == col_count for row in rows)
    
    @staticmethod
    def split_row(line):
        """
        Split a row into cells.
        """
        parts = line.split('|')
        if line.strip().startswith('|'):
            parts = parts[1:]
        if line.strip().endswith('|'):
            parts = parts[:-1]
        return [cell.strip() for cell in parts]
    
    @staticmethod
    def is_separator_row(cells):
        """
        Check if cells form a separator row.
        """
        return all(re.fullmatch(r':?-{3,}:?', cell) for cell in cells if cell)
    
    @staticmethod
    def get_table_style(line):
        """
        Get the table style (leading/trailing pipes).
        """
        stripped = line.strip()
        return (stripped.startswith('|'), stripped.endswith('|'))
    
    @staticmethod
    def pad_row(cells, target_cols):
        """
        Pad or trim a row to the target number of columns.
        """
        if len(cells) < target_cols:
            return cells + [''] * (target_cols - len(cells))
        elif len(cells) > target_cols:
            return cells[:target_cols-1] + [' '.join(cells[target_cols-1:])]
        return cells
    
    @staticmethod
    def format_row(cells, style):
        """
        Format a row with the specified style.
        """
        row = ' | '.join(cells)
        if style[0]:
            row = '| ' + row
        if style[1]:
            row = row + ' |'
        return row


class O1_pro_round_2:
    """
    Implementation based on O1-pro's solution for fixing invalid markdown tables.
    Early version with basic functionality.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        """
        Fix invalid markdown tables in the text.
        """
        lines = markdown_text.splitlines()
        out = []
        block = []
        in_table = False
        
        for line in lines:
            if '|' in line:
                block.append(line)
                in_table = True
            else:
                if in_table:
                    out.extend(O1_pro_round_2.fix_table_block(block))
                    block = []
                    in_table = False
                out.append(line)
                
        if block:
            out.extend(O1_pro_round_2.fix_table_block(block))
            
        return '\n'.join(out)
    
    @staticmethod
    def fix_table_block(block):
        """
        Fix a table block if it's invalid.
        """
        # Check if it's a valid table
        if O1_pro_round_2.is_valid_table(block):
            return block
            
        # Parse rows
        rows = [O1_pro_round_2.parse_row(line) for line in block]
        max_cols = max(len(row) for row in rows)
        
        # Get table style
        style = O1_pro_round_2.get_style(block[0])
        
        # Fix rows
        fixed = []
        
        # Add header row
        header = O1_pro_round_2.normalize_row(rows[0], max_cols)
        fixed.append(O1_pro_round_2.rebuild_row(header, style))
        
        # Add separator row
        if len(rows) > 1 and O1_pro_round_2.is_separator_row(rows[1]):
            # Use existing separator
            fixed.append(block[1])
            data_start = 2
        else:
            # Add new separator
            fixed.append(O1_pro_round_2.rebuild_row(['---'] * max_cols, style))
            data_start = 1
            
        # Add data rows
        for i in range(data_start, len(rows)):
            if not O1_pro_round_2.is_separator_row(rows[i]):
                data_row = O1_pro_round_2.normalize_row(rows[i], max_cols)
                fixed.append(O1_pro_round_2.rebuild_row(data_row, style))
                
        return fixed
    
    @staticmethod
    def is_valid_table(lines):
        """
        Check if a table is valid.
        """
        if len(lines) < 2:
            return False
            
        rows = [O1_pro_round_2.parse_row(line) for line in lines]
        
        # Check second row is separator
        if len(rows) < 2 or not O1_pro_round_2.is_separator_row(rows[1]):
            return False
            
        # Check consistent column count
        col_count = len(rows[0])
        return all(len(row) == col_count for row in rows)
    
    @staticmethod
    def parse_row(line):
        """
        Parse a row into cells.
        """
        s = line.strip()
        has_lead = s.startswith('|')
        has_tail = s.endswith('|')
        
        if has_lead:
            s = s[1:]
        if has_tail:
            s = s[:-1]
            
        return [c.strip() for c in s.split('|')]
    
    @staticmethod
    def is_separator_row(cells):
        """
        Check if cells form a separator row.
        """
        return all(re.fullmatch(r':?-{3,}:?', c.strip()) for c in cells if c.strip())
    
    @staticmethod
    def get_style(line):
        """
        Get table style (leading/trailing pipes).
        """
        s = line.strip()
        return (s.startswith('|'), s.endswith('|'))
    
    @staticmethod
    def normalize_row(row, target_cols):
        """
        Normalize row to have target number of columns.
        """
        if len(row) < target_cols:
            return row + [''] * (target_cols - len(row))
        elif len(row) > target_cols:
            return row[:target_cols-1] + [' '.join(row[target_cols-1:])]
        return row
    
    @staticmethod
    def rebuild_row(cells, style):
        """
        Rebuild row with specified style.
        """
        row = ' | '.join(cells)
        if style[0]:
            row = '| ' + row
        if style[1]:
            row = row + ' |'
        return row


class O3_mini_high_round_2:
    """
    Implementation based on o3-mini-high's solution for fixing invalid markdown tables.
    Early version with basic functionality.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        """
        Fix invalid markdown tables in the text.
        """
        lines = markdown_text.splitlines()
        out = []
        block = []
        in_table = False
        
        for line in lines:
            if '|' in line:
                block.append(line)
                in_table = True
            else:
                if in_table:
                    out.extend(O3_mini_high_round_2.process_table(block))
                    block = []
                    in_table = False
                out.append(line)
                
        if block:
            out.extend(O3_mini_high_round_2.process_table(block))
            
        return '\n'.join(out)
    
    @staticmethod
    def process_table(block):
        """
        Process a table block, fixing it if invalid.
        """
        if len(block) < 2:
            return block
            
        # Check if valid
        if O3_mini_high_round_2.is_valid_table(block):
            return block
            
        # Fix table
        parsed = [O3_mini_high_round_2.parse_row(line) for line in block]
        max_cols = max(len(row) for row in parsed)
        style = O3_mini_high_round_2.get_style(block[0])
        
        # Fix rows
        fixed = []
        
        # Header
        header = O3_mini_high_round_2.normalize_row(parsed[0], max_cols)
        fixed.append(O3_mini_high_round_2.rebuild_row(header, style))
        
        # Separator
        separator = ['---'] * max_cols
        fixed.append(O3_mini_high_round_2.rebuild_row(separator, style))
        
        # Data rows
        for i in range(1, len(parsed)):
            if not O3_mini_high_round_2.is_separator_row(parsed[i]):
                data_row = O3_mini_high_round_2.normalize_row(parsed[i], max_cols)
                fixed.append(O3_mini_high_round_2.rebuild_row(data_row, style))
                
        return fixed
    
    @staticmethod
    def is_valid_table(lines):
        """
        Check if a table is valid.
        """
        if len(lines) < 2:
            return False
            
        parsed = [O3_mini_high_round_2.parse_row(line) for line in lines]
        
        # Check second row is separator
        if not O3_mini_high_round_2.is_separator_row(parsed[1]):
            return False
            
        # Check consistent columns
        col_count = len(parsed[0])
        return all(len(row) == col_count for row in parsed)
    
    @staticmethod
    def parse_row(line):
        """
        Parse a row into cells.
        """
        s = line.strip()
        if s.startswith('|'):
            s = s[1:]
        if s.endswith('|'):
            s = s[:-1]
        return [cell.strip() for cell in s.split('|')]
    
    @staticmethod
    def is_separator_row(cells):
        """
        Check if cells form a separator row.
        """
        return all(re.fullmatch(r':?-{3,}:?', cell) for cell in cells if cell)
    
    @staticmethod
    def get_style(line):
        """
        Get table style (leading/trailing pipes).
        """
        s = line.strip()
        return (s.startswith('|'), s.endswith('|'))
    
    @staticmethod
    def normalize_row(row, target_cols):
        """
        Normalize row to have target number of columns.
        """
        if len(row) < target_cols:
            return row + [''] * (target_cols - len(row))
        elif len(row) > target_cols:
            return row[:target_cols-1] + [' '.join(row[target_cols-1:])]
        return row
    
    @staticmethod
    def rebuild_row(cells, style):
        """
        Rebuild row with specified style.
        """
        row = ' | '.join(cells)
        if style[0]:
            row = '| ' + row
        if style[1]:
            row = row + ' |'
        return row
    
class Claude37_round_3:
    """
    Implementation based on Claude3.7's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        """
        Fix invalid markdown tables in the input text while preserving valid tables
        and non-table content completely unchanged.
        
        Args:
            markdown_text (str): Input markdown text
            
        Returns:
            str: Markdown text with fixed tables
        """
        lines = markdown_text.splitlines()
        result_lines = []
        table_block = []
        inside_table = False
        
        def flush_table_block():
            """Process the accumulated table block and add to result"""
            nonlocal table_block, result_lines
            
            if not table_block:
                return
                
            # Is this actually a table? (minimum requirement: contains pipe characters)
            if sum('|' in line for line in table_block) < 2:
                result_lines.extend(table_block)
                return
                
            # First, merge continuation lines
            merged_lines = Claude37_round_3.merge_continuation_lines(table_block)
            
            if Claude37_round_3.is_valid_table(merged_lines):
                # Table is already valid, preserve it exactly
                result_lines.extend(table_block)
            else:
                # Table is invalid, fix it
                fixed_table = Claude37_round_3.fix_invalid_table(merged_lines)
                result_lines.extend(fixed_table)
            
            table_block.clear()
        
        # Process each line
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if '|' in line:
                # Potential table line
                if not inside_table:
                    # Starting a new table
                    inside_table = True
                    table_block = [line]
                else:
                    # Continue current table
                    table_block.append(line)
            elif inside_table and line.strip():
                # Might be a continuation line for a multi-line cell
                table_block.append(line)
            else:
                # Not part of a table, flush any accumulated table block
                if inside_table:
                    flush_table_block()
                    inside_table = False
                
                # Add the non-table line
                result_lines.append(line)
            
            i += 1
        
        # Handle any remaining table at the end
        if inside_table:
            flush_table_block()
        
        return '\n'.join(result_lines)

    @staticmethod
    def merge_continuation_lines(lines):
        """
        Merge lines that might be continuations of multi-line cells.
        """
        merged = []
        for line in lines:
            if '|' in line:
                merged.append(line)
            elif merged and line.strip():
                # This appears to be a continuation of the previous line
                merged[-1] += ' ' + line.strip()
            else:
                # Empty line or something else
                merged.append(line)
        return merged

    @staticmethod
    def is_valid_table(lines):
        """
        Check if a markdown table is valid.
        """
        # Need at least 2 lines for a valid table
        if len(lines) < 2:
            return False
        
        # Parse rows into cells
        rows = [Claude37_round_3.parse_table_row(line) for line in lines]
        
        # Check if second row is a separator
        if not Claude37_round_3.is_separator_row(rows[1]):
            return False
        
        # Check column count consistency
        col_count = len(rows[0])
        if not all(len(row) == col_count for row in rows):
            return False
        
        return True

    @staticmethod
    def is_separator_row(cells):
        """
        Check if cells represent a separator row.
        """
        if not cells:
            return False
            
        # Each cell must match the separator pattern
        return all(re.fullmatch(r':?-{3,}:?', cell.strip()) for cell in cells if cell.strip())

    @staticmethod
    def parse_table_row(line):
        """
        Parse a table row into cells, handling leading/trailing pipes.
        """
        # Split by pipe
        parts = line.split('|')
        
        # Handle leading/trailing pipes
        if line.strip().startswith('|'):
            parts = parts[1:]
        if line.strip().endswith('|'):
            parts = parts[:-1]
        
        return [p.strip() for p in parts]

    @staticmethod
    def get_table_style(line):
        """
        Determine the table style (leading/trailing pipes) from a row.
        """
        stripped = line.strip()
        has_leading = stripped.startswith('|')
        has_trailing = stripped.endswith('|')
        return (has_leading, has_trailing)

    @staticmethod
    def get_separator_style(lines):
        """
        Get the style of separator rows in the table.
        """
        # Default separator style
        sep_style = "---"
        
        # Look for existing separator rows
        for line in lines:
            cells = Claude37_round_3.parse_table_row(line)
            if Claude37_round_3.is_separator_row(cells):
                # Found a separator row, extract style from first non-empty cell
                for cell in cells:
                    if cell.strip():
                        sep_style = cell.strip()
                        break
                break
        
        return sep_style

    @staticmethod
    def detect_table_pattern(lines):
        """
        Detect the pattern of the table (e.g., if it has separators after each row).
        """
        parsed_rows = [Claude37_round_3.parse_table_row(line) for line in lines]
        separator_indices = [i for i, row in enumerate(parsed_rows) if Claude37_round_3.is_separator_row(row)]
        
        pattern = {
            'has_separators_after_each_row': False,
            'separator_indices': separator_indices
        }
        
        # Check for repeating pattern (separator after each data row)
        if len(separator_indices) >= 2:
            # Check if separator rows appear in a regular pattern
            if separator_indices and all(i % 2 == 1 for i in separator_indices):
                pattern['has_separators_after_each_row'] = True
        
        return pattern

    @staticmethod
    def fix_invalid_table(lines):
        """
        Fix an invalid markdown table.
        """
        # Handle empty input
        if not lines:
            return []
            
        # Get table style from the first line
        style = Claude37_round_3.get_table_style(lines[0])
        
        # Get separator style
        sep_style = Claude37_round_3.get_separator_style(lines)
        
        # Detect table pattern
        pattern = Claude37_round_3.detect_table_pattern(lines)
        
        # Parse all rows
        parsed_rows = [Claude37_round_3.parse_table_row(line) for line in lines]
        
        # Calculate max columns across all rows
        max_cols = max(len(row) for row in parsed_rows) if parsed_rows else 0
        
        # Identify rows that are data rows vs separators
        is_separator = [Claude37_round_3.is_separator_row(row) for row in parsed_rows]
        
        # Create fixed output
        fixed_lines = []
        
        if pattern['has_separators_after_each_row']:
            # Special case: table has separator after each row (seen in examples)
            # Start with header
            header = Claude37_round_3.normalize_row(parsed_rows[0], max_cols)
            fixed_lines.append(Claude37_round_3.rebuild_row(header, style[0], style[1]))
            
            # Add required separator after header
            separator = [sep_style] * max_cols
            fixed_lines.append(Claude37_round_3.rebuild_row(separator, style[0], style[1]))
            
            # Process remaining rows, ensuring separator after each data row
            i = 1
            while i < len(parsed_rows):
                if is_separator[i]:
                    # Skip existing separator
                    i += 1
                    continue
                    
                # Add data row
                data_row = Claude37_round_3.normalize_row(parsed_rows[i], max_cols)
                fixed_lines.append(Claude37_round_3.rebuild_row(data_row, style[0], style[1]))
                
                # Add separator after data row
                fixed_lines.append(Claude37_round_3.rebuild_row(separator, style[0], style[1]))
                
                i += 1
        else:
            # Standard table structure
            # Add header row (always the first row)
            header = Claude37_round_3.normalize_row(parsed_rows[0], max_cols)
            fixed_lines.append(Claude37_round_3.rebuild_row(header, style[0], style[1]))
            
            # Add separator row after header
            separator = [sep_style] * max_cols
            fixed_lines.append(Claude37_round_3.rebuild_row(separator, style[0], style[1]))
            
            # Add data rows, skipping any separators
            for i in range(1, len(parsed_rows)):
                if is_separator[i]:
                    continue
                    
                data_row = Claude37_round_3.normalize_row(parsed_rows[i], max_cols)
                fixed_lines.append(Claude37_round_3.rebuild_row(data_row, style[0], style[1]))
        
        return fixed_lines

    @staticmethod
    def normalize_row(row, target_cols):
        """
        Normalize a row to have the target number of columns.
        """
        if len(row) < target_cols:
            # Pad with empty cells
            return row + [''] * (target_cols - len(row))
        elif len(row) > target_cols:
            # Merge excess cells into the last one
            excess = ' '.join(row[target_cols-1:])
            return row[:target_cols-1] + [excess]
        else:
            # Already correct length
            return row

    @staticmethod
    def rebuild_row(cells, has_leading_pipe, has_trailing_pipe):
        """
        Rebuild a table row from its cells.
        """
        if not cells:
            return ''
            
        cell_str = ' | '.join(cells)
        
        if has_leading_pipe:
            cell_str = '| ' + cell_str
        
        if has_trailing_pipe:
            cell_str = cell_str + ' |'
        
        return cell_str


class Grok3_round_3:
    """
    Implementation based on Grok3's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        """
        Fixes invalid Markdown tables in the input text while leaving valid tables and non-table content unchanged.

        Args:
            markdown_text (str): The Markdown text containing potential tables.
        Returns:
            str: The Markdown text with invalid tables fixed.
        """
        lines = markdown_text.splitlines()
        output = []
        table_block = []
        inside_table = False

        # Process lines to identify and fix table blocks
        for line in lines:
            if '|' in line:
                table_block.append(line)
                inside_table = True
            elif inside_table and line.strip():
                table_block.append(line)  # Continuation line
            else:
                if table_block:
                    fixed = Grok3_round_3.fix_table_block(table_block)
                    output.extend(fixed)
                    table_block = []
                inside_table = False
                output.append(line)

        # Handle any remaining table block
        if table_block:
            fixed = Grok3_round_3.fix_table_block(table_block)
            output.extend(fixed)

        return '\n'.join(output)

    @staticmethod
    def is_separator_row(cells):
        """Check if a row is a separator (e.g., |---|---|)"""
        return all(re.fullmatch(r':?-{3,}:?', cell.strip()) for cell in cells if cell.strip())

    @staticmethod
    def split_row(line):
        """Split a row into cells, handling leading/trailing pipes"""
        stripped = line.strip()
        if stripped.startswith('|'):
            cells = stripped[1:].split('|')
            if stripped.endswith('|'):
                cells = cells[:-1]
        else:
            cells = stripped.split('|')
            if stripped.endswith('|'):
                cells = cells[:-1]
        return [cell.strip() for cell in cells]

    @staticmethod
    def merge_continuation_lines(lines):
        """Merge continuation lines into the previous row's last cell"""
        merged_rows = []
        for line in lines:
            if '|' in line:
                merged_rows.append(Grok3_round_3.split_row(line))
            elif merged_rows and line.strip():
                merged_rows[-1][-1] += ' ' + line.strip()
        return merged_rows

    @staticmethod
    def is_valid_table(rows):
        """Check if a table is valid"""
        if len(rows) < 2:
            return False
        if not Grok3_round_3.is_separator_row(rows[1]):
            return False
        col_count = len(rows[1])
        return all(len(row) == col_count for row in rows)

    @staticmethod
    def fix_table_block(lines):
        """Fix an invalid table block"""
        rows = Grok3_round_3.merge_continuation_lines(lines)
        if len(rows) < 2:
            return lines  # Not a table, return unchanged

        # If already valid, return original lines
        if Grok3_round_3.is_valid_table(rows):
            return lines

        # Determine style from the first line
        first_line = lines[0].strip()
        has_leading_pipe = first_line.startswith('|')
        has_trailing_pipe = first_line.endswith('|')

        # Find max column count
        max_cols = max(len(row) for row in rows)

        # Build fixed rows: header, separator, data
        fixed_rows = []
        header_added = False
        separator_added = False

        for i, row in enumerate(rows):
            if not header_added:
                fixed_rows.append(row)
                header_added = True
            elif not separator_added and (i == 1 or Grok3_round_3.is_separator_row(row)):
                fixed_rows.append(['---'] * max_cols)
                separator_added = True
            elif Grok3_round_3.is_separator_row(row):
                fixed_rows.append(row)  # Treat extra separators as data
            else:
                fixed_rows.append(row)

        # Insert separator if missing
        if not separator_added:
            fixed_rows.insert(1, ['---'] * max_cols)

        # Pad or adjust rows to max_cols
        for i, row in enumerate(fixed_rows):
            if len(row) < max_cols:
                fixed_rows[i] = row + [''] * (max_cols - len(row))
            elif len(row) > max_cols:
                fixed_rows[i] = row[:max_cols-1] + [' '.join(row[max_cols-1:])]

        # Reassemble lines with consistent style
        fixed_lines = []
        for row in fixed_rows:
            line = ' | '.join(row)
            if has_leading_pipe:
                line = '| ' + line
            if has_trailing_pipe:
                line += ' |'
            fixed_lines.append(line)
        return fixed_lines


class O1_pro_round_3:
    """
    Implementation based on O1-pro's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
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
            return all(re.fullmatch(r':?-{3,}:?', c.strip()) for c in cells if c.strip())

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


class O3_mini_high_round_3:
    """
    Implementation based on o3-mini-high's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        lines = markdown_text.splitlines()
        output = []
        table_block = []
        in_table = False

        for line in lines:
            # A line is "potentially" table-related if it contains a pipe.
            if '|' in line:
                table_block.append(line)
                in_table = True
            else:
                if in_table:
                    output.extend(O3_mini_high_round_3.process_table_block(table_block))
                    table_block = []
                    in_table = False
                output.append(line)
        if table_block:
            output.extend(O3_mini_high_round_3.process_table_block(table_block))
        return "\n".join(output)

    @staticmethod
    def process_table_block(block_lines):
        merged = O3_mini_high_round_3.merge_continuation_lines(block_lines)
        # If the merged block looks like a valid table, leave it untouched.
        if O3_mini_high_round_3.is_valid_table(merged):
            return block_lines
        else:
            return O3_mini_high_round_3.fix_table_block(merged)

    @staticmethod
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
                # blank line: flush current if exists
                if current is not None:
                    merged.append(current)
                    current = None
                merged.append(line)
        if current is not None:
            merged.append(current)
        return merged

    @staticmethod
    def is_valid_table(lines):
        if len(lines) < 2:
            return False
        header = O3_mini_high_round_3.parse_row(lines[0])
        sep = O3_mini_high_round_3.parse_row(lines[1])
        # The second row must be a proper separator row.
        if not sep or not all(O3_mini_high_round_3.is_valid_separator_cell(cell) for cell in sep if cell.strip() != ''):
            return False
        if len(header) != len(sep):
            return False
        # All remaining rows must have the same number of cells as header.
        for line in lines[2:]:
            if len(O3_mini_high_round_3.parse_row(line)) != len(header):
                return False
        return True

    @staticmethod
    def parse_row(row):
        parts = row.split('|')
        if row.strip().startswith('|'):
            parts = parts[1:]
        if row.strip().endswith('|'):
            parts = parts[:-1]
        return [p.strip() for p in parts]

    @staticmethod
    def is_valid_separator_cell(cell):
        return re.fullmatch(r':?-{3,}:?', cell.strip()) is not None

    @staticmethod
    def fix_table_block(lines):
        # Split merged lines into cell lists.
        rows = [O3_mini_high_round_3.parse_row(line) for line in lines]
        max_cols = max(len(r) for r in rows)
        norm_rows = []
        for r in rows:
            if len(r) < max_cols:
                r = r + [''] * (max_cols - len(r))
            elif len(r) > max_cols:
                r = r[:max_cols-1] + [" ".join(r[max_cols-1:])]
            norm_rows.append(r)
        # Preserve the header style (leading/trailing pipes) from the first line.
        style = O3_mini_high_round_3.table_style(lines[0])
        fixed = []
        # Rebuild header.
        fixed.append(O3_mini_high_round_3.rebuild_row(norm_rows[0], style))
        # Check if second row is a valid separator.
        if len(norm_rows) > 1 and all(O3_mini_high_round_3.is_valid_separator_cell(cell) for cell in norm_rows[1] if cell.strip()):
            sep_row = ['---'] * max_cols
            fixed.append(O3_mini_high_round_3.rebuild_row(sep_row, style))
            data_start = 2
        else:
            sep_row = ['---'] * max_cols
            fixed.append(O3_mini_high_round_3.rebuild_row(sep_row, style))
            data_start = 1
        # Rebuild remaining rows, skipping any extra separator rows.
        for r in norm_rows[data_start:]:
            if all(O3_mini_high_round_3.is_valid_separator_cell(cell) for cell in r if cell.strip()):
                continue
            fixed.append(O3_mini_high_round_3.rebuild_row(r, style))
        return fixed

    @staticmethod
    def table_style(row):
        s = row.strip()
        return (s.startswith('|'), s.endswith('|'))

    @staticmethod
    def rebuild_row(cells, style):
        s = " | ".join(cells)
        if style[0]:
            s = "|" + s
        if style[1]:
            s = s + "|"
        return s

class Claude37_round_4:
    """
    Implementation based on Claude3.7's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        """
        Fix invalid markdown tables in text while preserving valid tables and non-table content.
        
        This function:
        - Identifies invalid markdown tables
        - Diagnoses issues with the tables
        - Fixes them in a minimally invasive way
        - Makes no change to valid tables
        - Skips over non-table content
        
        Args:
            markdown_text (str): Markdown text containing potential tables
            
        Returns:
            str: Markdown text with fixed tables
        """
        lines = markdown_text.splitlines()
        result_lines = []
        table_block = []
        inside_table = False
        
        # Process each line of the input text
        i = 0
        while i < len(lines):
            line = lines[i]
            
            if '|' in line:
                # Potential table line
                if not inside_table:
                    # Starting a new table
                    inside_table = True
                table_block.append(line)
            elif inside_table and line.strip():
                # Continuation line for a multi-line cell
                table_block.append(line)
            else:
                # Not part of a table, process any accumulated table block
                if inside_table:
                    fixed_table = Claude37_round_4.process_table_block(table_block)
                    result_lines.extend(fixed_table)
                    table_block = []
                    inside_table = False
                
                # Add the non-table line
                result_lines.append(line)
            
            i += 1
        
        # Handle any remaining table at the end
        if inside_table:
            fixed_table = Claude37_round_4.process_table_block(table_block)
            result_lines.extend(fixed_table)
        
        return '\n'.join(result_lines)

    @staticmethod
    def process_table_block(block_lines):
        """
        Process a block of lines that might contain a markdown table.
        """
        # Skip if no table content
        if not block_lines or not any('|' in line for line in block_lines):
            return block_lines
        
        # First, merge continuation lines
        merged_lines = Claude37_round_4.merge_continuation_lines(block_lines)
        
        # Check if the merged version is a valid table
        if Claude37_round_4.is_valid_table(merged_lines):
            # Table is already valid, preserve it exactly
            return block_lines
        
        # Table is invalid, fix it
        return Claude37_round_4.fix_invalid_table(merged_lines)

    @staticmethod
    def merge_continuation_lines(lines):
        """
        Merge lines that are continuations of multi-line cells.
        """
        merged = []
        current = None
        
        for line in lines:
            if '|' in line:
                # This is a table row
                if current is not None:
                    merged.append(current)
                current = line
            elif line.strip() and current is not None:
                # This is a continuation of the previous line
                current += ' ' + line.strip()
            else:
                # Empty line or non-continuation
                if current is not None:
                    merged.append(current)
                    current = None
                if line.strip():
                    merged.append(line)
        
        if current is not None:
            merged.append(current)
        
        return merged

    @staticmethod
    def parse_table_row(line):
        """
        Parse a table row into cells, handling leading/trailing pipes.
        """
        if not line or '|' not in line:
            return []
        
        # Split by pipe
        parts = line.split('|')
        
        # Handle leading/trailing pipes
        if line.strip().startswith('|'):
            parts = parts[1:]
        if line.strip().endswith('|'):
            parts = parts[:-1]
        
        return [p.strip() for p in parts]

    @staticmethod
    def is_separator_cell(cell):
        """
        Check if a cell contains a valid separator pattern (e.g., ---, :--:).
        """
        return bool(re.fullmatch(r':?-{3,}:?', cell.strip()))

    @staticmethod
    def is_separator_row(cells):
        """
        Check if cells represent a separator row.
        """
        if not cells:
            return False
        
        # Every non-empty cell must match the separator pattern
        return all(Claude37_round_4.is_separator_cell(cell) for cell in cells if cell.strip())

    @staticmethod
    def is_valid_table(lines):
        """
        Check if a markdown table is valid.
        """
        # Need at least 2 lines for a valid table
        if len(lines) < 2:
            return False
        
        # Parse rows into cells
        rows = [Claude37_round_4.parse_table_row(line) for line in lines if '|' in line]
        if len(rows) < 2:
            return False
        
        # Check if second row is a separator
        if not Claude37_round_4.is_separator_row(rows[1]):
            return False
        
        # Check column count consistency
        col_count = len(rows[0])
        return all(len(row) == col_count for row in rows)

    @staticmethod
    def get_table_style(line):
        """
        Determine the table style (leading/trailing pipes) from a row.
        """
        stripped = line.strip()
        has_leading = stripped.startswith('|')
        has_trailing = stripped.endswith('|')
        return (has_leading, has_trailing)

    @staticmethod
    def detect_table_pattern(lines):
        """
        Detect the pattern of the table (e.g., if it has separators after each row).
        """
        table_lines = [line for line in lines if '|' in line]
        parsed_rows = [Claude37_round_4.parse_table_row(line) for line in table_lines]
        is_sep = [Claude37_round_4.is_separator_row(row) for row in parsed_rows]
        separator_indices = [i for i, sep in enumerate(is_sep) if sep]
        
        pattern = {
            'has_separators_after_each_row': False,
            'separator_indices': separator_indices
        }
        
        # Check for repeating pattern (separator after each data row)
        if len(separator_indices) >= 2:
            # Count how many rows have a separator after them
            separator_pattern_count = sum(1 for i in range(len(is_sep)-1) if not is_sep[i] and is_sep[i+1])
            data_row_count = sum(1 for sep in is_sep if not sep)
            
            # If more than half of data rows have a separator after them, consider it a pattern
            if separator_pattern_count >= data_row_count / 2:
                pattern['has_separators_after_each_row'] = True
        
        return pattern

    @staticmethod
    def normalize_row(row, target_cols):
        """
        Normalize a row to have the target number of columns.
        """
        if not row:
            return [''] * target_cols
        
        if len(row) < target_cols:
            # Pad with empty cells
            return row + [''] * (target_cols - len(row))
        elif len(row) > target_cols:
            # Merge excess cells into the last one
            if target_cols > 1:
                return row[:target_cols-1] + [' '.join(row[target_cols-1:])]
            else:
                return [' '.join(row)]
        else:
            # Already correct length
            return row

    @staticmethod
    def rebuild_row(cells, has_leading_pipe, has_trailing_pipe):
        """
        Rebuild a table row from its cells.
        """
        if not cells:
            return ''
        
        cell_str = ' | '.join(cells)
        
        if has_leading_pipe:
            cell_str = '| ' + cell_str
        
        if has_trailing_pipe:
            cell_str = cell_str + ' |'
        
        return cell_str

    @staticmethod
    def fix_invalid_table(lines):
        """
        Fix an invalid markdown table with minimal changes.
        """
        # Filter out lines that don't contain pipe characters
        table_lines = [line for line in lines if '|' in line]
        if not table_lines:
            return lines
        
        # Get table style from the first line
        style = Claude37_round_4.get_table_style(table_lines[0])
        
        # Parse all rows
        parsed_rows = [Claude37_round_4.parse_table_row(line) for line in table_lines]
        
        # Calculate max columns across all rows
        max_cols = max(len(row) for row in parsed_rows) if parsed_rows else 0
        
        # Identify rows that are data rows vs separators
        is_separator = [Claude37_round_4.is_separator_row(row) for row in parsed_rows]
        
        # Detect table pattern
        pattern = Claude37_round_4.detect_table_pattern(lines)
        
        # Create fixed output
        fixed_lines = []
        
        if pattern['has_separators_after_each_row']:
            # Special case: table has separator after each row (seen in examples)
            # Start with header
            header = Claude37_round_4.normalize_row(parsed_rows[0], max_cols)
            fixed_lines.append(Claude37_round_4.rebuild_row(header, style[0], style[1]))
            
            # Add separator after header
            separator = ['---'] * max_cols
            fixed_lines.append(Claude37_round_4.rebuild_row(separator, style[0], style[1]))
            
            # Process remaining rows, ensuring separator after each data row
            i = 1
            while i < len(parsed_rows):
                if is_separator[i]:
                    # Skip existing separator
                    i += 1
                    continue
                
                # Add data row
                data_row = Claude37_round_4.normalize_row(parsed_rows[i], max_cols)
                fixed_lines.append(Claude37_round_4.rebuild_row(data_row, style[0], style[1]))
                
                # Add separator after data row
                fixed_lines.append(Claude37_round_4.rebuild_row(separator, style[0], style[1]))
                
                i += 1
        else:
            # Standard table structure
            # Add header row (always the first row)
            header = Claude37_round_4.normalize_row(parsed_rows[0], max_cols)
            fixed_lines.append(Claude37_round_4.rebuild_row(header, style[0], style[1]))
            
            # Add separator row after header
            separator = ['---'] * max_cols
            fixed_lines.append(Claude37_round_4.rebuild_row(separator, style[0], style[1]))
            
            # Add data rows, skipping any separators
            for i in range(1, len(parsed_rows)):
                if is_separator[i]:
                    continue
                
                data_row = Claude37_round_4.normalize_row(parsed_rows[i], max_cols)
                fixed_lines.append(Claude37_round_4.rebuild_row(data_row, style[0], style[1]))
        
        return fixed_lines


class Grok3_round_4:
    """
    Implementation based on Grok3's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        """
        Fixes invalid Markdown tables in the input text while preserving valid tables and non-table content.
        """
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
                    output.extend(Grok3_round_4.process_table_block(table_block))
                    table_block = []
                    in_table = False
                output.append(line)
        if table_block:
            output.extend(Grok3_round_4.process_table_block(table_block))
        return "\n".join(output)

    @staticmethod
    def process_table_block(block_lines):
        """Processes a table block, merging continuation lines and fixing if invalid."""
        merged_lines = Grok3_round_4.merge_continuation_lines(block_lines)
        if len(merged_lines) < 2:
            return block_lines  # Too few lines to be a table
        if Grok3_round_4.is_valid_table(merged_lines):
            return block_lines  # Preserve valid tables
        return Grok3_round_4.fix_table_block(merged_lines)

    @staticmethod
    def merge_continuation_lines(lines):
        """Merges lines without pipes into the previous row's last cell."""
        merged = []
        for line in lines:
            if '|' in line:
                merged.append(line)
            elif merged and line.strip():
                merged[-1] += ' ' + line.strip()
        return merged

    @staticmethod
    def parse_row(line):
        """Splits a row into cells, handling leading/trailing pipes."""
        stripped = line.strip()
        if stripped.startswith('|'):
            cells = stripped[1:].split('|')
        else:
            cells = stripped.split('|')
        if stripped.endswith('|'):
            cells = cells[:-1]
        return [cell.strip() for cell in cells]

    @staticmethod
    def is_separator_row(cells):
        """Determines if a row is a separator (e.g., ---, :--, :-:)."""
        if not cells:
            return False
        return all(re.fullmatch(r':?-{3,}:?', cell.strip()) for cell in cells if cell.strip())

    @staticmethod
    def is_valid_table(lines):
        """Checks if a table is valid: has ≥2 rows, a separator as row 2, and consistent columns."""
        if len(lines) < 2:
            return False
        rows = [Grok3_round_4.parse_row(line) for line in lines]
        if not Grok3_round_4.is_separator_row(rows[1]):
            return False
        col_count = len(rows[0])
        return all(len(row) == col_count for row in rows)

    @staticmethod
    def normalize_row(row, col_count):
        """Normalizes a row to have the specified number of columns."""
        if len(row) < col_count:
            return row + [''] * (col_count - len(row))
        elif len(row) > col_count:
            return row[:col_count-1] + [' '.join(row[col_count-1:])]
        return row

    @staticmethod
    def rebuild_row(cells, has_leading_pipe, has_trailing_pipe):
        """Rebuilds a row from cells with specified pipe style."""
        cell_str = ' | '.join(cells)
        if has_leading_pipe:
            cell_str = '| ' + cell_str
        if has_trailing_pipe:
            cell_str += ' |'
        return cell_str

    @staticmethod
    def get_table_style(line):
        """Extracts table style (leading/trailing pipes) from a line."""
        stripped = line.strip()
        return (stripped.startswith('|'), stripped.endswith('|'))

    @staticmethod
    def fix_table_block(merged_lines):
        """Fixes an invalid table block, normalizing columns and rebuilding structure."""
        # Parse rows and identify separators
        parsed_rows = [Grok3_round_4.parse_row(line) for line in merged_lines]
        is_sep = [Grok3_round_4.is_separator_row(row) for row in parsed_rows]
        sep_indices = [i for i, s in enumerate(is_sep) if s]

        # Determine column count
        col_count = max(len(row) for row in parsed_rows) if parsed_rows else 0
        if col_count == 0:
            return merged_lines

        # Normalize all rows to col_count
        normalized_rows = [Grok3_round_4.normalize_row(row, col_count) for row in parsed_rows]

        # Detect table pattern
        if len(sep_indices) == 1 and sep_indices[0] == 1:
            pattern = 'standard'
        elif len(sep_indices) > 1 and all(i % 2 == 1 for i in sep_indices):
            pattern = 'separator_after_each'
        else:
            pattern = 'no_separator'

        # Preserve table style from first line
        style = Grok3_round_4.get_table_style(merged_lines[0])
        fixed_lines = []

        if pattern == 'standard':
            # Header, normalized separator, then data rows
            fixed_lines.append(Grok3_round_4.rebuild_row(normalized_rows[0], *style))
            separator = ['---'] * col_count
            fixed_lines.append(Grok3_round_4.rebuild_row(separator, *style))
            for i in range(2, len(normalized_rows)):
                if not is_sep[i]:
                    fixed_lines.append(Grok3_round_4.rebuild_row(normalized_rows[i], *style))

        elif pattern == 'separator_after_each':
            # Header, separator, then data row + separator pairs
            fixed_lines.append(Grok3_round_4.rebuild_row(normalized_rows[0], *style))
            separator = ['---'] * col_count
            fixed_lines.append(Grok3_round_4.rebuild_row(separator, *style))
            for i in range(2, len(normalized_rows), 2):
                if i < len(normalized_rows) and not is_sep[i]:
                    fixed_lines.append(Grok3_round_4.rebuild_row(normalized_rows[i], *style))
                    fixed_lines.append(Grok3_round_4.rebuild_row(separator, *style))

        else:  # no_separator
            # Insert separator after header
            fixed_lines.append(Grok3_round_4.rebuild_row(normalized_rows[0], *style))
            separator = ['---'] * col_count
            fixed_lines.append(Grok3_round_4.rebuild_row(separator, *style))
            for row in normalized_rows[1:]:
                fixed_lines.append(Grok3_round_4.rebuild_row(row, *style))

        return fixed_lines


class O1_pro_round_4:
    """
    Implementation based on O1-pro's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        def merge_continuation_lines(lines):
            merged = []
            cur = None
            for ln in lines:
                if '|' in ln:
                    if cur is not None: merged.append(cur)
                    cur = ln
                elif ln.strip():
                    if cur is not None: cur += " " + ln.strip()
                    else: cur = ln
                else:
                    if cur is not None: merged.append(cur)
                    cur = None
                    merged.append(ln)
            if cur is not None: merged.append(cur)
            return merged

        def parse_row(line):
            s = line.strip()
            has_lead = s.startswith('|')
            has_tail = s.endswith('|')
            if has_lead: s = s[1:]
            if has_tail: s = s[:-1]
            return [c.strip() for c in s.split('|')]

        def is_separator_cell(cell):
            return re.fullmatch(r':?-{3,}:?', cell.strip()) is not None

        def is_separator_row(cells):
            return all(is_separator_cell(c) for c in cells if c.strip())

        def is_valid_table(lines):
            if len(lines) < 2: return False
            rows = [parse_row(ln) for ln in lines]
            if not is_separator_row(rows[1]): return False
            n = len(rows[0])
            return all(len(r) == n for r in rows)

        def detect_repeated_separators(rows):
            # Returns True if more than half of the odd rows are separator lines
            if len(rows) < 3: return False
            odd_sep_count = sum(is_separator_row(rows[i]) for i in range(1, len(rows), 2))
            return odd_sep_count >= (len(rows) - 1)//2

        def rebuild_row(cells, style):
            s = " | ".join(cells)
            if style[0]: s = "| " + s
            if style[1]: s += " |"
            return s

        def fix_table_block(block):
            merged = merge_continuation_lines(block)
            if len(merged) < 2: return block
            if is_valid_table(merged): return block

            rows_parsed = [parse_row(ln) for ln in merged]
            style = (merged[0].strip().startswith('|'), merged[0].strip().endswith('|'))
            max_cols = max(len(r) for r in rows_parsed)
            sep_flags = [is_separator_row(r) for r in rows_parsed]
            repeated_sep = detect_repeated_separators(rows_parsed)

            def normalize(r):
                if len(r) < max_cols:
                    return r + ['']*(max_cols - len(r))
                elif len(r) > max_cols:
                    return r[:max_cols-1] + [' '.join(r[max_cols-1:])]
                else:
                    return r

            rows_parsed = [normalize(r) for r in rows_parsed]
            fixed = [rows_parsed[0]]
            fixed.append(["---"]*max_cols)
            if repeated_sep:
                i = 1
                while i < len(rows_parsed):
                    if sep_flags[i]:
                        i += 1
                        continue
                    fixed.append(rows_parsed[i])
                    fixed.append(["---"]*max_cols)
                    i += 1
            else:
                for i in range(2, len(rows_parsed)):
                    if not sep_flags[i]:
                        fixed.append(rows_parsed[i])
            return [rebuild_row(r, style) for r in fixed]

        lines = markdown_text.splitlines()
        out = []
        block = []
        in_table = False
        for line in lines:
            if '|' in line:
                block.append(line)
                in_table = True
            else:
                if in_table:
                    out.extend(fix_table_block(block))
                    block = []
                    in_table = False
                out.append(line)
        if block: out.extend(fix_table_block(block))
        return "\n".join(out)


class O3_mini_high_round_4:
    """
    Implementation based on o3-mini-high's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
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
                    output.extend(O3_mini_high_round_4.process_table_block(table_block))
                    table_block = []
                    in_table = False
                output.append(line)
        if table_block:
            output.extend(O3_mini_high_round_4.process_table_block(table_block))
        return "\n".join(output)

    @staticmethod
    def process_table_block(block_lines):
        merged = O3_mini_high_round_4.merge_continuation_lines(block_lines)
        if len(merged) < 2 or not any('|' in ln for ln in merged):
            return block_lines
        if O3_mini_high_round_4.is_valid_table(merged):
            return block_lines  # already valid
        return O3_mini_high_round_4.fix_table_block(merged, block_lines[0])

    @staticmethod
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

    @staticmethod
    def parse_row(line):
        s = line.strip()
        if s.startswith('|'):
            s = s[1:]
        if s.endswith('|'):
            s = s[:-1]
        return [cell.strip() for cell in s.split('|')]

    @staticmethod
    def is_separator_cell(cell):
        return re.fullmatch(r':?-{3,}:?', cell.strip()) is not None

    @staticmethod
    def is_separator_row(cells):
        return all(O3_mini_high_round_4.is_separator_cell(cell) for cell in cells if cell.strip())

    @staticmethod
    def is_valid_table(lines):
        if len(lines) < 2:
            return False
        rows = [O3_mini_high_round_4.parse_row(ln) for ln in lines if '|' in ln]
        if len(rows) < 2:
            return False
        if not O3_mini_high_round_4.is_separator_row(rows[1]):
            return False
        col_count = len(rows[0])
        return all(len(row) == col_count for row in rows)

    @staticmethod
    def detect_table_style(line):
        s = line.strip()
        return (s.startswith('|'), s.endswith('|'))

    @staticmethod
    def rebuild_row(cells, style):
        row = " | ".join(cells)
        if style[0]:
            row = "| " + row
        if style[1]:
            row += " |"
        return row

    @staticmethod
    def normalize_row(row, target_cols):
        if len(row) < target_cols:
            return row + [''] * (target_cols - len(row))
        elif len(row) > target_cols:
            return row[:target_cols-1] + [" ".join(row[target_cols-1:])]
        return row

    @staticmethod
    def detect_separator_pattern(parsed_rows):
        if len(parsed_rows) < 3:
            return False
        sep_indices = [i for i, row in enumerate(parsed_rows) if O3_mini_high_round_4.is_separator_row(row)]
        total_odds = (len(parsed_rows) - 1) // 2
        return len(sep_indices) >= total_odds and all(i % 2 == 1 for i in sep_indices)

    @staticmethod
    def fix_table_block(merged_lines, first_line):
        parsed = [O3_mini_high_round_4.parse_row(ln) for ln in merged_lines]
        style = O3_mini_high_round_4.detect_table_style(first_line)
        max_cols = max(len(r) for r in parsed)
        parsed = [O3_mini_high_round_4.normalize_row(r, max_cols) for r in parsed]
        fixed = []
        if O3_mini_high_round_4.detect_separator_pattern(parsed):
            # Use header then add a separator after each data row.
            fixed.append(parsed[0])
            fixed.append(['---'] * max_cols)
            idx = 1
            while idx < len(parsed):
                if O3_mini_high_round_4.is_separator_row(parsed[idx]):
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
                if O3_mini_high_round_4.is_separator_row(row):
                    continue
                fixed.append(row)
        return [O3_mini_high_round_4.rebuild_row(r, style) for r in fixed]

class Claude37_round_5:
    """
    A hybrid implementation for fixing invalid markdown tables, combining best elements
    from multiple approaches.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        """
        Fixes invalid Markdown tables in the input text while preserving valid tables and non-table content.

        Args:
            markdown_text (str): Markdown text containing potential tables.
        Returns:
            str: Markdown text with invalid tables fixed.
        """
        lines = markdown_text.splitlines()
        output = []
        table_block = []
        in_table = False

        for line in lines:
            if '|' in line:
                table_block.append(line)
                in_table = True
            elif in_table and line.strip():
                # Continuation line for a multi-line cell
                table_block.append(line)
            else:
                if in_table:
                    output.extend(Claude37_round_5.process_table_block(table_block))
                    table_block = []
                    in_table = False
                output.append(line)
        
        # Handle any remaining table at the end
        if table_block:
            output.extend(Claude37_round_5.process_table_block(table_block))
        
        return "\n".join(output)

    @staticmethod
    def process_table_block(block_lines):
        """
        Processes a block of lines that might contain a markdown table.
        """
        # First, merge continuation lines
        merged_lines = Claude37_round_5.merge_continuation_lines(block_lines)
        
        # Skip if no table content or too few lines
        if len(merged_lines) < 2 or not any('|' in line for line in merged_lines):
            return block_lines
        
        # Check if the merged version is a valid table
        if Claude37_round_5.is_valid_table(merged_lines):
            # Table is already valid, preserve it exactly
            return block_lines
        
        # Table is invalid, fix it
        return Claude37_round_5.fix_table_block(merged_lines)

    @staticmethod
    def merge_continuation_lines(lines):
        """
        Merges lines that are continuations of multi-line cells.
        """
        merged = []
        current = None
        
        for line in lines:
            if '|' in line:
                # This is a table row
                if current is not None:
                    merged.append(current)
                current = line.rstrip()
            elif line.strip():
                # This is a continuation of the previous line
                if current is not None:
                    current += " " + line.strip()
                else:
                    current = line.rstrip()
            else:
                # Empty line or non-continuation
                if current is not None:
                    merged.append(current)
                    current = None
                if line.strip():
                    merged.append(line)
        
        if current is not None:
            merged.append(current)
        
        return merged

    @staticmethod
    def parse_row(line):
        """
        Parse a table row into cells, handling leading/trailing pipes.
        """
        if not line or '|' not in line:
            return []
        
        s = line.strip()
        has_lead = s.startswith('|')
        has_tail = s.endswith('|')
        
        if has_lead:
            s = s[1:]
        if has_tail:
            s = s[:-1]
        
        return [cell.strip() for cell in s.split('|')]

    @staticmethod
    def is_separator_cell(cell):
        """
        Check if a cell contains a valid separator pattern (e.g., ---, :--:).
        """
        return bool(re.fullmatch(r':?-{3,}:?', cell.strip()))

    @staticmethod
    def is_separator_row(cells):
        """
        Check if cells represent a separator row.
        """
        if not cells:
            return False
        
        # Every non-empty cell must match the separator pattern
        return all(Claude37_round_5.is_separator_cell(cell) for cell in cells if cell.strip())

    @staticmethod
    def is_valid_table(lines):
        """
        Check if a markdown table is valid.
        """
        if len(lines) < 2:
            return False
        
        # Parse rows into cells
        rows = [Claude37_round_5.parse_row(line) for line in lines if '|' in line]
        if len(rows) < 2:
            return False
        
        # Check if second row is a separator
        if not Claude37_round_5.is_separator_row(rows[1]):
            return False
        
        # Check column count consistency
        col_count = len(rows[0])
        return all(len(row) == col_count for row in rows)

    @staticmethod
    def detect_table_style(line):
        """
        Determine the table style (leading/trailing pipes) from a row.
        """
        s = line.strip()
        return (s.startswith('|'), s.endswith('|'))

    @staticmethod
    def detect_separator_pattern(parsed_rows):
        """
        Detect if the table has separators after each data row.
        """
        if len(parsed_rows) < 3:
            return False
        
        # Get indices of separator rows
        sep_indices = [i for i, row in enumerate(parsed_rows) if Claude37_round_5.is_separator_row(row)]
        
        # Check if there are many separator rows and they follow a pattern
        if len(sep_indices) <= 1:
            return False
        
        # Calculate how many odd-indexed rows are separators (which suggests separators after each data)
        odd_sep_count = sum(1 for i in sep_indices if i % 2 == 1)
        total_odds = (len(parsed_rows) - 1) // 2
        
        # If more than half of the odd-indexed rows are separators, likely a pattern
        return odd_sep_count >= total_odds / 2

    @staticmethod
    def normalize_row(row, target_cols):
        """
        Normalize a row to have the target number of columns.
        """
        if len(row) < target_cols:
            # Pad with empty cells
            return row + [''] * (target_cols - len(row))
        elif len(row) > target_cols:
            # Merge excess cells into the last one
            if target_cols > 1:
                return row[:target_cols-1] + [' '.join(row[target_cols-1:])]
            else:
                return [' '.join(row)]
        else:
            # Already correct length
            return row

    @staticmethod
    def rebuild_row(cells, style):
        """
        Rebuild a table row from its cells.
        """
        if not cells:
            return ''
        
        row = " | ".join(cells)
        
        if style[0]:
            row = "| " + row
        
        if style[1]:
            row += " |"
        
        return row

    @staticmethod
    def fix_table_block(merged_lines):
        """
        Fix an invalid markdown table with minimal changes.
        """
        # Get table style from the first line
        style = Claude37_round_5.detect_table_style(merged_lines[0])
        
        # Parse all rows
        parsed_rows = [Claude37_round_5.parse_row(line) for line in merged_lines if '|' in line]
        
        # Calculate max columns across all rows
        max_cols = max(len(row) for row in parsed_rows) if parsed_rows else 0
        
        # Detect if separators follow data rows
        has_separators_after_rows = Claude37_round_5.detect_separator_pattern(parsed_rows)
        
        # Determine which rows are separators
        is_sep = [Claude37_round_5.is_separator_row(row) for row in parsed_rows]
        
        # Create fixed output
        fixed_lines = []
        
        # Always start with header row
        header = Claude37_round_5.normalize_row(parsed_rows[0], max_cols)
        fixed_lines.append(Claude37_round_5.rebuild_row(header, style))
        
        # Add separator after header
        separator = ['---'] * max_cols
        fixed_lines.append(Claude37_round_5.rebuild_row(separator, style))
        
        if has_separators_after_rows:
            # Separators after each data row pattern
            i = 1
            while i < len(parsed_rows):
                if is_sep[i]:
                    # Skip existing separators
                    i += 1
                    continue
                    
                # Add data row
                data_row = Claude37_round_5.normalize_row(parsed_rows[i], max_cols)
                fixed_lines.append(Claude37_round_5.rebuild_row(data_row, style))
                
                # Add separator after data row
                fixed_lines.append(Claude37_round_5.rebuild_row(separator, style))
                
                i += 1
        else:
            # Standard table: no separators between data rows
            for i in range(1, len(parsed_rows)):
                if not is_sep[i]:
                    data_row = Claude37_round_5.normalize_row(parsed_rows[i], max_cols)
                    fixed_lines.append(Claude37_round_5.rebuild_row(data_row, style))
        
        return fixed_lines


class Grok3_round_5:
    """
    Implementation based on Grok3's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        """
        Fixes invalid markdown tables in the input text while preserving valid tables and non-table content.
        """
        lines = markdown_text.splitlines()
        output = []
        table_block = []
        in_table = False

        # Iterate through lines to identify table blocks
        for line in lines:
            if '|' in line:
                table_block.append(line)
                in_table = True
            else:
                if in_table:
                    output.extend(Grok3_round_5.process_table_block(table_block))
                    table_block = []
                    in_table = False
                output.append(line)
        if table_block:
            output.extend(Grok3_round_5.process_table_block(table_block))
        return "\n".join(output)

    @staticmethod
    def process_table_block(block_lines):
        """Processes a table block, merging continuation lines and fixing if invalid."""
        merged = Grok3_round_5.merge_continuation_lines(block_lines)
        if len(merged) < 2 or not any('|' in ln for ln in merged):
            return block_lines  # Not a table
        if Grok3_round_5.is_valid_table(merged):
            return block_lines  # Preserve original formatting of valid tables
        return Grok3_round_5.fix_table_block(merged)

    @staticmethod
    def merge_continuation_lines(lines):
        """Merges lines without pipes into the previous row's last cell."""
        merged = []
        current = None
        for line in lines:
            if '|' in line:
                if current is not None:
                    merged.append(current)
                current = line.rstrip()
            elif line.strip() and current is not None:
                current += " " + line.strip()
            else:
                if current is not None:
                    merged.append(current)
                    current = None
                merged.append(line)
        if current is not None:
            merged.append(current)
        return merged

    @staticmethod
    def parse_row(line):
        """Parses a row into cells, removing leading/trailing pipes."""
        s = line.strip()
        if s.startswith('|'):
            s = s[1:]
        if s.endswith('|'):
            s = s[:-1]
        return [cell.strip() for cell in s.split('|')]

    @staticmethod
    def is_separator_cell(cell):
        """Checks if a cell is a separator (e.g., ---, :--, :-:)."""
        return re.fullmatch(r':?-{3,}:?', cell.strip()) is not None

    @staticmethod
    def is_separator_row(cells):
        """Determines if a row is a separator row."""
        return all(Grok3_round_5.is_separator_cell(c) for c in cells if c.strip())

    @staticmethod
    def is_valid_table(lines):
        """Validates a table: ≥2 rows, separator as second row, consistent columns."""
        if len(lines) < 2:
            return False
        rows = [Grok3_round_5.parse_row(ln) for ln in lines if '|' in ln]
        if len(rows) < 2:
            return False
        if not Grok3_round_5.is_separator_row(rows[1]):
            return False
        col_count = len(rows[0])
        return all(len(r) == col_count for r in rows)

    @staticmethod
    def rebuild_row(cells, style):
        """Rebuilds a row with the specified pipe style."""
        s = " | ".join(cells)
        if style[0]:
            s = "| " + s
        if style[1]:
            s += " |"
        return s

    @staticmethod
    def normalize_row(row, target_cols):
        """Normalizes a row to the target column count."""
        if len(row) < target_cols:
            return row + [''] * (target_cols - len(row))
        elif len(row) > target_cols:
            return row[:target_cols-1] + [' '.join(row[target_cols-1:])]
        return row

    @staticmethod
    def fix_table_block(merged_lines):
        """Fixes an invalid table block by normalizing and rebuilding it."""
        # Parse rows and determine style from the first line
        first_line = merged_lines[0]
        style = (first_line.strip().startswith('|'), first_line.strip().endswith('|'))
        parsed_rows = [Grok3_round_5.parse_row(ln) for ln in merged_lines if '|' in ln]
        if not parsed_rows:
            return merged_lines

        # Determine maximum column count
        max_cols = max(len(r) for r in parsed_rows)

        # Normalize all rows to max_cols
        parsed_rows = [Grok3_round_5.normalize_row(r, max_cols) for r in parsed_rows]
        sep_flags = [Grok3_round_5.is_separator_row(r) for r in parsed_rows]

        # Detect if table has separators after each row
        odd_sep_count = sum(1 for i in range(1, len(sep_flags), 2) if sep_flags[i])
        total_odds = (len(parsed_rows) - 1) // 2 + 1
        repeated_sep = odd_sep_count >= total_odds / 2 and odd_sep_count > 1

        fixed = []
        if repeated_sep:
            # Pattern: header, separator, data, separator, ...
            fixed.append(parsed_rows[0])  # Header
            fixed.append(['---'] * max_cols)  # Separator after header
            i = 1
            while i < len(parsed_rows):
                if sep_flags[i]:
                    i += 1
                    continue
                fixed.append(parsed_rows[i])  # Data row
                fixed.append(['---'] * max_cols)  # Separator after data
                i += 1
        else:
            # Standard pattern: header, separator, data rows
            fixed.append(parsed_rows[0])  # Header
            fixed.append(['---'] * max_cols)  # Separator
            for i in range(1, len(parsed_rows)):
                if not sep_flags[i]:
                    fixed.append(parsed_rows[i])  # Data rows

        return [Grok3_round_5.rebuild_row(r, style) for r in fixed]


class O1_pro_round_5:
    """
    Implementation based on O1-pro's solution for fixing invalid markdown tables.
    """
    
    @staticmethod
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
                    out.extend(O1_pro_round_5._process_table_block(table_block))
                    table_block = []
                    in_table = False
                # Add the non-table line
                out.append(line)

        # Handle any leftover table block at the end
        if table_block:
            out.extend(O1_pro_round_5._process_table_block(table_block))

        return "\n".join(out)

    @staticmethod
    def _process_table_block(block_lines):
        # Merge multi-line cells
        merged = O1_pro_round_5._merge_continuation_lines(block_lines)
        # If it's already a valid table, leave it as is
        if O1_pro_round_5._is_valid_table(merged):
            return block_lines
        # Otherwise, fix the invalid table
        fixed = O1_pro_round_5._fix_invalid_table(merged)
        return fixed

    @staticmethod
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

    @staticmethod
    def _is_valid_table(lines):
        # A valid table must have at least 2 lines, a separator row as line 2,
        # and consistent column counts across all rows
        if len(lines) < 2:
            return False
        rows = [O1_pro_round_5._parse_row(ln) for ln in lines if '|' in ln]
        if len(rows) < 2:
            return False
        # Check if second row is a valid separator row
        if not O1_pro_round_5._is_separator_row(rows[1]):
            return False
        # Check column count consistency
        col_count = len(rows[0])
        return all(len(r) == col_count for r in rows)

    @staticmethod
    def _parse_row(line):
        s = line.strip()
        has_lead = s.startswith('|')
        has_tail = s.endswith('|')
        if has_lead:
            s = s[1:]
        if has_tail:
            s = s[:-1]
        return [c.strip() for c in s.split('|')]

    @staticmethod
    def _is_separator_row(cells):
        # A separator row has cells that match :?-{3,}:?
        return all(O1_pro_round_5._is_separator_cell(c) for c in cells if c.strip())

    @staticmethod
    def _is_separator_cell(cell):
        return re.fullmatch(r':?-{3,}:?', cell.strip()) is not None

    @staticmethod
    def _fix_invalid_table(lines):
        # Parse rows
        parsed_rows = [O1_pro_round_5._parse_row(ln) for ln in lines if '|' in ln]
        if not parsed_rows:
            return lines  # Nothing to fix

        # Get style from the first line (leading/trailing pipes)
        first_line = lines[0]
        style = (first_line.strip().startswith('|'), first_line.strip().endswith('|'))

        # Determine max columns
        max_cols = max(len(r) for r in parsed_rows)

        # Check for repeated-separator pattern
        repeated_sep = O1_pro_round_5._detect_repeated_separators(parsed_rows)

        # Normalize rows to have consistent column count
        parsed_rows = [O1_pro_round_5._normalize_row(r, max_cols) for r in parsed_rows]

        # We'll build the fixed table depending on repeated-separator usage
        fixed = []

        # Always treat the first row as header
        fixed.append(O1_pro_round_5._rebuild_row(parsed_rows[0], style))
        # Then insert a single separator row right after the header
        fixed.append(O1_pro_round_5._rebuild_row(['---'] * max_cols, style))

        if repeated_sep:
            # If repeated separators are detected, we place a separator after every data row
            i = 1
            while i < len(parsed_rows):
                # Skip original separator rows
                if O1_pro_round_5._is_separator_row(parsed_rows[i]):
                    i += 1
                    continue
                fixed.append(O1_pro_round_5._rebuild_row(parsed_rows[i], style))
                fixed.append(O1_pro_round_5._rebuild_row(['---'] * max_cols, style))
                i += 1
        else:
            # Otherwise, just copy data rows, skipping any original separator lines
            for r in parsed_rows[1:]:
                if not O1_pro_round_5._is_separator_row(r):
                    fixed.append(O1_pro_round_5._rebuild_row(r, style))

        return fixed

    @staticmethod
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
            if O1_pro_round_5._is_separator_row(rows[i]):
                odd_sep_count += 1
        return odd_sep_count >= total_odd / 2.0

    @staticmethod
    def _normalize_row(row, target_cols):
        if len(row) < target_cols:
            return row + [''] * (target_cols - len(row))
        elif len(row) > target_cols:
            # merge excess into the last cell
            return row[:target_cols-1] + [' '.join(row[target_cols-1:])]
        return row

    @staticmethod
    def _rebuild_row(cells, style):
        # Rebuild a row from cells, respecting leading/trailing pipe style
        row_str = " | ".join(cells)
        if style[0]:
            row_str = "| " + row_str
        if style[1]:
            row_str += " |"
        return row_str


class O3_mini_high_round_5:
    """
    Implementation based on o3-mini-high's solution for fixing invalid markdown tables.
    Refactored from the compressed version.
    """
    
    @staticmethod
    def fix_invalid_markdown_tables(markdown_text):
        lines = markdown_text.splitlines()
        out = []
        block = []
        in_table = False
        
        for line in lines:
            if '|' in line:
                block.append(line)
                in_table = True
            else:
                if in_table:
                    out.extend(O3_mini_high_round_5.process_table_block(block))
                    block = []
                    in_table = False
                out.append(line)
        
        if block:
            out.extend(O3_mini_high_round_5.process_table_block(block))
        
        return "\n".join(out)

    @staticmethod
    def process_table_block(lines):
        merged = O3_mini_high_round_5.merge_continuation_lines(lines)
        if len(merged) < 2 or not any('|' in ln for ln in merged):
            return lines
        if O3_mini_high_round_5.is_valid_table(merged):
            return lines
        return O3_mini_high_round_5.fix_table_block(merged)

    @staticmethod
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

    @staticmethod
    def parse_row(line):
        s = line.strip()
        if s.startswith('|'):
            s = s[1:]
        if s.endswith('|'):
            s = s[:-1]
        return [cell.strip() for cell in s.split('|')]

    @staticmethod
    def is_separator_cell(cell):
        return re.fullmatch(r':?-{3,}:?', cell.strip()) is not None

    @staticmethod
    def is_separator_row(cells):
        if not cells:
            return False
        return all(O3_mini_high_round_5.is_separator_cell(cell) for cell in cells if cell.strip())

    @staticmethod
    def is_valid_table(lines):
        if len(lines) < 2:
            return False
        rows = [O3_mini_high_round_5.parse_row(ln) for ln in lines if '|' in ln]
        if len(rows) < 2 or not O3_mini_high_round_5.is_separator_row(rows[1]):
            return False
        col_count = len(rows[0])
        return all(len(r) == col_count for r in rows)

    @staticmethod
    def normalize_row(row, target):
        if len(row) < target:
            return row + [''] * (target - len(row))
        elif len(row) > target:
            return row[:target-1] + [" ".join(row[target-1:])]
        return row

    @staticmethod
    def get_table_style(line):
        s = line.strip()
        return (s.startswith('|'), s.endswith('|'))

    @staticmethod
    def rebuild_row(cells, lead, trail):
        row = " | ".join(cells)
        if lead:
            row = "| " + row
        if trail:
            row = row + " |"
        return row

    @staticmethod
    def detect_table_pattern(rows):
        sep_idx = [i for i, r in enumerate(rows) if O3_mini_high_round_5.is_separator_row(r)]
        if len(sep_idx) >= 2 and all(i % 2 == 1 for i in sep_idx):
            return 'separator_after_each'
        return 'standard'

    @staticmethod
    def fix_table_block(lines):
        parsed = [O3_mini_high_round_5.parse_row(ln) for ln in lines if '|' in ln]
        style = O3_mini_high_round_5.get_table_style(lines[0])
        max_cols = max(len(r) for r in parsed) if parsed else 0
        norm = [O3_mini_high_round_5.normalize_row(r, max_cols) for r in parsed]
        pattern = O3_mini_high_round_5.detect_table_pattern(norm)
        
        fixed = []
        sep_row = O3_mini_high_round_5.rebuild_row(['---'] * max_cols, *style)
        
        if pattern == 'separator_after_each':
            fixed.append(O3_mini_high_round_5.rebuild_row(norm[0], *style))
            fixed.append(sep_row)
            i = 1
            while i < len(norm):
                if O3_mini_high_round_5.is_separator_row(norm[i]):
                    i += 1
                    continue
                fixed.append(O3_mini_high_round_5.rebuild_row(norm[i], *style))
                fixed.append(sep_row)
                i += 1
        else:
            fixed.append(O3_mini_high_round_5.rebuild_row(norm[0], *style))
            fixed.append(sep_row)
            for r in norm[1:]:
                if O3_mini_high_round_5.is_separator_row(r):
                    continue
                fixed.append(O3_mini_high_round_5.rebuild_row(r, *style))
        
        return fixed


# Main script to process a markdown file with all algorithms
if __name__ == "__main__":
    def process_file_with_all_fixers(input_file):
        """
        Process an input file with all table fixing implementations
        and save the results to separate output files.
        
        Args:
            input_file (str): Path to the input markdown file
        """
        print(f"Processing {input_file} with all markdown table fixers...")
        
        # Read the input file
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {input_file}: {e}")
            return
        
        # Process with each implementation
        implementations = {
            "claude37_round_1": Claude37_round_1,
            "claude37_round_2": Claude37_round_2,
            "claude37_round_3": Claude37_round_3,
            "claude37_round_4": Claude37_round_4,
            "claude37_round_5": Claude37_round_5,
            "grok3_round_1": Grok3_round_1,
            "grok3_round_2": Grok3_round_2,
            "grok3_round_3": Grok3_round_3,
            "grok3_round_4": Grok3_round_4,
            "grok3_round_5": Grok3_round_5,
            "o1_pro_round_1": O1_pro_round_1,
            "o1_pro_round_2": O1_pro_round_2,
            "o1_pro_round_3": O1_pro_round_3,
            "o1_pro_round_4": O1_pro_round_4,
            "o1_pro_round_5": O1_pro_round_5,
            "o3_mini_high_round_1": O3_mini_high_round_1,
            "o3_mini_high_round_2": O3_mini_high_round_2,
            "o3_mini_high_round_3": O3_mini_high_round_3,
            "o3_mini_high_round_4": O3_mini_high_round_4,
            "o3_mini_high_round_5": O3_mini_high_round_5
        }
        
        for name, impl in implementations.items():
            try:
                # Process with this implementation
                start_time = __import__('time').time()
                fixed_content = impl.fix_invalid_markdown_tables(content)
                end_time = __import__('time').time()
                
                # Save the result
                output_file = f"{input_file.rsplit('.', 1)[0]}__fixed_tables__{name}.md"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                
                # Report
                processing_time = end_time - start_time
                print(f"  {name}: Processed in {processing_time:.3f} seconds, saved to {output_file}")
            except Exception as e:
                print(f"  {name}: Error processing file: {e}")
    
    # Process the specified file
    input_file = "sample_10k_reformatted.md"
    process_file_with_all_fixers(input_file)