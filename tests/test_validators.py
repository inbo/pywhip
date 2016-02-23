# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 15:46:18 2016

@author: stijn_vanhoey
"""

import yaml
import unittest

from dwcavalidator.validators import DwcaValidator

class TestDateValidators(unittest.TestCase):

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
        document1 = {'moment' : '20110101'}
        self.assertTrue(val.validate(document1))

    def test_daterange_line(self):
        # format with - inside range
        val =  DwcaValidator(yaml.load(self.yaml_string_date1))
        document2 = {'moment' : '2009-08-31'}
        self.assertTrue(val.validate(document2))

    def test_daterange_out(self):
        # outside the range
        val =  DwcaValidator(yaml.load(self.yaml_string_date1))
        document3 = {'moment' : '20150831'}
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
        document = {'moment' : '1997-01'} # False
        self.assertTrue(val.validate(document))

class TestDataTypes(unittest.TestCase):

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

    def test_uri_type(self):
        document = {'location': "https://github.com/LifeWatchINBO/dwca-validator"}
        schema = {'location':{'type':'uri'}}
        val = DwcaValidator(schema)
        self.assertTrue(val.validate(document))

    def test_wrong_uri_type(self):
        document = {'location': "https/github.com/LifeWatchINBO/dwca-validator"}
        schema = {'location':{'type':'uri'}}
        val = DwcaValidator(schema)
        self.assertFalse(val.validate(document))