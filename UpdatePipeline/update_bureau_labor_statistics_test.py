__author__ = 'hungtantran'

import time
import unittest
import json

from Common.constants_config import Config
import Common.logger
from update_bureau_labor_statistics import UpdateBureauLaborStatistics
import metrics
from metrics_database import MetricsDatabase
from ticker_info import TickerInfo
from string_helper import StringHelper


class TestUpdateBureauLaborStatistics(unittest.TestCase):
    def SetUp(self):
        self.update_obj = UpdateBureauLaborStatistics(
                'mysql',
                Config.test_mysql_username,
                Config.test_mysql_password,
                Config.test_mysql_server,
                Config.test_mysql_database)

        self.metrics_db = MetricsDatabase(
                'mysql',
                Config.test_mysql_username,
                Config.test_mysql_password,
                Config.test_mysql_server,
                Config.test_mysql_database,
                'us_fundamentals')

        self.metrics_db.create_metric()

    def TearDown(self):
        self.metrics_db.remove_metric()

    def test_parse_html_and_update_all_data(self):
        try:
            self.SetUp()

            with open('UpdatePipeline/test_files/bureau_labor_statistics.html') as f:
                html_content = f.read()

            database_list = self.update_obj.parse_database_list_from_html(html_content)
            self.assertEqual(len(database_list), 41)

            with open('UpdatePipeline/test_files/bureau_labor_statistics_database.html') as f:
                html_content = f.read()
            measure_list = self.update_obj.parse_measure_list_from_html(html_content)
            self.assertEqual(len(measure_list), 6)

            measure_name, measure_series_id = measure_list[0]
            self.assertEqual(measure_name, 'Days Of Idleness Resulting From Work Stoppages In Effect In The Period.')
            self.assertEqual(measure_series_id, 'WSU001')

            with open('UpdatePipeline/test_files/bureau_labor_statistics_database_2.html') as f:
                html_content = f.read()
            measure_list = self.update_obj.parse_measure_list_from_html(html_content)
            self.assertEqual(len(measure_list), 51)

            measure_name, measure_series_id = measure_list[0]
            self.assertEqual(measure_name, 'All industries- Fatalities, Total')
            self.assertEqual(measure_series_id, 'FWU00X00000080N00')
        finally:
            self.TearDown()

    def test_parse_json_time_series(self):
        try:
            self.SetUp()

            with open('UpdatePipeline/test_files/bureau_labor_statistics.json') as f:
                json_text = f.read()
            measures = self.update_obj.parse_json_time_series('CUUR0000SA0', 'fake_metric', json_text)
            self.assertEqual(len(measures), 84)
            self.assertEqual(measures[0].metric_name, 'fake_metric')
            self.assertEqual(measures[0].start_date.strftime("%Y-%m-%d %H:%M:%S"), '1919-12-01 00:00:00')
            self.assertEqual(measures[0].end_date.strftime("%Y-%m-%d %H:%M:%S"), '1920-01-01 00:00:00')
            self.assertEqual(measures[0].unit, None)
            self.assertEqual(measures[0].value, 18.9)

            with open('UpdatePipeline/test_files/bureau_labor_statistics_2.json') as f:
                json_text = f.read()
            measures = self.update_obj.parse_json_time_series('EBUMEDINC00000AP', 'fake_metric2', json_text)
            self.assertEqual(len(measures), 3)
            self.assertEqual(measures[0].metric_name, 'fake_metric2')
            self.assertEqual(measures[0].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2006-01-01 00:00:00')
            self.assertEqual(measures[0].end_date.strftime("%Y-%m-%d %H:%M:%S"), '2007-01-01 00:00:00')
            self.assertEqual(measures[0].unit, None)
            self.assertEqual(measures[0].value, 52)
        finally:
            self.TearDown()


if __name__ == '__main__':
    unittest.main()


