#!/bin/bash
# Hacking AMR 2019
# sekizuka@nih.go.jp
#
#
# dependency: esearch, efetch (ftp://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh)
#
# Setting the PATH:  Biosample-table-format-converter.pl
# 
# Usage: bash metadata-extraction-from-BioSample.bash [Genus_name] [species_name]
#    Ex: bash metadata-extraction-from-BioSample.bash Salmonella enterica 
#
#

GENUS=$1
SPECIES=$2

EDIRECTDIR=(path_to)/edirect
export PATH=$PATH:$EDIRECTDIR

esearch -db biosample -query "$GENUS $SPECIES[organism]" | efetch -db biosample >> ${GENUS}-${SPECIES}.BioSample-DL.txt

CONVERTER=(path_to)/Biosample-table-format-converter.pl

wget -O ${GENUS}_${SPECIES}.assembly_summary.txt ftp://ftp.ncbi.nlm.nih.gov/genomes/genbank/bacteria/${GENUS}_${SPECIES}/assembly_summary.txt

egrep '^Identifiers|^ +/host=|^ +/collection date=|^ +/geographic location=|^ +/strain=|^ +/isolation source=|^ +/latitude and longitude=' ${GENUS}-${SPECIES}.BioSample-DL.txt \
  | awk '{ if($1~/^Identifiers/){print $1,$2,$3}else{print $0} }' |  perl $CONVERTER | perl -pe 's/Identifiers: BioSample: //' | perl -pe 's/\;\t/\t/' > ${GENUS}-${SPECIES}.BioSample.tsv

cut -f1 ${GENUS}-${SPECIES}.BioSample.tsv | awk 'NR>1 {print $1}' > ${GENUS}-${SPECIES}.Biosample-list.txt
while read line ; do esearch -db nucleotide -query $line </dev/null | esummary | xtract -pattern DocumentSummary -element BioSample Extra >> ${GENUS}-${SPECIES}.BioSample-seqID.txt ; done < ${GENUS}-${SPECIES}.Biosample-list.txt

