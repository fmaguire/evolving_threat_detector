#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.1"

import time
import pandas as pd
import logging
import os, sys, csv, glob, json
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
    index = "ARO" # Best_Hit_ARO
    isolate = set(rgi_output[index])
    others = set()
    seq_df = rgi_output.iloc[:, lambda rgi_output: [10, 17]]
    sequences = {}
    # seq_df = pd.DataFrame()
    for f in files:
        # print(">>>", f)
        df2 = pd.read_csv(f, sep='\t')
        # sequences = (set(df2["ARO"]),"==>", set(df2["Predicted_DNA"]))
        # seq_df = df2.iloc[:, lambda df2: [10, 17]]
        # seqs = seq_df.to_dict(orient="index")
        # for s in seqs:
        #     # print(seqs[s]["ARO"])
        #     sequences[f] = {"ARO": seqs[s]["ARO"], "Predicted_DNA": seqs[s]["Predicted_DNA"]}
        # # exit("??")
        others.update(set(df2[index]))

    # print("Isolate - Others: ", isolate.difference(others))
    # print("Others - Isolate: ", others.difference(isolate))
    unique_to_isolate = isolate.difference(others)
    missing_from_isolate = others.difference(isolate)
    # add sequences for each uniq gene
    sequences = seq_df.to_dict(orient="index")
    seqs = {}
    # print(unique_to_isolate)
    # print(missing_from_isolate)
    for s in sequences:
        if sequences[s]["ARO"] in unique_to_isolate:
            seqs[sequences[s]["ARO"]] = sequences[s]["Predicted_DNA"]
    # print(sequences)
    # print(seq_df.to_dict(orient="index"))
    # print(json.dumps(seqs, indent=2))
    # exit("?")
    return {"unique_to_isolate": unique_to_isolate, "missing_from_isolate": missing_from_isolate, "sequences": seqs}

def get_genomic_context(df, gene):
    # df = pd.read_csv(os.path.join(args.database_dir, "index", "index-for-model-sequences.txt"), sep='\t')
    # gene="MCR-9"
    out = df.loc[df['aro_accession'] == "ARO:{}".format(gene)]
    out = out.loc[df['rgi_criteria'] == "Perfect"]

    out_plasmid = out.loc[df['data_type'] == "ncbi_plasmid"]
    out_chromosome = out.loc[df['data_type'] == "ncbi_chromosome"]

    s_plasmid = list(out_plasmid["species_name"])
    u_plasmid = []
    for i_plasmid in s_plasmid:
        if i_plasmid not in u_plasmid:
            u_plasmid.append(i_plasmid)

    s_chromosome = list(out_chromosome["species_name"])
    u_chromosome = []
    for i_chromosome in s_chromosome:
        if i_chromosome not in u_chromosome:
            u_chromosome.append(i_chromosome)

    return {"found_in_plasmids": u_plasmid, "found_in_chromosomes": u_chromosome}

def get_genomic_context_alt(df, gene):
    out = df.loc[df['ARO Accession'] == "ARO:{}".format(gene)]
    out = out.loc[df['Criteria'] == "perfect"]

    out = out.loc[ (df['NCBI Chromosome'] > 0.00) | (df['NCBI Plasmid'] > 0.00)]
    # Criteria
    return out.to_dict(orient="index")


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
    print("------- differences: (unique_to_isolate) ------------------")
    # print(json.dumps(differences, indent=2))
    print(differences)

    # load index file
    # index-for-model-sequences.txt
    # df = pd.read_csv(os.path.join(args.database_dir, "index", "index-for-model-sequences.txt.gz"), sep='\t', compression="gzip")
    df = pd.read_csv(os.path.join(args.database_dir, "index", "card_prevalence.txt.gz"), sep='\t', compression="gzip")
    context = {}
    for genes in differences:
        if genes == "unique_to_isolate":
            # print(differences[genes])
            for gene in differences[genes]:
                # context[gene] = get_genomic_context(df, gene)
                context[gene] = get_genomic_context_alt(df, gene)
        # place on evolutionary tree
        # compare genomic contexts
        # - has this gene moved from plamid to chromosome
        # - has this gene been found on this organism before
        # try and grab geographic data?
    print("------- Gene genomic contexts: (unique_to_isolate) ------------------")
    print(json.dumps(context, indent=2))
