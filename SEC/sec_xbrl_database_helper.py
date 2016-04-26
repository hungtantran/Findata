__author__ = 'hungtantran'


import datetime
import os
import re
import zipfile
from lxml import etree

import logger
from string_helper import StringHelper
from generic_model_database import GenericModelDatabase
from metrics import Metrics
from metrics_database import MetricsDatabase


class SecXbrlDatabaseHelper(object):
    def __init__(self, dbtype, username, password, server, database, table_name):
        self.dbtype = dbtype
        self.username = username
        self.password = password
        self.server = server
        self.database = database
        self.table_name = table_name
        self.metrics_db = MetricsDatabase(
                self.dbtype,
                self.username,
                self.password,
                self.server,
                self.database,
                table_name)

    def create_companies_metrics_table(self):
        print 'Try to create metrics table %s' % self.table_name
        self.metrics_db.create_metric()

    def insert_company_metrics_table(self, values):
        self.metrics_db.insert_metrics(new_metrics=values)

    def convert_parse_results_to_metrics(self, parse_results):
        metrics = []
        for metric_name in parse_results:
            metrics_results = parse_results[metric_name]
            for metrics_result in metrics_results:
                value = metrics_result[0]
                if (type(value) is float) or (type(value) is int):
                    value_float = value
                    value_string = str(value_float)
                elif type(value) is str:
                    value_float = None
                    value_string = value
                elif type(value) is datetime.datetime:
                    value_float = None
                    value_string = StringHelper.convert_datetime_to_string(value)

                start_date = metrics_result[1]
                end_date = metrics_result[2]
                unit = metrics_result[3]

                new_metric = Metrics(
                        metric_name=metric_name,
                        start_date=start_date,
                        end_date=end_date,
                        unit=unit,
                        value=value_float)
                metrics.append(new_metric)
        return metrics
