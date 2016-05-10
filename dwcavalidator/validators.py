# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 13:07:01 2016

@author: stijn_vanhoey
"""
import re
from datetime import datetime, date
from dateutil.parser import parse
from collections import Mapping, Sequence

import json
# https://pypi.python.org/pypi/rfc3987 regex on URI's en IRI's
from rfc3987 import match

from cerberus import Validator
from cerberus import errors
from cerberus.errors import ErrorDefinition
from cerberus.platform import _str_type

toy_error_handler = errors.ToyErrorHandler()
DELIMITER_SCHEMA = ErrorDefinition(0x82, 'delimitedvalues')

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
    #mandatory_validations = ('empty', 'nullable', 'readonly', 'type')
    priority_validations = ('empty', 'nullable', 'readonly', 'type')

    def __init__(self, *args, **kwargs):
        """add preprocessing rules to alter the schema
        """
        super(DwcaValidator, self).__init__(*args, **kwargs)

        if not self.schema:
            raise Exception('provide a schema to initiate Validator')

        # add coerce rules when type validations are required
        self.schema = self._schema_add_empty(self.schema)
        self._resolve_coerce(self.schema)

        # default rule to ignore None values on reader
        #self.ignore_none_values = True

        # prepare the string version of each document in the namespace
        self.document_str_version = None

    def validate(self, document, *args, **kwargs):
        """adds document parsing to the validation process
        """
        # store a dwcareader string version of the document
        self.document_str_version = document.copy() # ok in terms of memory, since Dwca is working row-based
        document = self.empty_string_none(document)

        return super(DwcaValidator, self).validate(document, *args, **kwargs)

    __call__ = validate

    @staticmethod
    def empty_string_none(doc):
        """convert empty strings to None values - assuming that the document
        structure will always be key:value (coming from DwcaReader)
        """
        for key, value in doc.iteritems():
            if value == "":
                doc[key] = None
        return doc

    @staticmethod
    def _add_coerce(rules):
        """provide the appropriate coerce lambda functions
        """
        to_float = lambda v: float(v) if v else v
        if rules['type'] == 'float':
            rules['coerce'] = to_float
        elif rules['type'] == 'int' or rules['type'] == 'integer':
            to_int = lambda v: int(v) if v else v
            rules['coerce'] = to_int
        elif rules['type'] == 'number':
            rules['coerce'] = to_float
        elif rules['type'] == 'boolean':
            to_bool = lambda v: bool(v) if v else v
            rules['coerce'] = to_bool

    def _resolve_coerce(self, schema):
        """add coerce rules to convert datatypes of int and float,
        recusively using the rules combinations of cerberus:
        {TERM : {RULE: --> str (STOP)
                       --> list/Sequence --> str (STOP)
                                         --> dict => (if type: ADD) + RECALL
                       --> dict/Mapping => (if type: ADD) + RECALL
                      }}
        """
        for term, rules in schema.iteritems():
            if isinstance(rules, _str_type):
                continue
            elif isinstance(rules, Sequence):
                for subschema in rules:
                    if isinstance(subschema, Mapping):
                        if 'type' in subschema.keys():
                             self._add_coerce(subschema)
                        self._resolve_coerce(subschema)
            elif isinstance(rules, Mapping):
               if 'type' in rules.keys():
                   self._add_coerce(rules)
               self._resolve_coerce(rules)
            else:
                NotImplemented

    @staticmethod
    def _schema_add_empty(dict_schema):
        """the empty rule should be added for each of the fields
        (should be possible to simplify using mandatory_validations, but this
        provides bug in cerberus that needs further check)
        """
        for term, rules in dict_schema.iteritems():
            if not 'empty' in rules.keys():
                rules['empty'] = True
        return dict_schema

    def _validate_nullable(self, nullable, field, value):
        """ {'type': 'boolean'} """
        # basically bypass the nullable test
        if not self.document_str_version[field]:
            return True
        else:
            return None

    def _validate_empty(self, empty, field, value):
        """ {'type': 'boolean'} """
        # port the nullable logic to the empty logic
        value_str = self.document_str_version[field]
        if isinstance(value_str, _str_type) and len(value_str) == 0:
            if not empty:
                self._error(field, errors.EMPTY_NOT_ALLOWED)
                return True
            else:
                return True

    def _validate_min(self, min_value, field, value):
        """ {'nullable': False, 'dependencies': ['type']} """
        # overwrite cerberus min to only consider int and float
        if (isinstance(value, int) or isinstance(value, float)) and \
                                        float(min_value) > value:
            self._error(field, errors.MIN_VALUE)
        elif isinstance(value, str):
            self._error(field, 'min validation ignores string type, add type validation')

    def _validate_max(self, min_value, field, value):
        """ {'nullable': False } """
        # overwrite cerberus max to only consider int and float
        if (isinstance(value, int) or isinstance(value, float)) and \
                                        float(min_value) < value:
            self._error(field, errors.MAX_VALUE)
        elif isinstance(value, str):
            self._error(field, 'max validation ignores string type, add type validation')

    def _parse_date(self, field, date_string):
        """try to parse a string to date and log error when failing
        """
        try:
            event_date = parse(date_string)
            return event_date
        except:
            self._error(field, "could not be interpreted as date or datetime")
            return None

    def _validate_mindate(self, min_date, field, value):
        """ {'type': ['date', 'datetime']} """

        # Remarks
        # -------
        #the yaml-reader prepares a datetime.date objects when possible,
        #the dwca-reader is not doing this, so compatibility need to be better
        #ensured

        # convert schema info to datetime to enable comparison
        if isinstance(min_date, date):
            min_date = datetime.combine(min_date, datetime.min.time())

        # try to parse the datetime-format
        event_date = self._parse_date(field, value)
        if event_date:
            if event_date < min_date:
                self._error(field, "date is before min limit " + \
                                                    min_date.date().isoformat())

    def _validate_maxdate(self, max_date, field, value):
        """ {'type': ['date', 'datetime']} """

        # Remarks
        # -------
        #the yaml-reader prepares a datetime.date objects when possible,
        #the dwca-reader is not doing this, so compatibility need to be better
        #ensured

        # convert schema info to datetime to enable comparison
        if isinstance(max_date, date):
            max_date = datetime.combine(max_date, datetime.min.time())

        # try to parse the datetime-format
        event_date = self._parse_date(field, value)
        if event_date:
            if event_date > max_date:
                self._error(field, "date is after max limit " + \
                                                    max_date.date().isoformat())

    def _validate_dateformat(self, ref_value, field, value):
        """ {'type': ['string', 'list']} """
        #dateformat : ['%Y-%m-%d', '%Y-%m', '%Y']
        #dateformat : '%Y-%m'

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
        """ {'type': ['integer', 'float']} """
        if (isinstance(value, int) or isinstance(value, float)) and \
                                                float(ref_value) != value:
            self._error(field, "".join(["value should be equal to ",
                                        str(ref_value),
                                        " instead of ",
                                        str(value)]))

    def _validate_numberrange(self, ref_range, field, value):
        """ {'type': 'list'} """
        # check if min < max
        if ref_range[0] >= ref_range[1]:
            raise Exception('min > max in range value')

        if value.isdigit():
            self._validate_min(self, ref_range[0], field, float(value))
            self._validate_max(self, ref_range[1], field, float(value))

    def _validate_length(self, length, field, value):
        """ {'type': 'integer', 'excludes': 'type'} """
        #check length of a given string
        if isinstance(value, str) and len(value) != length:
            self._error(field, "".join(["length mismatch: ", str(len(value)),
                                        " instead of ", str(length)]))
        elif not isinstance(value, str):
            self._error(field, 'length validation only active on strings')

    def _validate_maxlength(self, *args, **kwargs):
        """ {'type': 'integer', 'excludes': 'type'} """
        super(DwcaValidator, self)._validate_maxlength(*args, **kwargs)

    def _validate_minlength(self, *args, **kwargs):
        """ {'type': 'integer', 'excludes': 'type'} """
        super(DwcaValidator, self)._validate_minlength(*args, **kwargs)

    def _validate_numberformat(self, formatter, field, value):
        """ {'type': ['string'], 'regex': '[1-9].[1-9]|[1-9].$|^.[1-9]'} """

        value_str = self.document_str_version[field]
        if re.match("[1-9].[1-9]", formatter):
            value_parsed = [len(side) for side in value_str.split(".")]
        elif re.match(".[1-9]", formatter):
            if "." in value_str:
                value_parsed = [len(value_str.split(".")[1])]
            else:
                value_parsed = [0]
        elif re.match("[1-9].", formatter):
            value_parsed = [len(value_str.split(".")[0])]

        formatter_parsed = [int(length) for length in formatter.split(".") \
                                                        if not length == '']

        if formatter_parsed != value_parsed:
            self._error(field, "".join(["numberformat of value ",
                                        value_str,
                                        " not in agreement with ",
                                        formatter]))

    def _validate_if(self, ifset, field, value):
        """ {'type': 'dict'} """

        # extract dict values -> conditions
        conditions = {k: v for k, v in ifset.iteritems() if isinstance(v, dict)}
        # extract dict values -> rules
        rules = {k: v for k, v in ifset.iteritems() if not isinstance(v, dict)}

        valid=True
        # check for all conditions if they apply
        for term, cond in conditions.iteritems():
            subschema = {term : cond}
            tempvalidation = DwcaValidator(subschema)
            tempvalidation.allow_unknown = True
            if not tempvalidation.validate(self.document):
                valid = False

        #others -> conditional rules applied when valid condition
        if valid:
            tempvalidation = DwcaValidator({field: rules})
            tempvalidation.validate({field : self.document[field]})
            #convert eventual errors to object itself
            for field, err in tempvalidation.errors.items():
                self._error(field, err)


    def _validate_delimitedvalues(self, ruleset, field, value):
        """ {'type' : 'dict'} """
        # loosely constructed dusch as the __validate_schema_sequence

        # convert field string to list of values
        if not 'delimiter' in ruleset.keys():
            raise ValueError('Define delimiter as rule in delimitedvalues')
        value = [el for el in value.split(ruleset['delimiter'])]

        #check for empty string (edge case where we do not want 'male | ')
        if '' in value:
            self._error(field, "contains empty string combined with delimiters")

        #check for doubles ('male | female | male' needs error)
        if len(value) != len(set(value)):
            self._error(field, "contains duplicate values in delimitedvalues")

        # reorganise schema to be used in child_validator
        ruleset.pop('delimiter')
        schema = dict(((i, ruleset) for i in range(len(value))))

        validator = self._get_child_validator(
            document_crumb=field, schema_crumb=(field, 'schema'),
            schema=schema, allow_unknown=self.allow_unknown)

        validator.validate(dict(((i, v) for i, v in enumerate(value))),
                           normalize=True)
        if validator._errors:
            self._drop_nodes_from_errorpaths(validator._errors, [], [2])
            self._error(field, DELIMITER_SCHEMA, validator._errors)

    def _validate_listvalues(self):
        """ {'type': 'boolean'} """
        return None


#%% dtypes
    def _validate_type_json(self, field, value):
        """ Enables validation for json objects
        """
        try:
            json.loads(value)
        except:
            self._error(field, "is not a valid json type")

    def _validate_type_url(self, field, value):
        """ Enables validation for json objects
        """
        try:
            assert match(value, rule='URI')
        except:
            self._error(field, "is not a valid uri type")


