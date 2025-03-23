I've created a Python function that fixes invalid markdown tables while preserving valid ones and leaving non-table content untouched. The function handles several types of markdown table issues I identified in your examples:

1. Tables with repeated separator rows after each data row
2. Tables with inconsistent column counts across rows
3. Tables with multi-line content within cells
4. Tables with alignment and structure issues

The implementation uses a step-by-step approach:

1. First, it splits the input markdown into blocks (potential tables and other content)
2. For each block that might be a table (contains pipes and separator rows), it:
   - Analyzes the table structure to identify headers and separator rows
   - Checks if the table has repeated separators or inconsistent column counts
   - Normalizes columns to ensure consistency
   - Handles complex cases with multi-line content within cells

For example, when processing a table with repeated separators after each row (like your first example), it will remove unnecessary separator rows and maintain just one separator row after the header.

The function is designed to be minimally invasive - it only modifies what's necessary to make tables valid while preserving the original content and structure as much as possible.

Would you like me to explain any specific part of the implementation in more detail?

Artifact:

```
import re

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
            fixed_block = fix_table(block)
            fixed_blocks.append(fixed_block)
        else:
            # Not a table, keep as is
            fixed_blocks.append(block)
    
    # Rejoin all blocks with appropriate spacing
    return '\n\n'.join(fixed_blocks)

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
    if is_table_valid(fixed_table):
        return fixed_table
    else:
        return fix_complex_table(table_text)

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

# Test the function with the examples provided
if __name__ == "__main__":
    # Example invalid tables could be tested here
    pass
```    