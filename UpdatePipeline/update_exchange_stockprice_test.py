__author__ = 'hungtantran'


import unittest

from Common.constants_config import Config
import Common.logger
from update_exchange_stockprice import UpdateExchangeStockprice
from timeline_model_database import TimelineModelDatabase
from ticker_info import TickerInfo


class TestUpdateExchangeStockprice(unittest.TestCase):
    SUMMARY_LINKS_TEMPLATE = 'http://finance.yahoo.com/q/hp?s=%s+Historical+Prices'
    SUMMARY_DIMENSIONS = ['open', 'high', 'low', 'close', 'volume', 'adj_close']

    def test_parse_html_and_update_data(self):
        update_obj = UpdateExchangeStockprice('mysql',
                                              Config.test_mysql_username,
                                              Config.test_mysql_password,
                                              Config.test_mysql_server,
                                              Config.test_mysql_database)
        model_db = TimelineModelDatabase('mysql',
                                         Config.test_mysql_username,
                                         Config.test_mysql_password,
                                         Config.test_mysql_server,
                                         Config.test_mysql_database)

        html_content = ''
        with open('UpdatePipeline/test_files/exchange_stockprice_msft.html') as f:
            html_content = f.read()

        data = update_obj.data
        self.assertEquals(len(data), 0)

        msft_ticker = TickerInfo(cik=789019,
                                 ticker='MSFT',
                                 name='Microsoft Corporation',
                                 ipo_year=1986,
                                 sector='Technology',
                                 industry='Computer Software: Prepackaged Software',
                                 exchange='NASDAQ')
        update_obj.sanitize_info(msft_ticker)

        data = update_obj.data
        for dimension in UpdateExchangeStockprice.SUMMARY_DIMENSIONS:
            data[update_obj.get_data_source_name(msft_ticker, dimension)] = []
        self.assertEquals(len(data), 6)

        for key in data:
            update_obj.tablename[key] = 'exchange_stockprice_' + key

        update_obj.update_from_html_content(msft_ticker, html_content)
        for title in UpdateExchangeStockprice.SUMMARY_DIMENSIONS:
            dim = update_obj.get_data_source_name(msft_ticker, title)
            self.assertEquals(len(data[dim]), 66)

        self.assertEquals(data['msft_open'][0].value, 54.37)
        self.assertEquals(data['msft_open'][0].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-12 00:00:00')
        self.assertEquals(data['msft_open'][1].value, 54.49)
        self.assertEquals(data['msft_open'][1].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-11 00:00:00')
        self.assertEquals(data['msft_open'][2].value, 54.67)
        self.assertEquals(data['msft_open'][2].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-08 00:00:00')

        try:

            model_db.create_model('exchange_stockprice_msft_open')

            data = model_db.get_model_data('exchange_stockprice_msft_open')
            self.assertEqual(len(data), 0)

            times = ['2016-04-10', '2016-04-09']
            values = [0.27, 0.28]
            model_db.insert_values('exchange_stockprice_msft_open', times, values)
            data = model_db.get_model_data('exchange_stockprice_msft_open')
            self.assertEqual(len(data), 2)

            for i in range(2):
                update_obj.update_database(msft_ticker)
                data = model_db.get_model_data('exchange_stockprice_msft_open')
                self.assertEqual(len(data), 4)
        finally:
            model_db.remove_model('exchange_stockprice_msft_open')

if __name__ == '__main__':
    unittest.main()


