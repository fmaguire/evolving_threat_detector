#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
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

    args_in_input = set(input_rgi['Best_Hit_ARO'].values)
    args_in_relatives = set()
    for genome, rgi in closest_relatives_rgi.items():
        args_in_relatives.update(rgi['Best_Hit_ARO'].values)

    unique_to_isolate = args_in_input.difference(args_in_relatives)
    missing_from_isolate = args_in_relatives.difference(args_in_input)

    logging.info(f"Unique ARG in isolate compared to relatives {str(unique_to_isolate)}")
    logging.debug(f"Missing ARGs in isolate compared to relatives {str(missing_from_isolate)}")

    logging.debug(f"Grabbing predicted DNA sequences for unique ARGs in input")
    sequences_uniq_to_isolate = {}
    for arg_name in unique_to_isolate:
        arg_rgi_data = input_rgi[input_rgi['Best_Hit_ARO'] == arg_name]
        # needs handled better at some point but unique is fine for now
        if arg_rgi_data.shape[0] > 1:
            logging.warning(f"Multiple copes of {arg_name} so taking first")

        arg_sequence = arg_rgi_data['Predicted_DNA'].iloc[0]
        sequences_uniq_to_isolate[arg_name] = arg_sequence
    logging.debug(f"Sequences unique to isolate {str(sequences_uniq_to_isolate)}")

    return unique_to_isolate, sequences_uniq_to_isolate, missing_from_isolate
