#!/usr/bin/env bash
# Download reference databases used in TP2 (large downloads).
set -euo pipefail

# Human genome index for Bowtie2 (GRCh38, no alt analysis set)
mkdir -p ~/db/GRCh38 && cd ~/db/GRCh38
wget -c https://genome-idx.s3.amazonaws.com/bt/GRCh38_noalt_as.zip
unzip -n GRCh38_noalt_as.zip && rm GRCh38_noalt_as.zip

# Kraken2/Bracken Standard-8 (capped at 8 GB, prebuilt)
mkdir -p ~/db/k2_standard_08 && cd ~/db/k2_standard_08
wget -c https://genome-idx.s3.amazonaws.com/kraken/k2_standard_08_GB_20251015.tar.gz \
  || wget -c https://genome-idx.s3.amazonaws.com/kraken/k2_standard_08gb_20241228.tar.gz
tar -xzf k2_standard_08*.tar.gz && rm k2_standard_08*.tar.gz
