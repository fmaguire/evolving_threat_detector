#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import os
import logging

def find_rgi_differences(input_rgi, closest_relatives_rgi):
    """
    Between sets of RGI output tsvs as dataframes find those AMR genes unique
    to the input RGI output relative to the RGI results of the mash identified
    closest relatives

    Parameters:
        input_rgi: (pd.df) dataframe of RGI TSV for input genome
        closest_relatives_rgi: (dict) {genome name: RGI dataframe} for
                                closest relatives

    Returns:
        unique_to_isolate: (set) Names of ARGs unique to input compared to relatives
        sequences_uniq_to_isolate: (dict) {ARG name: DNA sequence} for sequences
                                    only found in isolate
        missing_from_isolate: (set) Names of ARGs not found in isolate but found in
                                    relatives
    """

    logging.info("Determining differences in RGI predictions")
    args_in_input = set(arg_tuple for arg_tuple in \
            input_rgi[['ARO', 'Best_Hit_ARO']].itertuples(index=False, name=None))
    set_args_in_relatives = set()

    for genome, rgi in closest_relatives_rgi.items():
        args_in_relative = set(arg_tuple for arg_tuple in \
            rgi[['ARO', 'Best_Hit_ARO']].itertuples(index=False, name=None))
        set_args_in_relatives.update(args_in_relative)

    unique_to_isolate = args_in_input.difference(set_args_in_relatives)
    missing_from_isolate = set_args_in_relatives.difference(args_in_input)

    logging.info(f"Unique ARG in isolate compared to relatives {str(unique_to_isolate)}")
    logging.debug(f"Missing ARGs in isolate compared to relatives {str(missing_from_isolate)}")

    logging.debug(f"Grabbing predicted DNA sequences for unique ARGs in input")
    sequences_uniq_to_isolate = {}
    for aro, arg_name in unique_to_isolate:
        arg_rgi_data = input_rgi[input_rgi['Best_Hit_ARO'] == arg_name]
        # needs handled better at some point but unique is fine for now
        if arg_rgi_data.shape[0] > 1:
            logging.warning(f"Multiple copies of {arg_name} so taking first")

        arg_sequence = arg_rgi_data['Predicted_DNA'].iloc[0]
        sequences_uniq_to_isolate[str(aro)] = (arg_name, arg_sequence)
    logging.debug(f"Sequences unique to isolate {str(sequences_uniq_to_isolate)}")

    return unique_to_isolate, sequences_uniq_to_isolate, missing_from_isolate


def prepare_context_analysis(run_name, unique_arg_seqs_in_isolate):
    """
    Create the folders and write the sequence data for the context analysis
    """
    main_dir = os.path.join(run_name, 'unique_to_isolate')
    os.mkdir(main_dir)

    gene_data = {}
    for aro, aro_data in unique_arg_seqs_in_isolate.items():
        gene_name = aro_data[0]
        sequence = aro_data[1]
        gene_dir = os.path.join(main_dir, aro)
        os.mkdir(gene_dir)
        gene_seq_file = os.path.join(gene_dir, aro + ".fas")
        with open(gene_seq_file, 'w') as fh:
            fh.write(f">new_ref_{aro}_{gene_name.replace('.', '').replace('-', '')}\n{sequence}")

        gene_data[aro] = {'seq_file': gene_seq_file, 'folder': gene_dir}

    return gene_data

