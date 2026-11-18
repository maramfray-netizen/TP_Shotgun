#!/usr/bin/env python3
"""Fill report.md with real numbers: FastQC summary (MultiQC) and Table 6."""
import csv, os, re

REPORT = "report.md"
rep = open(REPORT, encoding="utf-8").read()

# ---- FastQC summary from MultiQC ----
qc_file = "01_qc/multiqc_data/multiqc_fastqc.txt"
if os.path.exists(qc_file):
    with open(qc_file, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    cols = [("Sample", "Sample"), ("Total Sequences", "Total sequences"),
            ("avg_sequence_length", "Mean length"), ("%GC", "%GC"),
            ("total_deduplicated_percentage", "% remaining after dedup"),
            ("per_base_sequence_quality", "Per-base quality"),
            ("per_sequence_gc_content", "GC content"),
            ("adapter_content", "Adapters"),
            ("overrepresented_sequences", "Overrepresented")]
    lines = ["| " + " | ".join(h for _, h in cols) + " |",
             "|" + "---|" * len(cols)]
    for r in rows:
        lines.append("| " + " | ".join(str(r.get(k, "n/a")) for k, _ in cols) + " |")
    block = ("<!-- QC:START -->\n**FastQC summary (from MultiQC):**\n\n"
             + "\n".join(lines) + "\n<!-- QC:END -->\n")
    if "<!-- QC:START -->" in rep:
        rep = re.sub(r"<!-- QC:START -->.*?<!-- QC:END -->\n", lambda m: block, rep, flags=re.S)
    else:
        rep = rep.replace("## 3. Read cleaning and host removal",
                          block + "\n## 3. Read cleaning and host removal", 1)

# ---- Table 6 ----
t6 = "03_results/table6_read_counts.tsv"
if os.path.exists(t6):
    d = dict(l.rstrip("\n").split("\t") for l in open(t6) if not l.startswith("step"))
    raw = int(d["raw"])
    pct = lambda x: f"{100 * int(x) / raw:.1f} %"
    new = ("| Step | Read pairs | % of raw reads |\n|---|---|---|\n"
           f"| Raw reads | {raw:,} | 100 % |\n"
           f"| After fastp | {int(d['after_fastp']):,} | {pct(d['after_fastp'])} |\n"
           f"| After host removal | {int(d['after_host_removal']):,} | {pct(d['after_host_removal'])} |\n")
    pat = r"\| Step \| Read pairs \| % of raw reads \|\n\|---\|---\|---\|\n(?:\|.*\n){3}"
    rep = re.sub(pat, lambda m: new, rep)

open(REPORT, "w", encoding="utf-8").write(rep)
print("report.md updated")
