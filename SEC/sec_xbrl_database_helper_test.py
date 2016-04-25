__author__ = 'hungtantran'


import os
import unittest

import logger
from constants_config import Config
from sec_xbrl_database_helper import SecXbrlDatabaseHelper
from generic_model_database import GenericModelDatabase
from string_helper import StringHelper
from sec_xbrl_processor import SecXbrlProcessor


class TestSecXbrlDatabaseHelper(unittest.TestCase):
    def SetUp(self):
        self.metric_table_name = 'msft_metrics'
        self.database_helper = SecXbrlDatabaseHelper('mysql',
                                                     Config.test_mysql_username,
                                                     Config.test_mysql_password,
                                                     Config.test_mysql_server,
                                                     Config.test_mysql_database,
                                                     self.metric_table_name)

        self.model_db = GenericModelDatabase('mysql',
                                             Config.test_mysql_username,
                                             Config.test_mysql_password,
                                             Config.test_mysql_server,
                                             Config.test_mysql_database)

    def test_insert_company_metrics_table(self):
        try:
            self.SetUp()
            self.model_db.remove_model(self.metric_table_name)
            self.database_helper.create_companies_metrics_table()

            xbrl_file = './SEC/test_files/msft-20140930.xml'
            processor = SecXbrlProcessor()
            results = processor.parse_xbrl(xbrl_file)

            metrics = self.database_helper.convert_parse_results_to_metrics(parse_results=results)

            self.database_helper.insert_company_metrics_table(values=metrics)

            data = self.model_db.get_model_data(self.metric_table_name)
            self.assertEqual(len(data), 1236)
        finally:
            self.model_db.remove_model(self.metric_table_name)
            pass


if __name__ == '__main__':
    unittest.main()
