__author__ = 'hungtantran'


import unittest

import Common.logger
from yahoo_historical_parser import YahooHistoricalParser


class TestYahooHistoricalParser(unittest.TestCase):
    def test_parse(self):
        parser = YahooHistoricalParser()
        (titles, dates, results) = parser.parse(
            source_name='http://finance.yahoo.com/q/hp?s=MSFT&a=2&b=13&c=1986&d=2&e=27&f=2016&g=d&z=66&y=0',
            max_num_results=2)

        # Verify title content
        self.assertEqual(len(titles), 6)
        self.assertEqual(titles[0], 'open')
        self.assertEqual(titles[1], 'high')
        self.assertEqual(titles[2], 'low')
        self.assertEqual(titles[3], 'close')
        self.assertEqual(titles[4], 'volume')
        self.assertEqual(titles[5], 'adj close*')

        # Verify dates content
        self.assertEqual(len(dates), 2)

        # Verify results content
        self.assertEqual(len(results), 6)
        for col in results:
            self.assertEqual(len(col), 2)


if __name__ == '__main__':
    unittest.main()