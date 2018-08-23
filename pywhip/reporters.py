# -*- coding: utf-8 -*-

from collections import Mapping, defaultdict, MutableMapping


class WhipReportException(Exception):
    """Raised when the reporting of the errors contains errors"""
    pass


class SpecificationErrorHandler(Mapping):
    """Class handler for field-rule entity reporting

    Attributes
    ----------
    constraint : str
        The constraint linked to the specification (field-rule combination),
        expressed as string
    _samples : defaultdict(set)
        Dictionary with wrong data values as keys and the corresponding row
        identifiers as values.

    Notes
    -----
    The :class:`~pywhip.reporters.SpecificationErrorHandler` class is basically
    an enriched dictionary (using :term:`mapping`), directly building on top
    of a :class:`~collections.defaultdict` with the (wrong) values as
    keys and a :class:`set` as values to add (unique) rows for which
    that value occurs.
    """

    # TODO: add control that keys are tuples only (__setitem__)

    def __init__(self, constraint):
        self._samples = defaultdict(set)
        self.constraint = constraint

    def __getitem__(self, key):
        return self._samples[key]

    def __iter__(self):
        return iter(self._samples)

    def __len__(self):
        return len(self._samples)

    def _unique_value_messages(self):
        """Check if all values are linked to a single message"""
        return len(set([value[0] for value in self.keys()])) == len(
            set(self.keys()))

    def _failed_rows(self):
        """Overview of the failed row identifiers"""
        row_ids = set()
        for _, values in self.items():
            row_ids.update(values)
        return row_ids

    def build_error_report(self, total_rows_count, top_n):
        """Convert defaultdict to regular dict for json reporting


        Parameters
        -----------
        total_rows_count : int
            Total rows of the current document working with, used to calculate
            passed rows as well
        top_n : int
            Number of samples (ordered on the number of rows) to retain for
            reporting purposes

        Notes
        -----

        :meth:`~pywhip.reporters.SpecificationErrorHandler.build_error_report`
        combines the information contained by the
        :attr:`~pywhip.reporters.SpecificationErrorHandler._samples`
        attribute, for example::

            { ("07241981", "string format ...") : [2, 3, 5, 6],
              ("value", "message as provided by error") : [1, 2, 6,]
            }

        together with the other attributes into a json-style report::

            {"constraint": "%Y-%m-%d, %Y-%m, %Y",
             "failed_rows": 23,
             "passed_rows": 3,
             "samples": {
                "07241981": {
                    "failed_rows": 4,
                    "first_row": 2,
                    "message": "string format ..."
                },
                "value": {
                    "failed_rows": n_rows,
                    "first_row": minimum of row identifiers,
                    "message": "message as provided by error"
                    }
                }
            }
        """

        if not self._unique_value_messages():
            raise WhipReportException("Not all value-message "
                                      "combinations unique!")

        samples = {}
        for (value, message) in sorted(self, key=lambda k: len(self[k]),
                                       reverse=True)[:top_n]:
            row_id_list = self[(value, message)]
            samples[value] = {'message': message,
                              'first_row': min(row_id_list),
                              'failed_rows': len(row_id_list)}

        failed_rows_count = len(self._failed_rows())
        return {'constraint': self.constraint,
                'passed_rows': total_rows_count - failed_rows_count,
                'failed_rows': failed_rows_count,
                'samples': samples}
