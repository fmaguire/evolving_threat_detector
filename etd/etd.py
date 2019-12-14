#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.1"

import time
import pandas as pd
import logging
import os, sys, csv, glob
import subprocess

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
    logging.info(f"Using {num_threads} threads")

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
        logging.info("RGI run successful")
    else:
        logging.error(f"RGI output '{output_tsv}' does not exist")
        sys.exit(1)

    return rgi_output


def run_mash(input_genome, database_dir, num_threads, run_name):
    """
    Run mash for the input genome vs the CARD prevalence sketch (premade)

    Parameters:
        input_genome: path to the input genome fasta
        database_dir: path to the CARD prevalence database and mash sketch
        num_threads: (int) number of threads to use for mash
        run_name: path to output folder
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
    logging.info(f"Running Mash (v{mash_version}) with {num_threads} threads")

    # run mash
    reference_sketch = os.path.join(database_dir, 'card_prev.msh')
    mash_output = subprocess.run(['mash', 'dist', '-t', '-p', str(num_threads),
                                  reference_sketch, input_genome],
                                 check=True,
                                 stdout=subprocess.PIPE,
                                 encoding='utf-8')

    # parse mash output
    mash_output_file = os.path.join(mash_output_dir, 'mash_distances.tsv')
    with open(mash_output_file, 'w') as fh:
        fh.write(mash_output.stdout)
    logging.info(f"Mash output dumped to {mash_output_file}")

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

    return closest_taxa

def find_rgi_differences(rgi_output):
    files = rgi_output["genomes"]

    isolate = set(rgi_output["Best_Hit_ARO"])
    others = set()

    for f in files:
        df2 = pd.read_csv(f, sep='\t')
        others.update(set(df2["Best_Hit_ARO"]))

    # print("Isolate - Others: ", isolate.difference(others))
    # print("Others - Isolate: ", others.difference(isolate))

    return {"unique_to_isolate": isolate.difference(others), "missing_from_isolate": others.difference(isolate)}

def run(args):
    """
    Runner function for the evolving threat detector

    Parameters:
        args: argparse arguments
    """
    if not args.output_dir:
        # extract input filename
        run_name = os.path.splitext(os.path.basename(args.input_genome))[0]
        # add unix timestamp to name
        run_name = run_name + str(int(time.time()))
    else:
        run_name = args.output_dir

    # make run directory
    os.mkdir(run_name)

    # start logging
    if args.debug:
        logging.basicConfig(filename=f"{run_name}.log",
                            format='%(levelname)s:%(message)s',
                            level=logging.DEBUG)
    else:
        logging.basicConfig(filename=f"{run_name}.log",
                            format='%(levelname)s:%(message)s',
                            level=logging.INFO)

    logging.info(f"Started ETD '{run_name}' with input '{args.input_genome}'")
    # run RGI on input contigs
    rgi_output = run_rgi(args.input_genome, args.num_threads, run_name)

    # find nearest relatives complements of arg genes
    closest_relatives = find_relatives(args.input_genome,
                                       args.database_dir,
                                       args.mash_distance,
                                       args.num_threads,
                                       run_name)

    for g in closest_relatives:
        # find tab files for related genomes
        files = glob.glob(os.path.join(args.database_dir, "rgi_output", "*", "*.txt"))
        genomes = {}
        for f in files:
            if g in f:
                genomes = f
        rgi_output["genomes"] = genomes

    # get rgi output for closest from database dir
    # combine outputs into one dataframe
    # get difference between rgi hits and nearest relatives
    differences = find_rgi_differences(rgi_output)

    # for genes in differences:
        # print(genes)
        # place on evolutionary tree
        # compare genomic contexts
        # - has this gene moved from plamid to chromosome
        # - has this gene been found on this organism before
        # try and grab geographic data?
