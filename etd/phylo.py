#!/usr/bin/env python
# -*- coding: utf-8 -*

#import ete

def place_on_phylogeny(candidate_sequence, gene_dir, database_dir, num_threads):
    """
    Place the candidate novel AMR sequence onto the appropriate reference
    phylogeny
    """
    # make the run_folder if it doesn't exist
    phylo_output_dir = os.path.join(gene_dir, 'pplacer')
    if not os.path.exists(phylo_output_dir):
        os.mkdir(phylo_output_dir)


    # find the appropriate ref data for the candidate gene
    #taxit create -l MCR -P my.refpkg --aln-fasta clean_mcr.afa --tree-stats treestats.txt --tree-file clean_mcr.tree
    refpkg = get_phylo_ref_data(candidate_sequence)

    ref_alignment = os.path.join(refpkg, 'ref_alignment.sto')
    ref_hmm = os.path.join(refpkg, 'ref_alignment.hmm')

    combined_alignment = os.path.join(phylo_output_dir, 'combined_aln.sto')

    logging.info(f"Aligning candidate to reference hmm {ref_hmm}")
    subprocess.run(['hmmalign', '-o', combined_alignment,
                    '--mapali', ref_alignment, ref_hmm,
                    candidate_sequence_file], check=True)

    pplacer_version = subprocess.run(["pplacer", "--version"],
                                     check=True,
                                     stdout=subprocess.PIPE,
                                     encoding="utf-8")
    pplacer_version = pplacer_version.stdout.strip()

    logging.info(f"Running pplacer (v{pplacer_version}) with {num_threads} threads")

    #= os.path.join(phylo_output_dir, 'combined_aln.sto')
    subprocess.run(['pplacer', '-o', '-c', refpkg, combined_alignment],
                   check=True)

    logging.info(f"Running guppy (v{pplacer_version}) with {num_threads} threads")
    #subprocess.run(
    #        guppy tog combo.jplace
    #        o


