# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 11:18:53 2016

@author: stijn_vanhoey
"""

import os

import yaml
from dwca.read import DwCAReader

#%% Extract data dict from a row in the example DCA to test with
ABS_PATH = '/home/stijn_vanhoey/githubs/temp/validator_testdata2'

with DwCAReader(os.path.join(ABS_PATH, 'validator_testdata.zip')) as dwca:
    temp = dwca.get_row_by_index(1)
document = {k.split('/')[-1]: v for k, v in temp.data.iteritems()}
# document is the dict for which different validations need to be performed
# as defined by a user defined config file

document['samplingEffort']='temp'


#%% Load config fle with the schema to interpret -> apply to a single row
schema = yaml.load(open('./settings.yml'))

from cerberus import Validator

class MyValidator(Validator):
    def _validate_equals(self, ref_value, field, value):
        """ {'type': 'string'} """
        if isinstance(ref_value, list):
            Validator._validate_allowed(self, ref_value, field, value)
        else:
            if value != ref_value:
                self._error(field, "Must be equal to " + ref_value)

    def _validate_numberRange(self, ref_range, field, value):
        # check is min < max
        if ref_range[0] >= ref_range[1]:
            raise Exception('min > max in range value')
        Validator._validate_min(self, ref_range[0], field, float(value))
        Validator._validate_max(self, ref_range[1], field, float(value))

    def _validate_if(self, ifset, field, value):
        # extract dict values -> conditions
        conditions = {k: v for k, v in ifset.iteritems() if isinstance(v, dict)}
        rules = {k: v for k, v in ifset.iteritems() if not isinstance(v, dict)}

        valid=True
        # check for all conditions if they apply
        for term, cond in conditions.iteritems():
            subschema = {term : cond}
            tempvalidation = MyValidator(subschema)
            tempvalidation.allow_unknown = True
            if not tempvalidation.validate(self.document):
                valid=False
        #others -> conditional rules applied when valid condition
        if valid:
            tempvalidation = MyValidator({field: rules})
            tempvalidation.validate({field : self.document[field]})
            print tempvalidation.errors

v = MyValidator(schema)
v.allow_unknown = True
v.validate(document)










