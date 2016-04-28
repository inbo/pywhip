# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 11:04:07 2016

@author: stijn_vanhoey
"""

import yaml
from dwca.read import DwCAReader
from dwcavalidator.validators import DwcaValidator


#%% Read the YAML file

schema  ="""
                decimalLatitude:
                    type : float
                    nullable : True
                individualCount:
                    type : integer
                    min : 2
         """

testdoc = {'accessRights': u'http://www.inbo.be/en/norms-for-data-use',
           'decimalLatitude' : None,
           'individualCount': u'2'}

v = DwcaValidator(yaml.load(schema))
v.allow_unknown = True

#v.validate(document)
v.validate(testdoc)
print(v.errors)

#%%

to_float = lambda v: v if v == '' else float(v)

v = DwcaValidator({'flag': {'type': 'boolean', 'coerce': to_float}})
v.validate({'flag': ''})
print v.document, v.errors

#%%

schema = {'name': {'empty': True}}
document = {'name': None}
v = DwcaValidator(schema)
v.validate(document, schema)
v.errors

#%%

schema = """
         sex:
             required: True
         moment:
             required: False
         """

testdoc = {'moment' : '2016-12-11'}

v = DwcaValidator(yaml.load(schema))
v.allow_unknown = True

#v.validate(document)
v.validate(testdoc)
print(v.errors)