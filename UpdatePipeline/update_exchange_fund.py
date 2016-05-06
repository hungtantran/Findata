__author__ = 'hungtantran'

import datetime
import re
import urllib
import time
import threading
from bs4 import BeautifulSoup
import string

import logger
import metrics
import fund_info
import metrics_database
import fund_info_database
from string_helper import StringHelper
from Common.constants_config import Config


class UpdateExchangeFund(threading.Thread):
    FUND_LIST_LINK_TEMPLATE = 'http://www.marketwatch.com/tools/mutual-fund/list/%s'
    SUMMARY_LINKS_TEMPLATE = 'http://finance.yahoo.com/q/hp?s=%s&z=66&y=%d'
    SUMMARY_DIMENSIONS = ['open', 'high', 'low', 'close', 'volume', 'adj_close']
    NUM_RETRIES_DOWNLOAD = 2
    WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC = 1


    def __init__(self, db_type, username, password, server, database, update_history=False):
        threading.Thread.__init__(self)

        self.db_type = db_type
        self.username = username
        self.password = password
        self.server = server
        self.database = database

        # 12-hour update frequency
        self.update_frequency_seconds = 43200
        self.fund_info_db = fund_info_database.FundInfoDatabase(db_type, username, password, server, database)
        self.current_fund = None
        self.tablename = None
        self.data = None
        self.update_history = update_history

    def sanitize_info(self, info):
        info.ticker = info.ticker.lower()

    def run(self):
        while True:
            fund_list = self.get_latest_fund_list()
            self.update_fund_list(fund_list)

            for fund in fund_list:
                self.clear_data()
                self.sanitize_info(fund)
                # TODO make this more extensible
                if not fund.ticker.isalnum():
                    continue

                self.current_fund = fund.ticker
                self.data = []
                self.tablename = 'fund_%s_metrics' % self.current_fund

                metrics_db = metrics_database.MetricsDatabase(
                        self.db_type,
                        self.username,
                        self.password,
                        self.server,
                        self.database,
                        self.tablename)
                # Create table metric if it's 'update_history' mode
                if self.update_history:
                    metrics_db.create_metric()

                # Normal case
                self.update_fund_price(fund)
                self.update_database(fund, metrics_db)
                logger.Logger.log(logger.LogLevel.INFO, 'Sleep for %d secs before updating again' %
                        UpdateExchangeFund.WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC)
                time.sleep(UpdateExchangeFund.WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC)

            logger.Logger.log(logger.LogLevel.INFO,
                    'Sleep for %d secs before updating again' % self.update_frequency_seconds)
            # TODO make it sleep through weekend
            time.sleep(self.update_frequency_seconds)

    def clear_data(self):
        self.data = None
        self.tablename = None

    def get_latest_fund_list(self):
        fund_list = []
        for letter in string.ascii_uppercase:
            cur_link = UpdateExchangeFund.FUND_LIST_LINK_TEMPLATE % letter
            logger.Logger.log(logger.LogLevel.INFO, 'Get latest fund list from link %s' % cur_link)
            response = urllib.urlopen(cur_link)
            html_string = response.read()
            fund_list.extend(self.parse_fund_list_from_html(html_string))
        return fund_list

    def parse_fund_list_from_html(self, html_string):
        fund_list = []

        try:
            html_elem = BeautifulSoup(html_string, 'html.parser')
            table_elems = html_elem.findAll('table')
            if len(table_elems) != 1:
                logger.Logger.log(logger.LogLevel.ERROR, 'Found %d content table' % len(table_elems))
                return fund_list

            row_elems = table_elems[0].findAll('tr')
            for i in range(1, len(row_elems)):
                row_elem = row_elems[i]
                symbol_elems = row_elem.findAll('td', attrs={'class': 'quotelist-symb'})
                name_elems = row_elem.findAll('td', attrs={'class': 'quotelist-name'})
                if len(symbol_elems) != 1 or len(name_elems) != 1:
                    logger.Logger.log(logger.LogLevel.ERROR, 'Found %d symbol, %d name' % (len(symbol_elems), len(name_elems)))
                    continue

                # Symbol text should be like 'ACSBX;
                # Name text should be like 'Avenue Mutual Fund Trust: Avenue Credit Strategies Fund; Institutional Class Shares'
                ticker = symbol_elems[0].get_text().strip()
                name = None
                family = None
                class_share = None

                full_name = name_elems[0].get_text()
                parts = full_name.split(';')

                if len(parts) >= 2:
                    class_share = parts[1].strip()

                name_and_family = parts[0].split(':')
                family = name_and_family[0].strip()
                if len(name_and_family) >= 2:
                    name = name_and_family[1].strip()

                fund = fund_info.FundInfo(
                        id=None,
                        ticker=ticker,
                        name=name,
                        family=family,
                        class_share=class_share,
                        fund_type=None,
                        metadata=None)
                fund_list.append(fund)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)

        return fund_list

    def update_fund_price(self, info):
        try:
            upper_bound_page = 1
            if self.update_history:
                upper_bound_page = 1000

            for i in range(upper_bound_page):
                page_num = i + 1
                logger.Logger.log(logger.LogLevel.INFO, 'Update fund %s (%s) now for page %d' % (info.name, info.ticker, page_num))
                response = urllib.urlopen(UpdateExchangeFund.SUMMARY_LINKS_TEMPLATE % (info.ticker, 66 * page_num))
                html_string = response.read()
                data = self.update_from_html_content(html_string)
                self.data.extend(data)
                if len(data) == 0:
                    logger.Logger.log(logger.LogLevel.INFO, 'Found no more data for fund %s (%s) at page %d' % (info.name, info.ticker, page_num))
                    break
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def _yahoo_finance_get_content_table(self, html_elem):
        outer_content_table_elem = html_elem.findAll('table', attrs={'class': 'yfnc_datamodoutline1'})
        if len(outer_content_table_elem) != 1:
            logger.Logger.log(logger.LogLevel.ERROR, 'Found %d outer content table' % len(outer_content_table_elem))
            return None

        inner_content_table_elem = outer_content_table_elem[0].findAll('table')
        if len(inner_content_table_elem) != 1:
            logger.Logger.log(logger.LogLevel.ERROR, 'Found %d inner content table' % len(inner_content_table_elem))
            return None

        return inner_content_table_elem[0]

    def _yahoo_finance_extract_titles(self, header_elem):
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

    def update_from_html_content(self, html_string):
        num_fail = 0
        data = []
        try:
            html_elem = BeautifulSoup(html_string, 'html.parser')

            # Get the table html elem
            content_table_elem = self._yahoo_finance_get_content_table(html_elem)
            if content_table_elem is None:
                logger.Logger.log(logger.LogLevel.WARN, 'Exit found no content table')
                return

            rows_elem = content_table_elem.findAll('tr')
            if len(rows_elem) == 0:
                logger.Logger.log(logger.LogLevel.INFO, 'Exit found no row values left')
                return

            # Extract the title
            header_elem = rows_elem[0]
            titles = self._yahoo_finance_extract_titles(header_elem)
            if (titles is None) or (len(titles) != len(UpdateExchangeFund.SUMMARY_DIMENSIONS)):
                logger.Logger.log(logger.LogLevel.INFO, 'Does not find the expected titles')
                return

            # Iterate through each row in the table, extract date and value
            for i in range(1, len(rows_elem)):
                row_elem = rows_elem[i]
                tds_elem = row_elem.findAll('td')

                # The +1 is to account for the Date column, not in titles array
                # For special rows of dividends and stock split, there are 2 td elems
                if (len(tds_elem) != len(titles) + 1 and len(tds_elem) != 2):
                    logger.Logger.log(logger.LogLevel.WARN, 'Row with num elem %d not match with num titles %d' %
                                      (len(tds_elem), len(titles)))
                    continue

                date = StringHelper.convert_string_to_datetime(tds_elem[0].get_text())
                if date is None:
                    logger.Logger.log(logger.LogLevel.WARN, 'Cannot convert %s to date' % tds_elem[0].get_text())
                    continue

                # For normal stock price rows:
                if (len(tds_elem) == len(titles) + 1):
                    for j in range(1, len(tds_elem)):
                        cell_text = tds_elem[j].get_text().strip()
                        cell_value = StringHelper.parse_value_string(cell_text)
                        if cell_value is None:
                            logger.Logger.log(logger.LogLevel.WARN, 'Cannot convert %s to value' % cell_text)
                            continue

                        value = metrics.Metrics(
                                metric_name=UpdateExchangeFund.SUMMARY_DIMENSIONS[j - 1],
                                start_date=date,
                                end_date=date,
                                unit='usd',
                                value=cell_value)
                        data.append(value)
                elif len(tds_elem) == 2:
                    # For special dividends and stock splits rows
                    cell_text = tds_elem[1].get_text().strip()
                    if 'Dividend' in cell_text:
                        # Cell text is like this '0.48 Dividend'
                        dividend_value_string = cell_text.replace(' Dividend', '').strip()
                        dividend_value = StringHelper.parse_value_string(dividend_value_string)
                        value = metrics.Metrics(
                                metric_name='dividend',
                                start_date=date,
                                end_date=date,
                                unit='usd',
                                value=dividend_value)
                        data.append(value)
                    elif cell_text.endswith('Stock Split'):
                        # Cell text is like this '1: 5 Stock Split'
                        cell_value_string = cell_text.replace(' Stock Split', '').strip().split(':')
                        cell_value = StringHelper.parse_value_string(cell_value_string[0]) / StringHelper.parse_value_string(cell_value_string[1])
                        value = metrics.Metrics(
                                metric_name='stock split',
                                start_date=date,
                                end_date=date,
                                unit='ratio',
                                value=cell_value)
                        data.append(value)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)
        finally:
            return data

    def update_fund_list(self, fund_list):
        self.fund_info_db.insert_rows(fund_list)

    def update_database(self, info, metrics_db):
        logger.Logger.log(logger.LogLevel.INFO, 'Update database for %s' % info.name)

        # TODO this pull out the latest metrics, not necessary latest stock price, fix it
        latest_rows = metrics_db.get_metrics(max_num_results=1)
        latest_time = None
        try:
            latest_time = latest_rows[0].start_date
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
            latest_time = None
        self._update_database_with_given_data(self.data, latest_time, info, metrics_db)

    def _update_database_with_given_data(self, data, latest_time, info, metrics_db):
        logger.Logger.log(logger.LogLevel.INFO, 'Update database for %s with given data' % info.name)
        all_data = data

        num_value_update = 0
        for row in all_data:
            insert_rows = []
            # Only insert value later than the current latest value
            # TODO make it more flexible than that
            if (latest_time is None or row.start_date > latest_time):
                insert_rows.append(row)
                num_value_update += 1

            if len(insert_rows) > 0:
                metrics_db.insert_metrics(insert_rows)

        logger.Logger.log(logger.LogLevel.INFO,
                          'Update table %s with %d new values' % (self.tablename, num_value_update))


def main():
    try:
        update_obj = UpdateExchangeFund(
                'mysql',
                Config.mysql_username,
                Config.mysql_password,
                Config.mysql_server,
                Config.mysql_database)
        update_obj.daemon = True
        update_obj.start()

        while True:
            time.sleep(1)
    except Exception as e:
        logger.Logger.log(logger.LogLevel.ERROR, e)


if __name__ == '__main__':
    main()
