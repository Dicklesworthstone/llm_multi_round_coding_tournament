Below is our hybrid “best of all worlds” implementation. It first scans the Markdown text line‐by‐line, groups contiguous table lines (also merging “wrapped” lines), and then checks whether the table already conforms to Markdown rules (header, a proper divider row immediately afterward, and consistent column counts). If the table is already valid it’s left completely unchanged; otherwise the function fixes issues by:
 
• Ensuring each row has the same (maximum) number of columns (merging overflow cells into the final cell if needed)  
• Inserting a correct divider row (using a simple “---” per column) if the second row isn’t already valid  
• Removing extra divider rows

The code also preserves the original table’s style regarding leading/trailing pipes.

```python
import re
def fix_invalid_markdown_tables(markdown_text):
 l=markdown_text.splitlines();o=[];tb=[]
 def flush(tb):
  if not tb:return []
  m=merge(tb)
  return tb if is_valid(m) else process(m)
 i=0
 while i<len(l):
  if '|' in l[i] or (tb and l[i].strip() and '|' not in l[i]):
   tb.append(l[i])
  else:
   if tb:o.extend(flush(tb));tb=[]
   o.append(l[i])
  i+=1
 if tb:o.extend(flush(tb))
 return "\n".join(o)
def merge(b):
 m=[]
 for ln in b:
  if '|' in ln: m.append(ln.rstrip())
  elif m and ln.strip(): m[-1]+=" "+ln.strip()
  else: m.append(ln.rstrip())
 return m
def is_valid(rws):
 if len(rws)<2:return False
 p=[ [c.strip() for c in re.split(r'(?<!\\)\|', rw.strip().strip('|'))] for rw in rws ]
 if len(p)<2:return False
 h=p[0]; d=p[1]
 if len(d)!=len(h):return False
 if not all(re.fullmatch(r':?-{3,}:?', cell) for cell in d):return False
 for r in p[2:]:
  if len(r)!=len(h):return False
 return True
def process(rws):
 p=[ [c.strip() for c in re.split(r'(?<!\\)\|', rw.strip().strip('|'))] for rw in rws ]
 mc=max(len(r) for r in p)
 np=[]
 for r in p:
  if len(r)<mc: r+=[ '' ]*(mc-len(r))
  elif len(r)>mc: r=r[:mc-1]+[" ".join(r[mc-1:])]
  np.append(r)
 h=np[0]; out=[h]
 idx=1
 if len(np)>1 and is_div_row(np[1]):
  out.append(np[1]); idx=2
 else:
  out.append(['---']*mc)
 for r in np[idx:]:
  if not is_div_row(r): out.append(r)
 st=style(rws[0])
 return [assemble(r,st) for r in out]
def is_div_row(r): return all(re.fullmatch(r':?-{3,}:?', cell) for cell in r)
def style(row):
 s=row.strip()
 return (s.startswith('|'), s.endswith('|'))
def assemble(cells, st):
 s=" | ".join(cells)
 if st[0]: s="|"+s
 if st[1]: s=s+"|"
 return s
```

### How it works

1. The main function splits the input into lines and groups contiguous “table block” lines (including continuation lines without a pipe).  
2. The helper function `merge` glues lines that are continuations of a previous table row.  
3. The function `is_valid` parses the merged rows and checks that there’s a header followed immediately by a divider row (each cell matching a pattern like “---”, possibly with colons), and that every row has the same number of cells. If so, the original block is left untouched.  
4. Otherwise, `process` splits each row into cells, pads (or merges) cells so that every row has the same maximum number of columns, ensures there’s exactly one divider row immediately after the header (inserting one if needed and removing extras), and finally reassembles each row using the original table’s style (preserving any leading/trailing pipes).

This implementation combines the strengths of all four proposals—careful block detection and merging, validity checking to avoid needless changes, robust cell–count normalization, and handling of repeated divider rows—to produce a minimally invasive fix for invalid Markdown tables.