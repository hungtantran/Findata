__author__ = 'hungtantran'


import datetime
import os
import re
import zipfile
from lxml import etree

import logger
from string_helper import StringHelper
from generic_model_database import GenericModelDatabase


class SecXbrlDatabaseHelper(object):
    def __init__(self, dbtype, username, password, server ,database):
        self.model_db = GenericModelDatabase(dbtype, username, password,server, database)
        pass

    def create_companies_metrics_table(self, table_name=None):
        if table_name is None:
            table_name = 'Companies_Metrics'
        self.model_db.create_model(model=table_name,
                                   column_names=['cik', 'ticker', 'year', 'quarter', 'start_date', 'end_date', 'form_name', 'metrics_name', 'value_float', 'value_string', 'metrics_unit', 'standard'],
                                   column_types=['INTEGER', 'VARCHAR(32)', 'SMALLINT', 'SMALLINT', 'DATETIME', 'DATETIME', 'VARCHAR(255)', 'VARCHAR(255)', 'FLOAT', 'TEXT', 'VARCHAR(255)', 'VARCHAR(255)'],
                                   primary_key_columns=['cik', 'start_date', 'end_date', 'metrics_name'])

    def insert_company_metrics_table(self, values, table_name=None):
        if table_name is None:
            table_name = 'Companies_Metrics'
        self.model_db.insert_values(model=table_name,
                                    values=values,
                                    ignore_duplicated=True)

    def convert_processed_results_to_database_insert(self, cik, ticker, year, quarter, form_name, parse_results):
        converted_results = []
        for metrics_name in parse_results:
            metrics_results = parse_results[metrics_name]
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
                standard = metrics_result[3]
                converted_result = [cik, ticker, year, quarter, start_date, end_date, form_name, metrics_name, value_float, value_string, 'USD', standard]
                converted_results.append(converted_result)
        return converted_results
