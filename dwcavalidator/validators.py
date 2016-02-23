# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 13:07:01 2016

@author: stijn_vanhoey
"""

from datetime import datetime
from dateutil.parser import parse

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
        json, urixw
    """
    def _validate_daterange(self, ref_value, field, value):
        """

        Remarks
        -------
        the yaml-reader prepares a datetime.date objects when possible,
        the dwca-reader is not doing this, so compatibility need to be better
        ensured
        """
        # try to parse the datetime-format
        event_date = parse(value)

        # convert schema info to datetime to enable comparison
        start_date = datetime.combine(ref_value[0], datetime.min.time())
        end_date = datetime.combine(ref_value[1], datetime.min.time())

        if event_date < start_date:
            self._error(field, "date is before start limit " + \
                                                        start_date.isoformat())
        if event_date > end_date:
            self._error(field, "date is after end limit " + \
                                                        end_date.isoformat())

    def _validate_dateformat(self, ref_value, field, value):
        """
        dateformat : ['%Y-%m-%d', '%Y-%m', '%Y']
        dateformat : '%Y-%m'
        """
        if isinstance(ref_value, list):
            tester = False
            for formatstr in ref_value: # check if at least one comply
                try:
                    datetime.strptime(value, formatstr)
                    tester = True
                except:
                    pass
        else:
            try:
                datetime.strptime(value, ref_value)
                tester = True
            except:
                tester = False

        if not tester:
            self._error(field, "String format not compliant with" + \
                                                                    formatstr)

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


