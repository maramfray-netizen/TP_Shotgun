# TP 2: Shotgun Metagenomics, Read-Based Approach

Read-based analysis of a human fecal sample (Illumina paired-end, 2 × 150 bp): quality control, read cleaning, host read removal, taxonomic profiling and functional profiling, without assembly.

## Objectives

- Assess and improve the quality of Illumina shotgun reads
- Remove host (human) reads using GRCh38
- Obtain the taxonomic profile (Kraken2/Bracken, MetaPhlAn) and the functional profile (HUMAnN)

## Pipeline

| Step | Tool | Output |
|---|---|---|
| 1. Raw read QC | FastQC, MultiQC | `01_qc/` |
| 2. Read cleaning | fastp (`-q 20 -l 50`) | `02_clean/` |
| 3. Host removal | Bowtie2 (GRCh38, `--very-sensitive`) | `02_clean/sample_nohost_R*.fq.gz` |
| 4.1 Taxonomy | Kraken2 + Bracken (`-r 150 -l S`), Krona | `03_results/` |
| 4.2 Taxonomy | MetaPhlAn | `03_results/sample_metaphlan.txt` |
| 5. Function | HUMAnN (UniRef90, MetaCyc) | `03_results/humann/` |

## Data

- Sample: `SRRxxxxxxx` (to be completed)
- Raw reads are not versioned (see `.gitignore`).

## Environment

- Windows 11 + WSL2 (Ubuntu), VS Code
- Package manager: conda (Miniconda)
- Environments:
  - `tp2_qc`: fastqc, multiqc, fastp, bowtie2, kraken2, bracken, krona, sra-tools
  - `tp2_biobakery`: humann (includes MetaPhlAn)

```bash
conda create -n tp2_qc -c conda-forge -c bioconda fastqc multiqc fastp bowtie2 \
  kraken2 bracken krona sra-tools
conda create -n tp2_biobakery -c conda-forge -c bioconda humann
```

## Repository structure


## Reproducing the analysis

```bash
git clone https://github.com/maramfray-netizen/TP_Shotgun.git
cd TP_Shotgun
bash scripts/run_tp2.sh
```

Prerequisites: the reference databases (GRCh38 Bowtie2 index, Kraken2 database, HUMAnN ChocoPhlAn and UniRef90 databases) must be downloaded beforehand.

## References

- Wood et al., 2019: Kraken2
- Blanco-Míguez et al., 2023: MetaPhlAn 4

## Author

Maram Fray, M2 Bioinformatics
