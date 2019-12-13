#!/usr/bin/env python
# -*- coding: utf-8 -*-

from etd import etd
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
    parser.add_argument('-i', '--input',
                        type=lambda x: is_valid_file(parser, x),
                        required=True,
                        help="assembled bacterial contigs in fasta format")
    args = parser.parse_args()

    etd.run(args)
