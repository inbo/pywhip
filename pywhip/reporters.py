"""
S. Van Hoey
"""

from collections import Mapping, defaultdict


class WhipReportException(Exception):
    pass


class SpecificationErrorHandler(Mapping):

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
        """check if all values are linked to a single message"""
        return len(set([value[0] for value in self.keys()])) == len(
            set(self.keys()))

    def _failed_rows(self):
        """Overview of the failed rows"""
        row_ids = set()
        for _, values in self.items():
            row_ids.update(values)
        return row_ids

    def build_error_report(self, total_rows_count, top_n):
        """convert defaultdict to dict with key for message and row count"""

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