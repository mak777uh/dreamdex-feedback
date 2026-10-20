import re, pathlib
from collections import Counter
d = pathlib.Path(r"C:\111\agents\verifier\dreamdex-feedback\feedback")
rows=[]
for f in sorted(d.glob("*.md")):
    t=f.read_text(encoding="utf-8")
    sev=re.search(r"^Severity:\s*(\w+)",t,re.M).group(1)
    area=re.search(r"^Area:\s*(\w+)",t,re.M).group(1)
    rows.append((f.name[:2],sev,area))
maj=[r for r in rows if r[1]=="major"]; nor=[r for r in rows if r[1]=="normal"]
print("major:",len(maj)," normal:",len(nor))
print("major areas:", Counter(a for _,_,a in maj))
print("normal areas:", Counter(a for _,_,a in nor))
for r in rows: print(" ", r[0], r[1], r[2])