__author__ = 'hungtantran'


import unittest

import logger
from model_data_service import ModelDataService
from timeline_model_database import TimelineModelDatabase


class TestModelDataService(unittest.TestCase):
    db_type = 'mysql'
    username = 'root'
    password = 'test'
    server = '104.154.40.63'
    database = 'models'

    def test_parse_and_insert_model_data(self):
        model_data_service = ModelDataService(TestModelDataService.db_type,
                                              TestModelDataService.username,
                                              TestModelDataService.password,
                                              TestModelDataService.server,
                                              TestModelDataService.database)
        model_data_service.parse_and_insert_model_data('.\\Common\\test_files\\daily_treasury_yield_curve.csv')

        model_db = TimelineModelDatabase(TestModelDataService.db_type,
                                         TestModelDataService.username,
                                         TestModelDataService.password,
                                         TestModelDataService.server,
                                         TestModelDataService.database)
        data = model_db.get_model_data('1 Mo')
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0][0].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')
        self.assertEqual(data[0][1], 0.29)
        self.assertEqual(data[1][0].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')
        self.assertEqual(data[1][1], 0.28)
        model_db.remove_model('1 Mo')

        data = model_db.get_model_data('3 Mo')
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0][0].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')
        self.assertEqual(data[0][1], 0.33)
        self.assertEqual(data[1][0].strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')
        self.assertEqual(data[1][1], 0.36)
        model_db.remove_model('3 Mo')


if __name__ == '__main__':
    unittest.main()