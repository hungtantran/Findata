__author__ = 'hungtantran'


import unittest

from Common.constants_config import Config
import Common.logger
from update_fixedincome_ustreasurybill import UpdateFixedincomeUstreasuryBill
from timeline_model_database import TimelineModelDatabase


class TestUpdateFixedincomeUstreasuryBill(unittest.TestCase):
    HEADER_TITLES = ['1 mo', '3 mo', '6 mo', '1 yr', '2 yr', '3 yr', '7 yr', '10 yr', '20 yr', '30 yr']

    def test_parse_html_and_update_data(self):
        update_obj = UpdateFixedincomeUstreasuryBill('mysql',
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
        with open('UpdatePipeline/test_files/fixedincome_ustreasurybill_allyear.html') as f:
            html_content = f.read()

        data = update_obj.data
        self.assertEquals(len(data), 11)
        for title in TestUpdateFixedincomeUstreasuryBill.HEADER_TITLES:
            self.assertTrue(title in data)
            self.assertEquals(len(data[title]), 0)

        update_obj.update_from_html_content(html_content)
        for title in TestUpdateFixedincomeUstreasuryBill.HEADER_TITLES:
            self.assertTrue(title in data)

            if title == '1 mo' or title == '20 yr':
                self.assertEquals(len(data[title]), 0)
            else:
                self.assertEquals(len(data[title]), 3)

        self.assertEquals(data['10 yr'][0].value, 7.94)
        self.assertEquals(data['10 yr'][0].time.strftime("%Y-%m-%d %H:%M:%S"), '1990-01-02 00:00:00')
        self.assertEquals(data['10 yr'][1].value, 7.98)
        self.assertEquals(data['10 yr'][1].time.strftime("%Y-%m-%d %H:%M:%S"), '1990-01-04 00:00:00')
        self.assertEquals(data['10 yr'][2].value, 7.99)
        self.assertEquals(data['10 yr'][2].time.strftime("%Y-%m-%d %H:%M:%S"), '1990-01-03 00:00:00')

        try:

            model_db.create_model('fixedincome_ustreasurybill_10_yr')
            model_db.create_model('fixedincome_ustreasurybill_20_yr')

            data = model_db.get_model_data('fixedincome_ustreasurybill_10_yr')
            self.assertEqual(len(data), 0)
            data = model_db.get_model_data('fixedincome_ustreasurybill_20_yr')
            self.assertEqual(len(data), 0)

            times = ['1990-01-02', '1990-01-01']
            values = [0.27, 0.28]
            model_db.insert_values('fixedincome_ustreasurybill_10_yr', times, values)
            data = model_db.get_model_data('fixedincome_ustreasurybill_10_yr')
            self.assertEqual(len(data), 2)

            for i in range(2):
                update_obj.update_database()
                data = model_db.get_model_data('fixedincome_ustreasurybill_10_yr')
                self.assertEqual(len(data), 4)
                data = model_db.get_model_data('fixedincome_ustreasurybill_20_yr')
                self.assertEqual(len(data), 0)
        finally:
            model_db.remove_model('fixedincome_ustreasurybill_10_yr')
            model_db.remove_model('fixedincome_ustreasurybill_20_yr')

if __name__ == '__main__':
    unittest.main()


