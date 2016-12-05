# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 12:44:05 2016

@author: stijn_vanhoey
"""

from dwcavalidator.collect import DwcaScreening

inboveg = DwcaScreening('./dwc-event.yaml')
inboveg.screen_dwca('./dwca-inboveg-niche-vlaanderen-events-v0.8.zip',
                    maxentries=500)

print(inboveg.errors)
print(inboveg.list_error_types())
