__author__ = 'hungtantran'


import unittest

from Common.constants_config import Config
import Common.logger
from update_fixedincome_ustreasurybill import UpdateFixedincomeUstreasuryBill
import metrics
from metrics_database import MetricsDatabase
from string_helper import StringHelper


class TestUpdateFixedincomeUstreasuryBill(unittest.TestCase):
    HEADER_TITLES = ['1 mo', '3 mo', '6 mo', '1 yr', '2 yr', '3 yr', '7 yr', '10 yr', '20 yr', '30 yr']

    def test_parse_html_and_update_data(self):
        update_obj = UpdateFixedincomeUstreasuryBill('mysql',
                                                     Config.test_mysql_username,
                                                     Config.test_mysql_password,
                                                     Config.test_mysql_server,
                                                     Config.test_mysql_database)
        try:
            metrics_db = MetricsDatabase(
                    'mysql',
                    Config.test_mysql_username,
                    Config.test_mysql_password,
                    Config.test_mysql_server,
                    Config.test_mysql_database,
                    update_obj.tablename)

            metrics_db.create_metric()

            with open('UpdatePipeline/test_files/fixedincome_ustreasurybill_allyear.html') as f:
                html_content = f.read()

            update_obj.data = []
            update_obj.update_from_html_content(html_content)
            data = update_obj.data
            self.assertEquals(len(data), 27)

            ten_year_yield_data = [row for row in data if row.metric_name == '10_yr_yield']
            self.assertEquals(ten_year_yield_data[0].value, 7.94)
            self.assertEquals(ten_year_yield_data[0].start_date.strftime("%Y-%m-%d %H:%M:%S"), '1990-01-02 00:00:00')
            self.assertEquals(ten_year_yield_data[1].value, 7.98)
            self.assertEquals(ten_year_yield_data[1].start_date.strftime("%Y-%m-%d %H:%M:%S"), '1990-01-04 00:00:00')
            self.assertEquals(ten_year_yield_data[2].value, 7.99)
            self.assertEquals(ten_year_yield_data[2].start_date.strftime("%Y-%m-%d %H:%M:%S"), '1990-01-03 00:00:00')

            values = []
            values.append(metrics.Metrics(
                    metric_name='10_yr_yield',
                    start_date=StringHelper.convert_string_to_datetime('1990-01-02'),
                    end_date=StringHelper.convert_string_to_datetime('1990-01-02'),
                    unit='usd',
                    value=0.27))
            values.append(metrics.Metrics(
                    metric_name='10_yr_yield',
                    start_date=StringHelper.convert_string_to_datetime('1990-01-01'),
                    end_date=StringHelper.convert_string_to_datetime('1990-01-01'),
                    unit='usd',
                    value=0.28))
            metrics_db.insert_metrics(values)
            data = metrics_db.get_metrics()
            self.assertEqual(len(data), 2)

            for i in range(3):
                update_obj.update_database()
                data = metrics_db.get_metrics()
                self.assertEqual(len(data), 20)
        finally:
            metrics_db.remove_metric()

if __name__ == '__main__':
    unittest.main()


