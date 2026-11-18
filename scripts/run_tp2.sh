#!/usr/bin/env bash
# TP 2: Shotgun metagenomics, read-based approach
# Usage: bash scripts/run_tp2.sh   (run from the repository root)
set -euo pipefail

# ---------- Settings to edit ----------
RUN="SRR8114121"                      # human gut metagenome, Illumina paired-end
N_SPOTS=100000                        # number of read pairs kept (small test subset)
N_SPOTS=100000                        # number of read pairs kept (small test subset)
THREADS=8
HUMAN_INDEX="$HOME/db/GRCh38/GRCh38_noalt_as"
KRAKEN_DB="$HOME/db/k2_standard"             # Kraken2 database directory
# --------------------------------------

# Make "conda activate" work inside a script
source "$(conda info --base)/etc/profile.d/conda.sh"

mkdir -p 00_raw 01_qc 02_clean 03_results

# ===== 0. Download reads (small subset) =====
conda activate tp2_qc
if [ ! -f 00_raw/sample_R1.fastq.gz ]; then
  fastq-dump -X "$N_SPOTS" --split-3 --gzip -O 00_raw "$RUN"
  mv "00_raw/${RUN}_1.fastq.gz" 00_raw/sample_R1.fastq.gz
  mv "00_raw/${RUN}_2.fastq.gz" 00_raw/sample_R2.fastq.gz
  rm -f "00_raw/${RUN}.fastq.gz"   # unpaired reads, not used
fi

# ===== 1. QC of raw reads =====
fastqc 00_raw/sample_R1.fastq.gz 00_raw/sample_R2.fastq.gz --outdir 01_qc/ -t 2
multiqc 01_qc/ -o 01_qc/

# ===== 2. Read cleaning (adapters, Phred >= 20, length >= 50) =====
fastp -i 00_raw/sample_R1.fastq.gz -I 00_raw/sample_R2.fastq.gz \
  -o 02_clean/sample_R1.clean.fq.gz -O 02_clean/sample_R2.clean.fq.gz \
  --detect_adapter_for_pe -q 20 -l 50 -w 4 \
  -h 01_qc/fastp.html -j 01_qc/fastp.json

# QC of cleaned reads, then aggregate everything (before vs after)
fastqc 02_clean/sample_R1.clean.fq.gz 02_clean/sample_R2.clean.fq.gz --outdir 01_qc/ -t 2
multiqc 01_qc/ -o 01_qc/ --force

# ===== 3. Host read removal (GRCh38) =====
bowtie2 -x "$HUMAN_INDEX" \
  -1 02_clean/sample_R1.clean.fq.gz -2 02_clean/sample_R2.clean.fq.gz \
  --very-sensitive -p "$THREADS" \
  --un-conc-gz 02_clean/sample_nohost_R%.fq.gz -S /dev/null \
  2> 01_qc/bowtie2_host_removal.log

# Read pair counts for Table 6
count_pairs() { echo $(( $(zcat "$1" | wc -l) / 4 )); }
{
  echo -e "step\tread_pairs"
  echo -e "raw\t$(count_pairs 00_raw/sample_R1.fastq.gz)"
  echo -e "after_fastp\t$(count_pairs 02_clean/sample_R1.clean.fq.gz)"
  echo -e "after_host_removal\t$(count_pairs 02_clean/sample_nohost_R1.fq.gz)"
} > 03_results/table6_read_counts.tsv

# ===== 4.1 Taxonomic profile: Kraken2 + Bracken + Krona =====
kraken2 --db "$KRAKEN_DB" --paired --gzip-compressed --threads "$THREADS" \
  --report 03_results/sample.kreport --output 03_results/sample.kraken \
  02_clean/sample_nohost_R1.fq.gz 02_clean/sample_nohost_R2.fq.gz

bracken -d "$KRAKEN_DB" -i 03_results/sample.kreport \
  -o 03_results/sample.bracken -r 150 -l S -t 10

ktImportTaxonomy -t 5 -m 3 -o 03_results/sample_krona.html \
  03_results/sample.kreport

# ===== 4.2 Taxonomic profile: MetaPhlAn =====
conda activate tp2_biobakery
metaphlan 02_clean/sample_nohost_R1.fq.gz,02_clean/sample_nohost_R2.fq.gz \
  --input_type fastq --nproc "$THREADS" --mapout 03_results/sample.bt2.bz2 \
  -o 03_results/sample_metaphlan.txt

# ===== 5. Functional profile: HUMAnN =====
# HUMAnN ignores pairing: concatenate R1 and R2
cat 02_clean/sample_nohost_R1.fq.gz 02_clean/sample_nohost_R2.fq.gz \
  > 02_clean/sample_merged.fq.gz

humann --input 02_clean/sample_merged.fq.gz --output 03_results/humann/ \
  --taxonomic-profile 03_results/sample_metaphlan.txt --threads "$THREADS"

humann_renorm_table --input 03_results/humann/sample_merged_pathabundance.tsv \
  --units relab --output 03_results/humann/sample_pathabundance_relab.tsv

echo "Pipeline finished."
