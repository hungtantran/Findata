__author__ = 'hungtantran'


import unittest

from Common.constants_config import Config
import Common.logger
from company_metrics_database import CompanyMetricsDatabase
from company_metrics import CompanyMetrics
from string_helper import StringHelper


class TestCompanyMetricsDatabase(unittest.TestCase):
    def test_connection(self):
        metrics_db = CompanyMetricsDatabase(
                'mysql',
                 Config.test_mysql_username,
                 Config.test_mysql_password,
                 Config.test_mysql_server,
                 Config.test_mysql_database,
                 'msft_metrics')
        try:
            metrics_db.remove_metric()
            metrics_db.create_metric()
            metric = CompanyMetrics(
                    metric_name='open',
                    value=1,
                    unit='usd',
                    start_date=StringHelper.convert_string_to_datetime('Mar 06 2016'),
                    end_date=StringHelper.convert_string_to_datetime('Mar 06 2016'))
            metrics_db.insert_metric(metric)

            metric = CompanyMetrics(
                    metric_name='open',
                    value=2,
                    unit='usd',
                    start_date=StringHelper.convert_string_to_datetime('Mar 07 2016'),
                    end_date=StringHelper.convert_string_to_datetime('Mar 07 2016'))
            metrics_db.insert_metric(metric)

            metrics = []
            metrics.append(CompanyMetrics(
                    metric_name='close',
                    value=4,
                    unit='usd',
                    start_date=StringHelper.convert_string_to_datetime('Mar 09 2016'),
                    end_date=StringHelper.convert_string_to_datetime('Mar 09 2016')
            ))
            metrics.append(CompanyMetrics(
                    metric_name='close',
                    value=3,
                    unit='usd',
                    start_date=StringHelper.convert_string_to_datetime('Mar 08 2016'),
                    end_date=StringHelper.convert_string_to_datetime('Mar 08 2016')
            ))
            metrics_db.insert_metrics(metrics)

            data = metrics_db.get_metrics()
            self.assertEqual(len(data), 4)

            data = metrics_db.get_metrics('open')
            self.assertEqual(len(data), 2)

            data = metrics_db.get_metrics('close')
            self.assertEqual(len(data), 2)

            metric = data[0]
            self.assertEquals(metric.metric_name, 'close')
            self.assertEquals(metric.value, 3)
            self.assertEquals(metric.unit, 'usd')
            self.assertEquals(metric.start_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-08 00:00:00')
            self.assertEquals(metric.end_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-08 00:00:00')

            metric = data[1]
            self.assertEquals(metric.metric_name, 'close')
            self.assertEquals(metric.value, 4)
            self.assertEquals(metric.unit, 'usd')
            self.assertEquals(metric.start_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-09 00:00:00')
            self.assertEquals(metric.end_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-09 00:00:00')
        finally:
            metrics_db.remove_metric()


if __name__ == '__main__':
    unittest.main()


