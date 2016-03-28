__author__ = 'hungtantran'

import time
import urllib
from bs4 import BeautifulSoup

import logger
from generic_parser import GenericParser
from string_helper import StringHelper

class YahooHistoricalParser(GenericParser):
    def __init__(self, sleep_secs=5):
        self.parser_type = 'html.parser'
        self.sleep_secs = sleep_secs

    # Given source like https://finance.yahoo.com/q/hp?s=%5EDJI&a=0&b=29&c=1985&d=2&e=27&f=2016&g=d&z=200&y=0,
    # return https://finance.yahoo.com/q/hp?s=%5EDJI&a=0&b=29&c=1985&d=2&e=27&f=2016&g=d&z=200
    @staticmethod
    def extract_core_source(link):
        index = link.rfind('&y=')
        return link[:(index+3)]

    # Given source like https://finance.yahoo.com/q/hp?s=%5EDJI&a=0&b=29&c=1985&d=2&e=27&f=2016&g=d&z=200, page_num=1
    # return https://finance.yahoo.com/q/hp?s=%5EDJI&a=0&b=29&c=1985&d=2&e=27&f=2016&g=d&z=200&y=66
    @staticmethod
    def construct_link(link, page_num):
        return link + str(page_num * 66)

    @staticmethod
    def get_content_table(html_elem):
        outer_content_table_elem = html_elem.findAll('table', attrs={'class': 'yfnc_datamodoutline1'})
        if len(outer_content_table_elem) != 1:
            return None

        inner_content_table_elem = outer_content_table_elem[0].findAll('table')
        if len(inner_content_table_elem) != 1:
            return None

        return inner_content_table_elem[0]

    @staticmethod
    def extract_titles(header_elem):
        titles_elem = header_elem.findAll('th')
        if len(titles_elem) == 0:
            return None

        if titles_elem[0].get_text() != 'Date':
            return None

        titles = []
        for i in range(1, len(titles_elem)):
            titles.append(StringHelper.clean_name(titles_elem[i].get_text()))

        logger.Logger.log(logger.LogLevel.INFO, 'Found titles %s' % titles)
        return titles

    def parse(self, source_name, max_num_results=0):
        dates = []
        titles = []
        results = []

        core_source = YahooHistoricalParser.extract_core_source(source_name)

        page = 0
        num_fail = 0
        num_results = 0
        done = False
        while True:
            time.sleep(self.sleep_secs)
            link = YahooHistoricalParser.construct_link(core_source, page)
            page += 1

            try:
                logger.Logger.log(logger.LogLevel.INFO, 'link = %s' % link)
                response = urllib.urlopen(link)
                html_string = response.read()
                html_elem = BeautifulSoup(html_string, self.parser_type)

                # Get the table html elem
                content_table_elem = YahooHistoricalParser.get_content_table(html_elem)
                if content_table_elem is None:
                    logger.Logger.log(logger.LogLevel.INFO, 'Exit found no content table')
                    break

                rows_elem = content_table_elem.findAll('tr')
                if len(rows_elem) == 0:
                    logger.Logger.log(logger.LogLevel.INFO, 'Exit found no row values left')
                    break

                # This is the first page, extract the title
                if page == 1:
                    header_elem = rows_elem[0]
                    titles = YahooHistoricalParser.extract_titles(header_elem)
                    if titles is None:
                        logger.Logger.log(logger.LogLevel.INFO, 'Exit found no title')
                        break

                    for i in range(len(titles)):
                        results.append([])

                if len(titles) == 0:
                    logger.Logger.log(logger.LogLevel.INFO, 'Exit found no title after first page')
                    break

                logger.Logger.log(logger.LogLevel.INFO, 'Found %d row values on page %d' % (len(rows_elem) - 1, page))
                # Iterate through each row in the table, extract date and value
                for i in range(1, len(rows_elem)):
                    row_elem = rows_elem[i]
                    tds_elem = row_elem.findAll('td')

                    # The +1 is to account for the Date column, not in titles array
                    if len(tds_elem) != len(titles) + 1:
                        logger.Logger.log(logger.LogLevel.WARN, 'Row with num elem %d not match with num titles %d' %
                                          (len(tds_elem), len(titles)))
                        continue

                    if (max_num_results > 0) and (num_results >= max_num_results):
                        done = True
                        break
                    else:
                        num_results += 1

                    dates.append(tds_elem[0].get_text())
                    for j in range(1, len(tds_elem)):
                        results[j - 1].append(StringHelper.parse_value_string(tds_elem[j].get_text()))

                if done:
                    break
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
                num_fail += 1
                if num_fail > 0:
                    break
                else:
                    continue

        logger.Logger.log(logger.LogLevel.INFO, 'Finish parsing. Found %d results' % len(dates))

        return (titles, dates, results)


