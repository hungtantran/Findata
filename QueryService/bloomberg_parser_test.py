__author__ = 'hungtantran'

import unittest
from bs4 import BeautifulSoup


import bloomberg_parser


class TestBloombergParser(unittest.TestCase):
    def test_get_table_containers(self):
        with open(".\\QueryService\\test_html\\bloomberg_commodities.html", "r") as file:
            html = BeautifulSoup(file.read(), 'html.parser')
            table_containers = bloomberg_parser.BloombergParser.parse_table_containers(html)
            self.assertEqual(4, len(table_containers))


if __name__ == '__main__':
    unittest.main()