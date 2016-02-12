# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 17:30:46 2016

@author: stijn_vanhoey
"""

import os
from pprint import pprint

import yaml
from dwca.read import DwCAReader

from schemas import ExampleSchema, DWCASchema

##
ABS_PATH = '/home/stijn_vanhoey/githubs/temp/validator_testdata2'


config = yaml.load(open('./test/settings.yml'))

schema1 = ExampleSchema(context=config)


schema2 = DWCASchema(config)

with DwCAReader(os.path.join(ABS_PATH, 'validator_testdata.zip')) as dwca:
    temp = dwca.get_row_by_index(0).data
    #result = schema.load(dwca.get_row_by_index(0).data)
    #pprint(result.data)
    #pprint(result.errors)




