#!/usr/bin/env python
# -*- coding: utf-8 -*-

from etd import etd
import os
import argparse


def is_valid_file(parser, arg):
    """
    Checks whether input file exists

    Parameters:
        arg (str):The filename to be checked
    Returns:
        arg (str):The filename if it exists
    """
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        # return filename if valid
        return arg


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Evolving Threat Detector')
    parser.add_argument('-i', '--input_genome',
                        type=lambda x: is_valid_file(parser, x),
                        required=True,
                        help="assembled bacterial contigs in fasta format")
    parser.add_argument('-d', '--database_dir', type=str, required=True,
                        help="CARD prevalence database dir")
    parser.add_argument('-o', '--output_dir', default=False,
                        help="Output directory path")
    parser.add_argument('-j', '--num_threads', default=1, type=int,
                        help="Number of threads to use")
    parser.add_argument('--debug', action='store_true', default=False,
                        help="Run in debug mode")
    parser.add_argument('--verbose', action='store_true', default=False,
                        help="Run with verbose output")
    parser.add_argument('-v', '--version', action='store_true', default=False,
                        help="Output version and exit")

    args = parser.parse_args()

    etd.run(args)
