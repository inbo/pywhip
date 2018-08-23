======
pywhip
======

----

The pywhip package is a Python package to validate data against
`whip specifications`_, a human and machine-readable syntax to express
specifications for data.

.. _`whip specifications`: https://github.com/inbo/whip

The short story
==================

Pywhip is used to validate a data set:

::

    eventDate   individualCount  country
    2018-01-03  5                 BA
    2018-04-02  20                NL
    2016-07-06  3300              BE
    2017-03-02  2                 BE
    1018-01-08  1                 NL

against a set of `whip specifications`_:

.. _`whip specifications`: https://github.com/inbo/whip

::

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

to get a whip validator report:

.. raw:: html

    <iframe src="_static/report_observations.html" height="400px" width="100%"></iframe>

and celebrate or despair...

Table of Contents
==================

.. toctree::
   :maxdepth: 1

   installation
   tutorial
   reference
   contributing
   history
   authors

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
