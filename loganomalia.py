# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 15:12:07 2016

@author: stijn_vanhoey
"""

from dwca.darwincore.utils import qualname as qn

class LogAnomaliaDWCA(object):
    def __init__(self):
        self.log = {}

    def _check_if_new_failure(self):
        """check if the failure is different from the previous failures for
        this term-test combination; if so, store the value
        """


    def _add_failure(self, row, term):
        """add the row id to the specific term
        """
        if term in self.log.keys():
            # TODO prevent from endless list when single mistake in all rows??
            self.log[term].append(row.id)
        else:
            self.log[term] = [row.id]

    # EQUAL TO
    def check_equal(self, row, term, value):
        """test if a specific term is equal to the provided value, log row id
        if not equal
        """
        if not row.data[qn(term)]  == value:
            self._add_failure(row, term)

    # EQUAL TO OPTION
    def check_equal_options(self, row, term, values):
        """test if a specific term is equal to one of the provided options in
        a list
        """
        if not row.data[qn(term)]  in values:
            self._add_failure(row, term)