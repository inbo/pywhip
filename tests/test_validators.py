# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 15:46:18 2016

@author: stijn_vanhoey

# using nosetests...
"""

import yaml
import unittest
from datetime import datetime

from pywhip.validators import DwcaValidator


class TestDateValidator(unittest.TestCase):

    def setUp(self):
        self.yaml_string_date1 = """
                                 moment:
                                     mindate: 1830-01-01
                                     maxdate: 2014-10-20
                                 """
        self.yaml_string_date2 = """
                                    moment:
                                        dateformat: ['%Y-%m-%d', '%Y-%m', '%Y']
                                    """
        self.yaml_string_date3 = """
                                    moment:
                                        dateformat: '%Y-%m'
                                    """
        self.yaml_string_date4 = """
                                 moment:
                                     maxdate: 2014-10-20
                                 """
        self.yaml_string_date5 = """
                                 moment:
                                     dateformat: '%Y-%m-%d/%Y-%m-%d'
                                 """

    def test_daterange_iso(self):
        # isoformat
        val = DwcaValidator(yaml.load(self.yaml_string_date1))
        document1 = {'moment' : '20110101'}  #True
        self.assertTrue(val.validate(document1))

    def test_daterange_line(self):
        # format with - inside range
        val = DwcaValidator(yaml.load(self.yaml_string_date1))
        document2 = {'moment': '2009-08-31'}  # True
        self.assertTrue(val.validate(document2))

    def test_daterange_out(self):
        # outside the range
        val = DwcaValidator(yaml.load(self.yaml_string_date1))
        document = {'moment': '17000101'}  # False
        self.assertFalse(val.validate(document))

        val = DwcaValidator(yaml.load(self.yaml_string_date1))
        document = {'moment': '20150831'}  # False
        self.assertFalse(val.validate(document))

    def test_daterange_nodate(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date4))
        document = {'moment': '1700101'}  # False
        val.validate(document)
        self.assertEqual(val.errors,
                {'moment': ['could not be interpreted as date or datetime']})

    def test_dateformat_line(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date2))
        document = {'moment': '1997-01-05'}  # True
        self.assertTrue(val.validate(document))

    def test_dateformat_day(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date2))
        document = {'moment': '1997-01'}  # True
        self.assertTrue(val.validate(document))

    def test_dateformat_multiple_wrong(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date2))
        document = {'moment': '19970105'}  # False
        self.assertFalse(val.validate(document))

    def test_dateformat_single(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date3))
        document = {'moment': '1997-01'}  # True
        self.assertTrue(val.validate(document))

    def test_dateformat_period_valid(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date5))
        document = {'moment': '1997-02-01/2001-03-01'}  # True
        self.assertTrue(val.validate(document))

    def test_dateformat_period_invalid_first(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date5))
        document = {'moment': '1997-02/2001-03-01'}  # True
        self.assertFalse(val.validate(document))

    def test_dateformat_period_invalid_last(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date5))
        document = {'moment': '1997-02-01/03-01'}  # True
        self.assertFalse(val.validate(document))


class TestNumberFormatValidator(unittest.TestCase):

    def setUp(self):
        self.yaml_numberformat1 = """
                                    size:
                                        numberformat: '.5'
                                    """

        self.yaml_numberformat2 = """
                                    size:
                                        numberformat: '3.5'
                                    """

        self.yaml_numberformat3 = """
                                    size:
                                        numberformat: '4.'
                                    """

    def test_numberformat_right(self):
        val = DwcaValidator(yaml.load(self.yaml_numberformat1))
        document = {'size' : '1110.14372'} # True
        self.assertTrue(val.validate(document))
        document = {'size' : '.14372'} # True
        self.assertTrue(val.validate(document))
        document = {'size' : '0.1437'} # False
        self.assertFalse(val.validate(document))

    def test_numberformat_both(self):
        val = DwcaValidator(yaml.load(self.yaml_numberformat2))
        document = {'size' : '123.14372'} # True
        self.assertTrue(val.validate(document))
        document = {'size' : '0.1437'} # False
        self.assertFalse(val.validate(document))

    def test_numberformat_left(self):
        val = DwcaValidator(yaml.load(self.yaml_numberformat3))
        document = {'size' : '1234.14372'} # True
        self.assertTrue(val.validate(document))
        document = {'size' : '123.12'} # False
        self.assertFalse(val.validate(document))

    def test_numberformat_integer(self):
        val = DwcaValidator(yaml.load(self.yaml_numberformat3))
        document = {'size' : '1234.'} # True
        self.assertTrue(val.validate(document))
        document = {'size' : '1234.55555'} # True
        self.assertTrue(val.validate(document))
        document = {'size' : '1234'} # True
        self.assertTrue(val.validate(document))


class TestDelimitedValuesValidator(unittest.TestCase):

    def setUp(self):
        self.yaml_delimited1 = """
                                    sex:
                                        delimitedvalues:
                                            delimiter: " | "
                                            allowed: [male, female]
                                    """

        self.yaml_delimited2 = """
                                    age:
                                        delimitedvalues:
                                            delimiter: " | "
                                            if:
                                                lifestage:
                                                    allowed: [juvenile]
                                                max: 20
                                    lifestage:
                                        allowed: [juvenile, adult]
                                    """

        self.yaml_delimited3 = """
                                    stage:
                                        delimitedvalues:
                                            delimiter: " | "
                                            min: 1.
                                            max: 8
                                            numberformat: '.3'
                                            type: float
                                    """

        self.yaml_delimited4 = """
                                    sex:
                                        delimitedvalues:
                                            delimiter: " | "
                                            listvalues
                                    """

        self.yaml_delimited5 = """
                                    sex:
                                        delimitedvalues:
                                            allowed: [male, female]
                                    """

    def test_delimiter_doubles(self):
        val = DwcaValidator(yaml.load(self.yaml_delimited1))
        document = {'sex' : 'male | female | male'} # False
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'sex': ['contains duplicate values in delimitedvalues']})

    def test_delimiter_single_occurence(self):
        """should be passed and just checked as such
        """
        val = DwcaValidator(yaml.load(self.yaml_delimited1))
        document = {'sex' : 'male'} # True
        self.assertTrue(val.validate(document))

    def test_delimiter_wrong_delimiter(self):
        """splitting is just not occuring, so warning will be on
        unallowed value
        """
        val = DwcaValidator(yaml.load(self.yaml_delimited1))
        document = {'sex' : 'male ; female'} # False, due to wrong endname
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'sex': [{0: ['unallowed value male ; female']}]})

    def test_delimiter_enddelim_not_allowed(self):
        """pipe too much which can not be split anymore
        """
        val = DwcaValidator(yaml.load(self.yaml_delimited1))
        document = {'sex' : 'male | female |'} # False
        self.assertFalse(val.validate(document))

    def test_delimiter_empty_not_allowed(self):
        """pipe too much which results in empty value
        """
        val = DwcaValidator(yaml.load(self.yaml_delimited1))
        document = {'sex' : 'male | female | '} # False (pipe too much)
        self.assertFalse(val.validate(document))

    def test_delimiter_nest(self):
        val = DwcaValidator(yaml.load(self.yaml_delimited3))
        document = {'stage' : '0.123 | 4.235'} # True
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'stage': [{0: ['min value is 1.0']}]})

    def test_no_delimiter_error(self):
        """raise Error when no delimiter field added
        """
        val = DwcaValidator(yaml.load(self.yaml_delimited5))
        document = {'sex' : 'male | female '}
        with self.assertRaises(ValueError):
            val.validate(document)

#    def test_delimiter_if_condition_pass(self):
#        val = DwcaValidator(yaml.load(self.yaml_delimited2))
#        document = {'age' : '5 | 18 | 19', 'lifestage':'juvenile'} # True
#        self.assertTrue(val.validate(document))
#
#    def test_delimiter_if_condition_nonpass(self):
#        val = DwcaValidator(yaml.load(self.yaml_delimited2))
#        document = {'age' : '5 | 18 | 99', 'lifestage':'adult'} # True
#        self.assertFalse(val.validate(document))

    def test_delimiter_if_checkindication(self):
        val = DwcaValidator(yaml.load(self.yaml_delimited2))
        document = {'age' : '5 | 32', 'lifestage':'juvenile'} # False
        self.assertFalse(val.validate(document))

##    def test_delimiter_enlist(self):
##        """combine the listvalues within the delimitedvalues
##        """
##        #to check how enlist well be handled... (let op unieke enkel behouden)


class TestIfValidator(unittest.TestCase):

    def setUp(self):
        self.yaml_if = """
                        type:
                            if:
                                basisOfRecord:
                                    allowed: [HumanObservation]
                            allowed: [Event]
                            empty: False
                        basisOfRecord:
                            allowed: [HumanObservation, Machine]
                        """

        self.yaml_ifif = """
                            lifestage:
                                if:
                                    - age:
                                          min: 20
                                          type: integer
                                      allowed: [adult]
                                    - age:
                                          min: 20
                                          type: integer
                                      maxlength: 6
                            age:
                                type: integer
                            """

        self.yaml_ifcombi = """
                            basisOfRecord:
                                empty: false
                                allowed: [HumanObservation, PreservedSpecimen]
                                if:
                                    collectionCode:
                                        empty: true
                                    allowed: [PreservedSpecimen]
                            collectionCode:
                                empty: true
                            """

    def test_if(self):
        schema = yaml.load(self.yaml_if)
        document = {'basisOfRecord': 'HumanObservation', 'type': 'Event'}
        val = DwcaValidator(schema)
        self.assertTrue(val.validate(document))

    def test_ifnot(self):
        schema = yaml.load(self.yaml_if)
        document = {'basisOfRecord': 'HumanObservation', 'type': 'Measurement'}
        val = DwcaValidator(schema)
        self.assertFalse(val.validate(document))

    def test_multiple_if_error(self):
        """term trespasses both if clauses at the same time
        """
        schema = yaml.load(self.yaml_ifif)
        document = {'age' : '21', 'lifestage':'juvenile'} #True
        val = DwcaValidator(schema)
        val.validate(document)
        self.assertEqual(val.errors,
                         {'lifestage': [{'if_0': ['unallowed value juvenile'],
                                        'if_1': ['max length is 6']}]})

    def test_multiple_if_pass(self):
        """document satisfies both if clauses at the same time
        """
        schema = yaml.load(self.yaml_ifif)
        document = {'age' : '21', 'lifestage':'adult'} #True
        val = DwcaValidator(schema)
        self.assertTrue(val.validate(document))

    def test_multiple_if_combi(self):
        """document satisfies if and non-if clauses
        """
        schema = yaml.load(self.yaml_ifcombi)
        document = {'basisOfRecord': 'PreservedSpecimen', 'collectionCode': ''}
        val = DwcaValidator(schema)
        self.assertTrue(val.validate(document))

    def test_multiple_if_combi_nonpass(self):
        """document satisfies if and non-if clauses
        """
        schema = yaml.load(self.yaml_ifcombi)
        document = {'basisOfRecord': 'HumanObservation', 'collectionCode': ''}
        val = DwcaValidator(schema)
        val.validate(document)
        self.assertEqual(val.errors,
                         {'basisOfRecord': [{'if': ['unallowed value HumanObservation']}]})


class TestDataTypeValidator(unittest.TestCase):

    def test_json_type(self):
        yaml_string = """
                        perimeter:
                            type: json
                        """
        schema = yaml.load(yaml_string)
        document = {'perimeter': """
                                    {"top": 3, "centre": 5, "bottom": 6}
                                    """}
        val = DwcaValidator(schema)
        self.assertTrue(val.validate(document))

    def test_wrong_json_type(self):
        document = {'size' : 'large',
                    'perimeter': """
                                    {"top": 3, "centre": 5, "bottom": 6
                                    """}
        schema = {'perimeter':{'type':'json'}}
        val = DwcaValidator(schema)
        val.allow_unknown = True
        self.assertFalse(val.validate(document))

    def test_url_type(self):
        document = {'location': "https://github.com/LifeWatchINBO/dwca-validator"}
        schema = {'location':{'type':'url'}}
        val = DwcaValidator(schema)
        self.assertTrue(val.validate(document))

    def test_wrong_url_type(self):
        document = {'location': "https/github.com/LifeWatchINBO/dwca-validator"}
        schema = {'location':{'type':'url'}}
        val = DwcaValidator(schema)
        self.assertFalse(val.validate(document))

class TestLengthValidator(unittest.TestCase):
    """
    lenght is a new validator type created for the DwcaValidator
    """

    def setUp(self):
        self.yaml_length = """
                             verbatimCoordinateSystem:
                                 length : 5
                             coordinateSystem:
                                 length : 1
                             """

    def test_length(self):
        """test if the string has proper minimal length
        """
        val = DwcaValidator(yaml.load(self.yaml_length))
        document = {'verbatimCoordinateSystem' : '31UDS'}
        self.assertTrue(val.validate(document))
        document = {'verbatimCoordinateSystem' : '3'}
        self.assertFalse(val.validate(document))


class TestEqualsValidator(unittest.TestCase):
    """
    equals is a new validator type created for the DwcaValidator that works on
    integer and float values
    """

    def setUp(self):
        self.yaml_length = """
                             individualCount:
                                 equals : 1
                             precision:
                                 equals : 200.
                             """

    def test_euqals_int(self):
        """test if the integer value equals the given value
        """
        val = DwcaValidator(yaml.load(self.yaml_length))
        # here not type test needed in schema, value given as integer
        document = {'individualCount' : 1.000}
        self.assertTrue(val.validate(document))
        document = {'individualCount' : 2}
        self.assertFalse(val.validate(document))

    def test_euqals_float(self):
        """test if the float value equals the given value
        """
        val = DwcaValidator(yaml.load(self.yaml_length))
        # here not type test needed in schema, value given as float
        document = {'precision' : 200.00}
        self.assertTrue(val.validate(document))
        document = {'precision' : 200.001}
        self.assertFalse(val.validate(document))


class TestCerberusTypeValidator(unittest.TestCase):
    """
    int, float and number are tested here as if they are already interpreted in
    the document as such. The test for the string representations (with coerce)
    are given in test_cerberus_additions
    """

    def setUp(self):
        self.yaml_dtypes = """
                           age:
                               type: integer
                           decimalLatitude:
                               type: float
                           percentage:
                               type: number
                           datum:
                               type: datetime
                           abondance:
                               type: boolean
                           code:
                               type: string
                           """

    def test_str(self):
        """test if a field is a string
        """
        val = DwcaValidator(yaml.load(self.yaml_dtypes))
        document = {'code': 'ICZN'}
        self.assertTrue(val.validate(document))

    def test_int(self):
        """test if a field is an integer
        """
        val = DwcaValidator(yaml.load(self.yaml_dtypes))
        document = {'age': 5}
        self.assertTrue(val.validate(document))

    def test_float(self):
        """test if a field is a float
        """
        val = DwcaValidator(yaml.load(self.yaml_dtypes))
        document = {'decimalLatitude': 51.2}
        self.assertTrue(val.validate(document))

    def test_number(self):
        """test if a field is a number
        """
        val = DwcaValidator(yaml.load(self.yaml_dtypes))
        document = {'percentage': 2.2}
        self.assertTrue(val.validate(document))
        document = {'percentage': 2}
        self.assertTrue(val.validate(document))

    def test_boolean(self):
        """test if a field is a boolean
        """
        val = DwcaValidator(yaml.load(self.yaml_dtypes))
        document = {'abondance': True}
        self.assertTrue(val.validate(document))

    def test_datetime(self):
        """test if a field is a datetime object
        """
        val = DwcaValidator(yaml.load(self.yaml_dtypes))
        document = {'datum': datetime(2016, 11, 2)}
        self.assertTrue(val.validate(document))


class TestCerberusValidator(unittest.TestCase):
    """Test validation methods that are native to Cerberus already
    """

    def setUp(self):
        self.yaml_required = """
                             sex:
                                 required: False
                             moment:
                                 required: True
                             """

        self.yaml_length = """
                             verbatimCoordinateSystem:
                                 minlength : 5
                             coordinateSystem:
                                 maxlength : 5
                             code:
                                 minlength : 2
                             """

        self.yaml_value = """
                             individualCount:
                                 min : 5
                                 max : 8
                                 type : integer
                             percentage:
                                 min : 5.5
                                 max : 8.1
                                 type : float
                             code:
                                 type : integer
                                 min : 3
                             """
        self.yaml_string = """
                             individualCount:
                                 min : 5
                                 type : string
                             code:
                                 max : 3
                                 type : string
                             """

        self.yaml_allow = """
                          sex:
                              allowed : [male, female]
                          rightsHolder:
                              allowed : [INBO]
                          """

    def test_required(self):
        """test if a field (key) is present
        """
        val = DwcaValidator(yaml.load(self.yaml_required))
        document = {'moment' : '2016-12-11'}
        self.assertTrue(val.validate(document))

        document = {'sex' : '2016-12-11'}
        self.assertFalse(val.validate(document))

    def test_minlength(self):
        """test if the string has proper minimal length
        """
        val = DwcaValidator(yaml.load(self.yaml_length))
        document = {'verbatimCoordinateSystem' : '31UDS76C'}
        self.assertTrue(val.validate(document))
        document = {'verbatimCoordinateSystem' : '5'}
        self.assertFalse(val.validate(document))

    def test_maxlength(self):
        """test if the string has proper maximal length
        """
        val = DwcaValidator(yaml.load(self.yaml_length))
        document = {'coordinateSystem' : '31U'}
        self.assertTrue(val.validate(document))
        document = {'coordinateSystem' : '31UDS76C'}
        self.assertFalse(val.validate(document))

    def test_minlength_ignored_by_type(self):
        """test if an integer is ignored by length-options
        """
        val = DwcaValidator(yaml.load(self.yaml_length))
        document = {'code' : 5}
        self.assertTrue(val.validate(document))

    def test_minmax_float(self):
        """test if the value has minimal value
        """
        val = DwcaValidator(yaml.load(self.yaml_value))
        document = {'percentage' : 9.}
        self.assertFalse(val.validate(document))
        document = {'percentage' : 2.1}
        self.assertFalse(val.validate(document))

    def test_minmax_int(self):
        """test if the value has minimal value
        """
        val = DwcaValidator(yaml.load(self.yaml_value))
        document = {'individualCount' : 9}
        self.assertFalse(val.validate(document))
        document = {'individualCount' : 2}
        self.assertFalse(val.validate(document))

    def test_min_int_coerce(self):
        """test if the value has minimal value
        """
        val = DwcaValidator(yaml.load(self.yaml_value))
        document = {'code' : '6'}
        self.assertTrue(val.validate(document))
        document = {'code' : '2'}
        self.assertFalse(val.validate(document))

    def test_min_int_string(self):
        """test if the value has minimal value with string input
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'individualCount' : 'vijf'} # provide error on type mismatch
        val.validate(document)
        self.assertEqual(val.errors,
                    {'individualCount': ['min validation ignores string type, add type validation']},
                    msg="alert on datatype mismatch for min evaluation fails")

    def test_max_int_string(self):
        """test if the value has maximal value with string input
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'code' : 'vijf'} # provide error on type mismatch
        val.validate(document)
        self.assertEqual(val.errors,
                    {'code': ['max validation ignores string type, add type validation']},
                    msg="alert on datatype mismatch for min evaluation fails")

    def test_allowed_string(self):
        """test if the value is the allowed value
        """
        val = DwcaValidator(yaml.load(self.yaml_allow))
        document = {'rightsHolder' : 'INBO'}
        self.assertTrue(val.validate(document))
        document = {'rightsHolder' : 'ILVO'}
        self.assertFalse(val.validate(document))

    def test_allowed_list(self):
        """test if the value is one of the allowed values
        """
        val = DwcaValidator(yaml.load(self.yaml_allow))
        document = {'rightsHolder' : 'INBO'}
        self.assertTrue(val.validate(document))
        document = {'rightsHolder' : 'ILVO'}
        self.assertFalse(val.validate(document))









