# -*- coding: utf-8 -*-

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
from cerberus.errors import ErrorDefinition, BasicErrorHandler
from cerberus.platform import _str_type

"""
For each pywhip custom rule, a :class:`~cerberus.errors.ErrorDefinition` 
instance is created to link specifications with unique identifiers.
"""
DELIMITER_SCHEMA = ErrorDefinition(0x85, 'delimitedvalues')
IF_SCHEMA = ErrorDefinition(0x86, 'if')

DELIMITER_DOUBLE = ErrorDefinition(0x107, 'delimitedvalues')
DELIMITER_SPACE = ErrorDefinition(0x108, 'delimitedvalues')

MIN_NON_NUMERIC = ErrorDefinition(0x7, 'min')
MAX_NON_NUMERIC = ErrorDefinition(0x8, 'max')
MINDATE_VALUE = ErrorDefinition(0xA, 'mindate')
MAXDATE_VALUE = ErrorDefinition(0xB, 'maxdate')
MINDATE_NOT_PARSED = ErrorDefinition(0xC, 'mindate')
MAXDATE_NOT_PARSED = ErrorDefinition(0xD, 'maxdate')
DATEFORMAT = ErrorDefinition(0xE, 'dateformat')

NUMBERFORMAT_NON_NUM = ErrorDefinition(0x101, 'numberformat')
NUMBERFORMAT_NON_FLOAT = ErrorDefinition(0x102, 'numberformat')
NUMBERFORMAT_NON_INT = ErrorDefinition(0x103, 'numberformat')
NUMBERFORMAT_VALUE = ErrorDefinition(0x104, 'numberformat')
STRINGFORMAT_JSON = ErrorDefinition(0x105, 'stringformat')
STRINGFORMAT_URL = ErrorDefinition(0x106, 'stringformat')


class WhipErrorHandler(BasicErrorHandler):
    """Class to store custom error message handling

    The WhipErrorHandler updates the
    :class:`~cerberus.errors.BasicErrorHandler` with custom messages for
    pywhip specific specifications. Each of the messages updates the
    message of a specification error, using the unique code
    attributed in the :class:`~cerberus.errors.ErrorDefinition` setup.

    The message is a descriptive message about the error and can optionally
    use the following variables:

    * value
        This refers to the individual data value of the document,
        use ``{value}``
    * constraint
        This refers to the constraint provided by the whip
        specification right hand side of the colon, use ``{constraint}``
    """

    messages = BasicErrorHandler.messages.copy()
    messages[MIN_NON_NUMERIC.code] = "value '{value}' is not numeric"
    messages[MAX_NON_NUMERIC.code] = "value '{value}' is not numeric"
    messages[MINDATE_VALUE.code] = "date '{value}' is before min " \
                                   "limit '{constraint}'"
    messages[MAXDATE_VALUE.code] = "date '{value}' is after max " \
                                   "limit '{constraint}'"
    messages[MINDATE_NOT_PARSED.code] = "value '{value}' could not be " \
                                        "interpreted as date or datetime"
    messages[MAXDATE_NOT_PARSED.code] = "value '{value}' could not be " \
                                        "interpreted as date or datetime"
    messages[DATEFORMAT.code] = "string format of value '{value}' not " \
                                "compliant with '{constraint}'"
    messages[NUMBERFORMAT_NON_NUM.code] = "value '{value}' is not numerical"
    messages[NUMBERFORMAT_NON_FLOAT.code] = "value '{value}' is not a float"
    messages[NUMBERFORMAT_NON_INT.code] = "value '{value}' is not an integer"
    messages[NUMBERFORMAT_VALUE.code] = "numberformat of value '{value}' " \
                                        "not in agreement with '{constraint}'"
    messages[STRINGFORMAT_JSON.code] = "not a valid json format"
    messages[STRINGFORMAT_URL.code] = "not a valid url"

    messages[DELIMITER_DOUBLE.code] = "duplicate values in delimitedvalues"
    messages[DELIMITER_SPACE.code] = "contains empty string inside " \
                                     "delimitedvalues"

    def __iter__(self):
        raise NotImplementedError


class DwcaValidator(Validator):
    """Validates any mapping against specifications defined in a
    validation-schema

    In the context of pywhip, a mapping is generally a single line of data,
    with the keys the fields (data headers) and the values the data values for
    that particular line.

    Notes
    ------
    This class subclasses :class:`~cerberus.Validator` and adds pywhip specific
    ``_validate_<specification>`` methods.

    The whip specifications are a combination of cerberus native specifications
    and pywhip custom ones:

    * directly available by cerberus
        minlength, maxlength, regex

    * cerberus specifications overwritten by pywhip
        allowed, empty, min, max

    * pywhip specific specification functions
        numberformat, dateformat, mindate, maxdate, stringformat

    * pywhip specific specification environments:
        delimitedValues, if

    Each ``_validate_<specification>`` assumes the following input arguments:

    * constraint:
        The constraint provided in the whip specification, i.e. the
        right hand side of the colon in the whip specifications. In the
        implementation, the input parameter can be names differently to clarify
        the role of the constraint in the validation function.
    * field:
        The name of the field, i.e. the left hand side of the colon
        in the whip specifications which corresponds to the field header name
        in the data.
    * value:
        A single data value for which the whip specification needs to be tested
        using the provided constraint.

    To validate the schema input itself, cerberus validation rules can be added
    to the docstring TODO ADDLINK
    """

    def __init__(self, *args, **kwargs):
        """Extends the handling of Cerberus :class:`~cerberus.Validator`

        The following alterations are done:
        * Allow_unkown is default set on True
        * Initaition requires a schema
        * By default, all fields without ``empty`` specification get an
        ``empty: False`` specification. As such, empy strings are not allowed
        by default, according to whip specifications.

        Parameters
        ----------
        allow_unknown : boolean
            If False, only terms with specifications are allowed as input. As
            unknown fields are reported by pywhip after validation, the
            default value is False.
        """
        super(DwcaValidator, self).__init__(*args, **kwargs)

        if 'allow_unknown' in kwargs:
            self.allow_unknown = kwargs['allow_unknown']
        else:
            self.allow_unknown = True

        if not self.schema:
            raise Exception('provide a schema to initiate Validator')

        # Extend schema with empty: False by default
        self.schema = self._schema_add_empty(self.schema)

    @staticmethod
    def _schema_add_empty(dict_schema):
        """Add `empty: False`` specification for all fields without
        ``empty`` specification

        Parameters
        ----------
        dict_schema : dict
            Schema of ``field: specification`` items, for which each
            specification is a dict itself.
        """
        for term, rules in dict_schema.items():
            if 'empty' not in rules.keys():
                rules['empty'] = False
        return dict_schema

    def _validate_empty(self, empty, field, value):
        """ {'type': 'boolean'} """
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
            self._error(field, MIN_NON_NUMERIC)

    def _validate_max(self, max_value, field, value):
        """ {'nullable': False} """
        try:
            if float(max_value) < float(value):
                self._error(field, errors.MAX_VALUE)
        except ValueError:
            self._error(field, MAX_NON_NUMERIC)

    def _parse_date(self, date_string):
        """Try to parse a string to a Python :class:`~python3.datetime.dateime`
        datetime.

        Parameters
        ----------
        date_string : str

        Returns
        -------
        datetime | None
            If parsing fails, return None, otherwise parsed
            :class:`~python3.datetime.dateime`
        """
        try:
            event_date = parse(date_string)
            return event_date
        except ValueError:
            return None

    @staticmethod
    def _dateisrange(value):
        """Test if the given string representing date is a range

        Parameters
        ----------
        value : str
            date, e.g. 2018-01-01 (no range) or 2010-01-01/2018-05-01

        Returns
        -------
        value : boolean
            True if daterange is given, otherwise False
        """
        if len(re.findall('([0-9])/([0-9])', value)) > 1:
            NotImplemented
        elif len(re.findall('([0-9])/([0-9])', value)) == 1:
            return True
        else:
            return False

    @staticmethod
    def _dateformatisrange(value):
        """Test if the given dateformat representing is a range

        Parameters
        ----------
        value : str
            dateformat, e.g. %Y-%m-%d (no range) or %Y-%m-%d/%Y-%m-%d (range)

        Returns
        -------
        value : boolean
            True if daterange is given, otherwise False
        """
        datesymbols = re.sub('[^a-zA-Z]', '', value)
        return len(set(datesymbols)) != len(datesymbols)

    def _validate_mindate(self, min_date, field, value):
        """ {'type': ['date', 'datetime']} """

        # TODO:
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
            event_date = self._parse_date(value)
            if event_date:
                if event_date < min_date:
                    self._error(field, MINDATE_VALUE)
            else:
                self._error(field, MINDATE_NOT_PARSED)

    def _validate_maxdate(self, max_date, field, value):
        """ {'type': ['date', 'datetime']} """

        # TODO:
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
            event_date = self._parse_date(value)
            if event_date:
                if event_date > max_date:
                    self._error(field, MAXDATE_VALUE)
            else:
                self._error(field, MAXDATE_NOT_PARSED)

    def _help_dateformat(self, formatstr, value):
        """Test if a date is according to a given dateformat

        Parameters
        ----------
        formatstr : str
            dateformat string, e.g. %Y-%m-%d or %Y-%m-%d/%Y-%m-%d
        value : str
            date str representation, e.g. 2018-01-01 or 2015-01-01/2018-01-01

        Returns
        -------
        boolean
            when True, the date string is accoring to the format
        """
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
            self._error(field, DATEFORMAT)

    def _validate_numberformat(self, formatter, field, value):
        """ {'type': ['string'],
            'regex': '^[1-9]\.[1-9]$|^[1-9]\.$|^\.[1-9]$|^[1-9]$|^\.$|^x$'}
        """

        # ignore - sign to handle negative numbers
        value_str = re.sub("^-", "", value)

        # check if value is number format
        if not re.match('^[0-9]*\.[0-9]*$|^[0-9]+$', value_str):
            self._error(field, NUMBERFORMAT_NON_NUM)
        elif re.match('^x$', formatter):
            if not re.match('^[-+]?\d+$', value_str):
                self._error(field, NUMBERFORMAT_NON_INT)
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
                    self._error(field, NUMBERFORMAT_NON_INT)
            elif re.match("^\.$", formatter):
                if "." in value_str:
                    value_parsed = []
                else:
                    value_parsed = [None]
                    self._error(field, NUMBERFORMAT_NON_FLOAT)

            formatter_parsed = [int(length) for length in formatter.split(".")
                                if not length == '']

            if formatter_parsed != value_parsed and value_parsed != [None]:
                self._error(field, NUMBERFORMAT_VALUE)

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

            if tempvalidator.validate(copy(self.document),
                                      normalize=True):
                validator = self._get_child_validator(
                    document_crumb=(field, 'if'), schema_crumb=(field, 'if'),
                    schema={field: rules}, allow_unknown=True)
                validator.validate(copy(self.document),
                                   normalize=False) 

                if validator._errors:
                    self._drop_nodes_from_errorpaths(validator._errors,
                                                     [2], [2])
                    self._error(field, IF_SCHEMA, validator._errors)

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

                # when the conditional field is not existing in the document,
                # ignore the if-statement
                if not set(conditions.keys()).issubset(
                        set(self.document.keys())):
                    return True

                if tempvalidator.validate(copy(self.document),
                                          normalize=True):
                    validator = self._get_child_validator(
                        document_crumb=(field, ''.join(['if_', str(i)])),
                        schema_crumb=(field, 'if'),
                        schema={field: rules}, allow_unknown=True)
                    validator.validate(copy(self.document),
                                       normalize=False)

                    if validator._errors:
                        self._drop_nodes_from_errorpaths(validator._errors,
                                                         [2], [2])
                        self._error(field, IF_SCHEMA, validator._errors)

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
            self._error(field, DELIMITER_SPACE)
            return True

        # check for doubles ('male | female | male' needs error)
        if len(value) != len(set(value)):
            self._error(field, DELIMITER_DOUBLE)
            return True

        # reorganise schema to be used in child_validator
        ruleset.pop('delimiter')
        schema = dict(((i, ruleset) for i in range(len(value))))

        validator = self._get_child_validator(
            document_crumb=field, schema_crumb=(field, 'delimitedvalues'),
            schema=schema, allow_unknown=True)

        document = dict(((i, v) for i, v in enumerate(value)))

        # provide support for if-statements -> add field from root document
        if 'if' in ruleset.keys():
            term = [key for key in ruleset['if'].keys() if
                    isinstance(ruleset['if'][key], dict)]
            if len(term) > 1:  # multiple if statements  not supported
                NotImplementedError
            else:
                term = term[0]
            document[term] = validator.root_document[term]

        validator.validate(document, normalize=True)

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
                self._error(field, STRINGFORMAT_JSON)
        elif stringtype == 'url':
            if match(value, rule='URI'):
                return True
            else:
                self._error(field, STRINGFORMAT_URL)

