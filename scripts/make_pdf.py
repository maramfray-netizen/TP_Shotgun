#!/usr/bin/env python3
"""Build the TP2 summary PDF from the repository files (run from the repo root)."""
import json, os, re
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph,
                                Preformatted, SimpleDocTemplate, Spacer, Table, TableStyle)

# ------------------------- EDIT THESE (from the Galaxy forms) -------------------------
MPA_GALAXY = "MetaPhlAn on usegalaxy.eu, tool version and database: FILL_IN"
MPA_FILE = "03_results/sample_metaphlan.txt"
OUT = "TP2_Shotgun_Report_MaramFray.pdf"
REPO = "https://github.com/maramfray-netizen/TP_Shotgun"
# --------------------------------------------------------------------------------------

esc = lambda s: escape(str(s))
styles = getSampleStyleSheet()
B = ParagraphStyle("B", parent=styles["BodyText"], fontSize=10, leading=14, spaceAfter=6)
SM = ParagraphStyle("SM", parent=B, fontSize=8.5, leading=11, spaceAfter=2)
CODE = ParagraphStyle("CODE", parent=styles["Code"], fontSize=7, leading=8.8)
story, warnings = [], []

def p(t, st=B): story.append(Paragraph(t, st))
def h1(t): story.append(Paragraph(t, styles["Heading1"]))
def h2(t): story.append(Paragraph(t, styles["Heading2"]))
def code(t): story.append(Preformatted(t, CODE)); story.append(Spacer(1, 6))

def tbl(data, widths=None):
    rows = [[Paragraph(str(c), SM) for c in r] for r in data]
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                           ("VALIGN", (0, 0), (-1, -1), "TOP"),
                           ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8eef5"))]))
    story.append(t); story.append(Spacer(1, 8))

def fig(path, caption, width=15 * cm):
    if not os.path.exists(path):
        warnings.append(f"missing figure {path}")
        p(f"<i>[Figure missing: {esc(path)}]</i>"); return
    w, h = ImageReader(path).getSize()
    story.append(KeepTogether([Image(path, width=width, height=width * h / w),
                               Paragraph(f"<i>{esc(caption)}</i>", SM), Spacer(1, 8)]))

def norm(n): return n.replace("_", " ").strip().lower()

def bracken_top(n=10):
    f = "03_results/sample.bracken"
    if not os.path.exists(f): return []
    rows = [l.rstrip("\n").split("\t") for l in open(f, encoding="utf-8")][1:]
    return sorted([(r[0], float(r[6]) * 100) for r in rows], key=lambda x: -x[1])[:n]

def metaphlan_top(n=10):
    out = []
    if not os.path.exists(MPA_FILE): return out
    for line in open(MPA_FILE, encoding="utf-8"):
        if line.startswith("#"): continue
        f = line.rstrip("\n").split("\t")
        last = f[0].split("|")[-1]
        if last.startswith("s__") and len(f) > 2:
            try: out.append((last[3:].replace("_", " "), float(f[2])))
            except ValueError: pass
    return sorted(out, key=lambda x: -x[1])[:n]

def read_table6():
    f = "03_results/table6_read_counts.tsv"
    if not os.path.exists(f): return None
    return dict(l.rstrip("\n").split("\t") for l in open(f) if not l.startswith("step"))

# ================================ TITLE ================================
story.append(Paragraph("TP 2: Shotgun metagenomics, read-based approach", styles["Title"]))
p("<b>Maram Fray</b>, M2 research master's in bioinformatics (omics data analysis)", B)
p(f"Repository (code, scripts, figures, reports): <link href='{REPO}' color='blue'>{REPO}</link>", B)
p("<b>Summary.</b> Quality control, read cleaning, host-read removal and Kraken2/Bracken taxonomic "
  "profiling were completed on the command line. MetaPhlAn was run on Galaxy. The HUMAnN functional "
  "profile could not be obtained despite several attempts, which are documented honestly in section 5.", B)

# ================================ 1. INTRODUCTION ================================
h1("1. Introduction")
p("In shotgun metagenomics, all DNA of a sample is sequenced. In the read-based approach, each read is "
  "compared directly with reference databases, which is fast and sensitive, including for low-abundance "
  "organisms, but only detects what is already present in the databases. The assembly-based approach (TP 3) "
  "reconstructs contigs and genomes (MAGs), which can reveal new organisms at a higher computational cost.")
p("The objectives were: (i) assess and improve the quality of Illumina shotgun reads; (ii) remove host reads; "
  "(iii) obtain the taxonomic profile (Kraken2/Bracken, MetaPhlAn) and the functional profile (HUMAnN) "
  "of a human gut sample without assembly.")

# ================================ 2. DATA AND ENVIRONMENT ================================
h1("2. Data and environment")
p("<b>Dataset.</b> SRA run <b>SRR8114121</b> (human gut metagenome, Illumina, paired-end), chosen because no "
  "accession was provided. Only the first 100,000 spots were downloaded "
  "(<font face='Courier'>fastq-dump -X 100000 --split-3</font>), which gave 94,121 properly paired read pairs. "
  "Read lengths range from 44 to 143 bp: according to the study description the reads had already been "
  "quality-trimmed and filtered against the human genome by the submitters, so cleaning and host removal "
  "change little.")
p("<b>Computing environment.</b> Windows 11 with WSL2 (Ubuntu), VS Code, conda (Miniforge). WSL had 4 cores and "
  "about 2.8 GB of RAM, which limited the choice of reference databases (see section 5).")
tbl([["Tool", "Version"],
     ["FastQC", "0.13.0"], ["MultiQC", "1.35"], ["fastp", "1.4.0"], ["Bowtie2", "2.5.5"],
     ["Kraken2", "2.17.2"], ["SRA Toolkit (fastq-dump, fasterq-dump)", "3.4.1"],
     ["Bracken, Krona", "see environment_tp2_qc.yml in the repository"],
     ["MetaPhlAn (conda, local attempt)", "4.2.x (4.2.5 / 4.2.6 reported)"],
     ["HUMAnN (conda, local) and Galaxy tool", "3.9 (Galaxy: 3.9+galaxy1; 3.0.0+galaxy1 also tested)"],
     ["MetaPhlAn on Galaxy", esc(MPA_GALAXY)]], [7 * cm, 9.5 * cm])
tbl([["Database", "Use"],
     ["GRCh38 (GRCh38_noalt_as) Bowtie2 index", "Host read removal"],
     ["Kraken2/Bracken Standard-8 (prebuilt, capped at 8 GB)",
      "Taxonomic classification; chosen instead of the full Standard database because of limited RAM. "
      "Run with --memory-mapping. Bracken -r 150 as in the handout."]], [7 * cm, 9.5 * cm])

# ================================ 3. PIPELINE ================================
h1("3. Pipeline")
tbl([["Step", "Tool and parameters", "Justification"],
     ["1. Raw QC", "FastQC, MultiQC", "Phred quality per position, GC, duplication, adapters"],
     ["2. Cleaning", "fastp --detect_adapter_for_pe -q 20 -l 50",
      "Q20 = at most 1% base error; reads shorter than 50 bp align ambiguously"],
     ["3. Host removal", "Bowtie2 GRCh38 --very-sensitive --mm, keep unaligned pairs (--un-conc-gz)",
      "Reduce noise and computing time; protect donor genetic data"],
     ["4.1 Taxonomy", "Kraken2 --paired --memory-mapping; Bracken -r 150 -l S -t 10; Krona",
      "k-mer LCA assignment; Bracken re-estimates species abundance"],
     ["4.2 Taxonomy", "MetaPhlAn (Galaxy)", "Clade-specific marker genes; closer to cell abundance"],
     ["5. Function", "HUMAnN (Galaxy)", "Gene families and MetaCyc pathways (not obtained)"]],
    [2.6 * cm, 7 * cm, 6.9 * cm])
p("<b>Main commands (command line part)</b>")
code("""fastq-dump -X 100000 --split-3 --gzip -O 00_raw SRR8114121
fastqc 00_raw/sample_R1.fastq.gz 00_raw/sample_R2.fastq.gz --outdir 01_qc/ -t 2
multiqc 01_qc/ -o 01_qc/ -s
fastp -i 00_raw/sample_R1.fastq.gz -I 00_raw/sample_R2.fastq.gz \\
  -o 02_clean/sample_R1.clean.fq.gz -O 02_clean/sample_R2.clean.fq.gz \\
  --detect_adapter_for_pe -q 20 -l 50 -w 4 -h 01_qc/fastp.html -j 01_qc/fastp.json
bowtie2 -x GRCh38_noalt_as -1 02_clean/sample_R1.clean.fq.gz -2 02_clean/sample_R2.clean.fq.gz \\
  --very-sensitive --mm -p 4 --un-conc-gz 02_clean/sample_nohost_R%.fq.gz -S /dev/null
kraken2 --db k2_standard_08 --memory-mapping --paired --gzip-compressed --threads 4 \\
  --report 03_results/sample.kreport --output 03_results/sample.kraken \\
  02_clean/sample_nohost_R1.fq.gz 02_clean/sample_nohost_R2.fq.gz
bracken -d k2_standard_08 -i 03_results/sample.kreport -o 03_results/sample.bracken -r 150 -l S -t 10
ktImportTaxonomy -t 5 -m 3 -o 03_results/sample_krona.html 03_results/sample.kreport""")
p("The complete scripts are in the repository (<font face='Courier'>scripts/</font>).")

# ================================ 4. RESULTS ================================
h1("4. Results and answers to the questions")
h2("4.1 Quality control of the raw reads (Question 1)")
p("The raw dataset contains 94,121 read pairs (11.2 Mbp per file). Read lengths range from 44 to 143 bp "
  "(mean about 119 bp, median 128 bp) instead of a uniform 150 bp, which indicates that the reads were already "
  "quality-trimmed before submission. Mean GC content is 46% for R1 and R2, and about 2.3% of sequences are "
  "duplicates (FastQC). The per-base sequence quality, per-sequence quality and adapter content modules passed, "
  "and fastp found no adapter-dimer reads. Warnings were raised for per-sequence GC content, per-base sequence "
  "content and sequence length distribution (expected for a mixed gut community and trimmed reads), and for "
  "overrepresented sequences in the raw reads (not investigated further; no warning after cleaning). "
  "According to fastp, 97.4% of bases had Q20 or more and 90.7% had Q30 or more before cleaning.")
p("A Phred score is defined as Q = -10 x log<sub>10</sub>(P), where P is the probability that the base call is wrong. "
  "Q30 therefore means an error probability of 0.1% (99.9% accuracy), and Q20 means 1%.")
fp = "01_qc/fastp.json"
if os.path.exists(fp):
    j = json.load(open(fp)); s = j["summary"]; fr = j["filtering_result"]
    row = lambda k, name: [name, f"{s[k]['total_reads']:,}", f"{100*s[k]['q20_rate']:.1f}%",
                           f"{100*s[k]['q30_rate']:.1f}%", f"{100*s[k]['gc_content']:.1f}%"]
    tbl([["fastp", "Reads", "Q20", "Q30", "GC"],
         row("before_filtering", "Before cleaning"), row("after_filtering", "After cleaning")],
        [4 * cm, 3.5 * cm, 3 * cm, 3 * cm, 3 * cm])
    p(f"fastp removed {fr['low_quality_reads']:,} low-quality reads and {fr['too_short_reads']:,} reads shorter "
      f"than 50 bp.")
else:
    warnings.append("01_qc/fastp.json not found")
fig("figures/fig1_quality_per_position.png", "Figure 1. Mean base quality per position, before and after fastp.")
fig("figures/fig2_gc_per_position.png", "Figure 2. GC content per position, before and after fastp.")
fig("figures/fig3_read_length.png", "Figure 3. Read length distribution (R1), raw vs cleaned.", 10 * cm)

h2("4.2 Cleaning and host removal (Table 6)")
d = read_table6()
if d:
    raw = int(d["raw"]); pc = lambda x: f"{100 * int(x) / raw:.1f} %"
    tbl([["Step", "Read pairs", "% of raw reads"],
         ["Raw reads", f"{raw:,}", "100 %"],
         ["After fastp", f"{int(d['after_fastp']):,}", pc(d["after_fastp"])],
         ["After host removal", f"{int(d['after_host_removal']):,}", pc(d["after_host_removal"])]],
        [6 * cm, 4.5 * cm, 4.5 * cm])
else:
    warnings.append("table6_read_counts.tsv not found")
p("Bowtie2 reported an overall alignment rate of 0.01%, and no read pair was removed by host filtering. This is "
  "expected because the submitters had already filtered human reads. Note that --un-conc-gz keeps every pair "
  "that does not align concordantly, which is slightly less strict than discarding a pair when only one mate aligns.")
fig("figures/fig4_read_pairs.png", "Figure 4. Read pairs at each step.", 9 * cm)

h2("4.3 Kraken2/Bracken profile (Question 3)")
p("Kraken2 processed 89,953 read pairs: <b>47,392 (52.69%) were classified and 42,561 (47.31%) were unclassified</b>. "
  "Possible explanations, not tested individually: the Standard-8 database contains less reference information "
  "than the full Standard database; many gut organisms are uncultured or missing from RefSeq; reads are short and "
  "variable in length (50 to 143 bp), and Kraken2 needs exact k-mer matches, so errors reduce the hits; and "
  "organisms outside the database (fungi, phages, plasmids) cannot be assigned. A Krona chart is in the repository "
  "(<font face='Courier'>03_results/sample_krona.html</font>).")

h2("4.4 MetaPhlAn and comparison of profiles (Question 2, Table 7)")
bt, mt = bracken_top(), metaphlan_top()
if bt:
    n = max(len(bt), len(mt))
    rows = [["Rank", "Bracken species", "Bracken (%)", "MetaPhlAn species", "MetaPhlAn (%)"]]
    for i in range(n):
        b = bt[i] if i < len(bt) else ("", None)
        m = mt[i] if i < len(mt) else ("not run" if not mt else "", None)
        rows.append([i + 1, esc(b[0]), f"{b[1]:.2f}" if b[1] is not None else "",
                     esc(m[0]), f"{m[1]:.2f}" if m[1] is not None else ""])
    tbl(rows, [1.2 * cm, 5.2 * cm, 2.4 * cm, 5.2 * cm, 2.5 * cm])
else:
    warnings.append("sample.bracken not found")
if mt:
    shared = {norm(a) for a, _ in bt} & {norm(a) for a, _ in mt}
    p(f"MetaPhlAn was run on Galaxy ({esc(MPA_GALAXY)}). {len(shared)} of the top 10 species have the same name "
      "in both lists; differences in names (taxonomic synonyms between the Kraken2 RefSeq taxonomy and MetaPhlAn "
      "SGB names) can hide further matches and should be checked by hand before interpreting the ranks.")
else:
    p("The MetaPhlAn profile was not available when this PDF was generated.")
p("<b>Why the profiles differ.</b> Kraken2 assigns each read to the lowest common ancestor of the genomes that "
  "share its k-mers (k = 35) and Bracken redistributes reads to species level, so the output is a proportion of "
  "<i>reads</i>, biased towards organisms with large genomes or many reference genomes, against a RefSeq-based "
  "database. MetaPhlAn maps reads to clade-specific marker genes and normalises the coverage by marker length, "
  "so its output is closer to a proportion of <i>cells</i>, against a different catalogue (SGB marker genes). "
  "The units, databases, denominators and taxonomic names therefore differ, and taxa absent from one "
  "database appear only in the other tool.")

h2("4.5 Functional profile with HUMAnN (Question 4)")
p("<b>The HUMAnN functional profile was not obtained</b>, so the five most abundant MetaCyc pathways are not "
  "reported and no pathway names are given here. The failed attempts are described in section 5.")

h2("4.6 Limits of the read-based approach (Question 5)")
p("The read-based approach only detects what is already present in the reference databases. In a poorly described "
  "environmental microbiome most organisms are uncultured, so many reads cannot be assigned (even in this "
  "well-studied gut sample, 47% of read pairs were unclassified with Standard-8). Reads of novel organisms can "
  "also be assigned to the closest known relative, which biases the profile. Short reads give little gene context "
  "and cannot reconstruct genomes, so new genes and pathways are missed, and functional profiling is limited to "
  "genes already annotated in ChocoPhlAn or UniRef. Assembly-based approaches (TP 3) can discover new organisms, "
  "at the cost of heavier computation and the need for sufficient coverage.")

# ================================ 5. DIFFICULTIES ================================
h1("5. What did not work (and why)")
p("I report these attempts so the limits of the results are clear. Error texts are quoted from the tools.")
for t in [
    "<b>MetaPhlAn on the local machine.</b> The marker database archive was downloaded twice (about 14 GB, then "
    "18.7 GB). The first download was truncated (tar: Unexpected EOF). The second passed its md5 check, but "
    "MetaPhlAn reported that the downloaded indexes were not compatible with the installed Bowtie2 (2.5.5) and "
    "tried to rebuild the index; <font face='Courier'>bowtie2-build</font> was killed (SIGKILL), consistent with "
    "insufficient memory (about 2.8 GB of RAM available). The MetaPhlAn 4.1 documentation states that a large "
    "amount of memory is required (at least 25 GB).",
    "<b>HUMAnN on the local machine.</b> The conda environment initially used Python 3.13 and HUMAnN could not "
    "import its package; recreating it with Python 3.12 fixed this (HUMAnN 3.9 runs). The databases (ChocoPhlAn, "
    "UniRef90) and the MetaPhlAn profile were still missing, and the memory available was too small for the "
    "translated search.",
    "<b>MetaPhlAn on Galaxy (usegalaxy.eu).</b> This worked and gave the profile used in Table 7.",
    "<b>HUMAnN on Galaxy.</b> My first attempts used incorrect inputs. With the default DEMO databases, HUMAnN 3.9 "
    "stopped with: <i>CRITICAL ERROR: The directory provided for ChocoPhlAn contains files ... that are not of the "
    "expected version.</i> With the full databases and HUMAnN 3.0.0, it stopped with the same type of error, "
    "expecting version 201901b while the full database is v201901_v31. With HUMAnN 3.9 it then stopped with: "
    "<i>The MetaPhlAn taxonomic profile provided was not generated with the database version v3 or vJun23</i>, "
    "while the marker database offered in the form was mpa_vOct22_CHOCOPhlAnSGB_202212. I could not find a "
    "combination of tool version, database and profile accepted by HUMAnN on Galaxy in the time available."]:
    story.append(Paragraph("&bull; " + t, B))
p("Because of these failures, the functional part of the TP (Question 4) is not answered with data.")

# ================================ 6. AI QUESTION ================================
h1("6. AI question")
ai = "ai_question.md"
if os.path.exists(ai):
    text = open(ai, encoding="utf-8").read()
    if "TODO" in text: warnings.append("ai_question.md still contains TODO")
    buf = []
    def flush():
        global buf
        if buf: p(esc(" ".join(buf))); buf = []
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            flush(); story.append(Paragraph(esc(s.lstrip("# ").strip()), styles["Heading3"]))
        elif s.startswith("- "):
            flush(); p("&bull; " + esc(s[2:]))
        elif not s: flush()
        else: buf.append(s)
    flush()
else:
    warnings.append("ai_question.md not found")
    p("<i>[AI question section missing]</i>")

# ================================ 7. REPRODUCIBILITY + REFERENCES ================================
h1("7. Reproducibility")
p(f"All code, figures and reports are in <link href='{REPO}' color='blue'>{REPO}</link>: "
  "<font face='Courier'>scripts/run_tp2.sh</font> (pipeline), <font face='Courier'>scripts/make_figures.py</font>, "
  "<font face='Courier'>report.md</font>, <font face='Courier'>environment_tp2_qc.yml</font>.")
h1("References")
for r in [
    "Wood DE, Lu J, Langmead B. Improved metagenomic analysis with Kraken 2. Genome Biol. 2019;20:257. doi:10.1186/s13059-019-1891-0",
    "Lu J, Breitwieser FP, Thielen P, Salzberg SL. Bracken: estimating species abundance in metagenomics data. PeerJ Comput Sci. 2017;3:e104. doi:10.7717/peerj-cs.104",
    "Blanco-Miguez A, et al. Extending and improving metagenomic taxonomic profiling with uncharacterized species using MetaPhlAn 4. Nat Biotechnol. 2023;41:1633-1644. doi:10.1038/s41587-023-01688-w",
    "Beghini F, et al. Integrating taxonomic, functional, and strain-level profiling of diverse microbial communities with bioBakery 3. eLife. 2021;10:e65088. doi:10.7554/eLife.65088",
    "Chen S, Zhou Y, Chen Y, Gu J. fastp: an ultra-fast all-in-one FASTQ preprocessor. Bioinformatics. 2018;34:i884-i890. doi:10.1093/bioinformatics/bty560",
    "Langmead B, Salzberg SL. Fast gapped-read alignment with Bowtie 2. Nat Methods. 2012;9:357-359. doi:10.1038/nmeth.1923",
    "Ewels P, Magnusson M, Lundin S, Kaller M. MultiQC: summarize analysis results for multiple tools and samples in a single report. Bioinformatics. 2016;32:3047-3048. doi:10.1093/bioinformatics/btw354",
    "Ondov BD, Bergman NH, Phillippy AM. Interactive metagenomic visualization in a Web browser. BMC Bioinformatics. 2011;12:385. doi:10.1186/1471-2105-12-385",
    "The Galaxy Community. The Galaxy platform for accessible, reproducible, and collaborative data analyses: 2024 update. Nucleic Acids Res. 2024;52:W83-W94. doi:10.1093/nar/gkae410"]:
    story.append(Paragraph("&bull; " + esc(r), SM))
p("<i>The DOIs above should be opened and checked before submission.</i>", SM)

def footer(c, doc):
    c.setFont("Helvetica", 8)
    c.drawString(2 * cm, 1.1 * cm, "TP 2 Shotgun metagenomics - Maram Fray")
    c.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")

SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm,
                  topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                  title="TP2 Shotgun metagenomics", author="Maram Fray").build(
    story, onFirstPage=footer, onLaterPages=footer)
if "FILL_IN" in MPA_GALAXY: warnings.append("MPA_GALAXY still contains FILL_IN")
print("PDF written:", OUT)
for w in warnings: print("WARNING:", w)
