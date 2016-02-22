# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 16:01:01 2016

@author: stijn_vanhoey
"""

import yaml

from dwcavalidator.validators import DwcaValidator
from dwca.read import DwCAReader


#%% Read the archive
with DwCAReader('./broedvogel_corrupted_subset.zip') as dwca:
    test = dwca.get_row_by_index(1)

#%% Read the YAML file
schema = yaml.load(open('./settings.yaml'))

#%% Validate
v = DwcaValidator(schema)
v.allow_unknown = True

errors = {}
with DwCAReader('./broedvogel_corrupted_subset.zip') as dwca:
    for row in dwca:
        document = {k.split('/')[-1]: v for k, v in row.data.iteritems()}

        # validate each row and log the errors for each row
        v.validate(document)
        if len(v.errors) > 0:
            errors[row.id] = v.errors
print errors



