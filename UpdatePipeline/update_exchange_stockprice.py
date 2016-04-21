__author__ = 'hungtantran'

import datetime
import re
import urllib
import time
import threading
from bs4 import BeautifulSoup

import logger
import metrics
import ticker_info
import metrics_database
import ticker_info_database
from string_helper import StringHelper
from Common.constants_config import Config


class UpdateExchangeStockprice(threading.Thread):
    SUMMARY_LINKS_TEMPLATE = 'http://finance.yahoo.com/q/hp?s=%s+Historical+Prices'
    DIVIDEND_LINK_TEMPLATE = 'http://finance.yahoo.com/q/hp?s=%s&g=v&z=66&y=%d'
    SUMMARY_DIMENSIONS = ['open', 'high', 'low', 'close', 'volume', 'adj_close']
    NUM_RETRIES_DOWNLOAD = 2
    WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC = 1


    def __init__(self, db_type, username, password, server, database, update_historical_dividend=False):
        threading.Thread.__init__(self)

        self.db_type = db_type
        self.username = username
        self.password = password
        self.server = server
        self.database = database

        # 12-hour update frequency
        self.update_frequency_seconds = 43200
        self.ticker_info_db = ticker_info_database.TickerInfoDatabase(db_type, username, password, server, database)
        self.current_ticker = None
        self.tablename = None
        self.data = None
        self.update_historical_dividend = update_historical_dividend

    def sanitize_info(self, info):
        info.ticker = info.ticker.lower()

    def run(self):
        while True:
            ticker_info = self.ticker_info_db.get_ticker_info_data()
            for info in ticker_info:
                self.clear_data()
                self.sanitize_info(info)
                # TODO make this more extensible
                if not info.ticker.isalnum():
                    continue

                self.current_ticker = info.ticker
                self.data = []
                self.tablename = '%s_metrics' % self.current_ticker

                metrics_db = metrics_database.MetricsDatabase(
                        self.db_type,
                        self.username,
                        self.password,
                        self.server,
                        self.database,
                        self.tablename)

                # Normal case
                if not self.update_historical_dividend:
                    self.update_ticker_price(info)
                else:
                    # Special case of updating only dividends:
                    self.update_dividend(info)
                self.update_database(info, metrics_db)
                logger.Logger.log(logger.LogLevel.INFO, 'Sleep for %d secs before updating again' %
                                  UpdateExchangeStockprice.WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC)
                time.sleep(UpdateExchangeStockprice.WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC)

            logger.Logger.log(logger.LogLevel.INFO,
                              'Sleep for %d secs before updating again' % self.update_frequency_seconds)
            time.sleep(self.update_frequency_seconds)

    def clear_data(self):
        self.data = None
        self.tablename = None

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

    def update_ticker_price(self, info):
        try:
            logger.Logger.log(logger.LogLevel.INFO, 'Update company %s now' % info.name)
            response = urllib.urlopen(UpdateExchangeStockprice.SUMMARY_LINKS_TEMPLATE % info.ticker)
            html_string = response.read()
            return self.update_from_html_content(info, html_string)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def update_dividend(self, info):
        try:
            logger.Logger.log(logger.LogLevel.INFO, 'Update dividend of company %s now' % info.name)
            previous_data_size = len(self.data)
            page = 0
            while True:
                response = urllib.urlopen(UpdateExchangeStockprice.DIVIDEND_LINK_TEMPLATE % (info.ticker, page * 66))
                html_string = response.read()
                self.update_from_html_content(info, html_string)

                # If there is no new data, return
                if previous_data_size == len(self.data):
                    return

                previous_data_size = len(self.data)
                page += 1
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def update_from_html_content(self, info, html_string):
        num_fail = 0
        while True:
            try:
                html_elem = BeautifulSoup(html_string, 'html.parser')

                # Get the table html elem
                content_table_elem = self._yahoo_finance_get_content_table(html_elem)
                if content_table_elem is None:
                    logger.Logger.log(logger.LogLevel.INFO, 'Exit found no content table')
                    return

                rows_elem = content_table_elem.findAll('tr')
                if len(rows_elem) == 0:
                    logger.Logger.log(logger.LogLevel.INFO, 'Exit found no row values left')
                    return

                # Extract the title
                header_elem = rows_elem[0]
                titles = self._yahoo_finance_extract_titles(header_elem)
                if (titles is None) or (len(titles) != len(UpdateExchangeStockprice.SUMMARY_DIMENSIONS)):
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
                    if (len(tds_elem) == len(titles) + 1 and not self.update_historical_dividend):
                        for j in range(1, len(tds_elem)):
                            cell_text = tds_elem[j].get_text().strip()
                            cell_value = StringHelper.parse_value_string(cell_text)
                            if cell_value is None:
                                logger.Logger.log(logger.LogLevel.WARN, 'Cannot convert %s to value' % cell_text)
                                continue

                            value = metrics.Metrics(
                                    metric_name=UpdateExchangeStockprice.SUMMARY_DIMENSIONS[j - 1],
                                    start_date=date,
                                    end_date=date,
                                    unit='usd',
                                    value=cell_value)
                            self.data.append(value)
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
                            self.data.append(value)
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
                            self.data.append(value)
                break
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
                num_fail += 1
                if num_fail >= UpdateExchangeStockprice.NUM_RETRIES_DOWNLOAD:
                    break
                else:
                    continue

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
            if (self.update_historical_dividend or latest_time is None or row.start_date > latest_time):
                insert_rows.append(row)
                num_value_update += 1

            if len(insert_rows) > 0:
                metrics_db.insert_metrics(insert_rows)

        logger.Logger.log(logger.LogLevel.INFO,
                          'Update table %s with %d new values' % (self.tablename, num_value_update))


def main():
    try:
        update_obj = UpdateExchangeStockprice('mysql',
                                              Config.mysql_username,
                                              Config.mysql_password,
                                              Config.mysql_server,
                                              Config.mysql_database,
                                              update_historical_dividend=True)
        update_obj.daemon = True
        update_obj.start()

        while True:
            time.sleep(1)
    except Exception as e:
        logger.Logger.log(logger.LogLevel.ERROR, e)


if __name__ == '__main__':
    main()
