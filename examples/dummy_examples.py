# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 11:04:07 2016

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
v.allow_unknown = True

#v.validate(document)
v.validate(testdoc)
print(v.errors)