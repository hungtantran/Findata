__author__ = 'hungtantran'


import unittest

from Common.constants_config import Config
import Common.logger
from update_exchange_index import UpdateExchangeIndex
from timeline_model_database import TimelineModelDatabase


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
        model_db = TimelineModelDatabase('mysql',
                                         Config.test_mysql_username,
                                         Config.test_mysql_password,
                                         Config.test_mysql_server,
                                         Config.test_mysql_database)

        html_content = ''
        with open('UpdatePipeline/test_files/exchange_index_dowjones.html') as f:
            html_content = f.read()

        data = update_obj.data
        self.assertEquals(len(data), 18)
        for index in TestUpdateExchangeIndex.SUMMARY_LINKS:
            for title in TestUpdateExchangeIndex.SUMMARY_DIMENSIONS:
                dim = index + '_' + title
                self.assertTrue(dim in data)
                self.assertEquals(len(data[dim]), 0)

        update_obj.update_from_html_content('dowjones', html_content)
        for index in TestUpdateExchangeIndex.SUMMARY_LINKS:
            for title in TestUpdateExchangeIndex.SUMMARY_DIMENSIONS:
                dim = index + '_' + title
                if 'dowjones' in dim:
                    self.assertEquals(len(data[dim]), 3)
                else:
                    self.assertEquals(len(data[dim]), 0)

        self.assertEquals(data['dowjones_open'][0].value, 17555.39)
        self.assertEquals(data['dowjones_open'][0].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-08 00:00:00')
        self.assertEquals(data['dowjones_open'][1].value, 17687.28)
        self.assertEquals(data['dowjones_open'][1].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-07 00:00:00')
        self.assertEquals(data['dowjones_open'][2].value, 17605.45)
        self.assertEquals(data['dowjones_open'][2].time.strftime("%Y-%m-%d %H:%M:%S"), '2016-04-06 00:00:00')

        try:

            model_db.create_model('exchange_index_dowjones_open')

            data = model_db.get_model_data('exchange_index_dowjones_open')
            self.assertEqual(len(data), 0)

            times = ['2016-04-06', '2016-04-05']
            values = [0.27, 0.28]
            model_db.insert_values('exchange_index_dowjones_open', times, values)
            data = model_db.get_model_data('exchange_index_dowjones_open')
            self.assertEqual(len(data), 2)

            for i in range(2):
                update_obj.update_database()
                data = model_db.get_model_data('exchange_index_dowjones_open')
                self.assertEqual(len(data), 4)
        finally:
            model_db.remove_model('exchange_index_dowjones_open')

if __name__ == '__main__':
    unittest.main()


