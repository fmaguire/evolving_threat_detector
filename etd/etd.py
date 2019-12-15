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
    unique_arg_to_isolate, \
            unique_arg_seqs_in_isolate, \
            missing_from_isolate = diff.find_rgi_differences(rgi_output,
                                                             closest_relatives_rgi)

    unique_seq_paths = diff.prepare_context_analysis(run_name,
                                                     unique_arg_seqs_in_isolate)


    # Analyse the sequence changes
    for unique_seq, seq_paths in unique_seq_paths.items():
        # needs tidied and outputs dumped to appropriate path
        # sorry slightly broke things with using amr gene name instead of ARO
        #observed_context = context.get_genomic_context(unique_seq, seq_paths,
        #                                               args.database_dir)

        phylo_context = phylo.get_phylo_context(unique_seq, seq_paths,
                                                args.database_dir,
                                                args.num_threads)

        print(phylo_context)

        #metadata_context = metadata.get_spatiotemp_context(unique_seq, seq_paths,
        #                                                    args.database_dir)
