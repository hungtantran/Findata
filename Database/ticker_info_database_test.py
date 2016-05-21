__author__ = 'hungtantran'


import unittest

from Common.constants_config import Config
import Common.logger
from ticker_info_database import TickerInfoDatabase


class TestTickerInfoDatabase(unittest.TestCase):
    def test_connection(self):
        ticker_info_db = TickerInfoDatabase('mysql',
                                            Config.test_mysql_username,
                                            Config.test_mysql_password,
                                            Config.test_mysql_server,
                                            Config.test_mysql_database,
                                            'ticker_info')
        try:
            ticker_info_db.remove_ticker_info_table()
            ticker_info_db.create_ticker_info_table()
            ticker_info_db.insert_value(1, 'A', 'AA', 1991, 'AAA', 'AAAA', 'AAAAA', None, None)
            ticker_info_db.insert_value(2, 'B', 'BB', 1992, 'BBB', 'BBBB', 'BBBBB', 123, 456)

            data = ticker_info_db.get_ticker_info_data()
            self.assertEqual(len(data), 2)

            self.assertEquals(data[0].cik, 1)
            self.assertEquals(data[0].ticker, 'A')
            self.assertEquals(data[0].name, 'AA')
            self.assertEquals(data[0].ipo_year, 1991)
            self.assertEquals(data[0].sector, 'AAA')
            self.assertEquals(data[0].industry, 'AAAA')
            self.assertEquals(data[0].exchange, 'AAAAA')
            self.assertEquals(data[0].sic, None)
            self.assertEquals(data[0].naics, None)

            self.assertEquals(data[1].cik, 2)
            self.assertEquals(data[1].ticker, 'B')
            self.assertEquals(data[1].name, 'BB')
            self.assertEquals(data[1].ipo_year, 1992)
            self.assertEquals(data[1].sector, 'BBB')
            self.assertEquals(data[1].industry, 'BBBB')
            self.assertEquals(data[1].exchange, 'BBBBB')
            self.assertEquals(data[1].sic, 123)
            self.assertEquals(data[1].naics, 456)
        finally:
            ticker_info_db.remove_ticker_info_table()


if __name__ == '__main__':
    unittest.main()


