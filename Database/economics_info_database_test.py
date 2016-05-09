__author__ = 'hungtantran'


import unittest

from Common.constants_config import Config
import Common.logger
from economics_info_database import EconomicsInfoDatabase
from economics_info import EconomicsInfo


class TestEconomicsInfoDatabase(unittest.TestCase):
    def SetUp(self):
        self.economics_info_db = EconomicsInfoDatabase(
                'mysql',
                Config.test_mysql_username,
                Config.test_mysql_password,
                Config.test_mysql_server,
                Config.test_mysql_database,
                'economics_info')
        self.economics_info_db.create_economics_info_table()

    def TearDown(self):
        self.economics_info_db.remove_economics_info_table()

    def test_connection(self):
        try:
            self.SetUp()

            economics_info_obj = EconomicsInfo(
                id=None,
                name='A',
                location='AA',
                category='AAA',
                type='AAAA',
                source='AAAAA',
                metadata='AAAAAA')
            self.economics_info_db.insert_row(economics_info_obj)
            
            economics_info_obj = EconomicsInfo(
                id=None,
                name='B',
                location='BB',
                category='BBB',
                type='BBBB',
                source='BBBBB',
                metadata='BBBBBB')
            self.economics_info_db.insert_row(economics_info_obj)

            data = self.economics_info_db.get_economics_info_data()
            self.assertEqual(len(data), 2)

            self.assertEquals(data[0].id, 1)
            self.assertEquals(data[0].name, 'A')
            self.assertEquals(data[0].location, 'AA')
            self.assertEquals(data[0].category, 'AAA')
            self.assertEquals(data[0].type, 'AAAA')
            self.assertEquals(data[0].source, 'AAAAA')
            self.assertEquals(data[0].metadata, 'AAAAAA')

            self.assertEquals(data[1].id, 2)
            self.assertEquals(data[1].name, 'B')
            self.assertEquals(data[1].location, 'BB')
            self.assertEquals(data[1].category, 'BBB')
            self.assertEquals(data[1].type, 'BBBB')
            self.assertEquals(data[1].source, 'BBBBB')
            self.assertEquals(data[1].metadata, 'BBBBBB')
        finally:
            self.TearDown()

if __name__ == '__main__':
    unittest.main()


