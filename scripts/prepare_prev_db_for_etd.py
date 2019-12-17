#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tarfile
import argparse
import os, sys, glob, time
import logging

def check_dependencies():
    """
    Check all dependencies exist and work
    """
    missing=False
    for program in ['rgi', 'pplacer', 'hmmalign', 'guppy', 'esearch', 'esummary',
                    'xtract']:
        try:
            subprocess.run
            logging.debug(f"Tool {program} is installed")
        except:
            logging.error(f"Tool {program} is not installed")
            missing = True

    if missing:
        logging.error("One or more dependencies are missing please install")
        sys.exit(1)
    else:
        logging.debug("All dependencies found")

def get_files(card_prev_dir):
    taxa_folders = {}
    for folder in os.listdir(card_prev_dir):
        folder_path = os.path.join(args.card_prev_dir, folder)
        sequences = glob.glob(os.path.join(folder_path, '*.fa'))
        if os.path.isdir(folder_path) and len(sequences) > 0:
            taxa_folders[folder_path] = sequences
            logging.debug(f"Found {folder_path} containing {len(sequences)} "
                           "samples")

    if len(taxa_folders) > 0:
        logging.info(f"Found {len(taxa_folders)} taxa-specific "
                     "folders containing "
                     f"{sum([len(x) for x in taxa_folders.values()])} "
                     "sequence files")

    else:
        logging.warning("No taxa folders found, please check folder path, "
                        "ensure they are unzipped, and the sequences "
                        "have a .fa suffix")
        sys.exit(1)
    return taxa_folders


def run_mashtree(taxa, sequence_files):

    sketch_folder = os.path.join(taxa, 'sketches')
    if not os.path.exists(sketch_folder):
        os.mkdir(sketch_folder)
    else:
        info.warning(f"{sketch_folder} already exists for {taxa}")

    mashtree

def


def run(args):

    # start logging
    run_name = f"ETD_DB_preparation_{int(time.time())}"
    if args.verbose:
        logging.basicConfig(format='%(levelname)s:%(message)s',
                            level=logging.DEBUG,
                            handlers=[logging.FileHandler(f"{run_name}.log"),
                                      logging.StreamHandler()])
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s',
                            level=logging.INFO,
                            handlers=[logging.FileHandler(f"{run_name}.log"),
                                      logging.StreamHandler()])

    logging.info(f"Started ETD '{run_name}' in '{args.card_prev_dir}'")

    #check_dependencies()

    # find EXTRACTED folders (please extract first)
    taxa_folders = get_files(args.card_prev_dir)

    # for each folder run mashtree to generate a reference phylogeny
    # and save the sketches to build the overall mash sketch
    for taxa, sequences in taxa_folders:
        run_mashtree(taxa, sequences)






if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="ETD Database Formatter")
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Run with verbose output')
    parser.add_argument('-d', '--card_prev_dir', type=str, required=True,
                            help="CARD prevalence tarball genome directory")

    args = parser.parse_args()

    run(args)
