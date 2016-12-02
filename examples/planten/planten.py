# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 12:44:05 2016

@author: stijn_vanhoey
"""

from dwcavalidator.collect import DwcaScreening


planten = DwcaScreening('./dwc-occurrence.yaml',
                        lowercase_terms=True)
planten.screen_dwc('./planten-natuurpunt-occurrences.tsv',
                   delimiter='\t', maxentries=10)

print(planten.errors)
print(planten.list_error_types())

