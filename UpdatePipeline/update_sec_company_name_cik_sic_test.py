__author__ = 'hungtantran'


import unittest

from Common.constants_config import Config
import Common.logger
from string_helper import StringHelper
from ticker_info import TickerInfo
from ticker_info_database import TickerInfoDatabase
from update_sec_company_name_cik_sic import UpdateSecCompanyNameCikSic


class TestUpdateSecCompanyNameCikSic(unittest.TestCase):
    def SetUp(self, copy_from_existing_database=True):
        self.ticker_info_db = TickerInfoDatabase(
                'mysql',
                Config.test_mysql_username,
                Config.test_mysql_password,
                Config.test_mysql_server,
                Config.test_mysql_database)

        self.ticker_info_db.remove_ticker_info()

        if copy_from_existing_database:
            TickerInfoDatabase.copy_ticker_info_to_test()
        else:
            self.ticker_info_db.create_ticker_info_table()

        self.ticker_info_db = TickerInfoDatabase(
                'mysql',
                Config.test_mysql_username,
                Config.test_mysql_password,
                Config.test_mysql_server,
                Config.test_mysql_database)

    def TearDown(self):
        #self.ticker_info_db.remove_ticker_info()
        pass

    def test_parse_html_and_update_data(self):
        self.SetUp(copy_from_existing_database=True)
        update_obj = UpdateSecCompanyNameCikSic(
            'mysql',
             Config.test_mysql_username,
             Config.test_mysql_password,
             Config.test_mysql_server,
             Config.test_mysql_database)
        try:

            with open('UpdatePipeline/test_files/sec_company_name_cik_sic.html') as f:
                html_content = f.read()

            update_obj.data = []
            update_obj.update_from_html_content(html_content)
            data = update_obj.data
            self.assertEquals(len(data), 21)

            self.assertEquals(data[0][0], 'a consulting team inc')
            self.assertEquals(data[0][1], 1040792)
            self.assertEquals(data[0][2], 7380)

            self.assertEquals(data[1071][0], 'azz inc')
            self.assertEquals(data[1071][1], 8947)
            self.assertEquals(data[1071][2], 3640)

            existing_data = self.ticker_info_db.get_ticker_info_data()
            update_obj._update_database_with_given_data(data, existing_data)

            """self.ticker_info_db.insert_row(ticker_info.TickerInfo(
                self.cik = cik
                self.ticker = ticker
                self.name = name
                self.ipo_year = ipo_year
                self.sector = sector
                self.industry = industry
                self.exchange = exchange
                self.sic = sic
                self.naics = naics))

            self.ticker_info_db.insert_row(ticker_info.TickerInfo(
                self.cik = cik
                self.ticker = ticker
                self.name = name
                self.ipo_year = ipo_year
                self.sector = sector
                self.industry = industry
                self.exchange = exchange
                self.sic = sic
                self.naics = naics))

            data = self.ticker_info_db.get_ticker_info_data()
            self.assertEqual(len(data), 2)

            for i in range(3):
                update_obj.update_database()
                data = metrics_db.get_metrics()
                self.assertEqual(len(data), 20)"""
        finally:
            self.TearDown()


if __name__ == '__main__':
    unittest.main()


