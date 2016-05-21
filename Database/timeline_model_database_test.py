__author__ = 'hungtantran'


import unittest

from Common.constants_config import Config
import Common.logger
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
            self.assertEqual(data[0].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')
            self.assertEqual(data[0].value, 0.29)
            self.assertEqual(data[1].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')
            self.assertEqual(data[1].value, 0.28)
            self.assertEqual(data[2].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-03 00:00:00')
            self.assertEqual(data[2].value, 0.27)
            self.assertEqual(data[3].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-04 00:00:00')
            self.assertEqual(data[3].value, 0.26)
            self.assertAlmostEqual(model_db.get_average_model_data('bond_1_Mo'), 0.275)
            self.assertGreater(model_db.get_std_model_data('bond_1_Mo'), 0)

            data = model_db.get_latest_model_data('bond_1_Mo')
            self.assertEqual(data.time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-04 00:00:00')
            self.assertEqual(data.value, 0.26)
        finally:
            model_db.remove_model('bond_1_Mo')

    def test_get_tables(self):
        model_db = TimelineModelDatabase('mysql',
                                         Config.test_mysql_username,
                                         Config.test_mysql_password,
                                         Config.test_mysql_server,
                                         Config.test_mysql_database)
        try:
            tables = []
            for i in range(3):
                tables.append('fake%d' % i)
                model_db.create_model('fake%d' % i)

            tables_found = model_db.get_all_models_names()
            for table in tables:
                self.assertTrue(table in tables_found)
        finally:
            for table in tables:
                model_db.remove_model(table)


if __name__ == '__main__':
    unittest.main()


