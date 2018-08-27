# -*- coding: utf-8 -*-

import os
import csv
from datetime import datetime
from collections import defaultdict, Mapping, Sequence
from pkg_resources import resource_filename

from dwca.read import DwCAReader
from cerberus import SchemaError
from jinja2 import FileSystemLoader, Environment

from .validators import DwcaValidator, WhipErrorHandler
from .reporters import SpecificationErrorHandler


def whip_dwca(dwca_zip, specifications, maxentries=None):
    """Whip a Darwin Core Archive

    Validate the core file of a `Darwin Core Archive`_ zipped data set,
    using the :class:`~dwca.read.DwCAReader` reading and iterator capabilities.

    .. _Darwin Core Archive: https://en.wikipedia.org/wiki/Darwin_Core_Archive

    Parameters
    ----------
    dwca_zip : str
        Filename of the zipped Darwin Core Archive.
    specifications : dict
        Valid specifications whip dictionary schema.
    maxentries : int
        Define the limit of records to validate from the Archive, useful to
        have a quick set on the frst subset of data.

    Returns
    -------
    whip_it : pywhip.pywhi.Whip
        Whip validator clasc instance, containing the errors and reporting
        capabilities.
    """
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
    """Whip a CSV-like file

    Validate a CSV file, using the :class:`CSV <python3:csv.DictReader>`
    reading and iterator capabilities of the Python standard library.

    Parameters
    ----------
    csv_file : str
        Filename of the CSV file to whip validate.
    specifications : dict
        Valid specifications whip dictionary schema.
    delimiter : str
        A one-character string used to separate fields, e.g. ``','``.
    maxentries : int
        Define the limit of records to validate from the Archive, useful to
        have a quick set on the frst subset of data.

    Returns
    -------
    whip_it : pywhip.pywhi.Whip
        Whip validator class instance, containing the errors and reporting
        capabilities.
    """

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
    """Whip document validation class

    Validates (multiple row) documents against a whip specification schema
    using the high-level functions ``whip_...`` and creates a validation report
    with the :meth:`~pywhip.pywhip.Whip.get_report` method.

    Attributes
    ----------
    sample_size : int
        Number of value-examples to use in reporting
    schema : dict
        Whip specification schema, consisting of `field : constraint`
        combinations
    validation : pywhip.validators.DwcaValidator
        A :class:`~pywhip.validators.DwcaValidator` class instance.
    _report : dict
        Base report container to collect document errors. Errors are
        collected in the ['results']['specified_fields'] values, having
        a :class:`~pywhip.reporters.SpecificationErrorHandler` for each
        field-specification combination.
    """

    def __init__(self, schema, sample_size=10):
        """

        Parameters
        ----------
        schema : dict
            Whip specification schema, consisting of `field : constraint`
            combinations.
        sample_size : int
            For each of the field-rules combinations, the (top) number of data
            value samples/examples to include in the report.
        """

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
        return self._sample_size

    def get_report(self, format='json'):
        """Collect errors into reporting format (json/html)

        Converts the logged errors into a json or html style report.

        Parameters
        ----------
        format : json | html
            Define the output format the report is used.

        Returns
        -------
        str

        """
        if format == 'json':
            return self._report
        elif format == 'html':
            return self.create_html()

    @staticmethod
    def format_if_rule(rule, number):
        """Support to build if-based-rules in report

        Parameters
        ----------
        rule : str
            A whip specification rule.
        number : int
            The counter of the if-statements used in the whip specification,
            counter starts at 1.
        """
        return '{}_if_{}'.format(rule, number)

    @staticmethod
    def format_delimited_rule(rule):
        """Support to build delimitedvalues-based-rules in report

        Parameters
        ----------
        rule : str
            A whip specification rule.
        """
        return '{}_delimitedvalue'.format(rule)

    @staticmethod
    def clean_constraint(constraint):
        """Clean constraint for reports

        Parameters
        ----------
        constraint : str
            The constraint as defined in the whip specification.
        """
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

        Parameters
        ----------
        schema : dict
            Whip specification schema.
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

        Parameters
        ----------
        file_fields : list | set
            List of the field names present in the input data file.
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
        file_fields : list | set
            List of the field names present in the input data file
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
        """Validate whip specifications on the input

         For each entry of the input generator (which can be limited using the
         ``maxentries`` parameter, the validation is recording the errors. At
         the end, the :attr:`~pywhip.pywhip.Whip._report` attribute is updated
         with the error logs and other relevant metadata.

        Parameters
        ----------
        input_generator : iterator
            An iterator, yielding `field : value` combinations of the document
            on each iteration.
        field_names : list | set
            List of the field names present in the input data file.
        maxentries : int
            Define the limit of records to validate from the Archive, useful to
            have a quick set on the frst subset of data.
        """

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
                  'for a more detailed information.')

    @staticmethod
    def generate_dwca(dwca_zip):
        """Darwin core archive generator

        Yields `field : value` combinations of the document on each iteration,
        corresponding to individual rows of the data file.

        Parameters
        ----------
        dwca_zip : str
            Filename of the zipped Darwin Core Archive.

        Yields
        ------
        document : dict
            Provides a single line document values (as dict values) and
            field names (as dict keys).

        """
        with DwCAReader(dwca_zip) as dwca:
            for row in dwca:
                document = {k.split('/')[-1]: v for k, v in row.data.items()}
                yield document

    @staticmethod
    def generate_csv(csv_file, delimiter):
        """CSV File generator

        Yields `field : value` combinations of the document on each iteration,
        corresponding to individual rows of the data file.

        Parameters
        ----------
        csv_file : str
            Filename of the CSV file to whip validate.
        delimiter : str
            A one-character string used to separate fields, e.g. ``','``.

        Yields
        ------
        document : dict
            Provides a single line document values (as dict values) and
            field names (as dict keys).

        """
        with open(csv_file, "r") as dwc:
            reader = csv.DictReader(dwc, delimiter=delimiter)
            for document in reader:
                yield document

    @staticmethod
    def _report_specified_fields(specified_fields, nrows, nsample):
        """Transform the data objects to report objects

        Parameters
        ----------
        specified_fields : dict
            Dictionary with a `~pywhip.reporters.SpecificationErrorHandler`
            object for each field-specification combination.
        nrows : int
            Total rows of the current document working with, used to calculate
            passed rows as well
        nsample : int
            Number of samples (ordered on the number of rows) to retain for
            reporting purposes
        """

        for field, rules in specified_fields.items():
            for rule, error_report in rules.items():
                specified_fields[field][rule] = \
                    specified_fields[field][rule].build_error_report(nrows,
                                                                     nsample)
        return specified_fields

    def create_html(self):
        """Build html using template

        Returns
        -------
        str

        """

        path = "./static/template.html"

        html_template_path = resource_filename(__name__, path)
        env = Environment(loader=FileSystemLoader(
            os.path.dirname(html_template_path)))
        template = env.get_template(os.path.basename(html_template_path))
        html = template.render(report=self._report)

        return str(html)



