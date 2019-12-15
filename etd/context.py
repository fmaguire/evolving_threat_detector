#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import pandas as pd
import os
import sys
import seaborn as sns
import matplotlib.pyplot as plt

def load_metadata(database_dir):
    card_prev_metadata_path = os.path.join(database_dir, "index", "card_prevalence.txt.gz")
    if os.path.exists(card_prev_metadata_path):
        card_prev_metadata_df = pd.read_csv(card_prev_metadata_path,
                                            sep='\t', compression="gzip")
    else:
        logging.error(f"CARD prev index {card_prev_metadata_path} doesn't exist")
        sys.exit(1)

    return card_prev_metadata_df


def get_genomic_context(aro, amr_name, seq_paths, database_dir):

    # disable matplotlib font logger
    logging.getLogger('matplotlib.font_manager').disabled = True

    logging.info(f"Determing genomic context of {aro} in CARD-prevalence")
    context_output_dir = os.path.join(seq_paths['folder'], 'genomic_context')
    os.mkdir(context_output_dir)

    card_prev_data = load_metadata(database_dir)

    # grab only accessions
    card_prev_data = card_prev_data[card_prev_data['ARO Accession'] == f"ARO:{aro}"]

    # filter out any missing
    card_prev_data = card_prev_data[(card_prev_data['NCBI Chromosome'] > 0.00) \
            | (card_prev_data['NCBI Plasmid'] > 0.00)]

    # remove perfect only and take the perfect+strict data
    card_prev_data = card_prev_data[card_prev_data['Criteria'] == "perfect_strict"]

    card_prev_data = card_prev_data[['Pathogen' , 'NCBI Plasmid',
                                     'NCBI WGS', 'NCBI Chromosome']]


    gene_specific_prev_data = os.path.join(context_output_dir, 'prev_metadata.tsv')
    logging.debug(f"Dumping relevant CARD-prev context data for {aro}: {gene_specific_prev_data}")
    card_prev_data.to_csv(gene_specific_prev_data,
                          sep='\t')

    # summarise distribution of plasmid bornedness in isolates that have it
    overall_mobility = card_prev_data['NCBI Plasmid'].describe()

    logging.info(f"Overall mobility for {aro}: {overall_mobility['mean']}")

    generate_context_plots(aro, amr_name, card_prev_data, context_output_dir)


def generate_context_plots(aro, amr_name, metadata, context_output_dir):
    sns.set_context('paper')
    sns.set_style('whitegrid')

    subset = pd.melt(metadata[['Pathogen', 'NCBI Chromosome', 'NCBI Plasmid']],
                    id_vars='Pathogen',
                    var_name='Genomic Context',
                    value_name='% of Isolates')
    order = subset.groupby('Pathogen')['% of Isolates'].sum().sort_values(ascending=False).index.values

    sns.catplot(data = subset, y = 'Pathogen', x = '% of Isolates',
                hue='Genomic Context', kind='bar', order=order)
    plt.title(f"CARD Resistomes and Variants Context of {amr_name} ({aro})")
    plt.tight_layout()
    plot_path = os.path.join(context_output_dir, 'context_plot.png')
    logging.debug(f"Saving context plot for {aro}: {plot_path}")
    plt.savefig(plot_path, dpi=300)


def plot_gene_chromosome_plasmid_context(data):
    labels = []
    plasmid = []
    chromosome = []
    gene = ""
    # with open(os.path.join("data.json"), 'r') as jfile:
    #     data = json.load(jfile)
    for i in data:
        labels.append(data[i]["Pathogen"])
        plasmid.append(data[i]["NCBI Plasmid"])
        chromosome.append(data[i]["NCBI Chromosome"])
        gene = data[i]["Name"]

    x = np.arange(len(labels))  # the label locations
    width = 0.2  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, plasmid, width, label='Plasmid')
    rects2 = ax.bar(x + width/2, chromosome, width, label='Chromosome')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Percentage of Isolates')
    ax.set_title('Percentage by Plasmid and Chromosome for {}'.format(gene))
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    # ax.set_xticklabels(labels, rotation=45, rotation_mode="anchor")
    # ax.grid(True)
    ax.grid(color='grey', linestyle='-', linewidth=.5)
    ax.legend()

    autolabel(rects1, ax)
    autolabel(rects2, ax)

    # fig.tight_layout()
    plt.savefig("{}.svg".format(gene), dpi=150)
    plt.savefig("{}.png".format(gene), dpi=150)
    # plt.show()

def autolabel(rects, ax):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')
