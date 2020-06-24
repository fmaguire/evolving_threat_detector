#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import glob
import tarfile
import time
import json
import logging
import joblib
import subprocess


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
            one_line_output = output.stdout.strip()
            logging.debug(f"Tool {program} is installed: {one_line_output}")
        except:
            logging.error(f"Tool {program} is not installed")
            missing = True

    if missing:
        logging.error("One or more dependencies are missing please install")
        sys.exit(1)
    else:
        logging.debug("All dependencies found")


def build_db(database_dir, cores):
    """
    Parse the database dir and get the paths to all genomes with paired
    rgi results
    """

    etd_db = {'accessions': {}, 'amr': {}, 'genome_sketch': None}
    # accessions -> acc -> rgi
    #                   -> mashtree
    # amr        -> aro -> tree
    # sketch     -> genome_sketch

    rgi_dir = os.path.join(database_dir, 'rgi_results')
    genome_dir = os.path.join(database_dir, 'genomes')
    etd_db_dir = os.path.join(database_dir, 'etd_db')
    if not os.path.exists(etd_db_dir):
        os.mkdir(etd_db_dir)

    missing_count = 0
    all_sketches = []

    for genome_tarball in glob.glob(os.path.join(genome_dir, '*.tar.gz')):

        # get the files to use in the database
        seqs_to_use, rgi_to_use, \
                genomes_to_use, rgi_folder = get_files(genome_tarball,
                                                       rgi_dir)

        # sketch all the genomes
        sketches = create_genome_sketches(genomes_to_use, etd_db_dir, cores)
        # add to list of all sketches for combining
        all_sketches.extend(sketches)

        ## build mashtree
        mashtree = build_mashtree(sketches, etd_db_dir, cores)

        # add to the database
        for accession in seqs_to_use:
            entry = {}
            entry['rgi'] = os.path.join(rgi_folder, accession) + ".json"
            entry['genome_tree'] = mashtree
            etd_db['accessions'][accession] = entry

    ## combine/simplify sketches
    card_prev_sketch = combine_mash_sketches(all_sketches, etd_db_dir, cores)
    etd_db['genome_sketch'] = card_prev_sketch

    # prepare AMR phylogenies
    card = get_card(args.version)

    # generate



    with open(os.path.join(etd_db_dir, 'etd_db_index.json'), 'w') as fh:
        json.dump(etd_db, fh)

    print(etd_db)

    return etd_db


def get_files(genome_tarball, rgi_dir):
    """
    Handle extracting and gathering the genomes with paired RGI predictions
    """
    genome_folder = genome_tarball.replace('.tar.gz', '')
    # check if there is a corresponding rgi tarball
    rgi_tarball = os.path.join(rgi_dir, os.path.basename(genome_tarball))
    # genomes contain FASTA and the rgi_results contain NCBI so swap
    rgi_tarball = rgi_tarball.replace('FASTA', 'NCBI')
    rgi_folder = rgi_tarball.replace('.tar.gz', '')

    # rgi_results extract
    if os.path.exists(rgi_tarball) and not os.path.exists(rgi_folder):
        logging.info(f"Extracting RGI results: {rgi_tarball} to {rgi_folder}")
        with tarfile.open(rgi_tarball) as tar_fh:
            tar_fh.extractall(rgi_folder)

    elif os.path.exists(rgi_folder):
        logging.info(f"RGI results already extracted: {rgi_folder}")

    rgi_genome_results = [x for x in glob.glob(os.path.join(rgi_folder, '*.json'))]

    # extract the genomes for that taxa and get all the taxa
    with tarfile.open(genome_tarball) as tar_fh:
        tar_fh.extractall(genome_folder)
    genomes = [x for x in glob.glob(os.path.join(genome_folder, '*.fa'))]

    # compare genomes and rgi_results
    rgi_accessions = set([os.path.basename(x).replace(".json", '') for x in rgi_genome_results])
    genome_accessions = set([os.path.basename(x).replace(".fa", '') for x in genomes])
    rgi_only = rgi_accessions - genome_accessions
    if len(rgi_only) > 0:
        logging.warning(f"{len(rgi_only)} genomes missing in {genome_tarball}: {rgi_only}")
    genome_only = genome_accessions - rgi_accessions
    if len(genome_only) > 0:
        logging.warning(f"{len(genome_only)} rgi output missing in {rgi_folder}: {genome_only}")

    # use the sequences that have both a genome AND an rgi result
    seqs_to_use = rgi_accessions & genome_accessions

    rgi_to_use = [os.path.join(rgi_folder, x) + ".json" for x in seqs_to_use]
    genomes_to_use = [os.path.join(genome_folder, x) + ".fa" for x in seqs_to_use]

    return seqs_to_use, rgi_to_use, genomes_to_use, rgi_folder


def execute_cmd(cmd):
    """
    Run an arbitrary command
    """
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL)


def combine_mash_sketches(sketches, etd_db_dir, cores):
    """
    Combine all the mash sketches using paste
    """
    card_prev_msh_fp = os.path.join(etd_db_dir, 'card_prev.msh')

    if os.path.exists(card_prev_msh_fp):
        logging.info(f"Removing previous combined mash sketch: {card_prev_msh_fp}")
        os.remove(card_prev_msh_fp)

    mash_text_file = os.path.join(etd_db_dir, 'mash_list.txt')
    with open(mash_text_file, 'w') as fh:
        for sketch in sketches:
            fh.write(sketch + "\n")
    logging.info(f"Combining {len(sketches)} sketches into {card_prev_msh_fp}")

    mash_paste_cmd = ["mash", "paste", card_prev_msh_fp, "-l", mash_text_file]
    execute_cmd(mash_paste_cmd)

    # tidy up files that are not needed anymore
    os.remove(mash_text_file)
    for sketch in sketches:
        os.remove(sketch)
    sketch_dir = os.path.join(etd_db_dir, 'genome_sketches')
    for taxa_sketch_dir in os.listdir(sketch_dir):
        os.rmdir(os.path.join(sketch_dir, taxa_sketch_dir))
    os.rmdir(sketch_dir)

    return card_prev_msh_fp


def build_mashtree(sketches, etd_db_dir, cores):
    """
    Build a mashtree for all the sketches of each taxa
    """
    # make the directory
    genome_tree_folder = os.path.join(etd_db_dir, 'genome_trees')
    if not os.path.exists(genome_tree_folder):
        os.mkdir(genome_tree_folder)

    taxa = sketches[0].split(os.path.sep)[-2]

    mashtree_fp = os.path.join(genome_tree_folder, taxa + ".tree")

    # make list of taxafiles
    seq_file_list = os.path.join(genome_tree_folder, taxa + '_genome_list.txt')
    with open(seq_file_list, 'w') as fh:
        for sketch in sketches:
            fh.write(sketch + '\n')

    mashtree_cmd = ['mashtree', '--numcpus', str(cores),
                    "--file-of-files", seq_file_list,
                    '--outtree', mashtree_fp]

    logging.info(f"Running mashtree for taxa: {taxa}")

    execute_cmd(mashtree_cmd)

    os.remove(seq_file_list)

    return mashtree_fp


def create_genome_sketches(genome_fps, etd_db_dir, cores):
    """
    Run mash sketch on all the genomes for one taxa in parallel
    """
    taxa = genome_fps[0].split(os.path.sep)[-2]
    sketch_dir = os.path.join(etd_db_dir, 'genome_sketches')
    if not os.path.exists(sketch_dir):
        os.mkdir(sketch_dir)

    taxa_sketch_dir = os.path.join(etd_db_dir, 'genome_sketches', taxa)
    if not os.path.exists(taxa_sketch_dir):
        os.mkdir(taxa_sketch_dir)

    sketch_fps = []
    for genome_fp in genome_fps:
        sketch_fp = os.path.basename(genome_fp).replace('.fa', '.msh')
        sketch_fps.append(os.path.join(taxa_sketch_dir, sketch_fp))

    logging.info(f"Sketching genomes for taxa: {taxa}")
    sketch_cmds = []
    already_exists = 0
    for genome, sketch in zip(genome_fps, sketch_fps):
        # don't remake sketches that already exist
        # could be a problem if newer versions change the k-mer size etc
        if not os.path.exists(sketch):
            sketch_cmds.append(['mash', 'sketch', '-o', sketch, genome])
        else:
            already_exists += 1
    if already_exists > 0:
        logging.debug(f"Using {already_exists} sketches that already exist")
    logging.debug(f"Running {len(sketch_cmds)} genomic sketches")
    joblib.Parallel(n_jobs=cores)(joblib.delayed(execute_cmd)(cmd) for \
                                                        cmd in sketch_cmds)

    return sketch_fps


def check_index(index_filepath):
    """
    Validate index and

    Return False if index is invalid and return dict if valid
    """
    return False
    with open(index_filepath) as fh:
        index = json.load(fh)

    valid = True

    for access in index:
        if not os.path.exists(index[access]['genome']):
            valid = False
            logging.warning(f"Genome Missing: {index[access]['genome']}")

        if not os.path.exists(index[access]['rgi_results']):
            valid = False
            logging.warning(f"RGI Result Missing: {index[access]['rgi_results']}")

    # check other db parts TODO
    if not os.path.exists(index['genome_sketch']):
        valid = False
        logging.warning(f"Genome MASH sketch missing: {index['genome_sketch']}")

    return valid


def prepare_db(args):
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

    logging.info(f"Started ETD '{run_name}' in '{args.database_dir}'")

    check_dependencies()

    #check_db(args.database_dir, args.force)

    index_filepath = os.path.join(args.database_dir, 'etd_db', "etd_db_index.json")

    # if index already exists and not forcing rebuild
    if os.path.exists(index_filepath):
        logging.info(f"Pre-existing index found: {index_filepath}")

        db_valid = check_index(index_filepath)
        if db_valid and not args.force:
            logging.info(f"Using pre-existing index (use --force to rebuild): {index_filepath}")
            with open(index_filepath) as fh:
                etd_db = json.load(fh)
            return etd_db
        else:
            logging.info(f"Index incomplete: removing and rebuilding")
            os.remove(index_filepath)
    else:
        logging.info(f"No database found ({index_filepath}): building")

    etd_db = build_db(args.database_dir, args.num_threads)

    return etd_db
