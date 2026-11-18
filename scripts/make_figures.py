#!/usr/bin/env python3
"""Make report figures from fastp.json, the FASTQ files and Table 6."""
import gzip, json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

os.makedirs("figures", exist_ok=True)
j = json.load(open("01_qc/fastp.json"))

# Fig 1: mean base quality per position, before vs after fastp
fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, rd, title in zip(axes, ("read1", "read2"), ("Read 1", "Read 2")):
    for stage, label in (("before_filtering", "Before fastp"), ("after_filtering", "After fastp")):
        q = j[f"{rd}_{stage}"]["quality_curves"]["mean"]
        ax.plot(range(1, len(q) + 1), q, label=label)
    ax.axhline(30, ls="--", c="grey", lw=0.8)
    ax.axhline(20, ls=":", c="grey", lw=0.8)
    ax.set_title(title); ax.set_xlabel("Position in read (bp)")
axes[0].set_ylabel("Mean Phred score (dashed Q30, dotted Q20)")
axes[0].legend()
fig.tight_layout(); fig.savefig("figures/fig1_quality_per_position.png", dpi=150); plt.close(fig)

# Fig 2: GC content per position
fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, rd, title in zip(axes, ("read1", "read2"), ("Read 1", "Read 2")):
    for stage, label in (("before_filtering", "Before fastp"), ("after_filtering", "After fastp")):
        g = [100 * x for x in j[f"{rd}_{stage}"]["content_curves"]["GC"]]
        ax.plot(range(1, len(g) + 1), g, label=label)
    ax.set_title(title); ax.set_xlabel("Position in read (bp)")
axes[0].set_ylabel("GC content (%)"); axes[0].legend()
fig.tight_layout(); fig.savefig("figures/fig2_gc_per_position.png", dpi=150); plt.close(fig)

# Fig 3: read length distribution (R1), raw vs cleaned
def lengths(path):
    with gzip.open(path, "rt") as f:
        return [len(line.rstrip("\n")) for i, line in enumerate(f) if i % 4 == 1]

raw = lengths("00_raw/sample_R1.fastq.gz")
clean = lengths("02_clean/sample_R1.clean.fq.gz")
fig, ax = plt.subplots(figsize=(6, 4))
bins = range(40, 150, 2)
ax.hist(raw, bins=bins, alpha=0.6, label=f"Raw (n={len(raw):,})")
ax.hist(clean, bins=bins, alpha=0.6, label=f"After fastp (n={len(clean):,})")
ax.set_xlabel("Read length (bp)"); ax.set_ylabel("Number of reads"); ax.legend()
ax.set_title("Read length distribution (R1)")
fig.tight_layout(); fig.savefig("figures/fig3_read_length.png", dpi=150); plt.close(fig)

# Fig 4: read pairs at each step (Table 6)
t6 = dict(l.rstrip("\n").split("\t") for l in open("03_results/table6_read_counts.tsv") if not l.startswith("step"))
steps = ["Raw", "After fastp", "After host removal"]
vals = [int(t6["raw"]), int(t6["after_fastp"]), int(t6["after_host_removal"])]
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(steps, vals)
for i, v in enumerate(vals):
    ax.text(i, v, f"{v:,}", ha="center", va="bottom")
ax.set_ylabel("Read pairs"); ax.set_title("Read pairs at each step")
fig.tight_layout(); fig.savefig("figures/fig4_read_pairs.png", dpi=150); plt.close(fig)
print("Figures written to figures/")
