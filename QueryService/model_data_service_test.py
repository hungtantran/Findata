__author__ = 'hungtantran'


import unittest

from constants_config import Config
import logger
from model_data_service import ModelDataService
from timeline_model_database import TimelineModelDatabase


class TestModelDataService(unittest.TestCase):
    db_type = 'mysql'

    def test_parse_and_insert_model_data_from_file(self):
        model_db = TimelineModelDatabase(TestModelDataService.db_type,
                                         Config.test_mysql_username,
                                         Config.test_mysql_password,
                                         Config.test_mysql_server,
                                         Config.test_mysql_database)
        model_db.remove_model('1 Mo')
        model_db.remove_model('3 Mo')

        model_data_service = ModelDataService(TestModelDataService.db_type,
                                              Config.test_mysql_username,
                                              Config.test_mysql_password,
                                              Config.test_mysql_server,
                                              Config.test_mysql_database)
        model_data_service.parse_and_insert_model_data_from_file('.\\QueryService\\test_files\\daily_treasury_yield_curve.csv')
        try:
            data = model_db.get_model_data('1 Mo')
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')
            self.assertEqual(data[0].value, 0.29)
            self.assertEqual(data[1].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')
            self.assertEqual(data[1].value, 0.28)
        finally:
            model_db.remove_model('1 Mo')

        try:
            data = model_db.get_model_data('3 Mo')
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')
            self.assertEqual(data[0].value, 0.33)
            self.assertEqual(data[1].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')
            self.assertEqual(data[1].value, 0.36)
        finally:
            model_db.remove_model('3 Mo')

    def test_parse_and_insert_model_data_from_directory(self):
        model_db = TimelineModelDatabase(TestModelDataService.db_type,
                                         Config.test_mysql_username,
                                         Config.test_mysql_password,
                                         Config.test_mysql_server,
                                         Config.test_mysql_database)

        model_db.remove_model('1 Mo')
        model_db.remove_model('3 Mo')

        model_data_service = ModelDataService(TestModelDataService.db_type,
                                              Config.test_mysql_username,
                                              Config.test_mysql_password,
                                              Config.test_mysql_server,
                                              Config.test_mysql_database)
        model_data_service.parse_and_insert_model_data_from_directory('.\\Common\\test_files\\')

        try:
            data = model_db.get_model_data('1 Mo')
            self.assertEqual(len(data), 4)
            self.assertEqual(data[0].time.strftime("%Y-%m-%d %H:%M:%S"), '2015-01-02 00:00:00')
            self.assertEqual(data[0].value, 0.02)
            self.assertEqual(data[1].time.strftime("%Y-%m-%d %H:%M:%S"), '2015-01-05 00:00:00')
            self.assertEqual(data[1].value, 0.02)
            self.assertEqual(data[2].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')
            self.assertEqual(data[2].value, 0.29)
            self.assertEqual(data[3].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')
            self.assertEqual(data[3].value, 0.28)
        finally:
            model_db.remove_model('1 Mo')

        try:
            data = model_db.get_model_data('3 Mo')
            self.assertEqual(len(data), 4)
            self.assertEqual(data[0].time.strftime("%Y-%m-%d %H:%M:%S"), '2015-01-02 00:00:00')
            self.assertEqual(data[0].value, 0.02)
            self.assertEqual(data[1].time.strftime("%Y-%m-%d %H:%M:%S"), '2015-01-05 00:00:00')
            self.assertEqual(data[1].value, 0.03)
            self.assertEqual(data[2].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')
            self.assertEqual(data[2].value, 0.33)
            self.assertEqual(data[3].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')
            self.assertEqual(data[3].value, 0.36)
        finally:
            model_db.remove_model('3 Mo')


if __name__ == '__main__':
    unittest.main()