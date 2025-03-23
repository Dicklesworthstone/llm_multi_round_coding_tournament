Below is a “best‐of‐all‐worlds” implementation that blends the best ideas from the four solutions. In summary, the function first splits the input into lines and groups “table blocks” (lines containing pipes and their immediate continuations). For each table block it merges any continuation lines, checks if the table is already valid (at least two rows, a valid separator row immediately after the header, and consistent cell counts) and—if not—normalizes each row (padding or merging extra cells), forces a uniform separator row (using the header’s original leading/trailing‑pipe style) and skips any extra separator rows. This minimally invasive fix leaves valid tables completely untouched while repairing invalid ones.

```python
import re
def fix_invalid_markdown_tables(markdown_text):
	lines = markdown_text.splitlines()
	out, block, in_table = [], [], False
	for line in lines:
		if '|' in line:
			block.append(line)
			in_table = True
		else:
			if in_table:
				out.extend(process_block(block))
				block, in_table = [], False
			out.append(line)
	if block: out.extend(process_block(block))
	return "\n".join(out)
def process_block(block_lines):
	merged = merge_cont_lines(block_lines)
	if valid_table(merged): return block_lines
	return fix_block(merged)
def merge_cont_lines(lines):
	merged, cur = [], None
	for ln in lines:
		if '|' in ln:
			if cur is not None: merged.append(cur)
			cur = ln.rstrip()
		elif ln.strip():
			if cur is not None: cur += " " + ln.strip()
			else: cur = ln.rstrip()
		else:
			if cur is not None: merged.append(cur); cur = None
			merged.append(ln)
	if cur is not None: merged.append(cur)
	return merged
def parse_row(ln):
	s = ln.strip()
	if s.startswith('|'): s = s[1:]
	if s.endswith('|'): s = s[:-1]
	return [cell.strip() for cell in s.split('|')]
def valid_sep_cell(cell):
	return re.fullmatch(r':?-{3,}:?', cell) is not None
def valid_table(lines):
	if len(lines) < 2: return False
	hdr, sep = parse_row(lines[0]), parse_row(lines[1])
	if len(hdr) != len(sep) or not all(valid_sep_cell(c) for c in sep if c.strip()):
		return False
	n = len(hdr)
	for ln in lines[2:]:
		if len(parse_row(ln)) != n: return False
	return True
def table_style(ln):
	s = ln.strip()
	return (s.startswith('|'), s.endswith('|'))
def rebuild_row(cells, style):
	s = " | ".join(cells)
	if style[0]: s = "|" + s
	if style[1]: s = s + "|"
	return s
def fix_block(lines):
	rows = [parse_row(ln) for ln in lines]
	style = table_style(lines[0])
	max_cols = max(len(r) for r in rows)
	norm = []
	for r in rows:
		if len(r) < max_cols: r = r + ['']*(max_cols-len(r))
		elif len(r) > max_cols: r = r[:max_cols-1] + [" ".join(r[max_cols-1:])]
		norm.append(r)
	fixed = []
	# Always use first row as header.
	fixed.append(norm[0])
	# Use an inserted uniform separator row.
	if len(norm) > 1 and all(valid_sep_cell(cell) for cell in norm[1]): 
		fixed.append(["---"]*max_cols)
	else:
		fixed.append(["---"]*max_cols)
	# Append data rows (skip any extra separator rows)
	for r in norm[2:] if len(norm)>1 else norm[1:]:
		if all(valid_sep_cell(cell) for cell in r): continue
		fixed.append(r)
	return [rebuild_row(r, style) for r in fixed]
# Example usage:
if __name__=="__main__":
	txt = """| ●| we have a limited customer base and limited sales and relationships with
international customers;
---|---|---  
| ●| difficulty in managing multinational operations;
---|---|---"""
	print(fix_invalid_markdown_tables(txt))
``` 

### Explanation

1. **Grouping and Merging:**  
   The code scans the markdown line‐by‐line. Any line containing a “|” is added to a table block; lines without a pipe flush the block. Continuation lines (without a pipe) are merged into the previous row.

2. **Validation:**  
   The helper `valid_table` splits each merged line into cells and checks that there are at least two rows, the second row is a valid “separator” row (using a regex that accepts optional colons and three or more dashes), and all rows have the same number of cells.

3. **Fixing:**  
   If a table is invalid, the fixer normalizes every row to the maximum column count (padding with empty strings or merging extra cells) and inserts a proper separator row immediately after the header. It also preserves the table’s original “style” (whether rows start or end with a pipe).

This hybrid solution leaves valid tables completely unchanged and fixes invalid ones in a minimally invasive way while handling multi-line cells and separator row issues.