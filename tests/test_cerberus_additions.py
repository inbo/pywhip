# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 11:07:56 2016

@author: stijn_vanhoey
"""

import unittest

import yaml

from dwcavalidator.validators import DwcaValidator

class TestCoerceAddition(unittest.TestCase):
    """
    The validator adapts the provided schema with additional coerce statements
    when a datatype of integer or float is required. Since the DWCA reader is
    providing str for each of the values in the document, this
    pre-interpretation towards the tested datatype is required.
    """

    def setUp(self):

        self.yaml_string = """
                           decimalLatitude:
                               type : float
                           individualCount:
                               type : integer
                           percentage:
                                type : number
                           abundance:
                                type : boolean
                           """

    def test_float_usage(self):
        """see if the coerce is active, leading to correct dtype interpretation
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'decimalLatitude' : '51.55'}
        self.assertTrue(val.validate(document))

    def test_float_usage_coerce_fail(self):
        """if failing this, the coerce addition failed to work
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'decimalLatitude' : '51.55'}
        val.validate(document)
        self.assertNotEqual(val.errors,
                            {'decimalLatitude': 'must be of float type'},
                            msg="addition of coerce to pre-interpret datatype float is failing")

    def test_int_usage(self):
        """see if the coerce is active, leading to correct dtype interpretation
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'individualCount': u'1'}
        self.assertTrue(val.validate(document))

    def test_int_already(self):
        """see if the coerce is active, leading to correct dtype interpretation
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'individualCount': 2}
        self.assertTrue(val.validate(document))

    def test_int_usage_coerce_fail(self):
        """if failing this, the coerce addition failed to work
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'individualCount': u'1'}
        val.validate(document)
        self.assertNotEqual(val.errors,
                            {'individualCount': 'must be of integer type'},
                            msg="addition of coerce to pre-interpret datatype integer is failing")

    def test_number_usage(self):
        """see if the coerce is active, leading to correct dtype interpretation
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'percentage': u'1.2'}
        self.assertTrue(val.validate(document))

    def test_no_number_usage(self):
        """check the error statement providing info about datatype when coerce
        not possible
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'percentage': u'tien'}
        val.validate(document)
        self.assertIn('must be of number type', val.errors['percentage'])

    def test_boolean_usage(self):
        """see if the coerce is active, leading to correct dtype interpretation
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'abundance': u'true'}
        self.assertTrue(val.validate(document))

    def test_bool_usage_coerce_fail(self):
        """if failing this, the coerce addition failed to work
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'abundance': u'true'}
        val.validate(document)
        self.assertNotEqual(val.errors,
                            {'abundance': 'must be of boolean type'},
                            msg="addition of coerce to pre-interpret datatype boolean is failing")