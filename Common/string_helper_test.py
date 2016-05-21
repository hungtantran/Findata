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

    def test_extract_directory_and_file_name_from_path(self):
        (directory, file_name) = StringHelper.extract_directory_and_file_name_from_path('path/to/file.zip')
        self.assertEqual(directory, 'path/to')
        self.assertEqual(file_name, 'file.zip')

        (directory, file_name) = StringHelper.extract_directory_and_file_name_from_path('file.zip')
        self.assertEqual(directory, '.')
        self.assertEqual(file_name, 'file.zip')

    def test_remove_all_non_space_non_alphanumeric(self):
        self.assertEqual(StringHelper.remove_all_non_space_non_alphanumeric('@ROAD, INC'), 'ROAD INC')
        self.assertEqual(StringHelper.remove_all_non_space_non_alphanumeric('24/7 REAL MEDIA INC'), '247 REAL MEDIA INC')
        self.assertEqual(StringHelper.remove_all_non_space_non_alphanumeric('2-Track Global, Inc.'), '2Track Global Inc')
        self.assertEqual(StringHelper.remove_all_non_space_non_alphanumeric('8X8 INC /DE/'), '8X8 INC DE')


if __name__ == '__main__':
    unittest.main()
