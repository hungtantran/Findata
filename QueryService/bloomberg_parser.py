__author__ = 'hungtantran'


from bs4 import BeautifulSoup
import urllib

import logger


class BloombergParser:
    def __init__(self):
        self.parser_type = 'html.parser'

    def parse(self, link):
        logger.Logger.log(logger.LogLevel.INFO, 'BloombergParser attempts to parse link \'%s\'' % (link))
        link_handle = urllib.urlopen(link)
        soup = BeautifulSoup(link_handle.read(), self.parser_type)

        data_rows = soup.findAll('tr', attrs={'class': 'data-table__row'})
        for row in data_rows:
            name = row.findAll('td', attrs={'class': 'data-table__row__cell', 'data-type': 'name'})
            if len(name) != 1:
                logger.Logger.log(logger.LogLevel.WARN, 'There are %d names for row %s' % (len(name), name))
                continue
            else:
                print(name)

            value = row.findAll('td', attrs={'class': 'data-table__row__cell', 'data-type': 'value'})
            if len(value) != 1:
                logger.Logger.log(logger.LogLevel.WARN, 'There are %d values for row %s' % (len(value), value))
                continue
            else:
                print(value)


if __name__ == '__main__':
    bloomberg = BloombergParser();
    bloomberg.parse('http://www.bloomberg.com/markets/commodities')