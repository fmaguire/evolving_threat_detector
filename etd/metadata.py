#!/usr/bin/env python
# -*- coding: utf-8 -*

import os
import subprocess
import logging

def get_spatiotemp_context(run_name, closest_relatives):

    logging.info(f"Downloading metadata from biosample for: {closest_relatives}")
    # make the run_folder
    metadata_outdir = os.path.join(run_name, 'relatives_metadata')
    os.mkdir(metadata_outdir)

    for relative in closest_relatives:
        accession = "_".join(relative.split('_')[:-1])
        logging.debug(f"Downloading data for {accession}")

        biosample_id = subprocess.run(f"esearch -db nucleotide -query {accession} | esummary | xtract -pattern DocumentSummary -element BioSample",
                       shell=True, check=True, stdout=subprocess.PIPE,
                       encoding='utf-8')
        biosample_id = biosample_id.stdout.strip()
        if len(biosample_id) != 0:

            biosample_metadata = subprocess.run("esearch -db biosample -query "  + biosample_id + " | efetch",
                       shell=True, check=True, stdout=subprocess.PIPE,
                       encoding='utf-8')


#                    | egrep '^Identifiers|^Organism|^ +/host=|^ +/collection date=|^ +/geographic location=|^ +/strain=|^ +/isolation source=|^ +/latitude and longitude=' | awk '{ if($1~/^Identifiers/){print "BioSample_ID\t"$1,$2,$3}else{print $0} }' |  perl -pe 's/Identifiers: BioSample: //' | perl -pe 's/\;$//' | perl -pe 's/^ +\///' | perl -pe 's/\=\"/\t/' | perl -pe 's/\"$//' | perl -pe 's/Organism: /Organism\t/""",
        else:
            logging.warning(f"No biosample can be found for {accession}")


        with open(os.path.join(metadata_outdir, accession + ".biosample.txt"), 'w') as fh:
            fh.write(biosample_metadata.stdout)

