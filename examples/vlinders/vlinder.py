# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 12:44:05 2016

@author: stijn_vanhoey
"""

from dwcavalidator.collect import DwcaScreening

vlinders = DwcaScreening('./dwc-occurrence.yaml',
                         lowercase_terms=False, unknown_fields=True)

#vlinders.screen_dwca('./dwca-dagvlinders-inbo-occurrences-v1.2.zip',
#                     maxentries=1)

vlinders.screen_dwc('../vlinders/corrupted_test.tsv',
                    delimiter='\t', maxentries=4)



print(vlinders.errors)
print(vlinders.list_error_types())
