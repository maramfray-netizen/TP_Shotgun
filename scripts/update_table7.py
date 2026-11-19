#!/usr/bin/env python3
"""Fill Table 7 in report.md from Bracken (and MetaPhlAn when available)."""
import os, re

def norm(n):
    return n.replace("_", " ").strip().lower()

brk = []
for line in open("03_results/sample.bracken").read().splitlines()[1:]:
    f = line.split("\t")
    brk.append((f[0], float(f[6]) * 100))
top = sorted(brk, key=lambda x: -x[1])[:10]

mpa = {}
p = "03_results/sample_metaphlan.txt"
if os.path.exists(p):
    for line in open(p):
        if line.startswith("#"):
            continue
        f = line.rstrip("\n").split("\t")
        last = f[0].split("|")[-1]
        if last.startswith("s__"):
            mpa[norm(last[3:])] = float(f[2])

rows = ["| Rank | Species | Bracken relative abundance (%) | MetaPhlAn relative abundance (%) |",
        "|---|---|---|---|"]
for i, (name, ab) in enumerate(top, 1):
    if not mpa:
        m = "TODO"
    else:
        m = f"{mpa[norm(name)]:.2f}" if norm(name) in mpa else "not found"
    rows.append(f"| {i} | {name} | {ab:.2f} | {m} |")
new = "\n".join(rows) + "\n"

s = open("report.md", encoding="utf-8").read()
pat = (r"\| Rank \| Species \| Bracken relative abundance \(%\) \| "
       r"MetaPhlAn relative abundance \(%\) \|\n\|---\|---\|---\|---\|\n(?:\|.*\n){10}")
s, n = re.subn(pat, lambda m: new, s)
open("report.md", "w", encoding="utf-8").write(s)
print("Table 7 updated" if n else "Table 7 pattern not found")
