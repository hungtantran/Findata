__author__ = 'hungtantran'


import unittest

from constants_config import Config
import logger
from timeline_model_database import TimelineModelDatabase


class TestTimelineModelDatabase(unittest.TestCase):
    def test_connection(self):
        model_db = TimelineModelDatabase('mysql',
                                         Config.test_mysql_username,
                                         Config.test_mysql_password,
                                         Config.test_mysql_server,
                                         Config.test_mysql_database)
        model_db.create_model('bond_1_Mo')
        model_db.insert_value('bond_1_Mo', '3/1/2016', 0.29)
        model_db.insert_value('bond_1_Mo', '2016-03-02', 0.28)
        data = model_db.get_model_data('bond_1_Mo')
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0][0].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')
        self.assertEqual(data[0][1], 0.29)
        self.assertEqual(data[1][0].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')
        self.assertEqual(data[1][1], 0.28)
        model_db.remove_model('bond_1_Mo')


if __name__ == '__main__':
    unittest.main()


