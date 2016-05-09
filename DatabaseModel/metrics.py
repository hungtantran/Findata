__author__ = 'hungtantran'


class Metrics(object):
    def __init__(self, metric_name, id=None, start_date=None, end_date=None, unit=None, value=None, metadata=None):
        self.id = id
        self.metric_name = metric_name
        self.value = value
        self.unit = unit
        self.start_date = start_date
        self.end_date = end_date
        self.metadata = metadata

    def to_string(self):
        return '%s %s %s %s %s %s %s' % (
                self.id,
                self.metric_name,
                self.value,
                self.unit,
                self.start_date,
                self.end_date,
                self.metadata)