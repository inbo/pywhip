# -*- coding: utf-8 -*-

import os
import csv
from datetime import datetime
from collections import defaultdict, Mapping, Sequence
from pkg_resources import resource_filename

from dwca.read import DwCAReader
from cerberus import SchemaError
from jinja2 import FileSystemLoader, Environment

from pywhip.validators import DwcaValidator, WhipErrorHandler
from pywhip.reporters import SpecificationErrorHandler


def whip_dwca(dwca_zip, specifications, maxentries=None):
    """"""
    # Extract data header - only core support
    with DwCAReader(dwca_zip) as dwca:
        field_names = [field['term'].split('/')[-1] for field in
                       dwca.core_file.file_descriptor.fields]

    # Apply whip
    whip_it = Whip(specifications)
    whip_it._whip(whip_it.generate_dwca(dwca_zip),
                  field_names, maxentries)
    return whip_it


def whip_csv(csv_file, specifications, delimiter, maxentries=None):
    """"""

    # Extract data header
    with open(csv_file, "r") as dwc:
        reader = csv.DictReader(dwc, delimiter=delimiter)
        field_names = reader.fieldnames

    # Apply whip
    whip_it = Whip(specifications)
    whip_it._whip(whip_it.generate_csv(csv_file, delimiter),
                  field_names, maxentries)
    return whip_it


class Whip(object):
    """Some information"""

    def __init__(self, schema, sample_size=10):

        if not isinstance(schema, dict):
            raise SchemaError("Input schema need to be dictionary")
        self._schema = schema
        self._sample_size = sample_size

        # setup a DwcaValidator instance
        self.validation = DwcaValidator(self.schema,
                                        error_handler=WhipErrorHandler)

        self._report = {'executed_at': None,
                        'errors': [],
                        'results': {
                            'total_rows': 0,
                            'passed_rows': 0,
                            'failed_rows': 0,
                            'passed_row_ids': [],
                            'warnings': [],
                            'unspecified_fields': None,
                            'unknown_fields': None,
                            'specified_fields': {}
                            }
                        }

        self._total_row_count = 0

    @property
    def schema(self):
        return self._schema

    @property
    def sample_size(self):
        """Number of value-examples to use in reporting"""
        return self._sample_size

    def get_report(self, format='json'):
        if format == 'json':
            return self._report
        elif format == 'html':
            return self.create_html()
        return self._schema

    @staticmethod
    def format_if_rule(rule, number):
        """support to vuild if-based-rules in report"""
        return '{}_if_{}'.format(rule, number)

    @staticmethod
    def format_delimited_rule(rule):
        """support to vuild delimitedvalues-based-rules in report"""
        return '{}_delimitedvalue'.format(rule)

    @staticmethod
    def clean_constraint(constraint):
        """clean constraint for reports"""
        if isinstance(constraint, list):
            return ', '.join([str(el) for el in constraint])
        else:
            return str(constraint)

    def _extract_schema_blueprint(self, schema):
        """Extract fields and rules from schema

        For scopes if and delimitedvalues, the function need to extract the
        inner-rules from the scope and combine it with the if/delimitedvalue
        to ahve unique specification names. A delimitedvalues is providioned
        as well for generl delimitedvalues errors
        """
        schema_layout = {}
        for field, rules in schema.items():
            schema_layout[field] = {}
            for rule, conditions in rules.items():
                if rule == 'if':
                    for j, condition in enumerate(conditions):
                        # TODO: exclude to general schema-def on init validator
                        if 'empty' not in condition.keys():
                            condition['empty'] = False
                        for subrule, constraint in condition.items():
                            if subrule in self.validation.rules:
                                schema_layout[field][self.format_if_rule(
                                    subrule, j+1)] = \
                                    SpecificationErrorHandler(
                                        self.clean_constraint(constraint))
                elif rule == 'delimitedvalues':
                    schema_layout[field][rule] = SpecificationErrorHandler("")
                    for subrule, constraint in conditions.items():
                        if subrule != 'delimiter':
                            schema_layout[field][self.format_delimited_rule(
                                subrule)] = SpecificationErrorHandler(
                                self.clean_constraint(constraint))
                else:
                    schema_layout[field][rule] = \
                        SpecificationErrorHandler(
                            self.clean_constraint(conditions))
        return schema_layout

    def _conditional_fields(self, file_fields):
        """Extract the field names mentioned inside if conditions

        When fields are mentioned inside if statements, but not present in the
        data, this should raise a preliminar warning/message as part of the
        reporting
        """
        conditional_fields = []
        for _, specs in self.schema.items():
            if 'if' in specs.keys():
                if_rules = specs['if']
                # single if statement
                if isinstance(if_rules, Mapping):
                    conditional_fields += [key for key in if_rules.keys() if
                                          isinstance(if_rules[key], dict)]
                # multiple ifs combined
                elif isinstance(if_rules, Sequence):
                    for rule in if_rules:
                        conditional_fields += ([key for key in rule.keys() if
                                            isinstance(rule[key], dict)])
                else:
                    raise SchemaError
        if not set(conditional_fields).issubset(set(file_fields)):
            missing_if_fields = list(set(conditional_fields).difference(
                set(file_fields)))
            self._report['results']['warnings'].append(
                "Following fields mentioned inside if specifications do not "
                "exist inside the document: '{}'".format(
                    ', '.join(missing_if_fields)))

    def _compare_fields(self, file_fields):
        """Compare data fields and specifications

        Compare the fields mentioned by the specifications schema and the
        data set and update thereport attributes on unvalidated and missing
        fields

        Parameters
        ----------
        file_fields : list
            All fields present in the data-set.
        """
        try:
            file_fields = set(file_fields)
        except TypeError:
            raise TypeError

        self._report['results']['unspecified_fields'] = list(
            file_fields.difference(set(self.schema.keys())))
        self._report['results']['unknown_fields'] = list(set(
            self.schema.keys()).difference(file_fields))

    def _whip(self, input_generator, field_names, maxentries=None):
        """"""

        # preliminar checks
        self._compare_fields(field_names)
        self._conditional_fields(field_names)

        # prepare object to save errors
        specified_fields = self._extract_schema_blueprint(self.schema)
        passed_row_ids = []

        # validate each row and log the errors for each row
        for j, row in enumerate(input_generator):
            row_id = j + 1
            self.validation.validate(row)  # apply specification rules

            if len(self.validation.errors) > 0:
                for error in self.validation._errors:
                    field = error.field

                    if error.is_group_error:  # if/delimitedvalues
                        if error.rule == 'if':
                            for child_error in error.child_errors:
                                number = str(int(child_error.field.split(
                                    '_')[-1]) + 1)
                                rule = self.format_if_rule(
                                    child_error.rule, number)

                                message = self.validation.schema.validator.\
                                    error_handler._format_message(field,
                                                                  child_error)
                                specified_fields[field][rule][(
                                    child_error.value, message)].add(row_id)

                        elif error.rule == 'delimitedvalues':
                            for child_error in error.child_errors:
                                rule = self.format_delimited_rule(child_error.rule)

                                message = self.validation.schema.validator.\
                                    error_handler._format_message(field,
                                                                  child_error)
                                specified_fields[field][rule][(
                                    child_error.value, message)].add(row_id)

                        else:
                            NotImplementedError
                    else:
                        message = self.validation.schema.validator.\
                            error_handler._format_message(field, error)

                        specified_fields[field][error.rule][(error.value,
                                                             message)].add(row_id)
            else:
                passed_row_ids.append(row_id)
            if maxentries:
                if j >= maxentries-1:
                    break

        # fill report TODO: exclude his from in-function adapts to attributes
        self._total_row_count = j + 1
        self._report['results']['total_rows'] = self._total_row_count
        self._report['results']['passed_row_ids'] = passed_row_ids
        self._report['results']['passed_rows'] = len(passed_row_ids)
        self._report['results']['failed_rows'] = self._total_row_count - \
                                                 len(passed_row_ids)
        self._report['executed_at'] = datetime.now().strftime("%Y-%m-%d %H:%M")
        self._report['results']['specified_fields'] = \
            self._report_specified_fields(specified_fields,
                                          self._total_row_count,
                                          self.sample_size)
        self._isitgreat()

        # TODO: add generator function and dict-searches to query errors

    def _isitgreat(self):
        """check if there are any errors recorded"""
        if self._report['results']['failed_rows'] == 0:
            print("Hooray, your data set is according to the guidelines!")
        else:
            print('Dataset does not comply the specifications, check reports'
                  ' by using the `get_report` method '
                  'for a more detailed information.')

    @staticmethod
    def generate_dwca(dwca_zip):
        """"""
        with DwCAReader(dwca_zip) as dwca:
            for row in dwca:
                document = {k.split('/')[-1]: v for k, v in row.data.items()}
                yield document

    @staticmethod
    def generate_csv(csv_file, delimiter):
        """"""
        with open(csv_file, "r") as dwc:
            reader = csv.DictReader(dwc, delimiter=delimiter)
            for document in reader:
                yield document

    @staticmethod
    def _report_specified_fields(specified_fields, nrows, nsample):
        """Transform the data objects to report objects"""

        for field, rules in specified_fields.items():
            for rule, error_report in rules.items():
                specified_fields[field][rule] = \
                    specified_fields[field][rule].build_error_report(nrows,
                                                                     nsample)
        return specified_fields

    def create_html(self, html_output="index.html"):
        """build html from report

        Parameters
        -----------
        html_output : str
            relative path and filename to write the resulting index.html

        """
        path = "./static/template.html"

        html_template_path = resource_filename(__name__, path)
        env = Environment(loader=FileSystemLoader(
            os.path.dirname(html_template_path)))
        template = env.get_template(os.path.basename(html_template_path))
        html = template.render(report=self._report)

        return str(html)



