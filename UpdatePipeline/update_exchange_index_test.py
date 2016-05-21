__author__ = 'hungtantran'


import unittest

from Common.constants_config import Config
import Common.logger
from update_exchange_index import UpdateExchangeIndex
import metrics
from metrics_database import MetricsDatabase
from string_helper import StringHelper


class TestUpdateExchangeIndex(unittest.TestCase):
    SUMMARY_LINKS = {
        'nasdaq': 'http://finance.yahoo.com/q/hp?s=%5Eixic+historical+prices',
        'sp500': 'https://finance.yahoo.com/q/hp?s=%5EGSPC+Historical+Prices',
        'dowjones': 'https://finance.yahoo.com/q/hp?s=%5EDJI+Historical+Prices'}
    SUMMARY_DIMENSIONS = ['open', 'high', 'low', 'close', 'volume', 'adj_close']

    def test_parse_html_and_update_data(self):
        update_obj = UpdateExchangeIndex('mysql',
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
            with open('UpdatePipeline/test_files/exchange_index_dowjones.html') as f:
                html_content = f.read()

            update_obj.data = []
            update_obj.update_from_html_content('dowjones', html_content)
            data = update_obj.data
            self.assertEquals(len(data), 18)

            dowjones_open = [row for row in data if row.metric_name == 'dowjones_open']
            self.assertEquals(dowjones_open[0].value, 17555.39)
            self.assertEquals(dowjones_open[0].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-08 00:00:00')
            self.assertEquals(dowjones_open[1].value, 17687.28)
            self.assertEquals(dowjones_open[1].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-07 00:00:00')
            self.assertEquals(dowjones_open[2].value, 17605.45)
            self.assertEquals(dowjones_open[2].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-06 00:00:00')

            data = metrics_db.get_metrics()
            self.assertEqual(len(data), 0)

            values = []
            values.append(metrics.Metrics(
                    metric_name='dowjones_open',
                    start_date=StringHelper.convert_string_to_datetime('2016-04-06'),
                    end_date=StringHelper.convert_string_to_datetime('2016-04-06'),
                    unit='point',
                    value=0.27))
            values.append(metrics.Metrics(
                    metric_name='dowjones_open',
                    start_date=StringHelper.convert_string_to_datetime('2016-04-05'),
                    end_date=StringHelper.convert_string_to_datetime('2016-04-05'),
                    unit='point',
                    value=0.28))
            metrics_db.insert_metrics(values)
            data = metrics_db.get_metrics()
            self.assertEqual(len(data), 2)

            for i in range(2):
                update_obj.update_database()
                data = metrics_db.get_metrics()
                self.assertEqual(len(data), 14)
        finally:
            metrics_db.remove_metric()

if __name__ == '__main__':
    unittest.main()


