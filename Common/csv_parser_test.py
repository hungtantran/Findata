__author__ = 'hungtantran'


import unittest

import logger
from csv_parser import CsvParser


class TestCsvParser(unittest.TestCase):
    def test_parse(self):
        parser = CsvParser()
        (titles, dates, results) = parser.parse('.\\Common\\test_files\\daily_treasury_yield_curve.csv')

        # Verify title content
        self.assertEqual(len(titles), 2)
        self.assertEqual(titles[0], '1 Mo')
        self.assertEqual(titles[1], '3 Mo')

        # Verify dates content
        self.assertEqual(len(dates), 2)
        self.assertEqual(dates[0], '3/1/2016')
        self.assertEqual(dates[1], '3/2/2016')

        # Verify results content
        self.assertEqual(len(results), 2)
        for col in results:
            self.assertEqual(len(col), 2)

        self.assertEqual(results[0][0], 0.29)
        self.assertEqual(results[0][1], 0.28)
        self.assertEqual(results[1][0], 0.33)
        self.assertEqual(results[1][1], 0.36)


if __name__ == '__main__':
    unittest.main()