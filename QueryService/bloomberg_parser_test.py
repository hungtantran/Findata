__author__ = 'hungtantran'

import unittest
from bs4 import BeautifulSoup


import bloomberg_parser


class TestBloombergParser(unittest.TestCase):
    def test_parse(self):
        html_content = None
        with open(".\\QueryService\\test_html\\bloomberg_commodities.html", "r") as file:
            html_content = file.read()

        html = BeautifulSoup(html_content, 'html.parser')
        table_containers = bloomberg_parser.BloombergParser.parse_table_containers_from_html(html)
        self.assertEqual(4, len(table_containers))

        for index in range(len(table_containers)):
            table = table_containers[index]
            # Find the header and parse it to get header titles and verify them
            header_cell_titles = bloomberg_parser.BloombergParser.parse_header_titles_from_table(table)
            if index == 0:
                expected_titles = ['index', 'value', 'change', '%change', 'high', 'low', 'time (edt)', '2 day']
                self.assertEqual(len(expected_titles), len(header_cell_titles))
                for index2 in range(len(expected_titles)):
                    self.assertEqual(expected_titles[index2], header_cell_titles[index2])
            else:
                expected_titles = ['index', 'units', 'price', 'change', '%change', 'contract', 'time (edt)', '2 day']
                self.assertEqual(len(expected_titles), len(header_cell_titles))
                for index2 in range(len(expected_titles)):
                    self.assertEqual(expected_titles[index2], header_cell_titles[index2])

            # Parse all the data rows from the current table and verify them
            data_rows = bloomberg_parser.BloombergParser.parse_rows_from_table(table)
            self.assertEqual(5, len(data_rows))
            for row in data_rows:
                row_cells = bloomberg_parser.BloombergParser.parse_values_from_row(row)
                self.assertEqual(8, len(row_cells))


if __name__ == '__main__':
    unittest.main()