__author__ = 'hungtantran'


import unittest

import logger
from generic_file_parser import GenericFileParser


class TestGenericFileParser(unittest.TestCase):
    def test_parse_csv(self):
        parser = GenericFileParser()
        (titles, results) = parser.parse(source_name='.\\Common\\test_files\\daily_treasury_yield_curve.csv',
                                         delimiter=',',
                                         has_title=True)

        # Verify title content
        self.assertEqual(len(titles), 3)
        self.assertEqual(titles[0], 'Date')
        self.assertEqual(titles[1], '1 Mo')
        self.assertEqual(titles[2], '3 Mo')

        # Verify results content
        self.assertEqual(len(results), 3)
        for row in results:
            self.assertEqual(len(row), 2)

        self.assertEqual(results[0][0], '3/1/2016')
        self.assertEqual(results[0][1], '3/2/2016')
        self.assertEqual(results[1][0], '0.29')
        self.assertEqual(results[1][1], '0.28')
        self.assertEqual(results[2][0], '0.33')
        self.assertEqual(results[2][1], '0.36')

    def test_parse_txt(self):
        parser = GenericFileParser()
        (titles, results) = parser.parse(source_name='.\\Common\\test_files\\daily_treasury_yield_curve.txt',
                                         delimiter='\t',
                                         has_title=True)

        # Verify title content
        self.assertEqual(len(titles), 3)
        self.assertEqual(titles[0], 'Date')
        self.assertEqual(titles[1], '1 Mo')
        self.assertEqual(titles[2], '3 Mo')

        # Verify results content
        self.assertEqual(len(results), 3)
        for row in results:
            self.assertEqual(len(row), 2)

        self.assertEqual(results[0][0], '01/02/15')
        self.assertEqual(results[0][1], '01/05/15')
        self.assertEqual(results[1][0], '0.02')
        self.assertEqual(results[1][1], '0.02')
        self.assertEqual(results[2][0], '0.02')
        self.assertEqual(results[2][1], '0.03')


if __name__ == '__main__':
    unittest.main()