# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 11:18:53 2016

@author: stijn_vanhoey
"""

import os

import yaml
from dwca.read import DwCAReader
from dwca.darwincore.utils import qualname as qn

#%% Extract data dict from a row in the example DCA to test with
ABS_PATH = '/home/stijn_vanhoey/githubs/temp/validator_testdata2'

with DwCAReader(os.path.join(ABS_PATH, 'validator_testdata.zip')) as dwca:
    temp = dwca.get_row_by_index(1)
document = {k.split('/')[-1]: v for k, v in temp.data.iteritems()}
# document is the dict for which different validations need to be performed
# as defined by a user defined config file


#%% Load config fle with the schema to interpret
schema = yaml.load(open('./settings.yml'))

from cerberus import Validator

class MyValidator(Validator):
    def _validate_equals(self, ref_value, field, value):
        """ {'type': 'string'} """
        if value != ref_value:
            self._error(field, "Must be equal to " + ref_value)

v = MyValidator(schema)
v.allow_unknown = True
v.validate(document)

