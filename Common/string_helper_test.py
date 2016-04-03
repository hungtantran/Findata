__author__ = 'hungtantran'


import unittest

import logger
from string_helper import StringHelper

class TestStringHelper(unittest.TestCase):
    def test_convert_string_to_datetime(self):
        time = StringHelper.convert_string_to_datetime('3/1/2016')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-01 00:00:00')

        time = StringHelper.convert_string_to_datetime('2016-03-02')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-02 00:00:00')

        time = StringHelper.convert_string_to_datetime('2016/03/03')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-03 00:00:00')

        time = StringHelper.convert_string_to_datetime('03/04/16')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-04 00:00:00')

        time = StringHelper.convert_string_to_datetime('Mar 05, 2016')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-05 00:00:00')

        time = StringHelper.convert_string_to_datetime('Mar 06 2016')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-06 00:00:00')

        time = StringHelper.convert_string_to_datetime('07-Mar-16')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-07 00:00:00')

        time = StringHelper.convert_string_to_datetime('08-Mar-2016')
        self.assertEqual(time.strftime("%Y-%m-%d %H:%M:%S"), '2016-03-08 00:00:00')


if __name__ == '__main__':
    unittest.main()
