=============================
Evolving Threat Detector
=============================

.. image:: https://travis-ci.org/fmaguire/evolving_threat_detector.png?branch=master
    :target: https://travis-ci.org/fmaguire/evolving_threat_detector

Identifying changes in resistome relative to closest relatives and contextualising results

To run/test create a conda environment (or virtualenv) and run::

    pip install -r requirements.txt --editable .

Then you should be able to run::

    python etd.py

Make sure you add any new requirements you've added to the ``requirements.txt`` file

If you write then tests can be run as follows::

    pytest

Alternatively to run the full set of tests including different python versions,
pyflake code style, and building the documentation run::

    tox


Overview
--------

.. image:: docs/resources/etd_overview.png 
    :width: 300
    :alt: Schematic overview of the Evolving Threat Detector

Output Structure
----------------

The main output directory is either specified by the user or defaults to the
input genome name followed by the UNIX timestamp

::

    test_genome_1576349112
    ├── mash
    │   └── mash_distances.tsv
    ├── rgi
    │   ├── test_genome.json
    │   └── test_genome.txt
    ├── related_isolate_geospatial_analysis_of_relatives
    └── unique_to_isolate 
        ├── amr_gene1
        │   ├── phylogenetic
        │   └── genomic_context
        └── amr_gene2
            ├── phylogenetic
            └── genomic_context


External Dependencies
---------------------

- MASH
- PPLACER
- HHMER
- e-utils

Database Preparation
--------------------

The database can be built from the card underlying sequences i.e. a directory
containing a set of directories for each taxa you want to include.

These taxa directories must be extracted and should contain individual 
fasta files (ending in '.fna') named with the accession and the type (chromosome, plasmid, or WGS)
e.g. `NZ_LT905063.1_chromosome.fa`

Detailed Workflow
=================

.. image:: docs/resources/etd_workflow.pdf
    :width: 300
    :alt: Overview of the workflow used by the Evolving Threat Detector

