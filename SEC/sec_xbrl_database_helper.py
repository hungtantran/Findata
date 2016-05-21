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
                table_name,
                use_orm=False)

    def create_companies_metrics_table(self):
        print 'Try to create metrics table %s' % self.table_name
        self.metrics_db.create_metric()

    def insert_company_metrics_table(self, values):
        self.metrics_db.insert_metrics(new_metrics=values)

    def convert_parse_results_to_metrics(self, parse_results):
        metrics = []

        metric_hash = []
        for metric_name in parse_results:
            metrics_results = parse_results[metric_name]
            for metrics_result in metrics_results:
                start_date = metrics_result[1]
                end_date = metrics_result[2]

                value = metrics_result[0]
                if (type(value) is float) or (type(value) is int):
                    value_float = value
                elif type(value) is str:
                    value_float = None
                elif type(value) is datetime.datetime:
                    value_float = None

                unit = metrics_result[3]
                if (start_date is None) or (end_date is None) or (unit is None) or (value_float is None):
                    logger.Logger.log(logger.LogLevel.WARN, 'Invalid metric %s %s %s %s %s %s' %(
                            self.table_name, metric_name, start_date, end_date, unit, value_float))
                    continue

                # TODO: remove this hack (database has unique key so we need to use this hack for now)
                hash = (metric_name +
                        StringHelper.convert_datetime_to_string(start_date) +
                        StringHelper.convert_datetime_to_string(end_date))
                if hash in metric_hash:
                    continue
                else:
                    metric_hash.append(hash)

                new_metric = Metrics(
                        metric_name=metric_name,
                        start_date=start_date,
                        end_date=end_date,
                        unit=unit,
                        value=value_float)
                metrics.append(new_metric)
        return metrics
