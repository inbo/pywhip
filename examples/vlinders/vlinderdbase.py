# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 12:44:05 2016

@author: stijn_vanhoey
"""

import yaml
from dwca.read import DwCAReader
#from cerberus import Validator

#%% Read the archive
with DwCAReader('./dwca-dagvlinders-inbo-occurrences-v1.2.zip') as dwca:
    test = dwca.get_row_by_index(1)


#%% Read the YAML file
schema = yaml.load(open('./settings.yaml'))
