# TP 2: Shotgun Metagenomics, Read-Based Approach

**Author:** Maram Fray
**Sample:** SRRxxxxxxx (human fecal sample, Illumina paired-end 2 × 150 bp)
**Modality:** Command line (conda, WSL2 Ubuntu, VS Code)

## 1. Methods and parameter justification

| Step | Tool and parameters | Justification |
|---|---|---|
| QC | FastQC, MultiQC | Phred quality per position, GC content, duplication, adapters |
| Cleaning | fastp `--detect_adapter_for_pe -q 20 -l 50` | Q20 = at most 1% base error; reads shorter than 50 bp give ambiguous alignments |
| Host removal | Bowtie2 GRCh38 `--very-sensitive`, keep concordant unaligned pairs | Reduce noise and computing time; protect donor genetic data |
| Taxonomy 1 | Kraken2 (Standard DB, `--paired`) + Bracken `-r 150 -l S -t 10` | k-mer LCA assignment; Bracken re-estimates abundance at species level |
| Taxonomy 2 | MetaPhlAn (clade-specific marker genes) | Estimates relative abundance of cells, not reads |
| Function | HUMAnN (ChocoPhlAn, UniRef90, MetaCyc), reusing the MetaPhlAn profile | Consistent taxonomic and functional profiles |

## 2. Raw read quality control

**Question 1.** Describe the FastQC report: per-base quality (Phred score), GC content, overrepresented sequences, adapter presence. What does a Q30 score mean?

**Answer:**
TODO

*Hint:* Q = -10 × log10(P), so Q20 = 1% error and Q30 = 0.1% error (99.9% base call accuracy). Add a MultiQC screenshot (R1 vs R2, before vs after fastp).

## 3. Read cleaning and host removal

**Table 6.** Number of read pairs at each step (from `03_results/table6_read_counts.tsv`).

| Step | Read pairs | % of raw reads |
|---|---|---|
| Raw reads | | 100 % |
| After fastp | | |
| After host removal | | |

## 4. Taxonomic profiles

**Table 7.** Ten most abundant species.

| Rank | Species | Bracken relative abundance (%) | MetaPhlAn relative abundance (%) |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |
| 6 | | | |
| 7 | | | |
| 8 | | | |
| 9 | | | |
| 10 | | | |

**Question 2.** Compare the Kraken2/Bracken and MetaPhlAn profiles. Explain the differences from the principle of each tool (k-mer classification vs marker genes).

**Answer:**
TODO

**Question 3.** What proportion of reads was not classified by Kraken2? Suggest explanations.

**Answer:**
TODO (take the percentage from the first line of `sample.kreport`)

## 5. Functional profile

**Question 4.** List the 5 most abundant MetaCyc pathways. Which are assigned to a specific species and which remain "unclassified"?

**Answer:**
TODO

**Question 5.** What are the limits of the read-based approach for studying a poorly described environmental microbiome?

**Answer:**
TODO

## 6. AI question (TP 2)

Compare your Kraken2/Bracken and MetaPhlAn profiles of the same sample, then ask an AI to explain the differences. Check each explanation against the tool papers (Wood et al., 2019; Blanco-Míguez et al., 2023): reference database, unit of measure (read proportion vs genome relative abundance), taxa absent from the database. Does the AI confuse read abundance with cellular abundance? Conclude on the most suitable tool for your question.

### 6.1 Prompt(s) used
TODO

### 6.2 Extract of the AI response
TODO

### 6.3 Verification with primary sources (at least two, with DOI)
1. Wood et al., 2019. DOI: TODO
2. Blanco-Míguez et al., 2023. DOI: TODO

### 6.4 Errors or approximations found in the AI response
TODO

### 6.5 Conclusion: most suitable tool
TODO

## References
- TODO
