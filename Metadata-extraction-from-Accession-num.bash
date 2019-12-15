#!/bin/bash
#
# Hacking AMR 2019
# sekizuka@nih.go.jp
#
# dependency: esearch, efetch (ftp://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh)
#
# Usage: bash Metadata-extraction-from-Accession-num.bash [nucleotide accession number]
#    Ex: bash Metadata-extraction-from-Accession-num.bash NZ_WLTV00000000.1
#

# Accession number input
INPUT=$1

EDIRECTDIR=(path_to)/edirect
export PATH=$PATH:$EDIRECTDIR

INPUT=`esearch -db nucleotide -query $INPUT | esummary | xtract -pattern DocumentSummary -element BioSample`
echo -e "Input (Accession number)\t$1" > $1.out.txt
esearch -db biosample -query $INPUT | efetch -db biosample \
   | egrep '^Identifiers|^Organism|^ +/host=|^ +/collection date=|^ +/geographic location=|^ +/strain=|^ +/isolation source=|^ +/latitude and longitude=' \
   | awk '{ if($1~/^Identifiers/){print "BioSample_ID\t"$1,$2,$3}else{print $0} }' |  perl -pe 's/Identifiers: BioSample: //' \
   | perl -pe 's/\;$//' | perl -pe 's/^ +\///' | perl -pe 's/\=\"/\t/' | perl -pe 's/\"$//' | perl -pe 's/Organism: /Organism\t/' >> $1.out.txt

