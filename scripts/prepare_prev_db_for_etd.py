#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tarfile
import subprocess
import argparse
import os, sys, glob, time
import logging

def check_dependencies():
    """
    Check all dependencies exist and work
    """
    missing=False
    for program in ['mashtree', 'mash']:
        try:
            output = subprocess.run([program, '--version'],
                                    check=True,
                                    stdout=subprocess.PIPE,
                                    encoding='utf-8')
            logging.debug(f"Tool {program} is installed: {output.stdout}")
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


def run_mashtree(taxa, sequence_files, num_threads):

    sketch_folder = os.path.join(taxa, 'sketches')
    tree_folder = os.path.join(taxa, 'mashtree')
    mashtree_fp = os.path.join(tree_folder, "tree.tree")

    if not os.path.exists(sketch_folder):
        os.mkdir(sketch_folder)
    else:
        logging.warning(f"{sketch_folder} already exists for {taxa}")

    if not os.path.exists(tree_folder):
        os.mkdir(tree_folder)
    else:
        logging.warning(f"{tree_folder} already exists for {taxa}")


    if os.path.exists(mashtree_fp):
        logging.warning(f"mashtree {mashtree_fp} already exists")
        return

    # make list of taxafiles
    seq_file_list = os.path.join(tree_folder, 'genome_list.txt')
    with open(seq_file_list, 'w') as fh:
        for sequence_file in sequence_files:
            fh.write(sequence_file + '\n')

    subprocess.run(['mashtree', '--numcpus', str(num_threads),
                    "--file-of-files", seq_file_list,
                    '--outtree', mashtree_fp, '--save-sketches',
                    sketch_folder], check=True)


def create_mash_sketch(taxa_folders, card_prev_dir):

    db_combined_sketch = os.path.join(card_prev_dir, 'card_prev.msh')
    if os.path.exists(db_combined_sketch):
        logging.warning(f"DB sketch already exists {db_combined_sketch} skipping "
                        "regeneration")
        return


    # generate list of sketches
    all_sketches = []
    for taxa in taxa_folders:
        taxa_sketches = glob.glob(os.path.join(taxa, 'sketches', '*.msh'))
        all_sketches = all_sketches + taxa_sketches

    all_sketch_file = os.path.join(taxa, 'all_sketches.txt')
    with open(all_sketch_file, 'w') as fh:
        for sketch_fp in all_sketches:
            fh.write(sketch_fp + '\n')

    subprocess.run(['mash', 'paste', '-l', all_sketch_file,
                    db_combined_sketch], check=True)
    return


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

    check_dependencies()

    # find EXTRACTED folders (please extract first)
    taxa_folders = get_files(args.card_prev_dir)

    # for each folder run mashtree to generate a reference phylogeny
    # and save the sketches to build the overall mash sketch
    for taxa, sequences in taxa_folders.items():
        run_mashtree(taxa, sequences, args.num_threads)

    create_mash_sketch(taxa_folders, args.card_prev_dir)



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="ETD Database Formatter")
    parser.add_argument('--verbose', action='store_true', default=False,
                        help='Run with verbose output')
    parser.add_argument('-d', '--card_prev_dir', type=str, required=True,
                            help="CARD prevalence tarball genome directory")
    parser.add_argument('-j', '--num_threads', default=1, type=int,
                            help='Number of threads to use')

    args = parser.parse_args()

    run(args)
