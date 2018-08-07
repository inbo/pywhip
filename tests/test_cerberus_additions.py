# -*- coding: utf-8 -*-
"""
Created on Thu Apr 28 11:07:56 2016

@author: stijn_vanhoey
"""

import unittest
import pytest

import yaml

from pywhip.validators import DwcaValidator


class TestEmptyStringHandling(unittest.TestCase):
    """Test conversion from empty strings to None values before performing the
    evaluation and evaluate the default handling of empty strings and None
    values
    """

    def setUp(self):
        self.yaml_string = """
                           abundance:
                                type : float
                           sex:
                                allowed: [male, female]
                           """

        self.empty1 = """
                        number:
                            min: 2
                            empty: False
                            type: integer
                        sex:
                            allowed: [male, female]
                            empty: False
                        """

        self.empty2 = """
                        number:
                            min: 2
                            empty: True
                            type: integer
                        sex:
                            empty: True
                            allowed: [male, female]
                        """
        self.empty3 = """
                        field_1:
                            maxlength: 2
                        field_2:
                            maxlength: 0
                        field_3:
                          minlength: 0
                        field_4:
                          allowed: ''
                        field_5:
                          allowed: [male, female, '']
                        field_6:
                          regex: '^\s*$'
                        """
        self.empty4 = """
                        required_to_be_empty:
                            allowed: ''
                            empty: True
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
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))
        document = {'sex': 'female'}
        self.assertTrue(val.validate(document))
        document = {'sex': ''}
        self.assertFalse(val.validate(document))

    def test_default_ignore_none(self):
        """None values are just ignored by default
        """
        val = DwcaValidator(yaml.load(self.yaml_string))
        document = {'abundance': None}
        self.assertTrue(val.validate(document))

    def test_empty_notallowed(self):
        """empty string should provide an error when empty:False set"""
        document = {'number': ''}
        val = DwcaValidator(yaml.load(self.empty1))
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
        document = {'number': ''}
        val = DwcaValidator(yaml.load(self.empty2))
        self.assertTrue(val.validate(document))
        document = {'sex': 'male'}
        self.assertTrue(val.validate(document))
        document = {'sex': 'female'}
        self.assertTrue(val.validate(document))
        document = {'sex': ''}
        self.assertTrue(val.validate(document))

    def test_empty_other_context(self):
        """ following specifications will not accept empty values,
        even though you might intuitively think so:"""
        val = DwcaValidator(yaml.load(self.empty3))
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
        val = DwcaValidator(yaml.load(self.empty4))
        document = {'required_to_be_empty': ''}
        self.assertTrue(val.validate(document))
        document = {'required_to_be_empty': 'tdwg'}
        self.assertFalse(val.validate(document))
