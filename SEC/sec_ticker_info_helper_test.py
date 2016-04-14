__author__ = 'hungtantran'


import unittest

import logger
from constants_config import Config
from string_helper import StringHelper
from sec_xbrl_processor import SecTickerInfoHelper
from ticker_info_database import TickerInfoDatabase


class TestSecTickerInfoHelper(unittest.TestCase):
    def SetUp(self):
        self.ticker_info_helper = SecTickerInfoHelper('mysql',
                                                      Config.test_mysql_username,
                                                      Config.test_mysql_password,
                                                      Config.test_mysql_server,
                                                      Config.test_mysql_database)

        self.ticker_info_db = TickerInfoDatabase('mysql',
                                            Config.test_mysql_username,
                                            Config.test_mysql_password,
                                            Config.test_mysql_server,
                                            Config.test_mysql_database,
                                            'ticker_info')
        self.ticker_info_db.remove_ticker_info_table()
        self.ticker_info_db.create_ticker_info_table()

    def TearDown(self):
        self.ticker_info_db.remove_ticker_info_table()

    def test_ticker_ti_cik(self):
        try:
            self.SetUp()
            self.assertEqual(self.ticker_info_helper.ticker_to_cik('VRSK'), 1442145)
            self.assertEqual(self.ticker_info_helper.ticker_to_cik('TYC'), 833444)
            self.assertEqual(self.ticker_info_helper.ticker_to_cik('fake'), None)
        finally:
            self.TearDown()

    def test_insert_company_metrics_table(self):
        try:
            self.SetUp()
            self.assertEqual(self.ticker_info_helper.cik_to_ticker(1442145), 'VRSK')
            self.assertEqual(self.ticker_info_helper.cik_to_ticker(833444), 'TYC')
            self.assertEqual(self.ticker_info_helper.cik_to_ticker(000000), None)
        finally:
            self.TearDown()

    def test_company_name_to_cik(self):
        try:
            self.SetUp()
            self.assertEqual(self.ticker_info_helper.company_name_to_cik('Arbor Realty Trust'), 1253986)
            self.assertEqual(self.ticker_info_helper.company_name_to_cik('MICROSOFT'), None)
            self.assertEqual(self.ticker_info_helper.company_name_to_cik('fake company'), None)
        finally:
            self.TearDown()


if __name__ == '__main__':
    unittest.main()
