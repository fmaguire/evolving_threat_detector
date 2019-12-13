#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "0.0.1"


def run(args):
    """
    Runner function for the evolving threat detector

    Parameters:
        args: argparse arguments
    """
    print(args.input)

    # run RGI on input contigs
    # rgi_output = run_rgi(args.input)

    # find nearest relatives
    # relatives = find_relatives(args.input)
