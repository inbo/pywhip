# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 11:07:56 2016

@author: stijn_vanhoey
"""

import unittest
import pytest

import yaml

from pywhip.validators import DwcaValidator


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
    def test_nested_coerce_of_rules(self):
        """type statements can NOT be inside the *of rules
        cfr. https://github.com/nicolaiarocci/cerberus/issues/230
        """
        schema  ="""
                decimalLatitude:
                    oneof :
                        - allowed : [10]
                        - min : 3.
                          type : 'float'
                 """
        val = DwcaValidator(yaml.load(schema))
        document = {'decimalLatitude': '4'}
        self.assertFalse(val.validate(document))

    def test_nested_coerce_if(self):
        """type statements can be in if structure
        TODO
        """
        return None

    def test_nested_coerce_delimited(self):
        """type statements can be in delimited values structure
        TODO
        """
        return None


class TestAllowedExtension(unittest.TestCase):
    """Test the usage of string as input for allowed values
    """
    def setUp(self):
        self.yaml_string = """
                           abundance:
                               allowed: [many]
                           sex:
                               allowed: [male, female]
                           """
    def test_allow_string(self):
        """usage of string in allowed statement
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'abundance': 'many'}
        self.assertTrue(val.validate(document))

    def test_allow_list(self):
        """usage of list in allowed statement
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))


class TestEmptyStringHandling(unittest.TestCase):
    """Test conversion from empty strings to None values before performing the
    evaluation and evaluate the default handling of empty strings and None
    values
    """

    def setUp(self):
        self.yaml_string = """
                           abundance:
                                type : float
                           """

        self.empty1 = """
                        number:
                            min: 2
                            empty: False
                            type: integer
                        """

        self.empty2 = """
                        number:
                            min: 2
                            empty: True
                            type: integer
                        """

    def test_empty_string(self):
        """conversion empty string to None in document
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'abundance': ''}
        val.validate(document)
        self.assertEqual(val.document,
                    {'abundance': None},
                    msg="pre-conversion of empty strings to None not supported")

    def test_default_error_empty_string(self):
        """empty string (converted to None values) should provide an error
        by default
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'abundance': ''}
        self.assertFalse(val.validate(document))

    def test_default_ignore_none(self):
        """None values are just ignored by default
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'abundance': None}
        self.assertTrue(val.validate(document))

    def test_empty_notallowed(self):
        document = {'number': ''}
        val = DwcaValidator(yaml.load(self.empty1))
        self.assertFalse(val.validate(document))
        self.assertEqual(val.errors,
                         {'number': ['empty values not allowed']})

    def test_empty_allow_explicit(self):
        document = {'number': ''}
        val = DwcaValidator(yaml.load(self.empty2))
        self.assertTrue(val.validate(document))
