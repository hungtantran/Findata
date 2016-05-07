__author__ = 'hungtantran'

import time
import unittest

from Common.constants_config import Config
import Common.logger
from update_exchange_fund import UpdateExchangeFund
import metrics
from metrics_database import MetricsDatabase
from fund_info_database import FundInfoDatabase
from fund_info import FundInfo
from string_helper import StringHelper


class TestUpdateExchangeFund(unittest.TestCase):
    def SetUp(self):
        self.update_obj = UpdateExchangeFund(
                'mysql',
                Config.test_mysql_username,
                Config.test_mysql_password,
                Config.test_mysql_server,
                Config.test_mysql_database)

        self.fund_info_db = FundInfoDatabase(
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
                'fund_fakefund_metrics')

    def TearDown(self):
    	self.fund_info_db.remove_fund_info_table()
        self.metrics_db.remove_metric()

    def test_parse_html_and_update_all_data(self):
        try:
            self.SetUp()

            # Update fund info
            with open('UpdatePipeline/test_files/fund_mutualfund.html') as f:
                html_content = f.read()

            data = self.update_obj.parse_fund_list_from_html(html_content)
            self.assertEquals(len(data), 3)

            self.assertEquals(data[0].ticker, 'AMTYX')
            self.assertEquals(data[0].name, 'AB All Market Real Return Portfolio')
            self.assertEquals(data[0].family, 'AB Bond Fund, Inc')
            self.assertEquals(data[0].class_share, 'Advisor Class Shares')

            self.assertEquals(data[2].ticker, 'WISEX')
            self.assertEquals(data[2].name, 'Azzad Wise Capital Fund')
            self.assertEquals(data[2].family, 'Azzad Funds')
            self.assertEquals(data[2].class_share, None)

            self.fund_info_db.create_fund_info_table()
            for _ in range(3):
                self.update_obj.update_fund_list(data)
                fund_data = self.fund_info_db.get_fund_info_data()
                self.assertEquals(len(data), 3)

            # Update fund metrics
            fake_fund_info = FundInfo(
            		id=None,
            		ticker='ff',
            		name='fakefund',
            		family='fakefamily',
            		class_share='fakeclass',
            		fund_type='faketype',
            		metadata='fakemetadata')

            with open('UpdatePipeline/test_files/exchange_fund_amtyx.html') as f:
                html_content = f.read()

           	self.metrics_db.create_metric()

            self.update_obj.current_ticker = 'fakefund'
            self.update_obj.tablename = 'fund_fakefund_metrics'
            self.update_obj.data = []
            data = self.update_obj.update_from_html_content(html_content)
            self.update_obj.data.extend(data)
            self.assertEquals(len(data), 396)

            fake_fund_open_data = [row for row in data if row.metric_name == 'open']
            self.assertEquals(fake_fund_open_data[0].value, 8.16)
            self.assertEquals(fake_fund_open_data[0].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2015-10-26 00:00:00')
            self.assertEquals(fake_fund_open_data[1].value, 8.24)
            self.assertEquals(fake_fund_open_data[1].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2015-10-23 00:00:00')
            self.assertEquals(fake_fund_open_data[2].value, 8.25)
            self.assertEquals(fake_fund_open_data[2].start_date.strftime("%Y-%m-%d %H:%M:%S"), '2015-10-22 00:00:00')

            data = self.metrics_db.get_metrics()
            self.assertEqual(len(data), 0)

            values = []
            values.append(metrics.Metrics(
                    metric_name='open',
                    start_date=StringHelper.convert_string_to_datetime('2015-10-22'),
                    end_date=StringHelper.convert_string_to_datetime('2015-10-22'),
                    unit='usd',
                    value=0.27))
            values.append(metrics.Metrics(
                    metric_name='close',
                    start_date=StringHelper.convert_string_to_datetime('2015-10-21'),
                    end_date=StringHelper.convert_string_to_datetime('2015-10-21'),
                    unit='usd',
                    value=0.28))
            self.metrics_db.insert_metrics(values)
            data = self.metrics_db.get_metrics()
            self.assertEqual(len(data), 2)

            
            num_update = self.update_obj.update_database(fake_fund_info, self.metrics_db)
            data = self.metrics_db.get_metrics()
            self.assertEqual(len(data), 14)
            self.assertEqual(num_update, 12)

            num_update = self.update_obj.update_database(fake_fund_info, self.metrics_db)
            data = self.metrics_db.get_metrics()
            self.assertEqual(len(data), 14)
            self.assertEqual(num_update, 0)
        finally:
            self.TearDown()


if __name__ == '__main__':
    unittest.main()