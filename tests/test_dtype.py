# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 15:46:18 2016

@author: stijn_vanhoey
"""

import unittest

from dwcavalidator.validators import DwcaValidator

class TestDataTypes(unittest.TestCase):

    def test_json_type(self):
        document = {'size' : 'large',
                    'perimeter': """
                                    {"top": 3, "centre": 5, "bottom": 6}
                                    """}
        schema = {'perimeter':{'type':'json'}}
        val = DwcaValidator(schema)
        val.allow_unknown = True
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