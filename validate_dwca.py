# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 16:01:01 2016

@author: stijn_vanhoey
"""

# inspirations
# https://github.com/Datafable/gbif-dataset-metrics/blob/master/extraction_module/src/helpers.py
# https://github.com/Datafable/gbif-dataset-metrics/blob/master/extraction_module/src/descriptors.py
# https://github.com/Datafable/gbif-dataset-metrics/blob/master/extraction_module/bin/extract_data.py

# testfunctions
# https://github.com/LifeWatchINBO/data-publication/blob/master/guidelines/data/occurrence-guide.md

import os

from logroutine import LogAnomaliaDWCA
from dwca.read import DwCAReader

ABS_PATH = '/home/stijn_vanhoey/githubs/temp/'

#set up logging for row_id failures
logit = LogAnomaliaDWCA()

#with DwCAReader(os.path.join(ABS_PATH,
                        #'dwca-broedvogel-atlas-occurrences-v1.10.zip')) as dwca:
with DwCAReader(os.path.join(ABS_PATH, 'dwca_tester.zip')) as dwca:
    for row in dwca:
        logit.check_language(row)
        logit.check_rightsHolder(row)

# INBO:BROEDVOGELATLAS:AH:00000763:00070
# INBO:BROEDVOGELATLAS:AH:00000512:00070