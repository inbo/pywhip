# -*- coding: utf-8 -*-
"""
Created on Fri Feb  5 15:12:07 2016

@author: stijn_vanhoey
"""

from dwca.darwincore.utils import qualname as qn

class LogAnomaliaDWCA(object):
    def __init__(self):
        self.log = {}

    def _setup_termtest_dict(self):
        """create empty dictionary of the format:
            {"ids":[], "sample":[]}
        """
        return {"ids":[], "sample":[]}

    def _check_if_new_failure(self, row, term, test):
        """check if the failure is different from the previous failures for
        this term-test combination; if so, store the value
        """
        return row.data[qn(term)] in self.log[term][test]["sample"]

    def _add_failure(self, row, term, test):
        """add the row id to the specific term
        """
        if term in self.log.keys():
            if not test in self.log[term].keys():
                self.log[term][test] = {test : self._setup_termtest_dict()}

        else:
            self.log[term] = {test : self._setup_termtest_dict()}

        self.log[term][test]["ids"].append(row.id)
        if not self._check_if_new_failure(row, term, test):
            self.log[term][test]["sample"].append(row.data[qn(term)])

    # EQUAL TO
    def check_equal(self, row, term, value):
        """test if a specific term is equal to the provided value, log row id
        if not equal
        """
        if not row.data[qn(term)]  == value:
            self._add_failure(row, term, 'Equal')

    # EQUAL TO OPTION
    def check_equal_options(self, row, term, values):
        """test if a specific term is equal to one of the provided options in
        a list
        """
        if not row.data[qn(term)]  in values:
            self._add_failure(row, term, 'EqualList')