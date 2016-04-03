__author__ = 'hungtantran'


import unittest

import logger
from text_timeline_model_parser import TextTimelineModelParser


class TestTextTimelineModelParser(unittest.TestCase):
    def test_parse(self):
        parser = TextTimelineModelParser()
        (titles, dates, results) = parser.parse('.\\Common\\test_files\\daily_treasury_yield_curve.txt')

        # Verify title content
        self.assertEqual(len(titles), 2)
        self.assertEqual(titles[0], '1 Mo')
        self.assertEqual(titles[1], '3 Mo')

        # Verify dates content
        self.assertEqual(len(dates), 2)
        self.assertEqual(dates[0], '01/02/15')
        self.assertEqual(dates[1], '01/05/15')

        # Verify results content
        self.assertEqual(len(results), 2)
        for col in results:
            self.assertEqual(len(col), 2)

        self.assertEqual(results[0][0], 0.02)
        self.assertEqual(results[0][1], 0.02)
        self.assertEqual(results[1][0], 0.02)
        self.assertEqual(results[1][1], 0.03)


if __name__ == '__main__':
    unittest.main()