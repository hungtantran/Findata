__author__ = 'hungtantran'


import os
import unittest

import logger
from constants_config import Config
from sec_xbrl_index_file_parser import SecXbrlIndexFileParser


class TestSecXbrlIndexFileParser(unittest.TestCase):
    def test_parse(self):
        parser = SecXbrlIndexFileParser()
        results = parser.parse(source_name='SEC\\test_files\\latest_xbrl.idx')

        self.assertEqual(5, len(results))
        for row in results:
            self.assertEqual(2, len(row))

        # Verify CIK
        self.assertEqual(results[0][0], 1027596)
        self.assertEqual(results[0][1], 1070235)

        # Verify company name
        self.assertEqual(results[1][0], 'ADVISORS SERIES TRUST')
        self.assertEqual(results[1][1], 'BLACKBERRY Ltd')

        # Verify form type
        self.assertEqual(results[2][0], '485BPOS')
        self.assertEqual(results[2][1], '40-F')

        # Verify date filed
        self.assertEqual(results[3][0].strftime("%Y-%m-%d %H:%M:%S"), '2016-04-01 00:00:00')
        self.assertEqual(results[3][1].strftime("%Y-%m-%d %H:%M:%S"), '2016-04-01 00:00:00')

        # Verify file name
        self.assertEqual(results[4][0], '0000894189-16-008706')
        self.assertEqual(results[4][1], '0001070235-16-000129')


if __name__ == '__main__':
    unittest.main()
