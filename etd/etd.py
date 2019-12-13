#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.1"

import time
import os
import subprocess

def run_rgi(input_genome):
    """
    Run RGI on the input genome

    Parameters:
        input_genome: path to the input genome fasta
    """

    # make the run_folder
    input_genome
    run_name = os.mkdir(

    # get the rgi and card version
    rgi_version = subprocess("rgi --version")


    # run RGI
    subprocess.call(f"rgi --input_sequence {input_genome} \
            --output_file {run_name} --alignment_tool DIAMOND \
            --num_threads 2 --clean")

    # check rgi output
    subprocess.call

    # if valid


def run(args):
    """
    Runner function for the evolving threat detector

    Parameters:
        args: argparse arguments
    """
    input_genome = args.input

    if not args.output_dir:
        # extract input filename
        run_name = os.path.splitext(os.path.basename(args.input))[0]
        # add unix timestamp to name
        run_name = run_name + str(int(time.time())
    else:
        run_name = args.output_dir

    # make run directory
    os.mkdir(run_name)

    # run RGI on input contigs
    # rgi_output = run_rgi(args.input)




    # find nearest relatives
    # relatives = find_relatives(args.input)
