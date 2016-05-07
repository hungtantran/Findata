__author__ = 'hungtantran'


import unittest

from Common.constants_config import Config
import Common.logger
from fund_info_database import FundInfoDatabase
from fund_info import FundInfo


class TestFundInfoDatabase(unittest.TestCase):
    def SetUp(self):
        self.fund_info_db = FundInfoDatabase(
                'mysql',
                Config.test_mysql_username,
                Config.test_mysql_password,
                Config.test_mysql_server,
                Config.test_mysql_database)
        self.fund_info_db.remove_fund_info_table()
        self.fund_info_db.create_fund_info_table()

    def TearDown(self):
        self.fund_info_db.remove_fund_info_table()

    def test_connection(self):
        try:
            self.SetUp()
            self.fund_info_db.insert_value(['A'], ['AA'], ['AAA'], ['AAAA'], ['AAAAA'], ['AAAAAA'])
            fund = FundInfo(
                id=None,
                ticker='B',
                name='BB',
                family='BBB',
                class_share='BBBB',
                fund_type='BBBBB',
                metadata=None)
            self.fund_info_db.insert_row(fund)

            data = self.fund_info_db.get_fund_info_data()
            self.assertEqual(len(data), 2)

            self.assertEquals(data[0].id, 1)
            self.assertEquals(data[0].ticker, 'A')
            self.assertEquals(data[0].name, 'AA')
            self.assertEquals(data[0].family, 'AAA')
            self.assertEquals(data[0].class_share, 'AAAA')
            self.assertEquals(data[0].fund_type, 'AAAAA')
            self.assertEquals(data[0].metadata, 'AAAAAA')

            self.assertEquals(data[1].id, 2)
            self.assertEquals(data[1].ticker, 'B')
            self.assertEquals(data[1].name, 'BB')
            self.assertEquals(data[1].family, 'BBB')
            self.assertEquals(data[1].class_share, 'BBBB')
            self.assertEquals(data[1].fund_type, 'BBBBB')
            self.assertEquals(data[1].metadata, None)
        finally:
            self.TearDown()


if __name__ == '__main__':
    unittest.main()


