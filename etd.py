#!/usr/bin/env python
# -*- coding: utf-8 -*-

from etd import etd
import os
import sys
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

    parser = argparse.ArgumentParser(description="evolving threat detector "
                                                f"(v{etd.__version__}): "
                                        'compare antimicrobial resistance gene \
                                        predictions \n to nearest relatives of \
                                        isolate',
                                     prog='etd',
                                     usage='etd.py <command> <options>')
    parser.add_argument('-v', '--version', action='version',
                        version=f"%(prog)s {etd.__version__}")

    subparsers = parser.add_subparsers(title="available commands", help='',
                                        dest='command')

    # subparser for main execution of ETD on a genome
    subparser_run = subparsers.add_parser('run',
                                           help='Detect evolving threats \
                                                   from a bacterial genome',
                                           usage='etd.py run [options]',
                                           description='Run ETD on a genome \
                                                after database has been \
                                                prepared')

    subparser_run.add_argument('-v', '--version', action='version',
                        version=f"%(prog)s {etd.__version__}")
    subparser_run.add_argument('-i', '--input_genome',
                        type=lambda x: is_valid_file(parser, x),
                        required=True,
                        help="assembled bacterial contigs in fasta format")
    subparser_run.add_argument('-d', '--database_dir', type=str, required=True,
                        help="CARD prevalence database dir")
    subparser_run.add_argument('-o', '--output_dir', default=False,
                        help="Output directory path")
    subparser_run.add_argument('-x', '--mash_distance', default=0.01, type=float,
                        help="Maximum mash distance to retain")
    subparser_run.add_argument('-j', '--num_threads', default=1, type=int,
                        help="Number of threads to use")
    subparser_run.add_argument('--debug', action='store_true', default=False,
                        help="Run in debug mode")
    subparser_run.add_argument('--verbose', action='store_true', default=False,
                        help="Run with verbose output")

    # subparser for database generation tool
    subparser_db = subparsers.add_parser('database',
                                          help='Generate ETD database',
                                          usage='etd.py database [options]',
                                          description="Format and build \
                                                  database files needed for \
                                                  run execution")
    subparser_db.add_argument('-v', '--version', action='version',
                        version=f"%(prog)s {etd.__version__}")
    subparser_db.add_argument('--verbose', action='store_true', default=False,
                        help='Run with verbose output')
    subparser_db.add_argument('-d', '--card_prev_dir', type=str, required=True,
                            help="CARD prevalence tarball genome directory")
    subparser_db.add_argument('-j', '--num_threads', default=1, type=int,
                            help='Number of threads to use')


    args = parser.parse_args()

    if args.command == 'run':
        etd.run(args)
    elif args.command == 'database':
        etd.database(args)
    else:
        parser.print_help()
        sys.exit(1)
