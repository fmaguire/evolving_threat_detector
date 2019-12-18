#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.1"

import time
import pandas as pd
import logging
import os, sys, csv, glob, json
import subprocess

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from etd import rgi
from etd import relatives
from etd import diff
from etd import context
from etd import phylo
from etd import metadata

def check_dependencies():
    """
    Check all dependencies exist and work
    """
    missing=False
    for program in ['rgi', 'pplacer --version', 'hmmalign -h', 'guppy --version', 'esearch', 'esummary',
                    'xtract']:
        try:
            subprocess.run(program, shell=True, check=True)
            logging.debug(f"Tool {program} is installed")
        except:
            logging.error(f"Tool {program} is not installed")
            missing = True

    if missing:
        logging.error("One or more dependencies are missing please install")
        sys.exit(1)
    else:
        logging.debug("All dependencies found")


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
    if args.debug or args.verbose:
        logging.basicConfig(format='%(levelname)s:%(message)s',
                            level=logging.DEBUG,
                            handlers=[logging.FileHandler(f"{run_name}.log"),
                                      logging.StreamHandler()])
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s',
                            level=logging.INFO,
                            handlers=[logging.FileHandler(f"{run_name}.log"),
                                      logging.StreamHandler()])

    logging.info(f"Started ETD '{run_name}' with input '{args.input_genome}'")

    # check dependencies
    check_dependencies()

    # run RGI on input contigs
    rgi_output = rgi.run_rgi(args.input_genome, args.num_threads, run_name)

    # find nearest relatives complements of arg genes
    closest_relatives = relatives.find_relatives(args.input_genome,
                                                 args.database_dir,
                                                 args.mash_distance,
                                                 args.num_threads,
                                                 run_name)

    # recover rgi tables for relatives
    closest_relatives_rgi = relatives.get_rgi_results(closest_relatives,
                                                     args.database_dir)

    # combine outputs into one dataframe
    # get difference between rgi hits and nearest relatives
    unique_to_isolate, \
            sequences_uniq_to_isolate, \
            missing_from_isolate = diff.find_rgi_differences(rgi_output,
                                                             closest_relatives_rgi)
    unique_seq_paths = diff.prepare_context_analysis(run_name,
                                                     sequences_uniq_to_isolate)

    # get biosample metadata for closest relatives
    metadata_context = metadata.get_spatiotemp_context(run_name,
                                                       closest_relatives)

    # Analyse the sequence changes
    for unique_aro, seq_data in sequences_uniq_to_isolate.items():
        # lookup card-prev data
        amr_name = seq_data[0]
        seq_paths = unique_seq_paths[unique_aro]

        observed_context = context.get_genomic_context(unique_aro,
                                                       amr_name,
                                                       seq_paths,
                                                       args.database_dir)

        phylo_context = phylo.get_phylo_context(unique_aro, seq_paths,
                                                args.database_dir,
                                                args.num_threads)


