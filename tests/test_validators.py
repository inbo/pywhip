# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 15:46:18 2016

@author: stijn_vanhoey

# using nosetests...
"""

import yaml
import unittest
from datetime import datetime

from dwcavalidator.validators import DwcaValidator

class TestDateValidator(unittest.TestCase):

    def setUp(self):
        self.yaml_string_date1 = """
                                    moment:
                                        daterange: [1830-01-01, 2014-10-20]
                                    """
        self.yaml_string_date2 = """
                                    moment:
                                        dateformat: ['%Y-%m-%d', '%Y-%m', '%Y']
                                    """
        self.yaml_string_date3 = """
                                    moment:
                                        dateformat: '%Y-%m'
                                    """

    def test_daterange_iso(self):
        # isoformat
        val =  DwcaValidator(yaml.load(self.yaml_string_date1))
        document1 = {'moment' : '20110101'}  #True
        self.assertTrue(val.validate(document1))

    def test_daterange_line(self):
        # format with - inside range
        val =  DwcaValidator(yaml.load(self.yaml_string_date1))
        document2 = {'moment' : '2009-08-31'} # True
        self.assertTrue(val.validate(document2))

    def test_daterange_out(self):
        # outside the range
        val =  DwcaValidator(yaml.load(self.yaml_string_date1))
        document3 = {'moment' : '20150831'} # False
        self.assertFalse(val.validate(document3))

    def test_dateformat_line(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date2))
        document = {'moment' : '1997-01-05'} # True
        self.assertTrue(val.validate(document))

    def test_dateformat_day(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date2))
        document = {'moment' : '1997-01'} # True
        self.assertTrue(val.validate(document))

    def test_dateformat_multiple_wrong(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date2))
        document = {'moment' : '19970105'} # False
        self.assertFalse(val.validate(document))

    def test_dateformat_single(self):
        val = DwcaValidator(yaml.load(self.yaml_string_date3))
        document = {'moment' : '1997-01'} # True
        self.assertTrue(val.validate(document))


#class TestNumberFormatValidator(unittest.TestCase):
#
#    def setUp(self):
#        self.yaml_numberformat1 = """
#                                    size:
#                                        numberformat: ".5f"
#                                    """
#
#        self.yaml_numberformat2 = """
#                                    age:
#                                        numberformat: "d"
#                                    """
#
#    def test_numberformat_float(self):
#        val = DwcaValidator(yaml.load(self.yaml_numberformat1))
#        document = {'size' : '0.14372'} # True
#        self.assertTrue(val.validate(document))
#
#    def test_numberformat_integer_as_integer(self):
#        val = DwcaValidator(yaml.load(self.yaml_numberformat2))
#        document = {'age' : '2'} # True
#        self.assertTrue(val.validate(document))
#
#    def test_numberformat_integer_as_float(self):
#        val = DwcaValidator(yaml.load(self.yaml_numberformat2))
#        document = {'age' : '2.2'} # False
#        self.assertFalse(val.validate(document))


#class TestDelimitedValuesValidator(unittest.TestCase):
#
#    def setUp(self):
#        self.yaml_delimited1 = """
#                                    sex:
#                                        delimitedvalues:
#                                            delimiter: " | "
#                                    """
#
#        self.yaml_delimited2 = """
#                                    age:
#                                        delimitedvalues:
#                                            delimiter: " | "
#                                            if:
#                                                lifestage:
#                                                    allowed: juvenile
#                                                max: 20
#                                    """
#
#        self.yaml_delimited3 = """
#                                    stage:
#                                        delimitedvalues:
#                                            delimiter: " | "
#                                            min: 1.
#                                            max: 8
#                                            numberformat: .3f
#                                    """
#
#        self.yaml_delimited4 = """
#                                    sex:
#                                        delimitedvalues:
#                                            delimiter: " | "
#                                            listvalues
#                                    """
#
#        self.yaml_delimited5 = """
#                                    sex:
#                                        delimitedvalues:
#                                            delimiter: " | "
#                                            empty: false
#                                    """
#
#    def test_delimiter_valid(self):
#        val = DwcaValidator(yaml.load(self.yaml_delimited1))
#        document = {'sex' : 'male | female | male'} # True
#        self.assertTrue(val.validate(document))
#
#    def test_delimiter_single_occurence(self):
#        val = DwcaValidator(yaml.load(self.yaml_delimited1))
#        document = {'sex' : 'male'} # True
#        self.assertTrue(val.validate(document))
#
#    def test_delimiter_wrong_delimiter(self):
#        val = DwcaValidator(yaml.load(self.yaml_delimited1))
#        document = {'sex' : 'male ; female'} # False
#        self.assertFalse(val.validate(document))
#
#    def test_delimiter_if_condition_pass(self):
#        val = DwcaValidator(yaml.load(self.yaml_delimited2))
#        document = {'ages' : '5 | 18 | 19', 'lifestage':'juvenile'} # True
#        self.assertTrue(val.validate(document))
#
#    def test_delimiter_if_condition_nonpass(self):
#        val = DwcaValidator(yaml.load(self.yaml_delimited2))
#        document = {'ages' : '5 | 18 | 99', 'lifestage':'adult'} # True
#        self.assertTrue(val.validate(document))
#
#    def test_delimiter_if_checkindication(self):
#        val = DwcaValidator(yaml.load(self.yaml_delimited2))
#        document = {'ages' : '5 | 32', 'lifestage':'juvenile'} # False
#        self.assertFalse(val.validate(document))
#
#    def test_delimiter_nest(self):
#        val = DwcaValidator(yaml.load(self.yaml_delimited3))
#        document = {'sex' : 'male | female | male'} # True
#        self.assertTrue(val.validate(document))
#
#    def test_delimiter_empty_not_allowed(self):
#        val = DwcaValidator(yaml.load(self.yaml_delimited5))
#        document = {'sex' : 'male | female |'} # False (pipe too much)
#        self.assertFalse(val.validate(document))
#
##    def test_delimiter_enlist(self):
##        """combine the listvalues within the delimitedvalues
##        """
##        #to check how enlist well be handled... (let op unieke enkel behouden)

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

    def setUp(self):
        self.yaml_required = """
                             sex:
                                 required: False
                             moment:
                                 required: True
                             """

    def test_required(self):
        """test if a field (key) is present
        """
        val = DwcaValidator(yaml.load(self.yaml_required))
        document = {'moment' : '2016-12-11'}
        self.assertTrue(val.validate(document))

        document = {'sex' : '2016-12-11'}
        self.assertFalse(val.validate(document))




