#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import subprocess
import os, sys
import pandas as pd

def run_rgi(input_genome, num_threads, run_name):
    """
    Run RGI on the input genome

    Parameters:
        input_genome: path to the input genome fasta
        num_threads: (int) number of threads to use for rgi
        run_name: path to output folder
    """

    # make the run_folder
    rgi_output_dir = os.path.join(run_name, 'rgi')
    os.mkdir(rgi_output_dir)

    # get the rgi and card version
    rgi_version = subprocess.run(["rgi", "main", "--version"],
                                 check=True,
                                 stdout=subprocess.PIPE,
                                 encoding="utf-8")
    rgi_version = rgi_version.stdout.strip()

    card_version = subprocess.run(["rgi", "database", "--version"],
                                 check=True,
                                 stdout=subprocess.PIPE,
                                 encoding="utf-8")
    card_version = card_version.stdout.strip()

    logging.info(f"Running RGI (v{rgi_version}) with CARD (v{card_version})")
    logging.debug(f"Using {num_threads} threads")

    # run RGI
    output_name = os.path.join(rgi_output_dir, run_name)
    subprocess.run(['rgi', 'main', '--input_sequence', input_genome,
                    '--output_file', output_name, '--alignment_tool', 'DIAMOND',
                    '--num_threads', str(num_threads), '--clean'],
                    check=True)

    # check rgi output
    output_tsv = output_name + ".txt"
    if os.path.exists(output_tsv):
        rgi_output = pd.read_csv(output_tsv, sep='\t')
        logging.debug("RGI run successful")
    else:
        logging.error(f"RGI output '{output_tsv}' does not exist")
        sys.exit(1)

    return rgi_output

