# -*- coding: utf-8 -*-
"""
Created on Wed Feb 10 17:29:37 2016

@author: stijn_vanhoey
"""

from marshmallow import Schema, fields, validates, ValidationError


class ExampleSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    created_at = fields.DateTime()

    def validator_equals(self, value, check_value):
        if value != check_value:
            raise ValidationError('Does not equal given value')

    @validates('email')
    def validate_email(self, value):
        if 'email' in self.context['user']:
            if 'equals' in self.context['user']['email'].keys():
                self.validator_equals(value, self.context['user']['email']['equals'])


# de idee: we zetten ene ultra-minimum Schema op en dan voegen we de andere
# zaken on the fly toe: _add_to_schema(field_name, schema)
class DWCASchema(Schema):
    class Meta:
        fields = ("language", "rightsHolder")

    def validator_equals(self, value, check_value):
        if value != check_value:
            raise ValidationError('Does not equal given value')




#    class Meta:
#        accessor = get_from_dict