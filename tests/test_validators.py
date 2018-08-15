# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 15:46:18 2016

@author: stijn_vanhoey

"""

import yaml
import unittest
from datetime import datetime

import cerberus
import pytest

from pywhip.validators import DwcaValidator, WhipErrorHandler


class TestAllowedValidator(unittest.TestCase):
    """Test the usage of string as input for allowed values
    (Cerberus native validation)
    """
    def setUp(self):

        self.yaml_allowed_string = """
                                   abundance:
                                       allowed: many                                  
                                   """

        self.yaml_allowed_list = """
                     rightsHolder:
                         allowed : [INBO]   
                     sex:
                         allowed : [male, female]
                     age:
                         allowed : [adult, juvenile, 'adult | juvenile']                                     
                     """

        self.yaml_allowed_inputs = """
                     age:
                         allowed : 30
                     abundance:
                         allowed : '30'                                                                
                     """

    def test_allowed_string(self):
        """test if the value is the allowed value
        """
        val = DwcaValidator(yaml.load(self.yaml_allowed_string),
                            error_handler=WhipErrorHandler)
        document = {'abundance': 'many'}
        self.assertTrue(val.validate(document))
        document = {'abundance': 'female'}
        self.assertFalse(val.validate(document))

    def test_allowed_list(self):
        """test if the value is one of the allowed values
        """
        val = DwcaValidator(yaml.load(self.yaml_allowed_list),
                            error_handler=WhipErrorHandler)
        document = {'rightsHolder': 'INBO'}
        self.assertTrue(val.validate(document))
        document = {'rightsHolder': 'ILVO'}
        self.assertFalse(val.validate(document))
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))
        document = {'sex': 'female'}
        self.assertTrue(val.validate(document))
        document = {'sex': 'Female'}
        self.assertFalse(val.validate(document))
        document = {'age': 'adult'}
        self.assertTrue(val.validate(document))
        document = {'age': 'juvenile'}
        self.assertTrue(val.validate(document))
        document = {'age': 'adult | juvenile'}
        self.assertTrue(val.validate(document))
        document = {'age': 'adult|juvenile'}
        self.assertFalse(val.validate(document))

    def test_allowed_list(self):
        """see https://github.com/inbo/whip/issues/22
        """
        with pytest.raises(cerberus.schema.SchemaError) as excinfo:
            val = DwcaValidator(yaml.load(self.yaml_allowed_inputs),
                                error_handler=WhipErrorHandler)

        #val = DwcaValidator(yaml.load(self.yaml_allowed_inputs))
        #document = {'age': '30'}
        #val.validate(document)
        #document = {'abundance': '30'}
        #self.assertTrue(val.validate(document))


class TestAllowedQuoteFlavors(unittest.TestCase):
    """Test validation method `allowed` (native cerberus)
    according to https://github.com/inbo/whip specifications
    """
    def setUp(self):
        self.yaml_allow1 = """
                          sex:
                              allowed : male
                          """

        self.yaml_allow2 = """
                          sex:
                              allowed : "male"
                          """

        self.yaml_allow3 = """
                          sex:
                              allowed : 'male'
                          """

        self.yaml_allow4 = """
                          sex:
                              allowed : [male]
                          """

        self.yaml_allow5 = """
                          sex:
                              allowed : [male, female]
                          """

        self.yaml_allow6 = """
                          sex:
                              allowed : [male, female, 'male, female']
                          """

    def test_allow_noquote(self):
        """test if allowed accepts a single allowed value without quotes
        """
        val = DwcaValidator(yaml.load(self.yaml_allow1),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))

        document = {'sex': 'female'}
        self.assertFalse(val.validate(document))

    def test_allow_doublequote(self):
        """test if allowed accepts a single allowed value with double quotes
        """
        val = DwcaValidator(yaml.load(self.yaml_allow2),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))

        document = {'sex': 'female'}
        self.assertFalse(val.validate(document))

    def test_allow_singlequote(self):
        """test if allowed accepts a single allowed value with single quotes
        """
        val = DwcaValidator(yaml.load(self.yaml_allow3),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))

        document = {'sex': 'female'}
        self.assertFalse(val.validate(document))

    def test_allow_bracket(self):
        """test if allowed accepts a single allowed value in list
        """
        val = DwcaValidator(yaml.load(self.yaml_allow4),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))

        document = {'sex': 'female'}
        self.assertFalse(val.validate(document))

    def test_allow_bracket_multiple(self):
        """test if allowed accepts multiple values in list  without quotes
        """
        val = DwcaValidator(yaml.load(self.yaml_allow5),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))

        document = {'sex': 'female'}
        self.assertTrue(val.validate(document))

        document = {'sex': 'male, female'}
        self.assertFalse(val.validate(document))

    def test_allow_bracket_multiplemix(self):
        """test if allowed accepts multiple values and terms with quotes
        """
        val = DwcaValidator(yaml.load(self.yaml_allow6),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))

        document = {'sex': 'female'}
        self.assertTrue(val.validate(document))

        document = {'sex': 'male, female'}
        self.assertTrue(val.validate(document))

        document = {'sex': 'male,female'}
        self.assertFalse(val.validate(document))


class TestLengthValidator(unittest.TestCase):
    """Test validation methods `minlength` and `maxlength`,
    (Cerberus native validation)
    according to https://github.com/inbo/whip specifications
    """

    def setUp(self):
        self.yaml_length = """
                             postal_code :
                                 minlength : 4
                                 required: False
                             license_plate:
                                 maxlength: 6
                                 required: False
                             code:
                                 minlength : 2
                                 maxlength : 2
                                 required: False
                             """

    def test_minlength(self):
        """test if the string has proper minimal length

        (remark, all values from DwC are coming in as string value)
        """
        val = DwcaValidator(yaml.load(self.yaml_length),
                            error_handler=WhipErrorHandler)
        document = {'postal_code': '9050'}
        self.assertTrue(val.validate(document))

        document = {'postal_code': 'B-9050'}
        self.assertTrue(val.validate(document))

        document = {'postal_code': '905'}
        self.assertFalse(val.validate(document))

    def test_maxlength(self):
        """test if the string has proper maximal length
        """
        val = DwcaValidator(yaml.load(self.yaml_length),
                            error_handler=WhipErrorHandler)
        document = {'license_plate': 'AF8934'}
        self.assertTrue(val.validate(document))

        document = {'license_plate': '123456'}
        self.assertTrue(val.validate(document))

        document = {'license_plate': 'AF893'}
        self.assertTrue(val.validate(document))

        document = {'license_plate': 'AF8-934'}
        self.assertFalse(val.validate(document))

        document = {'license_plate': 'AF   934'}
        self.assertFalse(val.validate(document))

    def test_minmaxlength(self):
        """test if the string has proper length
        """
        val = DwcaValidator(yaml.load(self.yaml_length),
                            error_handler=WhipErrorHandler)
        document = {'code': 'AA'}
        self.assertTrue(val.validate(document))

        document = {'code': 'A'}
        self.assertFalse(val.validate(document))

        document = {'code': 'ABC'}
        self.assertFalse(val.validate(document))

    def test_minlength_ignored_formats(self):
        """test if an integer or float is ignored by length-options

        Remark, using DwcA, all values are coming in as a string, so testing
        of length will occur for these as well.
        """
        val = DwcaValidator(yaml.load(self.yaml_length),
                            error_handler=WhipErrorHandler)
        document = {'code': 5}
        self.assertTrue(val.validate(document))
        document = {'code': '5'}
        self.assertFalse(val.validate(document))
        document = {'code': 5.2}
        self.assertTrue(val.validate(document))
        document = {'code': '5.2'}
        self.assertFalse(val.validate(document))


class TestStringformatValidator(unittest.TestCase):
    """Test validation method stringformat
    according to https://github.com/inbo/whip specifications
    """

    def setUp(self):
        self.yaml_json = """
                             measurements:
                                stringformat: json
                             """
        self.yaml_url = """
                             website:
                                stringformat: url
                             """

    def test_json_stringformat(self):
        val = DwcaValidator(yaml.load(self.yaml_json),
                            error_handler=WhipErrorHandler)
        document = {'measurements': """
                                    {"top": 3, "centre": 5, "bottom": 6}
                                    """}
        self.assertTrue(val.validate(document))
        document = {'measurements': """
                                    {"length": 2.0}
                                    """}
        self.assertTrue(val.validate(document))
        document = {'measurements': """
                                    {"length": 2.0, "length_unit": "cm"}
                                    """}
        self.assertTrue(val.validate(document))

    def test_wrong_json_stringformat(self):
        val = DwcaValidator(yaml.load(self.yaml_json),
                            error_handler=WhipErrorHandler)
        val.allow_unknown = True
        document = {'size': 'large',
                    'measurements': """
                                    {"top": 3, "centre": 5, "bottom": 6
                                    """}
        self.assertFalse(val.validate(document))
        document = {'measurements': """
                                    {'length': 2.0}
                                    """}
        self.assertFalse(val.validate(document))
        document = {'measurements': """
                                    {length: 2.0}
                                    """}
        self.assertFalse(val.validate(document))
        document = {'measurements': """
                                    length: 2.0
                                    """}
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'measurements': ['not a valid json format']})

    def test_url_stringformat(self):
        val = DwcaValidator(yaml.load(self.yaml_url),
                            error_handler=WhipErrorHandler)
        document = {'website': "https://github.com/LifeWatchINBO/dwca-validator"}
        self.assertTrue(val.validate(document))
        document = {'website': "http://github.com/inbo/whip"}
        self.assertTrue(val.validate(document))

    def test_wrong_url_stringformat(self):
        val = DwcaValidator(yaml.load(self.yaml_url),
                            error_handler=WhipErrorHandler)
        document = {'website': "https/github.com/LifeWatchINBO/dwca-validator"}
        self.assertFalse(val.validate(document))
        document = {'website': "github.com/inbo/whip"}
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'website': ['not a valid url']})


class TestRegexValidator(unittest.TestCase):
    """Test validation method regex
    (Cerberus native validation)
    according to https://github.com/inbo/whip specifications
    """

    def setUp(self):
        self.yaml_regex = """
            observation_id:
                regex: 'INBO:VIS:\d+'
                required: False
            issue_url:
                regex: 'https:\/\/github\.com\/inbo\/whip\/issues\/\d+'
                required: False
            utm1km:
                regex: '31U[D-G][S-T]\d\d\d\d'
                required: False
             """
        self.yaml_regexit = """
            quotes:
                regex: [D - G]
            """

        self.yaml_regexitdouble = """
            quotes:
                regex: "31U[D-G][S-T]\d\d\d\d"
            """

        self.yaml_regexfullmatch = """
            occurrenceid:
                regex: '\d{3}:\d{8}'   
            """

    def test_regex_inbo_ids(self):
        """test if inbo ids structure works on the regex specs"""
        val = DwcaValidator(yaml.load(self.yaml_regex),
                            error_handler=WhipErrorHandler)
        document = {'observation_id': "INBO:VIS:12"}
        self.assertTrue(val.validate(document))
        document = {'observation_id': "INBO:VIS:456"}
        self.assertTrue(val.validate(document))
        document = {'observation_id': "INBO:VIS:"}
        self.assertFalse(val.validate(document))
        document = {'observation_id': "INBO:VIS:ABC"}
        self.assertFalse(val.validate(document))

    def test_regex_advanced_url_regex(self):
        """test if specific url structure can be checked for"""
        val = DwcaValidator(yaml.load(self.yaml_regex),
                            error_handler=WhipErrorHandler)
        document = {'issue_url': "https://github.com/inbo/whip/issues/4"}
        self.assertTrue(val.validate(document))
        document = {'issue_url': "https:\\github.com\inbo\whip\issues\4"}
        self.assertFalse(val.validate(document))

    def test_regex_utm_code(self):
        """test if utm code can be tested on with regex"""
        val = DwcaValidator(yaml.load(self.yaml_regex),
                            error_handler=WhipErrorHandler)
        document = {'utm1km': "31UDS8748"}
        self.assertTrue(val.validate(document))
        document = {'utm1km': "31UDS874A"}
        self.assertFalse(val.validate(document))

    def test_regex_noquotehandling(self):
        """error handling without quotes on regex specifications"""

        with pytest.raises(cerberus.schema.SchemaError) as excinfo:
            val = DwcaValidator(yaml.load(self.yaml_regexit),
                                error_handler=WhipErrorHandler)

        assert "{'quotes': [{'regex': ['must be of string type']}]}" in \
               str(excinfo.value)

    def test_regex_doublequotehandling(self):
        """error handling with double quotes on regex specifications"""
        with pytest.raises(yaml.scanner.ScannerError) as excinfo:
            val = DwcaValidator(yaml.load(self.yaml_regexitdouble),
                                error_handler = WhipErrorHandler)
        assert "found unknown escape character 'd'" in str(excinfo.value)

    def test_regex_onlyfullmatch(self):
        """Make sure regex is full match to pass """
        val = DwcaValidator(yaml.load(self.yaml_regexfullmatch),
                            error_handler=WhipErrorHandler)

        document = {'occurrenceid': "123:12345678"}
        self.assertTrue(val.validate(document))
        document = {'occurrenceid': "123:123456789"}
        self.assertFalse(val.validate(document))


class TestMinMaxValidator(unittest.TestCase):

    def setUp(self):

        self.yaml_value = """
                             individualCount:
                                 min : 5
                                 max : 8
                                 required: False
                             percentage:
                                 min : 5.5
                                 max : 8.1
                                 required: False
                             code:
                                 min : '3'
                                 required: False
                             age_1:
                                 min: 9
                                 required: False
                             age_2:
                                 min: 9.
                                 required: False
                             age_3:
                                 max: 99
                                 required: False
                             age_4:
                                 max: 99.0
                                 required: False
                             """

    def test_min(self):
        """test if the value has minimal value
        """
        val = DwcaValidator(yaml.load(self.yaml_value),
                            error_handler=WhipErrorHandler)
        min_true = ['9', '9.0', '9.1', '10']
        for value in min_true:
            document = {'age_1': value}
            self.assertTrue(val.validate(document))
            document = {'age_2': value}
            self.assertTrue(val.validate(document))

        min_false = ['8.99999', '-9']
        for value in min_false:
            document = {'age_1': value}
            self.assertFalse(val.validate(document))
            document = {'age_2': value}
            self.assertFalse(val.validate(document))

    def test_max(self):
        """test if the value has minimal value
        """
        val = DwcaValidator(yaml.load(self.yaml_value),
                            error_handler=WhipErrorHandler)
        max_true = ['99', '99.0', '89.9', '88', '-99']
        for value in max_true:
            document = {'age_3': value}
            self.assertTrue(val.validate(document))
            document = {'age_4': value}
            self.assertTrue(val.validate(document))

        max_false = ['99.1', '100']
        for value in max_false:
            document = {'age_3': value}
            self.assertFalse(val.validate(document))
            document = {'age_4': value}
            self.assertFalse(val.validate(document))

    def test_minmax(self):
        """test if the value is between given range
        """
        val = DwcaValidator(yaml.load(self.yaml_value),
                            error_handler=WhipErrorHandler)
        document = {'percentage': 9.}
        self.assertFalse(val.validate(document))
        document = {'percentage': 2.1}
        self.assertFalse(val.validate(document))

        val = DwcaValidator(yaml.load(self.yaml_value),
                            error_handler=WhipErrorHandler)
        document = {'individualCount': 9}
        self.assertFalse(val.validate(document))
        document = {'individualCount': 2}
        self.assertFalse(val.validate(document))

    def test_min_int_string(self):
        """test if the value has minimal value with string input
        """
        val = DwcaValidator(yaml.load(self.yaml_value),
                            error_handler=WhipErrorHandler)
        # provide error on type mismatch
        document = {'code': 'vijf'}
        val.validate(document)
        self.assertEqual(val.errors,
                         {'code': ["value 'vijf' is not numeric"]},
                         msg="alert on datatype mismatch for min "
                             "evaluation fails")

    def test_max_int_string(self):
        """test if the value has maximal value with string input
        """
        val = DwcaValidator(yaml.load(self.yaml_value),
                            error_handler=WhipErrorHandler)
        document = {'age_3': 'vijf'}  # provide error on type mismatch
        val.validate(document)
        self.assertEqual(val.errors,
                         {'age_3': ["value 'vijf' is not numeric"]},
                         msg="alert on datatype mismatch for max "
                             "evaluation fails")


class TestNumberFormatValidator(unittest.TestCase):

    def setUp(self):
        self.yaml_numberformat1 = """
                                    size:
                                        numberformat: '.5'
                                        required: False
                                    length:
                                        numberformat: '.3'
                                        required: False
                                    """

        self.yaml_numberformat2 = """
                                    size:
                                        numberformat: '3.5'
                                        required: False
                                    length:
                                        numberformat: '2.3'
                                        required: False
                                    """

        self.yaml_numberformat3 = """
                                    size:
                                        numberformat: '4.'
                                        required: False
                                    length:
                                        numberformat: '2.'
                                        required: False
                                    height:
                                        numberformat: '2'
                                        required: False
                                    """
        self.yaml_numberformat4 = """
                                    size:
                                        numberformat: '.'
                                    """
        self.yaml_numberformat5 = """
                                    size:
                                        numberformat: 'x'
                                    """

    def test_numberformat_right(self):
        val = DwcaValidator(yaml.load(self.yaml_numberformat1),
                            error_handler=WhipErrorHandler)
        document = {'size': '1110.14372'}  # True
        self.assertTrue(val.validate(document))
        document = {'size': '.14372'}  # True
        self.assertTrue(val.validate(document))
        document = {'size': '0.1437'}  # False
        self.assertFalse(val.validate(document))
        document = {'length': '.123'}  # True
        self.assertTrue(val.validate(document))
        document = {'length': '1.123'}  # True
        self.assertTrue(val.validate(document))
        document = {'length': '12.123'}  # True
        self.assertTrue(val.validate(document))
        document = {'length': '1.12'}  # False
        self.assertFalse(val.validate(document))
        document = {'length': '1.1234'}  # False
        self.assertFalse(val.validate(document))

    def test_numberformat_both(self):
        val = DwcaValidator(yaml.load(self.yaml_numberformat2),
                            error_handler=WhipErrorHandler)
        document = {'size': '123.14372'}  # True
        self.assertTrue(val.validate(document))
        document = {'size': '0.1437'}  # False
        self.assertFalse(val.validate(document))
        document = {'length': '12.123'}  # False
        self.assertTrue(val.validate(document))
        document = {'length': '1223'}  # False
        val.validate(document)
        self.assertEqual(val.errors,
                         {'length': ["numberformat of value '1223' not in "
                                     "agreement with '2.3'"]})

    def test_numberformat_left(self):
        val = DwcaValidator(yaml.load(self.yaml_numberformat3),
                            error_handler=WhipErrorHandler)
        document = {'size': '1234.14372'}  # True
        self.assertTrue(val.validate(document))
        document = {'size': '123.12'}  # False
        self.assertFalse(val.validate(document))
        document = {'length': '12'}  # True
        self.assertTrue(val.validate(document))
        document = {'length': '12.'}  # True
        self.assertTrue(val.validate(document))
        document = {'length': '12.1'}  # True
        self.assertTrue(val.validate(document))
        document = {'length': '123'}  # False
        self.assertFalse(val.validate(document))
        document = {'height': '12'}  # True
        self.assertTrue(val.validate(document))
        document = {'height': '.1'}  # False
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'height': ["value '.1' is not an integer"]})
        document = {'height': '12.1'}  # False
        self.assertFalse(val.validate(document))

    def test_numberformat_integer(self):
        val = DwcaValidator(yaml.load(self.yaml_numberformat3),
                            error_handler=WhipErrorHandler)
        document = {'size': '1234.'}  # True
        self.assertTrue(val.validate(document))
        document = {'size': '1234.55555'}  # True
        self.assertTrue(val.validate(document))
        document = {'size': '1234'}  # True
        self.assertTrue(val.validate(document))

    def test_numberformat_anyfloat(self):
        val = DwcaValidator(yaml.load(self.yaml_numberformat4),
                            error_handler=WhipErrorHandler)
        document = {'size': '1234.2222'}  # True
        self.assertTrue(val.validate(document))
        document = {'size': '0.2222'}  # True
        self.assertTrue(val.validate(document))
        document = {'size': '1234.'}  # True
        self.assertTrue(val.validate(document))
        document = {'size': '1'}  # False
        val.validate(document)
        self.assertEqual(val.errors,
                         {'size': ["value '1' is not a float"]})

    def test_numberformat_anyinteger(self):
        val = DwcaValidator(yaml.load(self.yaml_numberformat5),
                            error_handler=WhipErrorHandler)
        document = {'size': '1234'}  # True
        self.assertTrue(val.validate(document))
        document = {'size': '1'}  # True
        self.assertTrue(val.validate(document))
        document = {'size': '1234.'}  # False
        self.assertFalse(val.validate(document))
        document = {'size': '.'}  # False
        self.assertFalse(val.validate(document))
        document = {'size': '1.0'}  # False
        val.validate(document)
        self.assertEqual(val.errors,
                         {'size': ["value '1.0' is not an integer"]})

    def test_numberformat_isnumber(self):
        val = DwcaValidator(yaml.load(self.yaml_numberformat1),
                            error_handler=WhipErrorHandler)
        document = {'size': '1234f.'}  # Not a number
        val.validate(document)
        self.assertEqual(val.errors,
                         {'size': ["value '1234f.' is not numerical"]})
        document = {'length': 'a.abc'}  # False
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'length': ["value 'a.abc' is not numerical"]})
        document = {'length': ';'}  # False
        self.assertFalse(val.validate(document))

    def test_numberformat_negative(self):
        val = DwcaValidator(yaml.load(self.yaml_numberformat2),
                            error_handler=WhipErrorHandler)
        document = {'size': '-123.14372'}  # negative  float
        val.validate(document)
        self.assertTrue(val.validate(document))
        val = DwcaValidator(yaml.load(self.yaml_numberformat3),
                            error_handler=WhipErrorHandler)
        document = {'length': '-22'}  # negative int
        self.assertTrue(val.validate(document))
        document = {'length': '2-2'}  # negative int
        val.validate(document)
        self.assertEqual(val.errors,
                         {'length': ["value '2-2' is not numerical"]})


class TestDateValidator(unittest.TestCase):

    def setUp(self):
        self.yaml_string_date1 = """
                                 moment:
                                     mindate: 1830-01-01
                                     maxdate: 2014-10-20
                                     required: False
                                 date:
                                    mindate: 1985-11-29
                                    maxdate: 2012-09-12
                                    required: False
                                 """
        self.yaml_string_date2 = """
                                    moment:
                                        dateformat: ['%Y-%m-%d', '%Y-%m', '%Y']
                                        required: False
                                    date:
                                        dateformat: '%Y-%m-%d'
                                        required: False
                                    """
        self.yaml_string_date3 = """
                                    moment:
                                        dateformat: '%Y-%m'
                                    """
        self.yaml_string_date4 = """
                                 moment:
                                     maxdate: 2014-10-20
                                 date:
                                     maxdate: 2014-10-20
                                     mindate: 2000-10-20                                         
                                 """
        self.yaml_string_date5 = """
                                 moment:
                                     dateformat: '%Y-%m-%d/%Y-%m-%d'
                                     required: False
                                 date:
                                     dateformat: ['%Y-%m-%d/%Y-%m-%d']
                                     required: False
                                    
                                 """

    def test_daterange_iso(self):
        # isoformat
        val = DwcaValidator(yaml.load(self.yaml_string_date1),
                            error_handler=WhipErrorHandler)
        document1 = {'moment': '20110101'}  # True
        self.assertTrue(val.validate(document1))

    def test_daterange_line(self):
        # format with - inside range
        val = DwcaValidator(yaml.load(self.yaml_string_date1),
                            error_handler=WhipErrorHandler)
        document2 = {'moment': '2009-08-31'}  # True
        self.assertTrue(val.validate(document2))
        document2 = {'date': '1985-11-29'}  # True
        self.assertTrue(val.validate(document2))
        document2 = {'date': '2012-09-12'}  # True
        self.assertTrue(val.validate(document2))
        document2 = {'date': '2012-09-12'}  # True
        self.assertTrue(val.validate(document2))
        document2 = {'date': '1985-11-29'}  # True
        self.assertTrue(val.validate(document2))

    def test_daterange_out(self):
        # outside the range
        val = DwcaValidator(yaml.load(self.yaml_string_date1),
                            error_handler=WhipErrorHandler)
        document = {'moment': '17000101'}  # False
        self.assertFalse(val.validate(document))
        val = DwcaValidator(yaml.load(self.yaml_string_date1),
                            error_handler=WhipErrorHandler)
        document = {'moment': '20150831'}  # False
        self.assertFalse(val.validate(document))
        document = {'date': '1942-11-26'}  # False
        val.validate(document)
        self.assertEqual(val.errors,
                         {'date': ["date '1942-11-26' is before min "
                                   "limit '1985-11-29'"]})
        document = {'date': '2016-12-07'}  # False
        val.validate(document)
        self.assertEqual(val.errors,
                         {'date': ["date '2016-12-07' is after max "
                                   "limit '2012-09-12'"]})

    def test_daterange_nodate(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date4),
                            error_handler=WhipErrorHandler)
        document = {'moment': '1700101'}  # False
        val.validate(document)
        self.assertEqual(val.errors,
                         {'moment': [
                             "value '1700101' could not be interpreted as "
                             "date or datetime"]})

        document = {'date': '1700101'}  # False
        val.validate(document)
        self.assertEqual(val.errors,
                         {'date': [
                             "value '1700101' could not be interpreted as "
                             "date or datetime",
                             "value '1700101' could not be interpreted as "
                             "date or datetime"]})

    def test_dateformat_line(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date2),
                            error_handler=WhipErrorHandler)
        document = {'moment': '1997-01-05'}  # True
        self.assertTrue(val.validate(document))
        document = {'date': '2016-12-07'}  # True
        self.assertTrue(val.validate(document))
        document = {'date': '2016/12/07'}  # False
        self.assertFalse(val.validate(document))
        document = {'date': '07-12-2016'}  # False
        self.assertFalse(val.validate(document))
        document = {'date': '2016-12'}  # False
        self.assertFalse(val.validate(document))


    def test_dateformat_line_error(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date2),
                            error_handler=WhipErrorHandler)
        document = {'date': '2016-12-32'}  # False
        val.validate(document)
        self.assertEqual(val.errors, {'date': ["string format of value "
                                               "'2016-12-32' not compliant "
                                               "with '%Y-%m-%d'"]})

    def test_dateformat_day(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date2),
                            error_handler=WhipErrorHandler)
        document = {'moment': '1997-01'}  # True
        self.assertTrue(val.validate(document))
        document = {'moment': '2016-12'}  # True
        self.assertTrue(val.validate(document))
        document = {'moment': '2016'}  # True
        self.assertTrue(val.validate(document))
        document = {'moment': '2016-12-07'}  # True
        self.assertTrue(val.validate(document))

    def test_dateformat_multiple_wrong(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date2),
                            error_handler=WhipErrorHandler)
        document = {'moment': '19970105'}  # False
        self.assertFalse(val.validate(document))
        val.validate(document)
        self.assertEqual(val.errors,
                         {'moment': ["string format of value '19970105' not "
                                     "compliant with "
                                     "'['%Y-%m-%d', '%Y-%m', '%Y']'"]})

    def test_dateformat_single(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date3),
                            error_handler=WhipErrorHandler)
        document = {'moment': '1997-01'}  # True
        self.assertTrue(val.validate(document))

    def test_dateformat_period_valid(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date5),
                            error_handler=WhipErrorHandler)
        document = {'moment': '1997-02-01/2001-03-01'}  # True
        self.assertTrue(val.validate(document))
        document = {'date': '2016-01-01/2017-02-13'}  # True
        self.assertTrue(val.validate(document))

    def test_dateformat_period_invalid_first(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date5),
                            error_handler=WhipErrorHandler)
        document = {'moment': '1997-02/2001-03-01'}  # True
        self.assertFalse(val.validate(document))

    def test_dateformat_period_invalid_last(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date5),
                            error_handler=WhipErrorHandler)
        document = {'moment': '1997-02-01/03-01'}  # True
        self.assertFalse(val.validate(document))


class TestEmptyStringHandling(unittest.TestCase):
    """Test conversion from empty strings to None values before performing the
    evaluation and evaluate the default handling of empty strings and None
    values
    """

    def setUp(self):
        self.yaml_string = """
                           abundance:
                                minlength : 1
                                required: False
                           sex:
                                allowed: [male, female]
                                required: False
                           """

        self.empty1 = """
                        number:
                            empty: False
                            required: False
                        sex:
                            allowed: [male, female]
                            empty: False
                            required: False
                        """

        self.empty2 = """
                        number:
                            min: 2
                            empty: True
                            required: False
                        sex:
                            empty: True
                            allowed: [male, female]
                            required: False
                        """
        self.empty3 = """
                        field_1:
                            maxlength: 2
                            required: False
                        field_2:
                            maxlength: 0
                            required: False
                        field_3:
                          minlength: 0
                          required: False
                        field_4:
                          allowed: ''
                          required: False
                        field_5:
                          allowed: [male, female, '']
                          required: False
                        field_6:
                          regex: '^\s*$'
                          required: False
                        """
        self.empty4 = """
                        required_to_be_empty:
                            allowed: ''
                            empty: True
                        """

        self.empty5 = """
                        field_1:
                            min: 4
                            max: 2
                            numberformat: '.'
                            empty: False
                            required: False
                        field_2:
                            min: 4
                            max: 2
                            numberformat: '.'
                            empty: True    
                            required: False                 
                        """

    def test_default_error_empty_string(self):
        """empty string should provide an error by default
        """
        val = DwcaValidator(yaml.load(self.yaml_string),
                            error_handler=WhipErrorHandler)
        document = {'abundance': ''}
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'abundance': ['empty values not allowed']})
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))
        document = {'sex': 'female'}
        self.assertTrue(val.validate(document))
        document = {'sex': ''}
        self.assertFalse(val.validate(document))

    def test_default_handling_none(self):
        """None values are not allowed. Remark, in whip all inputs are
        string, so an incoming None is - normally - not possible
        """
        val = DwcaValidator(yaml.load(self.yaml_string),
                            error_handler=WhipErrorHandler)
        document = {'abundance': None}
        val.validate(document)
        self.assertEqual(val.errors,
                         {'abundance': ['null value not allowed']})

    def test_empty_notallowed(self):
        """empty string should provide an error when empty:False set"""
        val = DwcaValidator(yaml.load(self.empty1),
                            error_handler=WhipErrorHandler)
        document = {'number': ''}
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'number': ['empty values not allowed']})
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))
        document = {'sex': 'female'}
        self.assertTrue(val.validate(document))
        document = {'sex': ''}
        self.assertFalse(val.validate(document))

    def test_empty_allow_explicit(self):
        """specifically define the possibility of empty values"""
        val = DwcaValidator(yaml.load(self.empty2),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))
        document = {'sex': 'female'}
        self.assertTrue(val.validate(document))
        document = {'sex': ''}
        self.assertTrue(val.validate(document))

    def test_empty_other_context(self):
        """ following specifications will not accept empty values,
        even though you might intuitively think so:"""
        val = DwcaValidator(yaml.load(self.empty3),
                            error_handler=WhipErrorHandler)
        document = {'field_1': ''}
        self.assertFalse(val.validate(document))
        document = {'field_2': ''}
        self.assertFalse(val.validate(document))
        document = {'field_3': ''}
        self.assertFalse(val.validate(document))
        document = {'field_4': ''}
        self.assertFalse(val.validate(document))
        document = {'field_5': ''}
        self.assertFalse(val.validate(document))
        document = {'field_6': ''}
        self.assertFalse(val.validate(document))

    def test_empty_required_only(self):
        """only accept empty values (and nothing else) syntax"""
        val = DwcaValidator(yaml.load(self.empty4),
                            error_handler=WhipErrorHandler)
        document = {'required_to_be_empty': ''}
        self.assertTrue(val.validate(document))
        document = {'required_to_be_empty': 'tdwg'}
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'required_to_be_empty': ['unallowed value tdwg']})

    def test_empty_drop_remaining_rules(self):
        """cerberus does not drop all remaining rules after empty validation,
        pywhip does this. Testing with min/max (which is different)
        """
        val = DwcaValidator(yaml.load(self.empty5),
                            error_handler=WhipErrorHandler)
        document = {'field_1': '3'}
        val.validate(document)
        self.assertEqual(val.errors,
                         {'field_1': ['max value is 2', 'min value is 4',
                                      "value '3' is not a float"]})
        document = {'field_2': ''}
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
                                    """

        self.yaml_delimited5 = """
                                    sex:
                                        delimitedvalues:
                                            allowed: [male, female]
                                    """

        self.yaml_delimited6 = """
                                    sex:
                                        delimitedvalues:
                                            delimiter: " | "
                                            allowed: [male, female]
                                        empty: True
                                    """

        self.yaml_delimited7 = """
                                    sex:
                                        empty: True
                                        delimitedvalues:
                                            delimiter: " | "
                                    """

    def test_delimiter_doubles(self):
        val = DwcaValidator(yaml.load(self.yaml_delimited1),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male | female | male'} # False
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'sex': ['duplicate values in delimitedvalues']})

    def test_delimiter_single_occurence(self):
        """should be passed and just checked as such
        """
        val = DwcaValidator(yaml.load(self.yaml_delimited1),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male'}  # True
        self.assertTrue(val.validate(document))

    def test_delimiter_wrong_delimiter(self):
        """splitting is just not occuring, so warning will be on
        unallowed value
        """
        val = DwcaValidator(yaml.load(self.yaml_delimited1),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male ; female'}  # False, due to wrong endname
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'sex': [{0: ['unallowed value male ; female']}]})

    def test_delimiter_enddelim_not_allowed(self):
        """pipe too much which can not be split anymore
        """
        val = DwcaValidator(yaml.load(self.yaml_delimited1),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male | female |'}  # False
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'sex': [{1: ['unallowed value female |']}]})

    def test_delimiter_empty_not_allowed(self):
        """pipe too much which results in empty value
        """
        val = DwcaValidator(yaml.load(self.yaml_delimited1),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male | female | '}  # False (pipe too much)
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'sex': ['contains empty string inside '
                                  'delimitedvalues']})
        # regular empty value is default False
        document = {'sex': ''}
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'sex': ['empty values not allowed']})

    def test_delimiter_all_valid_options(self):
        """test the valid options produced by delimited syntax
        """
        val = DwcaValidator(yaml.load(self.yaml_delimited6),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))
        document = {'sex': 'female'}
        self.assertTrue(val.validate(document))
        document = {'sex': 'male | female'}
        self.assertTrue(val.validate(document))
        document = {'sex': 'female | male'}
        self.assertTrue(val.validate(document))
        document = {'sex': ''}
        self.assertTrue(val.validate(document))

    def test_delimiter_non_valid_options(self):
        """raise Error when no delimiter field added
        """
        val = DwcaValidator(yaml.load(self.yaml_delimited6),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male, female'}  # wrong delimiter
        self.assertFalse(val.validate(document))
        document = {'sex': 'male|female'}  # no spaces
        self.assertFalse(val.validate(document))
        document = {'sex': 'male | '}  # end delimiter without value
        self.assertFalse(val.validate(document))
        document = {'sex': 'male | | female'}
        self.assertFalse(val.validate(document))  # in field empty

    def test_delimiter_nest(self):
        val = DwcaValidator(yaml.load(self.yaml_delimited3),
                            error_handler=WhipErrorHandler)
        document = {'stage': '0.123 | 4.235'}  # True
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'stage': [{0: ['min value is 1.0']}]})

    def test_no_delimiter_error(self):
        """raise Error when no delimiter field added
        """
        val = DwcaValidator(yaml.load(self.yaml_delimited5),
                            error_handler=WhipErrorHandler)
        document = {'sex': 'male | female'}
        with self.assertRaises(ValueError):
            val.validate(document)

    def test_delimiter_if_condition_pass(self):
        val = DwcaValidator(yaml.load(self.yaml_delimited2),
                            error_handler=WhipErrorHandler)
        document = {'age': '5 | 18 | 19', 'lifestage': 'juvenile'}  # True
        self.assertTrue(val.validate(document))

    def test_delimiter_if_condition_nonpass(self):
        val = DwcaValidator(yaml.load(self.yaml_delimited2),
                            error_handler=WhipErrorHandler)
        document = {'age': '50 | 30 | 99', 'lifestage': 'juvenile'}  # True
        self.assertFalse(val.validate(document))

    def test_delimiter_if_condition_false_condition(self):
        val = DwcaValidator(yaml.load(self.yaml_delimited2),
                            error_handler=WhipErrorHandler)
        document = {'age': '50 | 30 | 99', 'lifestage': 'adult'}  # True
        self.assertTrue(val.validate(document))

    def test_delimiter_if_checkindication(self):
        val = DwcaValidator(yaml.load(self.yaml_delimited2),
                            error_handler=WhipErrorHandler)
        document = {'age': '5 | 32', 'lifestage': 'juvenile'}  # False
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'age': [{1: [{'if': ['max value is 20']}]}]})
        document = {'age': '50 | 32', 'lifestage': 'juvenile'}  # False
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'age': [{0: [{'if': ['max value is 20']}],
                                   1: [{'if': ['max value is 20']}]}]})

    def test_delimiter_default_non_empty(self):
        val = DwcaValidator(yaml.load(self.yaml_delimited7),
                            error_handler=WhipErrorHandler)
        document = {'sex': ''}  # True
        self.assertTrue(val.validate(document))
        document = {'sex': ' | '}  # False
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'sex': ['contains empty string inside '
                                  'delimitedvalues']})


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
                            allowed: [HumanObservation, Machine, Measurement]
                        """

        self.yaml_ifif = """
                            lifestage:
                                if:
                                    - age:
                                          min: 20
                                      allowed: [adult]
                                      maxlength: 6
                                    - age:
                                          max: 20
                                      minlength: 6
                                    - age:
                                          min: 20
                                      maxlength: 5
                            age:
                                numberformat: 'x'
                            """

        self.yaml_ifcombi = """
                            basisOfRecord:
                                empty: False
                                allowed: [HumanObservation, PreservedSpecimen]
                                if:
                                    collectionCode:
                                        empty: True
                                    allowed: [PreservedSpecimen]
                            collectionCode:
                                empty: True
                            """

        self.yaml_conditional_empty = """
                                        sex:
                                            empty: True
                                        lifestage:
                                            empty: True 
                                            if:
                                                - sex:
                                                      allowed: [male, female]
                                                  allowed: adult
                                                - sex:
                                                      allowed: ''
                                                      empty: True
                                                  allowed: ''
                                                  empty: True
                                        """

        self.yaml_pre_empty = """
                                sex:
                                    empty: True
                                lifestage:
                                    empty: True
                                    if:
                                        sex:
                                            allowed: [male]
                                        allowed: [adult]
                                """

        self.yaml_prepost_empty = """
                                sex:
                                    empty: True
                                lifestage:
                                    empty: True
                                    if:
                                        sex:
                                            allowed: [male]
                                        allowed: [adult]
                                        empty: True
                                """

    def test_if(self):
        schema = yaml.load(self.yaml_if)
        document = {'basisOfRecord': 'HumanObservation', 'type': 'Event'}
        val = DwcaValidator(schema, error_handler=WhipErrorHandler)
        self.assertTrue(val.validate(document))

    def test_ifnot(self):
        schema = yaml.load(self.yaml_if)
        document = {'basisOfRecord': 'HumanObservation', 'type': 'Measurement'}
        val = DwcaValidator(schema, error_handler=WhipErrorHandler)
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors, {'type': [{'if': ['unallowed value '
                                                       'Measurement']}]})

        # empty values by default not allowed
        document = {'basisOfRecord': 'Machine', 'type': ''}
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors, {'type': ['empty values not allowed']})

    def test_multiple_if_error(self):
        """term trespasses both if clauses at the same time
        """
        schema = yaml.load(self.yaml_ifif)
        document = {'age': '21', 'lifestage': 'juvenile'}
        val = DwcaValidator(schema, error_handler=WhipErrorHandler)
        val.validate(document)
        self.assertEqual(val.errors,
                         {'lifestage': [{'if_0': ['unallowed value juvenile',
                                                  'max length is 6'],
                                        'if_2': ['max length is 5']}]})

    def test_multiple_if_pass(self):
        """document satisfies both if clauses at the same time
        """
        schema = yaml.load(self.yaml_ifif)
        val = DwcaValidator(schema, error_handler=WhipErrorHandler)
        document = {'age': '21', 'lifestage': 'adult'}  # True
        self.assertTrue(val.validate(document))

        document = {'age': '2', 'lifestage': 'juvenile'}  # True
        val = DwcaValidator(schema, error_handler=WhipErrorHandler)
        self.assertTrue(val.validate(document))

    def test_multiple_if_combi(self):
        """document satisfies if and non-if clauses
        """
        schema = yaml.load(self.yaml_ifcombi)
        document = {'basisOfRecord': 'PreservedSpecimen', 'collectionCode': ''}
        val = DwcaValidator(schema, error_handler=WhipErrorHandler)
        self.assertTrue(val.validate(document))

    def test_multiple_if_combi_nonpass(self):
        """document satisfies if and non-if clauses
        """
        schema = yaml.load(self.yaml_ifcombi)
        document = {'basisOfRecord': 'HumanObservation', 'collectionCode': ''}
        val = DwcaValidator(schema, error_handler=WhipErrorHandler)
        val.validate(document)
        self.assertEqual(val.errors,
                         {'basisOfRecord': [{'if': ['unallowed value '
                                                    'HumanObservation']}]})

    def test_conditional_empty(self):
        schema = yaml.load(self.yaml_conditional_empty)
        val = DwcaValidator(schema, error_handler=WhipErrorHandler)
        document = {'lifestage': 'adult', 'sex': 'male'}
        self.assertTrue(val.validate(document))
        document = {'lifestage': 'adult', 'sex': 'female'}
        self.assertTrue(val.validate(document))
        document = {'lifestage': 'adul', 'sex': 'male'}
        self.assertFalse(val.validate(document))
        document = {'lifestage': '', 'sex': 'male'}
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'lifestage': [{'if_0': ['empty values not allowed']}]})
        document = {'lifestage': 'adult', 'sex': ''}
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'lifestage': [{'if_1': ['unallowed value adult']}]})
        document = {'lifestage': '', 'sex': ''}
        self.assertTrue(val.validate(document))
        self.assertEqual(val.errors, {})

    def test_pre_empty(self):
        schema = yaml.load(self.yaml_pre_empty)
        val = DwcaValidator(schema, error_handler=WhipErrorHandler)
        document = {'lifestage': 'adult', 'sex': 'male'}
        self.assertTrue(val.validate(document))  # should be True
        document = {'lifestage': 'juvenile', 'sex': 'male'}
        self.assertFalse(val.validate(document))  # should be False
        document = {'lifestage': '', 'sex': ''}
        self.assertTrue(val.validate(document))  # should be True

        # if statement overrules the empty
        document = {'lifestage': '', 'sex': 'male'}
        self.assertFalse(val.validate(document))  # should be False
        self.assertEqual(val.errors,
                         {'lifestage': [{'if': ['empty values not allowed']}]})

        # additional empty: True inside the if statement enables empty there
        schema = yaml.load(self.yaml_prepost_empty)
        val = DwcaValidator(schema, error_handler=WhipErrorHandler)
        document = {'lifestage': '', 'sex': 'male'}
        self.assertTrue(val.validate(document))  # should be True


class TestRequiredValidator(unittest.TestCase):

    def setUp(self):

        self.yaml_single_term = """
                                abundance:
                                    allowed: many                          
                                """

        self.yaml_multiple_term = """
                                  abundance:
                                    allowed: many
                                  eventDate:
                                    dateformat: '%Y-%m-%d'  
                                    required: True                  
                                  """

        self.yaml_presence_check = """
                                   abundance:
                                     empty: True                   
                                   """

        self.yaml_presence_inside_if = """
                                        coordinateUncertaintyInMeters:
                                          empty: true
                                          if:
                                            - verbatimCoordinateSystem:
                                                allowed: UTM 1km
                                              numberformat: x
                                              allowed: '707'
                                            - verbatimCoordinateSystem:
                                                allowed: UTM 5km
                                              numberformat: x
                                              allowed: '3536'
                                        """

    def test_allow_unknown_argument(self):
        """by providing the allow_unkown argument, not-mentioned fields are
         allowed or not in the document"""
        schema = yaml.load(self.yaml_single_term)

        val = DwcaValidator(schema, allow_unknown=True,
                            error_handler=WhipErrorHandler)
        document = {'abundance': 'many', 'eventDate': '2018-01-01'}
        self.assertTrue(val.validate(document))

        val = DwcaValidator(schema, allow_unknown=False,
                            error_handler=WhipErrorHandler)
        document = {'abundance': 'many', 'eventDate': '2018-01-01'}
        val.validate(document)
        self.assertEqual(val.errors, {'eventDate': ['unknown field']})

    def test_required_term(self):
        """ by default, all listed terms are required"""
        schema = yaml.load(self.yaml_multiple_term)

        val = DwcaValidator(schema, error_handler=WhipErrorHandler)
        document = {'abundance': 'many'}
        val.validate(document)
        self.assertEqual(val.errors, {'eventDate': ['required field']})

    def test_default_required(self):
        """ the handling of required specification is handled on data set
        level, so the individual specification is not using required as a
        rule

        Still, requried can be added to have the errors explicitly taken into
        row-evaluation.
        """
        schema = yaml.load(self.yaml_multiple_term)
        val = DwcaValidator(schema, error_handler=WhipErrorHandler)

        document = {'abundance': 'many'}
        val.validate(document)
        self.assertEqual(val.errors, {'eventDate': ['required field']})

        document = {'eventDate': '2018-01-01'}
        val.validate(document)
        self.assertEqual(val.errors, {})

    def test_check_presence_only(self):
        """A minimal check on the presence of a specific column can be
        achieved by adding the term and the specification of empty: True"""
        schema = yaml.load(self.yaml_presence_check)
        val = DwcaValidator(schema, allow_unknown=True,
                            error_handler=WhipErrorHandler)

        document = {'abundance': 'many'}
        self.assertTrue(val.validate(document))
        document = {'abundance': ''}
        self.assertTrue(val.validate(document))
        document = {'eventDate': ''}
        val.validate(document)
        self.assertEqual(val.errors, {})

    def test_check_presence_on_if(self):
        """When a field is mentioned inside an if condition, the condition
        can not be checked. Warning is provided in the general whip-environment
        as a preliminar check, here the if-statements are not executed
        (no errors generated)"""

        schema = yaml.load(self.yaml_presence_inside_if)
        val = DwcaValidator(schema, error_handler=WhipErrorHandler)

        document = {'coordinateUncertaintyInMeters': '22'}
        val.validate(document)
        self.assertEqual(val.errors, {})



