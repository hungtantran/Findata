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
        try:
            model_db.create_model('bond_1_Mo')
            model_db.insert_value('bond_1_Mo', '3/1/2016', 0.29)
            model_db.insert_value('bond_1_Mo', '2016-03-02', 0.28)

            times = ['2016-03-03', 'Mar 04 2016']
            values = [0.27, 0.26]
            model_db.insert_values('bond_1_Mo', times, values)

            data = model_db.get_model_data('bond_1_Mo')
            self.assertEqual(len(data), 4)
            self.assertEqual(data[0][0].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')
            self.assertEqual(data[0][1], 0.29)
            self.assertEqual(data[1][0].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')
            self.assertEqual(data[1][1], 0.28)
            self.assertEqual(data[2][0].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-03 00:00:00')
            self.assertEqual(data[2][1], 0.27)
            self.assertEqual(data[3][0].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-04 00:00:00')
            self.assertEqual(data[3][1], 0.26)
            self.assertAlmostEqual(model_db.get_average_model_data('bond_1_Mo'), 0.275)
        finally:
            model_db.remove_model('bond_1_Mo')

    def test_convert_time(self):
        time = TimelineModelDatabase.convert_time('3/1/2016')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')

        time = TimelineModelDatabase.convert_time('2016-03-02')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')

        time = TimelineModelDatabase.convert_time('2016/03/03')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-03 00:00:00')

        time = TimelineModelDatabase.convert_time('03/04/16')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-04 00:00:00')

        time = TimelineModelDatabase.convert_time('Mar 05, 2016')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-05 00:00:00')

        time = TimelineModelDatabase.convert_time('Mar 06 2016')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-06 00:00:00')

        time = TimelineModelDatabase.convert_time('07-Mar-16')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-07 00:00:00')

        time = TimelineModelDatabase.convert_time('08-Mar-2016')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-08 00:00:00')

if __name__ == '__main__':
    unittest.main()


