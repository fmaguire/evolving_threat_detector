#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import subprocess
import os, sys
import glob
import logging

def run_mash(input_genome, database_dir, num_threads, run_name):
    """
    Run mash for the input genome vs the CARD prevalence sketch (premade)

    Parameters:
        input_genome: path to the input genome fasta
        database_dir: path to the CARD prevalence database and mash sketch
        num_threads: (int) number of threads to use for mash
        run_name: path to output folder
    Return:
        mash_distances: (pd.df) dataframe of mash calculated distances
    """
    # create output directory
    mash_output_dir = os.path.join(run_name, 'mash')
    os.mkdir(mash_output_dir)

    # check mash version and log it
    mash_version = subprocess.run(["mash", "--version"],
                                 check=True,
                                 stdout=subprocess.PIPE,
                                 encoding="utf-8")
    mash_version = mash_version.stdout.strip()
    logging.info(f"Finding relatives using Mash (v{mash_version}) with {num_threads} threads")

    # run mash
    reference_sketch = os.path.join(database_dir, 'etd_db', 'card_prev.msh')
    mash_output = subprocess.run(['mash', 'dist', '-t', '-p', str(num_threads),
                                  reference_sketch, input_genome],
                                 check=True,
                                 stdout=subprocess.PIPE,
                                 encoding='utf-8')

    # parse mash output
    mash_output_file = os.path.join(mash_output_dir, 'mash_distances.tsv')
    with open(mash_output_file, 'w') as fh:
        fh.write(mash_output.stdout)
    logging.debug(f"Mash output dumped to {mash_output_file}")

    # get dataframe and take transpose
    mash_distances = pd.read_csv(mash_output_file, sep='\t', index_col=0).T

    return mash_distances


def find_relatives(input_genome, database_dir, mash_distance,
                   num_threads, run_name):
    """
    Using MASH find the nearest reference sequences in CARD prevalence

    Parameters:
        input_genome: path to the input genome fasta
        database_dir: path to the CARD prevalence database and mash sketch
        num_threads: (int) number of threads to use for mash
        run_name: path to output folder
    Returns:
        closest_taxa: (list) of closest relative genome names
    """
    # run mash
    mash_distances = run_mash(input_genome, database_dir,
                              num_threads, run_name)

    # get closest relatives (distances < 0.02)
    closest = mash_distances[mash_distances[input_genome] <= mash_distance]
    closest = closest.sort_values(input_genome, ascending=True)

    # grab top 10 or all if fewer than 10 genomes had a hit this close
    if closest.shape[0] > 10:
        closest_taxa = closest.head(10).values
    else:
        closest_taxa = closest.index

    logging.debug(f"Closest relatives found: {str(closest_taxa)}")
    return closest_taxa



def get_rgi_results(closest_relatives, database_dir):
    """
    Recover the RGI files from the CARD-prev data structure for the closest
    relative genomes

    Parameters:
        closest_relatives: (list) of closest relative genome names
        database_dir: (str) path to the directory containing card-prev data
    Returns:
        closest_relative_rgi: (dict) {genome_name: genome_rgi_dataframe}
    """
    logging.debug("Gathering RGI outputs from CARD-prev database")
    closest_relative_rgi = {}
    for genome in closest_relatives:
        rgi_glob = os.path.join(database_dir, "rgi_results", "*",
                                genome + ".json")
        rgi_path = glob.glob(rgi_glob)
        if len(rgi_path) > 1:
            logging.error(f"Duplicate matches to rgi output for {rgi_path}: {str(rgi_path)}")
            sys.exit(1)
        else:
            rgi_path = rgi_path[0]

        if not os.path.exists(rgi_path):
            logging.error(f"RGI output for relative {genome} cannot be found {rgi_path}")
            sys.exit(1)
        else:
            # store dataframe in dict keyed with genome name
            closest_relative_rgi[genome] = pd.read_csv(rgi_path, sep='\t')
        logging.debug(f"Recovering RGI table for {genome}: {rgi_path}")

    return closest_relative_rgi
