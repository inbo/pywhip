# -*- coding: utf-8 -*-

"""Console script for pywhip."""

import re

import yaml
import click

from pywhip import whip_csv


def _get_output_format(filename):
    """Extract data type format from provided filepath"""
    regex_extension = "(?<=\.)[a-zA-Z]+$"
    extension = re.findall(regex_extension, filename)[0]
    if extension not in ["json", "html"]:
        raise Exception("Not a valid output file extension for whip reporting,"
                        "use json or html")
    return extension


@click.command()
@click.argument('data_file', type=click.Path(exists=True))
@click.argument('specifications_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path(), required=False)
@click.option('--delimiter', help='Delimiter of the data file',
              required=False)
def main(data_file, specifications_file, output_file="index.html",
         delimiter=","):
    """Validate a CSV data set using whip specifications.

    \b
    DATA_FILE :  Input CSV data file to whip.
    SPECIFICATIONS_FILE : Whip specifications to validate data set.
    OUTPUT_FILE : Output file to write report, either with a json or html
    file extension
    """

    click.echo("Validate data against whip specifications")
    click.echo("")

    with open(specifications_file) as schema_file:
        specifications = yaml.load(schema_file)

    whip_it = whip_csv(data_file, specifications, delimiter)

    output_format = _get_output_format(output_file)
    if output_format == "html":
        with open(output_file, "w") as index_page:
            index_page.write(whip_it.get_report('html'))
    elif output_format == "json":
        with open(output_file, "w") as json_report:
            json_report.write(whip_it.get_report('json'))
    else:
        NotImplementedError

    click.echo("Check your pywhip report by at {}".format(output_file))


if __name__ == "__main__":
    main()
