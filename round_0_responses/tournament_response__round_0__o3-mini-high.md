Below is one implementation. It first groups consecutive lines that look like part of a table, then (using helper functions) checks whether the merged table block is valid (i.e. has a header, a proper “divider” row with dashes/colons and consistent cell counts, and all data rows matching the header’s column count). If not, it pads or merges extra cells and—in the absence of a valid divider row—inserts one immediately after the header, all while preserving the original pipe‐style. Valid tables (and non‑table content) pass through unchanged.

```python
import re
def fix_invalid_markdown_tables(markdown_text):
 def merge_block(block):
  merged = []
  for line in block:
   if '|' in line:
    merged.append(line.rstrip())
   elif merged and line.strip():
    merged[-1] += " " + line.strip()
   else:
    merged.append(line.rstrip())
  return merged
 def parse_row(line):
  s = line.strip()
  lead = s.startswith('|')
  trail = s.endswith('|')
  if lead: s = s[1:]
  if trail: s = s[:-1]
  return [cell.strip() for cell in s.split('|')]
 def is_separator_cell(cell):
  return bool(re.fullmatch(r':?-{3,}:?', cell.strip()))
 def is_valid_table_block(block):
  m = merge_block(block)
  if len(m) < 2: return False
  header = parse_row(m[0])
  divider = parse_row(m[1])
  if len(header) < 2 or len(divider) != len(header): return False
  if not all(is_separator_cell(cell) for cell in divider): return False
  for line in m[2:]:
   cells = parse_row(line)
   if len(cells) != len(header): return False
  return True
 def fix_table_block(block):
  m = merge_block(block)
  rows = [parse_row(line) for line in m if '|' in line]
  if not rows: return block
  max_cols = max(len(r) for r in rows)
  norm = []
  for r in rows:
   if len(r) < max_cols:
    r += [""] * (max_cols - len(r))
   elif len(r) > max_cols:
    r = r[:max_cols-1] + [" ".join(r[max_cols-1:]).strip()]
   norm.append(r)
  if len(norm) < 2 or not all(is_separator_cell(x) for x in norm[1]):
   sep = ["---"] * max_cols
   norm.insert(1, sep)
  else:
   norm[1] = ["---"] * max_cols
  first = m[0].strip()
  lead = first.startswith('|')
  trail = first.endswith('|')
  fixed = []
  for row in norm:
   line = " | ".join(row)
   if lead: line = "|" + line
   if trail: line = line + "|"
   fixed.append(line)
  return fixed
 lines = markdown_text.splitlines()
 out, block = [], []
 for line in lines:
  if '|' in line or (block and line.strip() and '|' not in line):
   block.append(line)
  else:
   if block:
    out.extend(block if is_valid_table_block(block) else fix_table_block(block))
    block = []
   out.append(line)
 if block:
  out.extend(block if is_valid_table_block(block) else fix_table_block(block))
 return "\n".join(out)
```

In this implementation the table “block” is only fixed when the parsed rows are inconsistent (or missing a proper divider). Otherwise the original text is left untouched. This meets the requirement of being minimally invasive and only fixing invalid markdown tables.