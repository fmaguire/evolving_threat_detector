#!/bin/bash

conda create -n etd -c conda-forge -c bioconda -y install mash hmmer entrez-direct rgi==5.1.0 pplacer
conda activate etd
tox
