# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 15:12:07 2016

@author: stijn_vanhoey
"""

from dwca.darwincore.utils import qualname as qn

class LogAnomaliaDWCA(object):
    def __init__(self):
        self.log = {}

    def _add_failure(self, row, term):
        """add the row id to the specific term
        """
        if term in self.log.keys():
            self.log[term] = self.log[term].append(row.id)
        else:
            self.log[term] = [row.id]

    # EQUAL TO
    def _term_check_equal(self, row, term, value):
        """test if a specific term is equal to the provided value, log row id
        if not equal
        """
        if not row.data[qn(term)]  == value:
            self._add_failure(row, term)

    def check_institutionCode(self, row, institutionCode='INBO'):
        self._term_check_equal(row, 'institutionCode', institutionCode)

    def check_language(self, row, language='en'):
        self._term_check_equal(row, 'language', language)

    def check_license(self, row,
            licenze='http://creativecommons.org/publicdomain/zero/1.0/'):
        self._term_check_equal(row, 'license', licenze)

    def check_rightsHolder(self, row, rightsHolder='INBO'):
        self._term_check_equal(row, 'rightsHolder', rightsHolder)

    def check_accessRights(self, row,
            accessRights='http://www.inbo.be/en/norms-for-data-use'):
        self._term_check_equal(row, 'accessRights', accessRights)

    def check_continent(self, row, continent='Europe'):
        self._term_check_equal(row, 'continent', continent)

    def check_geodeticDatum(self, row, geodeticDatum='WGS84'):
        self._term_check_equal(row, 'geodeticDatum', geodeticDatum)

    # EQUAL TO OPTION
    def _term_check_equal_options(self, row, term, values):
        """test if a specific term is equal to one of the provided options in
        a list
        """
        if not row.data[qn(term)]  in values:
            self._add_failure(row, term)

    def check_nomenclaturalCode(self, row, nomenclaturalCode=['ICZN','ICBN']):
        self._term_check_equal(row, 'nomenclaturalCode', nomenclaturalCode)

    def check_verbatimSRS(self, row, verbatimSRS=['Belgian Datum 1972',
                                                  'ED50', 'WGS84']):
        self._term_check_equal(row, 'verbatimSRS', verbatimSRS)

