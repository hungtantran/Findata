__author__ = 'hungtantran'


class CompanyMetrics(object):
    def __init__(self, cik, ticker, year, quarter, start_date, end_date, form_name, metrics_name, value_float,
                 value_string, metrics_unit, standard):
        self.cik = cik
        self.ticker = ticker
        self.year = year
        self.quarter = quarter
        self.start_date = start_date
        self.end_date = end_date
        self.form_name = form_name
        self.metrics_name = metrics_name
        self.value_float = value_float
        self.value_string = value_string
        self.metrics_unit = metrics_unit
        self.standard = standard