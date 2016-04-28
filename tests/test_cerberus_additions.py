# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 11:07:56 2016

@author: stijn_vanhoey
"""

import yaml
import unittest

from dwcavalidator.validators import DwcaValidator

class TestCoerceAddition(unittest.TestCase):

    def setUp(self):

        self.yaml_string  ="""
                        decimalLatitude:
                            type : float
                            max : 51.51
                        individualCount:
                            type : integer
                            min : 2
                 """

    def test_float_usage(self):
        val =  DwcaValidator(yaml.load(self.yaml_string))
        document = {'decimalLatitude' : '51.55'}
        val.validate(document)
        self.assertEqual(val.errors, {'decimalLatitude': 'max value is 51.51'})

    def test_int_usage(self):
        val =  DwcaValidator(yaml.load(self.yaml_string))
        document = {'individualCount': u'1'}
        val.validate(document)
        self.assertEqual(val.errors, {'individualCount': 'min value is 2'})

    def test_int_result(self):
        val =  DwcaValidator(yaml.load(self.yaml_string))
        document = {'individualCount': u'5'}
        self.assertTrue(val.validate(document))