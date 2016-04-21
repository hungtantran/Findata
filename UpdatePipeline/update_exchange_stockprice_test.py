__author__ = 'hungtantran'

import time
import unittest

from Common.constants_config import Config
import Common.logger
from update_exchange_stockprice import UpdateExchangeStockprice
import metrics
from metrics_database import MetricsDatabase
from ticker_info import TickerInfo
from string_helper import StringHelper


class TestUpdateExchangeStockprice(unittest.TestCase):
    SUMMARY_LINKS_TEMPLATE = 'http://finance.yahoo.com/q/hp?s=%s+Historical+Prices'
    SUMMARY_DIMENSIONS = ['open', 'high', 'low', 'close', 'volume', 'adj_close']

    def test_parse_html_and_update_all_data(self):
        update_obj = UpdateExchangeStockprice(
                'mysql',
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
                    'msft_metrics')

            metrics_db.create_metric()
            with open('UpdatePipeline/test_files/exchange_stockprice_msft.html') as f:
                html_content = f.read()

            msft_ticker = TickerInfo(cik=789019,
                                     ticker='MSFT',
                                     name='Microsoft Corporation',
                                     ipo_year=1986,
                                     sector='Technology',
                                     industry='Computer Software: Prepackaged Software',
                                     exchange='NASDAQ')
            update_obj.sanitize_info(msft_ticker)

            update_obj.current_ticker = 'msft'
            update_obj.tablename = 'msft_metrics'
            update_obj.data = []
            update_obj.update_from_html_content(msft_ticker, html_content)
            data = update_obj.data
            self.assertEquals(len(data), 399)

            msft_open_data = [row for row in data if row.metric_name == 'open']
            self.assertEquals(msft_open_data[0].value, 54.37)
            self.assertEquals(msft_open_data[0].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-12 00:00:00')
            self.assertEquals(msft_open_data[1].value, 54.49)
            self.assertEquals(msft_open_data[1].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-11 00:00:00')
            self.assertEquals(msft_open_data[2].value, 54.67)
            self.assertEquals(msft_open_data[2].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-08 00:00:00')

            msft_dividend_data = [row for row in data if row.metric_name == 'dividend']
            self.assertEquals(len(msft_dividend_data), 2)
            self.assertEquals(msft_dividend_data[0].value, 0.36)
            self.assertEquals(msft_dividend_data[0].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-02-16 00:00:00')
            self.assertEquals(msft_dividend_data[1].value, 0.48)
            self.assertEquals(msft_dividend_data[1].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-11 00:00:00')

            msft_stock_split_data = [row for row in data if row.metric_name == 'stock split']
            self.assertEquals(len(msft_stock_split_data), 1)
            self.assertEquals(msft_stock_split_data[0].value, 0.2)
            self.assertEquals(msft_stock_split_data[0].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-12 00:00:00')

            data = metrics_db.get_metrics()
            self.assertEqual(len(data), 0)

            values = []
            values.append(metrics.Metrics(
                    metric_name='open',
                    start_date=StringHelper.convert_string_to_datetime('2016-04-10'),
                    end_date=StringHelper.convert_string_to_datetime('2016-04-10'),
                    unit='usd',
                    value=0.27))
            values.append(metrics.Metrics(
                    metric_name='close',
                    start_date=StringHelper.convert_string_to_datetime('2016-04-09'),
                    end_date=StringHelper.convert_string_to_datetime('2016-04-09'),
                    unit='usd',
                    value=0.28))
            metrics_db.insert_metrics(values)
            data = metrics_db.get_metrics()
            self.assertEqual(len(data), 2)

            for i in range(3):
                update_obj.update_database(msft_ticker, metrics_db)
                data = metrics_db.get_metrics()
                self.assertEqual(len(data), 16)
        finally:
            metrics_db.remove_metric()

    def test_parse_html_and_update_dividend(self):
        update_obj = UpdateExchangeStockprice(
                'mysql',
                Config.test_mysql_username,
                Config.test_mysql_password,
                Config.test_mysql_server,
                Config.test_mysql_database,
                update_historical_dividend=True)

        try:
            metrics_db = MetricsDatabase(
                    'mysql',
                    Config.test_mysql_username,
                    Config.test_mysql_password,
                    Config.test_mysql_server,
                    Config.test_mysql_database,
                    'msft_metrics')

            metrics_db.create_metric()
            with open('UpdatePipeline/test_files/exchange_dividend_msft.html') as f:
                html_content = f.read()

            msft_ticker = TickerInfo(cik=789019,
                                     ticker='MSFT',
                                     name='Microsoft Corporation',
                                     ipo_year=1986,
                                     sector='Technology',
                                     industry='Computer Software: Prepackaged Software',
                                     exchange='NASDAQ')
            update_obj.sanitize_info(msft_ticker)

            update_obj.current_ticker = 'msft'
            update_obj.tablename = 'msft_metrics'
            update_obj.data = []
            update_obj.update_from_html_content(msft_ticker, html_content)
            data = update_obj.data
            self.assertEquals(len(data), 58)

            msft_dividend_data = [row for row in data if row.metric_name == 'dividend']
            self.assertEquals(len(msft_dividend_data), 49)
            self.assertEquals(msft_dividend_data[0].value, 0.36)
            self.assertEquals(msft_dividend_data[0].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2016-02-16 00:00:00')
            self.assertEquals(msft_dividend_data[1].value, 0.36)
            self.assertEquals(msft_dividend_data[1].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2015-11-17 00:00:00')

            msft_stock_split_data = [row for row in data if row.metric_name == 'stock split']
            self.assertEquals(len(msft_stock_split_data), 9)
            self.assertEquals(msft_stock_split_data[0].value, 2)
            self.assertEquals(msft_stock_split_data[0].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2003-02-18 00:00:00')

            data = metrics_db.get_metrics()
            self.assertEqual(len(data), 0)

            for i in range(3):
                update_obj.update_database(msft_ticker, metrics_db)
                data = metrics_db.get_metrics()
                self.assertEqual(len(data), 58)
        finally:
            metrics_db.remove_metric()

if __name__ == '__main__':
    unittest.main()


