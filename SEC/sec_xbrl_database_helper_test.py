__author__ = 'hungtantran'


import filecmp
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
        self.database_helper = SecXbrlDatabaseHelper('mysql',
                                                     Config.test_mysql_username,
                                                     Config.test_mysql_password,
                                                     Config.test_mysql_server,
                                                     Config.test_mysql_database)

        self.model_db = GenericModelDatabase('mysql',
                                             Config.test_mysql_username,
                                             Config.test_mysql_password,
                                             Config.test_mysql_server,
                                             Config.test_mysql_database)

    def test_create_companies_metrics_table(self):
        try:
            self.SetUp()
            self.model_db.remove_model('company_metrics')
            self.database_helper.create_companies_metrics_table(table_name='company_metrics')

            test_values = []
            test_values.append([1,
                                2014,
                                None,
                                StringHelper.convert_string_to_datetime('2014-03-03'),
                                StringHelper.convert_string_to_datetime('2014-03-03'),
                                None,
                                'test_metrics',
                                1,
                                None,
                                'USD',
                                None])
            self.model_db.insert_values('company_metrics', values=test_values)
            data = self.model_db.get_model_data('company_metrics')
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0][0], 1)
            self.assertEqual(data[0][1], 2014)
            self.assertEqual(data[0][2], None)
            self.assertEqual(data[0][3].strftime("%Y-%m-%d %H:%M:%S"), '2014-03-03 00:00:00')
            self.assertEqual(data[0][4].strftime("%Y-%m-%d %H:%M:%S"), '2014-03-03 00:00:00')
            self.assertEqual(data[0][5], None)
            self.assertEqual(data[0][6], 'test_metrics')
            self.assertEqual(data[0][7], 1)
            self.assertEqual(data[0][8], None)
            self.assertEqual(data[0][9], 'USD')
            self.assertEqual(data[0][10], None)
        finally:
            self.model_db.remove_model('company_metrics')

    def test_insert_company_metrics_table(self):
        try:
            self.SetUp()
            self.model_db.remove_model('company_metrics')
            self.database_helper.create_companies_metrics_table(table_name='company_metrics')

            xbrl_file = './SEC/test_files/msft-20140930.xml'
            processor = SecXbrlProcessor()
            results = processor.parse_xbrl(xbrl_file)

            converted_results = self.database_helper.convert_processed_results_to_database_insert(
                1, 2014, None, '10Q', results)

            self.database_helper.insert_company_metrics_table(values=converted_results, table_name='company_metrics')

            data = self.model_db.get_model_data('company_metrics')
            self.assertEqual(len(data), 412)
        finally:
            self.model_db.remove_model('company_metrics')
            pass


if __name__ == '__main__':
    unittest.main()
