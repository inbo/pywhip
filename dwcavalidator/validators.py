# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 13:07:01 2016

@author: stijn_vanhoey
"""


import json
# https://pypi.python.org/pypi/rfc3987 regex on URI's en IRI's
from rfc3987 import match

from cerberus import Validator

class DwcaValidator(Validator):
    """
    directly available by cerberus:
        required, allowed, minlength, maxlength, minimum, maximum, regex,

    custom validation functions:
        daterange, numberformat, dateformat
        listvalues

    environments:
        delimitedValues, if

    dtypes to add for the type comparison:
        json, uri
    """




    def _validate_equals(self, ref_value, field, value):
        """ {'type': 'string'} """
        if isinstance(ref_value, list):
            Validator._validate_allowed(self, ref_value, field, value)
        else:
            if value != ref_value:
                self._error(field, "Must be equal to " + ref_value)

    def _validate_numberrange(self, ref_range, field, value):
        # check is min < max
        if ref_range[0] >= ref_range[1]:
            raise Exception('min > max in range value')

        if value.isdigit():
            Validator._validate_min(self, ref_range[0], field, float(value))
            Validator._validate_max(self, ref_range[1], field, float(value))

#%% dtypes
    def _validate_type_json(self, field, value):
        """ Enables validation for json objects
        """
        try:
            json.loads(value)
        except:
            self._error(field, "is not a valid json type")

    def _validate_type_uri(self, field, value):
        """ Enables validation for json objects
        """
        try:
            assert match(value, rule='URI')
        except:
            self._error(field, "is not a valid uri type")


