__author__ = 'hungtantran'


import filecmp
import os
import unittest

import logger
from constants_config import Config
from sec_xbrl_processor import SecXbrlProcessor
from sec_xbrl_database_helper import SecXbrlDatabaseHelper
from generic_model_database import GenericModelDatabase
from sec_ticker_info_helper import SecTickerInfoHelper


class TestSecXbrlProcessor(unittest.TestCase):
    def SetUp(self):
        self.sec_xbrl_database_helper = SecXbrlDatabaseHelper('mysql',
                                                              Config.test_mysql_username,
                                                              Config.test_mysql_password,
                                                              Config.test_mysql_server,
                                                              Config.test_mysql_database)
        self.model_db = GenericModelDatabase('mysql',
                                             Config.test_mysql_username,
                                             Config.test_mysql_password,
                                             Config.test_mysql_server,
                                             Config.test_mysql_database)
        self.ticker_info_helper = SecTickerInfoHelper('mysql',
                                                      Config.test_mysql_username,
                                                      Config.test_mysql_password,
                                                      Config.test_mysql_server,
                                                      Config.test_mysql_database)
        self.model_db.remove_model('IBM_metrics')
        self.processor = SecXbrlProcessor()

    def TearDown(self):
        self.model_db.remove_model('IBM_metrics')

    def test_extract_xbrl_zip_file(self):
        try:
            self.SetUp()
            target_directory = './SEC/test_output_files'
            target_file_path = "%s/ibm-20090630.xml" % target_directory
            zip_file_path = './SEC/test_files/51143-2009-qtr3-10-Q-0001104659-09-045198-xbrl.zip'

            try:
                os.remove(target_file_path)
            except Exception:
                pass

            self.processor.extract_xbrl_zip_file(zip_file_path=zip_file_path,
                                                 extracted_directory=target_directory)

            with open(target_file_path, 'r') as file:
                self.assertTrue(filecmp.cmp(target_file_path, './SEC/test_files/ibm-20090630.xml'))
        finally:
            self.TearDown()

    def test_parse_xbrl(self):
        try:
            self.SetUp()
            xbrl_file = './SEC/test_files/ibm-20090630.xml'

            results = self.processor.parse_xbrl(xbrl_file)

            self.assertGreater(len(results), 0)
            self.assertTrue('GrossProfit' in results)
            self.assertTrue('Liabilities' in results)
            self.assertTrue('Assets' in results)
            self.assertTrue('EarningsPerShareBasic' in results)
            self.assertTrue('EarningsPerShareDiluted' in results)

            self.assertEqual(len(results['Liabilities']), 2)
            self.assertEqual(results['Liabilities'][0][0], 95939000000)
            self.assertEqual(results['Liabilities'][0][1].strftime("%Y-%m-%d %H:%M:%S"), '2008-12-31 00:00:00')
            self.assertEqual(results['Liabilities'][0][2].strftime("%Y-%m-%d %H:%M:%S"), '2008-12-31 00:00:00')
            self.assertEqual(results['Liabilities'][0][3], 'http://xbrl.us/us-gaap/2009-01-31')
            self.assertEqual(results['Liabilities'][1][0], 88182000000)
            self.assertEqual(results['Liabilities'][1][1].strftime("%Y-%m-%d %H:%M:%S"), '2009-06-30 00:00:00')
            self.assertEqual(results['Liabilities'][1][2].strftime("%Y-%m-%d %H:%M:%S"), '2009-06-30 00:00:00')
            self.assertEqual(results['Liabilities'][1][3], 'http://xbrl.us/us-gaap/2009-01-31')
        finally:
            self.TearDown()

    def test_process_xbrl_zip_file_and_push_database(self):
        try:
            self.SetUp()
            self.processor.process_xbrl_zip_file_and_push_database(
                    zip_file_path='SEC/test_files/51143-2009-qtr3-10-Q-0001104659-09-045198-xbrl.zip',
                    sec_xbrl_database_helper=self.sec_xbrl_database_helper,
                    sec_ticker_info_helper=self.ticker_info_helper,
                    extracted_directory='SEC/test_output_files',
                    remove_extracted_file_after_done=False)
            data = self.model_db.get_model_data('IBM_metrics')
            self.assertEqual(len(data), 225)
        finally:
            self.TearDown()

    def test_process_xbrl_directory_and_push_database(self):
        try:
            self.SetUp()
            self.processor.process_xbrl_directory_and_push_database(
                    xbrl_zip_directory='SEC/test_files/',
                    sec_xbrl_database_helper=self.sec_xbrl_database_helper,
                    sec_ticker_info_helper=self.ticker_info_helper,
                    extracted_directory='SEC/test_output_files',
                    remove_extracted_file_after_done=False)
            data = self.model_db.get_model_data('IBM_metrics')
            self.assertEqual(len(data), 225)
        finally:
            self.TearDown()


if __name__ == '__main__':
    unittest.main()
