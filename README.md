# pywhip

The pywhip package is a Python package to validate data against
[whip specifications](https://github.com/inbo/whip), a human and 
machine-readable syntax to express specifications for data.

* Free software: MIT license
* Documentation: https://inbo.github.io/pywhip

[![Build Status](https://img.shields.io/pypi/v/pywhip.svg)](https://pypi.python.org/pypi/pywhip)

[![Build Status](https://travis-ci.org/inbo/pywhip.svg?branch=master)](https://travis-ci.org/inbo/pywhip)

[![Updates](https://pyup.io/repos/github/inbo/pywhip/shield.svg)](https://pyup.io/repos/github/inbo/pywhip/)

Check the [documentation pages](https://inbo.github.io/pywhip/installation.html) for more information.

## Installation

To install pywhip, run this command in your terminal:

```shell
pip install pywhip
```

For more detailed installation instructions, see the 
[documentation pages](https://inbo.github.io/pywhip/installation.html).

## Quickstart

To validate a CSV data file with the field headers `country`, `eventDate`
and `individualCount`, write whip specifications, according to the
[whip syntax](https://github.com/inbo/whip):

```
specifications = """
    country:
       allowed: [BE, NL]
    eventDate:
        dateformat: '%Y-%m-%d'
        mindate: 2016-01-01
        maxdate: 2018-12-31
    individualCount:
        numberformat: x  # needs to be an integer value
        min: 1
        max: 100
    """
```

To whip your data set, e.g. ``my_data.csv``, pass the data to
whip specifications:


```python
from pywhip import whip_csv

example = whip_csv("my_data.csv", specifications, delimiter=',')
```

and write the output report to an html file:

```python
with open("report_example.html", "w") as index_page:
    index_page.write(example.get_report('html'))
```

Resulting in a [report](https://inbo.github.io/pywhip/report_observations.html) like this. For a more
detailed introduction, see [the documentaton tutorial](https://inbo.github.io/pywhip/tutorial.html).

## Credits

This package was created with [Cookiecutter](https://github.com/audreyr/cookiecutter) 
and the [audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage) 
project template.

Validation of data rows is using the [Cerberus](http://docs.python-cerberus.org/en/stable/) 
package.
