#!/usr/bin/env python
# -*- coding: utf-8 -*-



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
    # plot
    res = out.to_dict(orient="index")
    # with open("data.json", "w") as af:
    #     af.write(json.dumps(res,sort_keys=True))
    # exit("done")
    plot_gene_chromosome_plasmid_context(res)
    return res

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


