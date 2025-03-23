Below is a “best‐of‐all‐worlds” implementation that combines robust table‐block detection, careful merging of continuation lines, style preservation, and pattern‐based fixing. In brief, the function splits the input into table blocks (lines containing “|”), merges any continuation lines (i.e. lines without pipes that belong to the previous cell), checks if the table is already valid (with a header, a proper separator row, and consistent column counts) and—if not—rebuilds the table. The rebuild routine first normalizes each row to the maximum number of cells (padding or merging extra cells) and then uses one of two patterns: either the standard “header + one separator + data” or, if it detects a repeating “separator after every data row” pattern, it preserves that rhythm. This approach preserves valid tables entirely while minimally modifying invalid ones.

Below is the complete code:

```python
import re
def fix_invalid_markdown_tables(markdown_text):
 lines=markdown_text.splitlines(); out=[]; block=[]; in_table=False
 for line in lines:
  if '|' in line:
   block.append(line)
   in_table=True
  else:
   if in_table:
    out.extend(process_table_block(block)); block=[]; in_table=False
   out.append(line)
 if block: out.extend(process_table_block(block))
 return "\n".join(out)
def process_table_block(lines):
 merged=merge_continuation_lines(lines)
 if len(merged)<2 or not any('|' in ln for ln in merged): return lines
 if is_valid_table(merged): return lines
 return fix_table_block(merged)
def merge_continuation_lines(lines):
 merged=[]; current=None
 for line in lines:
  if '|' in line:
   if current is not None: merged.append(current)
   current=line.rstrip()
  elif line.strip():
   if current is not None: current+=" "+line.strip()
   else: current=line.rstrip()
  else:
   if current is not None: merged.append(current); current=None
   merged.append(line)
 if current is not None: merged.append(current)
 return merged
def parse_row(line):
 s=line.strip()
 if s.startswith('|'): s=s[1:]
 if s.endswith('|'): s=s[:-1]
 return [cell.strip() for cell in s.split('|')]
def is_separator_cell(cell):
 return re.fullmatch(r':?-{3,}:?',cell.strip()) is not None
def is_separator_row(cells):
 if not cells: return False
 return all(is_separator_cell(cell) for cell in cells if cell.strip())
def is_valid_table(lines):
 if len(lines)<2: return False
 rows=[parse_row(ln) for ln in lines if '|' in ln]
 if len(rows)<2 or not is_separator_row(rows[1]): return False
 col_count=len(rows[0])
 return all(len(r)==col_count for r in rows)
def normalize_row(row, target):
 if len(row)<target: return row+['']*(target-len(row))
 elif len(row)>target: return row[:target-1]+[" ".join(row[target-1:])]
 return row
def get_table_style(line):
 s=line.strip()
 return (s.startswith('|'), s.endswith('|'))
def rebuild_row(cells, lead, trail):
 row=" | ".join(cells)
 if lead: row="| "+row
 if trail: row=row+" |"
 return row
def detect_table_pattern(rows):
 sep_idx=[i for i,r in enumerate(rows) if is_separator_row(r)]
 if len(sep_idx)>=2 and all(i%2==1 for i in sep_idx): return 'separator_after_each'
 return 'standard'
def fix_table_block(lines):
 parsed=[parse_row(ln) for ln in lines if '|' in ln]
 style=get_table_style(lines[0])
 max_cols=max(len(r) for r in parsed) if parsed else 0
 norm=[normalize_row(r, max_cols) for r in parsed]
 pattern=detect_table_pattern(norm)
 fixed=[]; sep_row=rebuild_row(['---']*max_cols,*style)
 if pattern=='separator_after_each':
  fixed.append(rebuild_row(norm[0],*style)); fixed.append(sep_row)
  i=1
  while i<len(norm):
   if is_separator_row(norm[i]): i+=1; continue
   fixed.append(rebuild_row(norm[i],*style)); fixed.append(sep_row); i+=1
 else:
  fixed.append(rebuild_row(norm[0],*style)); fixed.append(sep_row)
  for r in norm[1:]:
   if is_separator_row(r): continue
   fixed.append(rebuild_row(r,*style))
 return fixed

# Example usage:
if __name__=="__main__":
 txt="""| ●| we have a limited customer base and limited sales and relationships with
international customers;  
---|---|---  
| ●| difficulty in managing multinational operations;  
---|---|---"""
 print(fix_invalid_markdown_tables(txt))
```

This hybrid solution preserves valid tables exactly, correctly merges continuation lines, and uses pattern detection to minimally fix irregularities.