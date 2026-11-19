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
The raw dataset contains 94,121 read pairs (11.2 Mbp per file). Read lengths range from 44 to 143 bp (mean about 119 bp, median 128 bp) instead of a uniform 150 bp, which shows that the reads had already been quality-trimmed by the data submitters. The mean GC content is 46% for both R1 and R2, and duplication is low (about 2.3% of sequences are duplicates).

The per-base sequence quality and per-sequence quality modules passed: the median Phred score is at least 25 at every position, and fastp reports that 97.4% of bases have Q >= 20 and 90.7% have Q >= 30. The adapter content module passed and fastp found no adapter-dimer reads, consistent with the pre-trimming. Four modules raised warnings: the per-sequence GC content deviates from a single normal distribution, which is expected for a gut metagenome that mixes many genomes with different GC contents; the per-base sequence content shows composition bias, typical of fragmentation-based libraries and trimmed reads; the sequence length distribution is non-uniform because of the trimming; and a small set of overrepresented sequences was flagged in the raw reads [add the sequence(s) and their possible source from the FastQC report], which no longer appeared after cleaning.

A Phred score is defined as Q = -10 x log10(P), where P is the probability that the base call is wrong. A Q30 score therefore means an error probability of 0.1% (99.9% base call accuracy), and Q20 means 1%.

After fastp (-q 20, -l 50), 89,953 read pairs remained (95.6% of the raw pairs): 2,798 reads were removed for low quality and 5,538 reads for being shorter than 50 bp, and Q30 rose slightly to 91.4%.

*Hint:* Q = -10 × log10(P), so Q20 = 1% error and Q30 = 0.1% error (99.9% base call accuracy). Add a MultiQC screenshot (R1 vs R2, before vs after fastp).

<!-- QC:START -->
**FastQC summary (from MultiQC):**

| Sample | Total sequences | Mean length | %GC | % remaining after dedup | Per-base quality | GC content | Adapters | Overrepresented |
|---|---|---|---|---|---|---|---|---|
| sample_R1.clean.fq.gz | 89953.0 | 121.47777728369259 | 46.0 | 97.88667415205718 | pass | warn | pass | pass |
| sample_R1.fastq.gz | 94121.0 | 119.45243356955409 | 46.0 | 97.68277005131692 | pass | warn | pass | warn |
| sample_R2.clean.fq.gz | 89953.0 | 122.36348426400454 | 46.0 | 98.00117839316087 | pass | pass | pass | pass |
| sample_R2.fastq.gz | 94121.0 | 119.47217411629711 | 46.0 | 97.82407751723845 | pass | warn | pass | warn |
<!-- QC:END -->

## 3. Read cleaning and host removal

**Table 6.** Number of read pairs at each step (from `03_results/table6_read_counts.tsv`).

| Step | Read pairs | % of raw reads |
|---|---|---|
| Raw reads | 94,121 | 100 % |
| After fastp | 89,953 | 95.6 % |
| After host removal | 89,953 | 95.6 % |

## 4. Taxonomic profiles

**Table 7.** Ten most abundant species.

| Rank | Species | Bracken relative abundance (%) | MetaPhlAn relative abundance (%) |
|---|---|---|---|
| 1 | Agathobacter rectalis | 25.03 | TODO |
| 2 | Faecalibacterium prausnitzii | 11.34 | TODO |
| 3 | Roseburia intestinalis | 7.65 | TODO |
| 4 | Bifidobacterium longum | 5.46 | TODO |
| 5 | Phocaeicola vulgatus | 4.35 | TODO |
| 6 | Blautia wexlerae | 4.21 | TODO |
| 7 | Roseburia faecis | 3.34 | TODO |
| 8 | Coprococcus sp. ART55/1 | 2.75 | TODO |
| 9 | Anaerostipes hadrus | 1.95 | TODO |
| 10 | Phocaeicola coprocola | 1.79 | TODO |

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
