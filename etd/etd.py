#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse

__version__ = "0.0.1"


def run():
    print('runner')
    parser = argparse.ArgumentParser(description='Evolving Threat Detector')
    parser.parse_args()
