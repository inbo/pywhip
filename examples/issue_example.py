# -*- coding: utf-8 -*-
"""
Created on Mon Feb 15 13:35:15 2016

@author: stijn_vanhoey
"""

from cerberus import Validator


#document1 = {'type' : 'Event', 'basisOfRecord': 'HumanObservation'}
#document2 = {'type' : 'PhysicalObject', 'basisOfRecord': 'PreservedSpecimen'}
#
#schema1 = {'type': {'allowed': 'Event'}, 'basisOfRecord':{'allowed':'HumanObservation'}}
#schema2 = {'type': {'allowed': 'PhysicalObject'}, 'basisOfRecord':{'allowed':'PreservedSpecimen'}}
#
#
#schema = {'anyof': [schema1, schema2]}

#v = Validator(schema1)
#v.validate(document1)
#print v.errors

#%%

class MyValidator(Validator):
    def _validate_if(self, ifset, field, value):
        # extract dict values -> conditions
        conditions = {k: v for k, v in ifset.iteritems() if isinstance(v, dict)}
        # extract dict values -> rules
        rules = {k: v for k, v in ifset.iteritems() if not isinstance(v, dict)}

        valid=True
        # check for all conditions if they apply
        for term, cond in conditions.iteritems():
            subschema = {term : cond}
            tempvalidation = MyValidator(subschema)
            tempvalidation.allow_unknown = True
            if not tempvalidation.validate(self.document):
cd                valid=False

        #others -> conditional rules applied when valid condition
        if valid:
            tempvalidation = MyValidator({field: rules})
            tempvalidation.validate({field : self.document[field]})
            #convert to object itself
            for field, err in tempvalidation.errors.items():
                self._error(field, err)

# EXAMPLE 1
##document = {'amount' : 2, 'basisOfRecord': 'HumanObservation'}
#document = {'amount' : 2, 'basisOfRecord': 'Robot'}
#
#schema = {'amount': {'if': {'basisOfRecord': {'allowed': 'HumanObservation'}, 'min': 5},
#                   'type':'integer'}}
#val = MyValidator(schema)
#val.allow_unknown = True
#val.validate(document)

#%% EXAMPLE 2

#document = {'size' : 2, 'perimeter': 'HumanObservation'}
#document = {'size' : 'medium', 'perimeter': 20}
document = {'size' : 'large', 'perimeter': 12}

schema = {'size': {'if': {'perimeter': {'min': 10, 'max': 30}, 'allowed': 'medium'}}}
val = MyValidator(schema)
val.allow_unknown = True
val.validate(document)
print val.errors


#%% DATE TESTING

document = {'type' : 'Event', 'eventDate': '20160101 00:00'}

schema = {'type': {'allowed': 'Event'}, 'eventDate':{'type':'datetime', 'min':'20150101'}}

v = Validator(schema)
v.validate(document)
print v.errors





