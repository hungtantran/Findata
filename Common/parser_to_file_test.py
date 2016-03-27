__author__ = 'hungtantran'


import os
import unittest

import logger
from parser_to_file import ParserToFile
from csv_parser_test import CsvParser


class TestParserToFile(unittest.TestCase):
    def test_write_parse_result_to_file(self):
        try:
            titles = ['Test Val', 'Test Val 2']
            dates = ['3/1/2016', '3/2/2016']
            results = [[1, 2], [3, 4]]
            ParserToFile.write_parse_result_to_file(titles, dates, results,
                                                    output_file_name='test_parse_result_to_file.csv',
                                                    delimiter=',')

            parser = CsvParser()
            (titles, dates, results) = parser.parse('test_parse_result_to_file.csv')

            # Verify title content
            self.assertEqual(len(titles), 2)
            self.assertEqual(titles[0], 'Test Val')
            self.assertEqual(titles[1], 'Test Val 2')

            # Verify dates content
            self.assertEqual(len(dates), 2)
            self.assertEqual(dates[0], '3/1/2016')
            self.assertEqual(dates[1], '3/2/2016')

            # Verify results content
            self.assertEqual(len(results), 2)
            for col in results:
                self.assertEqual(len(col), 2)

            self.assertEqual(results[0][0], 1)
            self.assertEqual(results[0][1], 2)
            self.assertEqual(results[1][0], 3)
            self.assertEqual(results[1][1], 4)
        finally:
            os.remove('test_parse_result_to_file.csv')


if __name__ == '__main__':
    unittest.main()
