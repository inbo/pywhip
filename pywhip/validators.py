# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 13:07:01 2016

@author: stijn_vanhoey
"""
import re
from copy import copy
from datetime import datetime, date
from dateutil.parser import parse
from collections import Mapping, Sequence

import json
# https://pypi.python.org/pypi/rfc3987 regex on URI's en IRI's
from rfc3987 import match

from cerberus import Validator
from cerberus import errors
from cerberus.errors import ErrorDefinition
from cerberus.platform import _str_type, _int_types

toy_error_handler = errors.ToyErrorHandler()
DELIMITER_SCHEMA = ErrorDefinition(0x82, 'delimitedvalues')
IF_SCHEMA = ErrorDefinition(0x82, 'if')


class DwcaValidator(Validator):
    """
    directly available by cerberus:
        allowed, minlength, maxlength, minimum, maximum, regex

    custom validation functions:
        daterange, numberformat, dateformat
        listvalues

    environments:
        delimitedValues, if
    """

    def __init__(self, *args, **kwargs):
        """add pre processing rules to alter the schema

        Parameters
        ----------
        allow_unknown : boolean
            if False only terms with specifications are allowed as input
        """
        # prepare the string version of each document in the namespace
        self.document_str_version = None

        super(DwcaValidator, self).__init__(*args, **kwargs)

        if 'allow_unknown' in kwargs:
            self.allow_unknown = kwargs['allow_unknown']
        else:
            self.allow_unknown = True

        if not self.schema:
            raise Exception('provide a schema to initiate Validator')

        # Extend schema with empty: False by default
        self.schema = self._schema_add_empty(self.schema)
        self.schema = self._schema_add_required(self.schema)

    def validate(self, document, *args, **kwargs):
        """adds document parsing to the validation process
        """
        # store a dwcareader string version of the document
        # if not self.document_str_version:
        self.document_str_version = document.copy()

        return super(DwcaValidator, self).validate(document, *args, **kwargs)

    __call__ = validate

    @staticmethod
    def _schema_add_empty(dict_schema):
        """the empty rule should be added for each of the fields
        (should be possible to simplify using mandatory_validations, but this
        provides bug in cerberus that needs further check)
        """
        for term, rules in dict_schema.items():
            if 'empty' not in rules.keys():
                rules['empty'] = False
        return dict_schema

    @staticmethod
    def _schema_add_required(dict_schema):
        """the required rule should be added for each of the fields, as whip
        defines enlisted as default required
        """
        for term, rules in dict_schema.items():
            if 'required' not in rules.keys():
                rules['required'] = True
        return dict_schema

    def _validate_empty(self, empty, field, value):
        """{'type': 'boolean'}
        """
        # Dropping all remaining rules except of if (instead of subselection)
        # when empty = True
        from collections import Sized
        if isinstance(value, Sized) and len(value) == 0:
            # ALL rules, except of if
            self._drop_remaining_rules(
                'allowed',
                'forbidden',
                'items',
                'minlength',
                'maxlength',
                'regex',
                'check_with',
                'stringformat',
                'min', 'max',
                'numberformat',
                'mindate', 'maxdate',
                'dateformat',
                'delimitedvalues'
            )
            if not empty:
                self._error(field, errors.EMPTY_NOT_ALLOWED)

    def _validate_allowed(self, allowed_values, field, value):
        """ {'type': ['list', 'string']} """

        # support single string values as well (cerberus only supports lists)
        if isinstance(allowed_values, _str_type):
            allowed_values = [allowed_values]

        super(DwcaValidator, self)._validate_allowed(allowed_values,
                                                     field, value)

    def _validate_min(self, min_value, field, value):
        """ {'nullable': False} """
        try:
            if float(min_value) > float(value):
                self._error(field, errors.MIN_VALUE)
        except ValueError:
            self._error(field,
                        'min validation failed, value is not numeric')

    def _validate_max(self, max_value, field, value):
        """ {'nullable': False} """
        try:
            if float(max_value) < float(value):
                self._error(field, errors.MAX_VALUE)
        except ValueError:
            self._error(field,
                        'max validation failed, value is not numeric')

    def _parse_date(self, field, date_string):
        """try to parse a string to date and log error when failing
        """
        try:
            event_date = parse(date_string)
            return event_date
        except ValueError:
            self._error(field, "could not be interpreted as date or datetime")
            return None

    @staticmethod
    def _dateisrange(value):
        """"""
        if len(re.findall('([0-9])/([0-9])', value)) > 1:
            NotImplemented
        elif len(re.findall('([0-9])/([0-9])', value)) == 1:
            return True
        else:
            return False

    @staticmethod
    def _dateformatisrange(value):
        """"""
        datesymbols = re.sub('[^a-zA-Z]', '', value)
        return len(set(datesymbols)) != len(datesymbols)

    def _validate_mindate(self, min_date, field, value):
        """ {'type': ['date', 'datetime']} """

        # Remarks
        # -------
        # the yaml-reader prepares a datetime.date objects when possible,
        # the dwca-reader is not doing this, so compatibility need to be better
        # ensured

        if self._dateisrange(value):
            [self._validate_mindate(min_date, field, valdate) for valdate in
             value.split("/")]
        else:
            # convert schema info to datetime to enable comparison
            if isinstance(min_date, date):
                min_date = datetime.combine(min_date, datetime.min.time())

            # try to parse the datetime-format
            event_date = self._parse_date(field, value)
            if event_date:
                if event_date < min_date:
                    self._error(field, "date is before min limit " +
                                min_date.date().isoformat())

    def _validate_maxdate(self, max_date, field, value):
        """ {'type': ['date', 'datetime']} """

        # Remarks
        # -------
        # the yaml-reader prepares a datetime.date objects when possible,
        # the dwca-reader is not doing this, so compatibility need to be better
        # ensured

        if self._dateisrange(value):
            for valdate in value.split("/"):
                self._validate_maxdate(max_date, field, valdate)
        else:
            # convert schema info to datetime to enable comparison
            if isinstance(max_date, date):
                max_date = datetime.combine(max_date, datetime.min.time())

            # try to parse the datetime-format
            event_date = self._parse_date(field, value)
            if event_date:
                if event_date > max_date:
                    self._error(field, "date is after max limit " +
                                max_date.date().isoformat())

    def _help_dateformat(self, formatstr, value):
        """"""
        if self._dateformatisrange(formatstr):
            if self._dateisrange(value):  # both ranges-> test
                range_test = [self._help_dateformat(dt_format, dt) for
                              dt_format, dt in zip(formatstr.split('/'),
                                                   value.split('/'))]
                # both must be valid interpretable dates
                return sum(range_test) == 2

            else:
                return False
        else:

            try:
                datetime.strptime(value, formatstr)
                tester = True
            except ValueError:
                tester = False
                pass
            return tester

    def _validate_dateformat(self, ref_value, field, value):
        """ {'type': ['string', 'list']} """
        # dateformat : ['%Y-%m-%d', '%Y-%m', '%Y']
        # dateformat : '%Y-%m'
        tester = False

        if isinstance(ref_value, list):
            for formatstr in ref_value:  # check if at least one comply
                current_test = self._help_dateformat(formatstr, value)
                if current_test:
                    tester = True

        else:
            tester = self._help_dateformat(ref_value, value)

        if not tester:
            self._error(field, "String format not compliant with " +
                        ', '.join(ref_value))

    def _validate_numberformat(self, formatter, field, value):
        """ {'type': ['string'],
            'regex': '^[1-9]\.[1-9]$|^[1-9]\.$|^\.[1-9]$|^[1-9]$|^\.$|^x$'}
        """

        # value_str = self.document_str_version[field]

        # ignore - sign to handle negative numbers
        value_str = re.sub("^-", "", value)

        # check if value is number format
        if not re.match('^[0-9]*\.[0-9]*$|^[0-9]+$', value_str):
            self._error(field, "".join([value_str,
                                        " is not numerical"]))
        elif re.match('^x$', formatter):
            if not re.match('^[-+]?\d+$', value_str):
                self._error(field, "".join(["value ",
                                            value_str,
                                            " is not an integer"]))
        else:
            if re.match("[1-9]\.[1-9]", formatter):
                value_parsed = [len(side) for side in value_str.split(".")]
            elif re.match("\.[1-9]", formatter):
                if "." in value_str:
                    value_parsed = [len(value_str.split(".")[1])]
                else:
                    value_parsed = [0]
            elif re.match("[1-9]\.", formatter):
                value_parsed = [len(value_str.split(".")[0])]
            elif re.match("[1-9]", formatter):
                if re.match("[0-9]+", value_str):
                    value_parsed = [len(value_str)]
                else:
                    value_parsed = [None]
                    self._error(field, "".join(["value ",
                                                value_str,
                                                " is not an integer"]))
            elif re.match("^\.$", formatter):
                if "." in value_str:
                    value_parsed = []
                else:
                    value_parsed = [None]
                    self._error(field, "".join(["value ",
                                                value_str,
                                                " is not a float"]))

            formatter_parsed = [int(length) for length in formatter.split(".")
                                if not length == '']

            if formatter_parsed != value_parsed and value_parsed != [None]:
                self._error(field, "".join(["numberformat of value ",
                                            value_str,
                                            " not in agreement with ",
                                            formatter]))

    def _validate_if(self, ifset, field, value):
        """ {'type': ['dict', 'list']} """

        if isinstance(ifset, Mapping):
            # extract dict values -> conditions
            conditions = {k: v for k, v in ifset.items() if
                          isinstance(v, dict)}
            # extract dict values -> rules
            rules = {k: v for k, v in ifset.items() if not
                     isinstance(v, dict)}

            tempvalidator = DwcaValidator(conditions)
            tempvalidator.allow_unknown = True

            if tempvalidator.validate(copy(self.document_str_version),
                                      normalize=True):
                validator = self._get_child_validator(
                    document_crumb=(field, 'if'), schema_crumb=(field, 'if'),
                    schema={field: rules}, allow_unknown=True)
                validator.validate(copy(self.document_str_version),
                                   normalize=False) 

                if validator._errors:
                    self._drop_nodes_from_errorpaths(validator._errors,
                                                     [2], [2])
                    self._error(field, IF_SCHEMA, validator._errors)
#            else:
#                self._error(field, "condition not fulfilled in if statement")

        elif isinstance(ifset, Sequence) and not isinstance(ifset, _str_type):
            for i, ifsubschema in enumerate(ifset):
                # extract dict values -> conditions
                conditions = {k: v for k, v in ifsubschema.items() if
                              isinstance(v, dict)}
                # extract dict values -> rules
                rules = {k: v for k, v in ifsubschema.items() if not
                         isinstance(v, dict)}

                tempvalidator = DwcaValidator(conditions)
                tempvalidator.allow_unknown = True

                if tempvalidator.validate(copy(self.document_str_version),
                                          normalize=True):
                    validator = self._get_child_validator(
                        document_crumb=(field, ''.join(['if_', str(i)])),
                        schema_crumb=(field, 'if'),
                        schema={field: rules}, allow_unknown=True)
                    validator.validate(copy(self.document_str_version),
                                       normalize=False)

                    if validator._errors:
                        self._drop_nodes_from_errorpaths(validator._errors,
                                                         [2], [2])
                        self._error(field, IF_SCHEMA, validator._errors)
#                else:
#                    self._error(field, "condition not fulfilled in if
#                    statement")

    def _validate_delimitedvalues(self, ruleset_schema, field, value):
        """ {'type' : 'dict'} """
        # loosely constructed such as the __validate_schema_sequence

        ruleset = copy(ruleset_schema)
        # convert field string to list of values
        if 'delimiter' not in ruleset.keys():
            raise ValueError('Define delimiter as rule in delimitedvalues')
        value = [el for el in value.split(ruleset['delimiter'])]

        # check for empty string (edge case where we do not want 'male | ')
        if '' in value:
            self._error(field,
                        "contains empty string combined with delimiters")
            return True

        # check for doubles ('male | female | male' needs error)
        if len(value) != len(set(value)):
            self._error(field, "contains duplicate values in delimitedvalues")

        # reorganise schema to be used in child_validator
        ruleset.pop('delimiter')
        schema = dict(((i, ruleset) for i in range(len(value))))

        validator = self._get_child_validator(
            document_crumb=field, schema_crumb=(field, 'delimitedvalues'),
            schema=schema, allow_unknown=self.allow_unknown)

        validator.validate(dict(((i, v) for i, v in enumerate(value))),
                           normalize=True)
        if validator._errors:
            self._drop_nodes_from_errorpaths(validator._errors, [], [2])
            self._error(field, DELIMITER_SCHEMA, validator._errors)

    def _validate_stringformat(self, stringtype, field, value):
        """ {'allowed': ['url', 'json']} """
        if stringtype == 'json':
            try:
                json.loads(value)
                return True
            except ValueError:
                self._error(field, "no valid json format")
        elif stringtype == 'url':
            if match(value, rule='URI'):
                return True
            else:
                self._error(field, "no valid url format")
