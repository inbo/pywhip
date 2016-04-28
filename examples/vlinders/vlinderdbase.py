# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 12:44:05 2016

@author: stijn_vanhoey
"""

import yaml
from dwca.read import DwCAReader
from dwcavalidator.validators import DwcaValidator


#%% Read the YAML file
#schema = yaml.load(open('./settings.yaml'))

schema  ="""
                decimalLatitude:
                    type : float
                    min : 50.68
                    max : 51.51
                individualCount:
                    type : integer
                    min : 2
         """

testdoc = {'accessRights': u'http://www.inbo.be/en/norms-for-data-use',
           'decimalLatitude' : '51.55',
           'individualCount': u'1'}

v = DwcaValidator(yaml.load(schema))
#v = DwcaValidator(yaml.load(schema))
#v = DwcaValidator(_preprocess_schema(yaml.load(schema)))
v.allow_unknown = True

#v.validate(document)
v.validate(testdoc)
print(v.errors)


#%%


#%% Read the archive
errors = {}
with DwCAReader('./dwca-dagvlinders-inbo-occurrences-v1.2.zip') as dwca:
    for row in dwca:
        document = {k.split('/')[-1]: v for k, v in row.data.iteritems()}

        # validate each row and log the errors for each row
        v.validate(document)
        if len(v.errors) > 0:
            errors[row.id] = v.errors
print errors
