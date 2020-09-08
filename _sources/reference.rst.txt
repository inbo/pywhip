API reference
=============

High level functions
--------------------

.. autofunction:: pywhip.pywhip.whip_csv

.. autofunction:: pywhip.pywhip.whip_dwca

Document validation
--------------------

.. autoclass:: pywhip.pywhip.Whip
    :members: create_html, get_report

Specification handling
----------------------

The :class:`~pywhip.validators.DwcaValidator` is the underlying engine to handle
the validation of incoming values against the whip specifications. It
extends the existing :class:`Cerberus Validator <cerberus.Validator>` class.

.. automodule:: pywhip.validators
    :members:

Reporter Objects
------------------

.. automodule:: pywhip.reporters
    :members:
