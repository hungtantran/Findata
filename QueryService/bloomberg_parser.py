__author__ = 'hungtantran'


from bs4 import BeautifulSoup
import urllib

import logger
import re

class BloombergParser:
    def __init__(self):
        self.parser_type = 'html.parser'

    @staticmethod
    def clean_name(name_str):
        name_str = name_str.strip()
        name_str = name_str.replace('\n', '')
        name_str = re.sub('( )+', ' ', name_str)
        return name_str

    @staticmethod
    def parse_table_containers(html_elem):
        return html_elem.findAll('div', attrs={'class': 'table-container'})

    def parse(self, link):
        logger.Logger.log(logger.LogLevel.INFO, 'BloombergParser attempts to parse link \'%s\'' % (link))
        link_handle = urllib.urlopen(link)
        html = BeautifulSoup(link_handle.read(), self.parser_type)

        table_containers = self.parse_table_containers(html)

        # Iterate through each table
        for table in table_containers:
            # Find the header and parse it
            header = table.findAll('tr', attrs={'class': 'data-table__headers'})
            if len(header) != 1:
                logger.Logger.log(logger.LogLevel.WARN, 'Found %d headers, more than 1' % (len(header)))
                continue

            header_cells = header[0].findAll('th', attrs={'class': 'data-table__headers__cell'})
            # A list of titles of the table like ['INDEX', 'UNITS', 'PRICE', 'CHANGE', '%CHANGE']
            header_cell_titles = [cell.get_text() for cell in header_cells]

            # Parse all the data rows from the current table
            data_rows = table.findAll('tr', attrs={'class': 'data-table__row'})
            for row in data_rows:
                row_cells = row.findAll('td', attrs={'class': 'data-table__row__cell'})
                if (len(row_cells) != len(header_cell_titles)):
                    logger.Logger.log(
                            logger.LogLevel.WARN,
                            'Found %d value cells not matching with %d title cells' % (
                                    len(row_cells), len(header_cell_titles)))
                    continue

                # A list of values like ['CL1:COM', 'USD/bll.', '39.44', '-1.89%']
                row_cell_values = [BloombergParser.clean_name(cell.get_text()) for cell in row_cells]
                # Zip the titles and values together to create a list of tuple (title, value)
                titles_and_values = zip(header_cell_titles, row_cell_values)
                logger.Logger.log(logger.LogLevel.INFO, 'Found following values in the cell: %s' % titles_and_values)


if __name__ == '__main__':
    bloomberg = BloombergParser();
    bloomberg.parse('http://www.bloomberg.com/energy')