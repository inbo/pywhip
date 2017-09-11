# -*- coding: utf-8 -*-
"""
Created on Wed May 18 11:08:55 2016

@author: stijn_vanhoey
"""

import csv
import yaml

from collections import defaultdict

#import pandas as pd

from pywhip.validators import DwcaValidator
from dwca.read import DwCAReader


def normalize_list(messages):
    """"""
    normalized = []
    for message in messages:
        if isinstance(message, str):
            normalized.append(message)
        elif isinstance(message, dict):
            for value in message.values():
                normalized += normalize_list(value)
        else:
            NotImplemented
    return normalized


class DwcaScreening(object):

    def __init__(self, schema,
                 lowercase_terms=False,
                 unknown_fields=True):

        if isinstance(schema, str):
            schema = yaml.load(open(schema))

        if lowercase_terms:
            self.schema = self._decapitalize_schema(schema)
        else:
            self.schema = schema

        # setup a DwcaValidator instance
        self.validation = DwcaValidator(self.schema)
        self.validation.allow_unknown = unknown_fields

        self.errors = {}
        self._errorlog = defaultdict(lambda: defaultdict(list))

    @staticmethod
    def _decapitalize_schema(schema):
        """remove capitalize form"""
        lowercase_schema = {}
        for dwcterm, specification in schema.items():
            lowercase_schema[dwcterm.lower()] = specification
        return lowercase_schema

    def _isitgreat(self):
        """chekck if there are any errors recorded"""
        if len(self.errors) == 0:
            print("Hooray, your data set is according to the guidelines!")
        else:
            print('Dataset does not comply the specifications, check errors'
                  ' for a more detailed information.')

    def screen_dwca(self, dwca_zip, maxentries=None):
        """"""
        with DwCAReader(dwca_zip) as dwca:
            for j, row in enumerate(dwca):
                document = {k.split('/')[-1]: v for k, v in row.data.items()}

                # validate each row and log the errors for each row
                self.validation.validate(document)
                if len(self.validation.errors) > 0:
                    self.errors[j+1] = self.validation.errors
                if maxentries:
                    if j >= maxentries-1:
                        break
        self._error_list_ids()
        self._isitgreat()

    def screen_dwc(self, dwc_csv, delimiter, maxentries=None):
        """"""
        with open(dwc_csv, "r") as dwc:
            reader = csv.DictReader(dwc, delimiter=delimiter)
            for j, document in enumerate(reader):
                self.validation.validate(document)
                if len(self.validation.errors) > 0:
                    self.errors[j+1] = self.validation.errors
                if maxentries:
                    if j >= maxentries-1:
                        break

        self._error_list_ids()
        self._isitgreat()

    def _error_list_ids(self):
        """"""

        for ids, errordict in self.errors.items():
            for term, errormessage in errordict.items():
                if isinstance(errormessage, list):
                    errormessage = normalize_list(errormessage)
                    for error in errormessage:
                        self._errorlog[term][error].append(ids)

    @staticmethod
    def _get_list_items(value):
        """"""
        if isinstance(value, list):
            return value[0]
        else:
            return value

    def export_table(self, filename=None):
        """"""
        NotImplemented

        """
        errors_table = pd.DataFrame(self.errors).transpose()\
            .applymap(self._get_list_items)

        if len(errors_table) == 0:
            print("No report generated. No worries, your data set is "
                  "according to the guidelines!")
        if filename:
            errors_table.to_csv(filename)
        else:
            return errors_table
        """

    def list_error_types(self):
        """"""
        error_types = []
        for terms, errors in self._errorlog.items():
            error_types += [error for error in errors.keys()]
        return error_types