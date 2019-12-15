#!/usr/bin/env python
# -*- coding: utf-8 -*

#import ete
import pandas as pd
import os
import logging
import subprocess

def get_phylo_context(aro, seq_paths, database_dir, num_threads):

    # make the run_folder if it doesn't exist
    phylo_output_dir = os.path.join(seq_paths['folder'], 'pplacer')
    if not os.path.exists(phylo_output_dir):
        os.mkdir(phylo_output_dir)

    #get appropriate refpkg from index in database dir
    #taxit create -l MCR -P my.refpkg --aln-fasta clean_mcr.afa --tree-stats treestats.txt --tree-file clean_mcr.tree
    phylo_db_dir = os.path.join(database_dir, 'phylo')
    refpkg_index = pd.read_csv(os.path.join(phylo_db_dir, 'index.tsv'),
            sep='\t', dtype={'ARO': str, 'refpkg_path': str})

    refpkg_name = refpkg_index[refpkg_index['ARO'] == aro]['refpkg_path'].iloc[0]

    refpkg_path = os.path.join(phylo_db_dir, refpkg_name)
    ref_alignment = os.path.join(refpkg_path, 'ref_alignment.sto')
    ref_hmm = os.path.join(refpkg_path, 'ref_alignment.hmm')

    combined_alignment = os.path.join(phylo_output_dir, 'combined_aln.sto')
    logging.info(f"Aligning candidate to reference hmm {ref_hmm}")
    subprocess.run(['hmmalign', '-o', combined_alignment,
                    '--mapali', ref_alignment, ref_hmm,
                    seq_paths['seq_file']], check=True)

    pplacer_version = subprocess.run(["pplacer", "--version"],
                                     check=True,
                                     stdout=subprocess.PIPE,
                                     encoding="utf-8")
    pplacer_version = pplacer_version.stdout.strip()

    logging.info(f"Running pplacer (v{pplacer_version}) with {num_threads} threads")
    jplace_file = os.path.join(phylo_output_dir, 'pplacer.jplace')
    print(" ".join(['pplacer', '-o', jplace_file, '-j', str(num_threads), '-c', refpkg_path, combined_alignment]))
    subprocess.run(['pplacer', '-o', jplace_file, '-j', str(num_threads),
                    '-c', refpkg_path, combined_alignment],
                    check=True)

    guppy_raw_tree = os.path.join(phylo_output_dir, 'guppy.tree')
    subprocess.run(['guppy', 'fat', '-o', guppy_raw_tree, jplace_file],
                    check=True)

    return guppy_raw_tree
