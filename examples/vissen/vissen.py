# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 12:44:05 2016

@author: stijn_vanhoey
"""

from dwcavalidator.collect import DwcaScreening

vissen = DwcaScreening('./dwc-occurrence.yaml', lowercase_terms=True)
vissen.screen_dwc('./vissen-natuurpunt-occurrences.tsv',
                  delimiter='\t', maxentries=500)

print(vissen.errors)
print(vissen.list_error_types())

