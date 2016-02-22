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

        if value.isdigit():
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

v = MyValidator(schema)
v.allow_unknown = True
v.validate(document)

#%% Multiple rows

v = MyValidator(schema)
v.allow_unknown = True

errors = {}
with DwCAReader(os.path.join(ABS_PATH, 'validator_testdata.zip')) as dwca:
    for row in dwca:
        document = {k.split('/')[-1]: v for k, v in row.data.iteritems()}

        # validate each row and log the errors for each row
        v.validate(document)
        if len(v.errors) > 0:
            errors[row.id] = v.errors

#%%


"""
* try to check mapping in between current yaml and the cerberus naming conventions
* create validator function for each of the current defined tests + unittets for each individually
* for the delimitedValues and if: see if recursively is right way to do + how to port errors and characteristics
* alternatively collect/restructure the errors:
    * ids of the rows appending for the term/test combination
    * sample of the failure definition added
    * when listValues asked, collect sample for each
    * check how error messages are handled...
    -- when working on a row, directly map to dict in the readme (+ unique samples)
* based on information of dict -> report creation
    * html-dashboard => wat zijn de opties?
        * First draft idea: Pandas dframe + conditional formatting: http://pandas.pydata.org/pandas-docs/stable/style.html
        * templating engine, cfr. jinja2 achtig: HTML-format + invullen... http://jinja.pocoo.org/docs/dev/templates/
        * HTML specific python-code creation: http://www.yattag.org/ or https://github.com/Knio/dominate
    zou mooi zijn: http://tinyurl.com/gnnwb57
"""















