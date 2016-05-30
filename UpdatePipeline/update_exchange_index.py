__author__ = 'hungtantran'


import init_app
import datetime
import re
import urllib
import time
import threading
from bs4 import BeautifulSoup

import logger
import metrics
import metrics_database
from string_helper import StringHelper
from Common.constants_config import Config


class UpdateExchangeIndex(threading.Thread):
    SUMMARY_LINKS = {
        'nasdaq': 'http://finance.yahoo.com/q/hp?s=%5Eixic+historical+prices',
        'sp500': 'https://finance.yahoo.com/q/hp?s=%5EGSPC+Historical+Prices',
        'dowjones': 'https://finance.yahoo.com/q/hp?s=%5EDJI+Historical+Prices'}
    SUMMARY_DIMENSIONS = ['open', 'high', 'low', 'close', 'volume', 'adj_close']
    NUM_RETRIES_DOWNLOAD = 2

    def __init__(self, db_type, username, password, server, database):
        threading.Thread.__init__(self)
        # 12-hour update frequency
        self.update_frequency_seconds = 43200
        self.tablename = 'exchange_index_metrics'
        self.metrics_db = metrics_database.MetricsDatabase(
                db_type,
                username,
                password,
                server,
                database,
                self.tablename)

        self.data = None

    def run(self):
        while True:
            self.data = []
            self.update_nasdaq()
            self.update_downjones()
            self.update_sp500()
            self.update_database()
            logger.Logger.log(logger.LogLevel.INFO, 'Sleep for %d secs before updating again' % self.update_frequency_seconds)
            time.sleep(self.update_frequency_seconds)

    def clear_data(self):
        self.data = None

    def update_nasdaq(self):
        try:
            logger.Logger.log(logger.LogLevel.INFO, 'Update nasdaq now')
            response = urllib.urlopen(UpdateExchangeIndex.SUMMARY_LINKS['nasdaq'])
            html_string = response.read()
            return self.update_from_html_content('nasdaq', html_string)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def update_downjones(self):
        try:
            logger.Logger.log(logger.LogLevel.INFO, 'Update downjones now')
            response = urllib.urlopen(UpdateExchangeIndex.SUMMARY_LINKS['dowjones'])
            html_string = response.read()
            return self.update_from_html_content('dowjones', html_string)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def update_sp500(self):
        try:
            logger.Logger.log(logger.LogLevel.INFO, 'Update sp500 now')
            response = urllib.urlopen(UpdateExchangeIndex.SUMMARY_LINKS['sp500'])
            html_string = response.read()
            return self.update_from_html_content('sp500', html_string)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def _yahoo_finance_get_content_table(self, html_elem):
        outer_content_table_elem = html_elem.findAll('table', attrs={'class': 'yfnc_datamodoutline1'})
        if len(outer_content_table_elem) != 1:
            return None

        inner_content_table_elem = outer_content_table_elem[0].findAll('table')
        if len(inner_content_table_elem) != 1:
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

    def update_from_html_content(self, index, html_string):
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
                if (titles is None) or (len(titles) != len(UpdateExchangeIndex.SUMMARY_DIMENSIONS)):
                    logger.Logger.log(logger.LogLevel.INFO, 'Does not find the expected titles')
                    return

                # Iterate through each row in the table, extract date and value
                for i in range(1, len(rows_elem)):
                    row_elem = rows_elem[i]
                    tds_elem = row_elem.findAll('td')

                    # The +1 is to account for the Date column, not in titles array
                    if len(tds_elem) != len(titles) + 1:
                        logger.Logger.log(logger.LogLevel.WARN, 'Row with num elem %d not match with num titles %d' %
                                          (len(tds_elem), len(titles)))
                        continue

                    date = StringHelper.convert_string_to_datetime(tds_elem[0].get_text())
                    if date is None:
                        logger.Logger.log(logger.LogLevel.WARN, 'Cannot convert %s to date' % tds_elem[0].get_text())
                        continue

                    for j in range(1, len(tds_elem)):
                        cell_text = tds_elem[j].get_text().strip()
                        cell_value = StringHelper.parse_value_string(cell_text)
                        if cell_value is None:
                            logger.Logger.log(logger.LogLevel.WARN, 'Cannot convert %s to value' % cell_text)
                            continue

                        value = metrics.Metrics(
                                metric_name=index + '_' + UpdateExchangeIndex.SUMMARY_DIMENSIONS[j - 1],
                                start_date=date,
                                end_date=date,
                                unit='point',
                                value=cell_value)
                        self.data.append(value)
                break
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
                num_fail += 1
                if num_fail >= UpdateExchangeIndex.NUM_RETRIES_DOWNLOAD:
                    break
                else:
                    continue

    def update_database(self):
        logger.Logger.log(logger.LogLevel.INFO, 'Update database')
        latest_rows = self.metrics_db.get_metrics(max_num_results=1)
        try:
            latest_time = latest_rows[0].start_date
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
            latest_time = None

        self._update_database_with_given_data(self.data, latest_time)

    def _update_database_with_given_data(self, data, latest_time):
        logger.Logger.log(logger.LogLevel.INFO, 'Update database with given data')
        all_data = data

        num_value_update = 0
        for row in data:
            # Only insert value later than the current latest value
            # TODO make it more flexible than that
            if (latest_time is None or row.start_date > latest_time):
                self.metrics_db.insert_metric(row)
                num_value_update += 1

        logger.Logger.log(logger.LogLevel.INFO, 'Update table %s with %d new values' % (self.tablename, num_value_update))


def main():
    try:
        update_obj = UpdateExchangeIndex('mysql',
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