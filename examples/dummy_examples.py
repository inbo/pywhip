# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 11:04:07 2016

@author: stijn_vanhoey
"""

import yaml
from dwca.read import DwCAReader
from dwcavalidator.validators import DwcaValidator

def empty_string_none(doc):
    """convert empty strings to None values
    """
    for key, value in doc.iteritems():
        if value == "":
            doc[key] = None
    return doc

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
           'decimalLatitude' : '',
           'individualCount': u'2'}

v = DwcaValidator(yaml.load(schema))
v.allow_unknown = True

#v.validate(document)
v.validate(empty_string_none(testdoc))
#v.validate(testdoc)
print(v.errors)

#%%

schema  ="""
                decimalLatitude:
                    type : float
                    nullable : True
         """

testdoc = {'accessRights': u'http://www.inbo.be/en/norms-for-data-use',
           'decimalLatitude' : ''}

v = DwcaValidator(yaml.load(schema))
v.allow_unknown = True

#v.validate(document)
v.validate(empty_string_none(testdoc))
#v.validate(testdoc)
print(v.errors)

#%%

schema  ="""
                decimalLatitude:
                    type : float
                    min : 3
         """

v = DwcaValidator(yaml.load(schema))
v.allow_unknown = True

testdoc = {'decimalLatitude' : '4.'}
v.validate(empty_string_none(testdoc))
print(v.errors)

testdoc = {'decimalLatitude' : '4'}
v.validate(empty_string_none(testdoc))
print(v.errors)

testdoc = {'decimalLatitude' : ''}
v.validate(empty_string_none(testdoc))
print(v.errors)

testdoc = {'decimalLatitude' : '2.'}
v.validate(empty_string_none(testdoc))
print(v.errors)


#%% Read the YAML file

schema  ="""
        decimalLatitude:
            oneof :
                - allowed : ''
                - min : 3.
                  coerce : !!python/name:float
                  type : float
         """

v = Validator(yaml.load(schema))
v.allow_unknown = True

testdoc = {'decimalLatitude' : '4.'}
v.validate(testdoc)
print(v.errors)

testdoc = {'decimalLatitude' : '4'}
v.validate(testdoc)
print(v.errors)

testdoc = {'decimalLatitude' : ''}
v.validate(testdoc)
print(v.errors)

testdoc = {'decimalLatitude' : '2.'}
v.validate(testdoc)
print(v.errors)

#%%

def to_float(value):
    """
    """
    if value == "":
        return None
    else:
        return float(value)

v = Validator({'flag': {'type': 'integer', 'coerce' : to_float, 'nullable' : True}})
v.validate({'flag': None})
print v.document, v.errors

#%%
# todo: we'll keep this structure (integrates cerberus + consistent); but update coerce structure to handle this type of list datatypes

from cerberus import Validator

#schema = {'name': {'type': 'float', 'coerce' : to_float, 'nullable' : True}}
schema = {'name': {'oneof' : [{'type': 'float',
                               'coerce' : float},
                              {'allowed' : ''}],
                    'nullable' : True }}

document = {'name': '4.2'}  # should be ok
v = Validator(schema)
v.validate(document, schema)
print v.document, v.errors#, v.schema

document = {'name': None} # should be ok
v = Validator(schema)
v.validate(document, schema)
print v.document, v.errors#, v.schema

document = {'name': ''}  # should be ok as well
v = Validator(schema)
v.validate(document, schema)
print v.document, v.errors#, v.schema


#%%
# todo: we'll keep this structure (integrates cerberus + consistent); but update coerce structure to handle this type of list datatypes
schema = {'name': {'type': 'float', 'min' : 3}}
document = {'name': ''}
v = DwcaValidator(schema)
v.validate(document, schema)
print v.document, v.errors, v.schema

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