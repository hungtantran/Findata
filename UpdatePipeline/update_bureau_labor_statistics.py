__author__ = 'hungtantran'

import init_app

import datetime
import re
import urllib
import time
import threading
import json
import urllib, urllib2
from bs4 import BeautifulSoup
import string
import Queue
import HTMLParser
import unicodedata

import logger
import metrics
import metrics_database
import ticker_info_database
from economics_info_database import EconomicsInfoDatabase
from economics_info import EconomicsInfo
from string_helper import StringHelper
from Common.constants_config import Config


class UpdateBureauLaborStatistics(threading.Thread):
    HOME_PAGE = 'http://www.bls.gov/data/'
    DATA_PAGE_v1 = 'http://api.bls.gov/publicAPI/v1/timeseries/data/'
    DATA_PAGE_v2 = 'http://api.bls.gov/publicAPI/v2/timeseries/data/'
    NUM_RETRIES_DOWNLOAD = 2
    WAIT_TIME_BETWEEN_DOWNLOAD_IN_SEC = 5
    MAX_PROCESSING_THREADS = 1
    UPDATE_FREQUENCY_SECONDS = 86400
    API_KEY = '510cd0884a714325bc6b88cf122f0632'
    QUOTA = 500

    def __init__(
            self, db_type, username, password, server, database,
            max_num_threads=None, update_frequency_seconds=None,
            update_list=False, update_history=False, api_version=1):
        threading.Thread.__init__(self)

        self.db_type = db_type
        self.username = username
        self.password = password
        self.server = server
        self.database = database

        self.update_frequency_seconds = (
                update_frequency_seconds or
                UpdateBureauLaborStatistics.UPDATE_FREQUENCY_SECONDS)

        self.max_num_threads = (
                max_num_threads or
                UpdateBureauLaborStatistics.MAX_PROCESSING_THREADS)

        self.economics_info_db = EconomicsInfoDatabase(
                self.db_type,
                self.username,
                self.password,
                self.server,
                self.database)

        self.update_list = update_list
        self.update_history = update_history
        self.api_version = api_version
        self.daily_api_call = 0
        self.q = Queue.Queue()

    def populate_work_queue(self):
        if self.update_list:
            self.get_latest_measure_list()

        measure_list = self.economics_info_db.get_economics_info_data(
                source='bureau_of_labor_statistics')

        for measure in measure_list:
            self.q.put(measure)

    def run(self):
        while True:
            self.daily_api_call = 0
            self.populate_work_queue()

            # Start threads to update
            threads = []
            for i in range(self.max_num_threads):
                t = threading.Thread(target=self.update_measures)
                threads.append(t)
                t.start()

            for i in range(len(threads)):
                wait_thread = threads[i]
                logger.Logger.info('Wait for thread %s' % wait_thread.name)
                wait_thread.join()
                logger.Logger.info('Thread %s done' % wait_thread.name)

            logger.Logger.log(logger.LogLevel.INFO,
                    'Sleep for %d secs before updating again' % (
                            self.update_frequency_seconds))
            # TODO make it sleep through weekend
            time.sleep(self.update_frequency_seconds)

    def get_latest_measure_list(self):
        cur_link = UpdateBureauLaborStatistics.HOME_PAGE
        logger.Logger.info('Get latest measures list from link %s' % cur_link)

        response = urllib.urlopen(cur_link)
        html_string = response.read()
        database_list = self.parse_database_list_from_html(html_string)
        logger.Logger.info('Found %d measures' % len(database_list))

        for table_header, db_name, db_link in database_list:
            logger.Logger.info('Check measure from link %s' % db_link)
            response = urllib.urlopen(db_link)
            html_string = response.read()

            measure_list = self.parse_measure_list_from_html(html_string)
            for measure_name, measure_series_id in measure_list:
                metadata = {}
                metadata['link'] = db_link
                metadata['series_id'] = measure_series_id

                economics_info = EconomicsInfo(
                        id=None,
                        name=measure_name,
                        location='us',
                        category=table_header,
                        type=db_name,
                        source='bureau_of_labor_statistics',
                        metadata=json.dumps(metadata))
                self.economics_info_db.insert_row(economics_info)

    def parse_database_list_from_html(self, html_string):
        database_list = []

        try:
            remove_non_alphanumeric_space = re.compile('[^a-zA-Z0-9() ]')

            html_elem = BeautifulSoup(html_string, 'html.parser')
            table_elems = html_elem.findAll(
                    'table', attrs={'class': 'matrix-table'})
            if len(table_elems) != 14:
                logger.Logger.error('Found %d content table' % len(table_elems))
                return database_list

            table_header_elems = html_elem.findAll('h1')
            if len(table_header_elems) != 15:
                logger.Logger.error(
                        'Found %d table headers' % len(table_header_elems))
                return database_list

            for i, table_elem in enumerate(table_elems):
                table_header_elem = table_header_elems[i + 1]
                table_header = HTMLParser.HTMLParser().unescape(
                        table_header_elem.get_text())
                row_elems = table_elem.findAll('tr')

                if len(row_elems) < 1:
                    logger.Logger.error('Found %d rows' % len(row_elems))
                    continue

                headers = row_elems[0].findAll('th')
                if (len(headers) < 1 or
                    headers[0].get_text() != 'Database Name' or
                    headers[1].get_text() != 'SpecialNotice' or
                    re.sub(r'\W+', '', headers[2].get_text()) != 'TopPicks'):
                    logger.Logger.error(
                            'Found headers %s (not expected)' % headers)
                    continue

                for i in range(1, len(row_elems)):
                    cell_elems = row_elems[i].findAll('td')
                    if len(cell_elems) != len(headers):
                        logger.Logger.error(
                                'Found %d cells (not expected)' % len(cell_elems))
                        continue

                    db_name = remove_non_alphanumeric_space.sub('', cell_elems[0].get_text())
                    db_link_elems = cell_elems[2].findAll('a')
                    if len(db_link_elems) != 1:
                        logger.Logger.error(
                                'Found %d links (not expected)' % len(db_link_elems))
                        continue

                    db_link = db_link_elems[0]['href']
                    database_list.append((table_header, db_name, db_link))
        except Exception as e:
            logger.Logger.error(e)

        return database_list

    def parse_measure_list_from_html(self, html_string):
        measure_list = []
        try:
            remove_non_alphanumeric_space = re.compile('[^a-zA-Z0-9() ]')

            regex = re.compile(pattern='<DD><INPUT TYPE=checkbox NAME=series_id VALUE=.+> (.+) - (.+)')
            for measure_match in regex.finditer(html_string):
                measure_name = measure_match.group(1).strip()
                measure_series_id = measure_match.group(2).strip()
                measure_list.append((measure_name, measure_series_id))
        except Exception as e:
            logger.Logger.error(e)

        return measure_list

    def get_time_series_data_and_update(self, economics_info, update_history):
        metadata = json.loads(economics_info.metadata)
        metric_name = '%s (%s) (%s)' % (economics_info.name,
                                        economics_info.category,
                                        economics_info.type)
        tablename = self.get_economics_info_table_name(economics_info)

        metrics_db = metrics_database.MetricsDatabase(
                self.db_type,
                self.username,
                self.password,
                self.server,
                self.database,
                tablename)
        metrics_db.create_metric()

        latest_time, earliest_time = metrics_db.get_earliest_and_latest_time()
        # If the table is empty, default to use update history option
        if latest_time is None:
            update_history = True 
        today = datetime.datetime.today()

        # The bureau release monthly data one month late
        latest_available_data = today - datetime.timedelta(days=30)
        if ((not update_history) and (latest_time is not None) and
            (latest_available_data.year == latest_time.year) and
            (latest_available_data.month == latest_time.month)):
            logger.Logger.info("The latest info is at %s, update to date, so skip updating" % latest_time)
            return

        current_year = (today.year - 1) if not update_history else 1940
        logger.Logger.info("Get time series info for %s from year %d to year %d. Earliest time %s, latest time %s" % (
                economics_info.name,
                current_year,
                today.year,
                earliest_time,
                latest_time))
        
        while current_year <= today.year:
            end_year = min(current_year + 20, today.year)
            # Skip year in the middle of earliest and latest time
            if (latest_time is not None and earliest_time is not None and
                current_year > earliest_time.year and
                current_year < latest_time.year):
                logger.Logger.info("Skip updating %s for year %d" % (
                        economics_info.name,
                        current_year))
                current_year = min(today.year, current_year + 20)
                continue

            logger.Logger.info('Update %s (%s) (%s) from year %d to year %d' % (
                    economics_info.name, economics_info.category,
                    economics_info.type, current_year, end_year))

            data_url = UpdateBureauLaborStatistics.DATA_PAGE_v1
            if self.api_version == 2:
                data_url = UpdateBureauLaborStatistics.DATA_PAGE_v2

            values = {
                    "seriesid": [unicodedata.normalize(
                            'NFKD',
                            metadata['series_id']).encode('ascii','ignore')],
                    "startyear" : "%d" % current_year,
                    "endyear" : "%d" % end_year}
            if self.api_version == 2:
                values["registrationKey"] = UpdateBureauLaborStatistics.API_KEY
            data = json.dumps(values)

            try:
                self.daily_api_call += 1
                if self.daily_api_call > UpdateBureauLaborStatistics.QUOTA:
                    logger.Logger.info('Exceed daily quota of %d' % (
                            UpdateBureauLaborStatistics.QUOTA))
                    return

                headers = {'Content-type': 'application/json'}
                req = urllib2.Request(data_url, data, headers)
                rsp = urllib2.urlopen(req)
                response = rsp.read()
                new_measures = self.parse_json_time_series(
                        metadata['series_id'], metric_name, response)

                logger.Logger.info(
                        'Update database for %s (%s) (%s) with given data' % (
                                economics_info.name,
                                economics_info.category,
                                economics_info.type))
                metrics_db.update_database_with_given_data(
                        data=new_measures,
                        latest_time=latest_time,
                        earliest_time=earliest_time)
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, e)

            current_year += 20
            logger.Logger.info('Sleep for 10 secs before downloading json again')
            time.sleep(10)

    def get_start_end_date_from_period_info(self, year, periodName, period):
        start_date = None
        end_date = None

        # Annual System
        if periodName == 'Annual':
            start_date = datetime.datetime(year, 1, 1)
            end_date = datetime.datetime(year + 1, 1, 1)
        # Month System
        elif periodName == 'January':
            start_date = datetime.datetime(year, 1, 1)
            end_date = datetime.datetime(year, 2, 1)
        elif periodName == 'February':
            start_date = datetime.datetime(year, 2, 1)
            end_date = datetime.datetime(year, 3, 1)
        elif periodName == 'March':
            start_date = datetime.datetime(year, 3, 1)
            end_date = datetime.datetime(year, 4, 1)
        elif periodName == 'April':
            start_date = datetime.datetime(year, 4, 1)
            end_date = datetime.datetime(year, 5, 1)
        elif periodName == 'May':
            start_date = datetime.datetime(year, 5, 1)
            end_date = datetime.datetime(year, 6, 1)
        elif periodName == 'June':
            start_date = datetime.datetime(year, 6, 1)
            end_date = datetime.datetime(year, 7, 1)
        elif periodName == 'July':
            start_date = datetime.datetime(year, 7, 1)
            end_date = datetime.datetime(year, 8, 1)
        elif periodName == 'August':
            start_date = datetime.datetime(year, 8, 1)
            end_date = datetime.datetime(year, 9, 1)
        elif periodName == 'September':
            start_date = datetime.datetime(year, 9, 1)
            end_date = datetime.datetime(year, 10, 1)
        elif periodName == 'October':
            start_date = datetime.datetime(year, 10, 1)
            end_date = datetime.datetime(year, 11, 1)
        elif periodName == 'November':
            start_date = datetime.datetime(year, 11, 1)
            end_date = datetime.datetime(year, 12, 1)
        elif periodName == 'December':
            start_date = datetime.datetime(year, 12, 1)
            end_date = datetime.datetime(year + 1, 1, 1)
        # Quarter system
        elif periodName == '1st Quarter':
            start_date = datetime.datetime(year, 1, 1)
            end_date = datetime.datetime(year, 4, 1)
        elif periodName == '2nd Quarter':
            start_date = datetime.datetime(year, 4, 1)
            end_date = datetime.datetime(year, 7, 1)
        elif periodName == '3rd Quarter':
            start_date = datetime.datetime(year, 7, 1)
            end_date = datetime.datetime(year, 10, 1)
        elif periodName == '4th Quarter':
            start_date = datetime.datetime(year, 10, 1)
            end_date = datetime.datetime(year + 1, 1, 1)
        # Half system
        elif periodName == '1st Half':
            start_date = datetime.datetime(year, 1, 1)
            end_date = datetime.datetime(year, 7, 1)
        elif periodName == '2nd Half':
            start_date = datetime.datetime(year, 7, 1)
            end_date = datetime.datetime(year + 1, 1, 1)

        return start_date, end_date

    def parse_json_time_series(self, series_id, metric_name, json_text):
        measures = []
        json_data = json.loads(json_text)
        if json_data['status'] != 'REQUEST_SUCCEEDED':
            logger.Logger.info("Fail to get results for series %s json %s" % (
                    series_id, json_data))
            return measures

        results = json_data['Results']['series'][0]
        found_series_id = results['seriesID']
        if found_series_id != series_id:
            logger.Logger.error("Found series id %s instead of expected %s" % (
                    found_series_id, series_id))
            return measures

        data = results['data']
        # Row can look like these:
        # + {"year":"2006","period":"A01","periodName":"Annual","value":"52","footnotes":[{}]}
        # + {"year":"1919","period":"M12","periodName":"December","value":"18.9","footnotes":[{}]}
        for row in data:
            try:
                year = int(row['year'])
                value = float(row['value'])
                periodName = row['periodName']
                period = row['period']
                start_date, end_date = self.get_start_end_date_from_period_info(
                        year, periodName, period)
                if start_date is None or end_date is None:
                    logger.Logger.error(
                            "Fail to parse start end date from period %s, period name %s" % (
                                    period, periodName))
                    continue

                new_measure = metrics.Metrics(
                        metric_name=metric_name,
                        start_date=start_date,
                        end_date=end_date,
                        unit=None,
                        value=value)
                measures.append(new_measure)
            except Exception as e:
                logger.Logger.error("Fail to parse row %s" % row)

        logger.Logger.info("Parse %d results from downloaded json" % len(measures))
        return measures

    def get_economics_info_table_name(self, economics_info):
        return 'economics_info_%d_metrics' % economics_info.id

    def update_measures(self):
        try:
            count = 0
            while not self.q.empty():
                economics_info = self.q.get()
                count += 1
                if (count < 1000):
                    continue

                if self.daily_api_call > UpdateBureauLaborStatistics.QUOTA:
                    logger.Logger.info('Exceed daily quota of %d' % (
                            UpdateBureauLaborStatistics.QUOTA))
                    return

                logger.Logger.info(
                        '(%s) Processing economic measure %s (%s) (%s) and push to database' % (
                        threading.current_thread().name, economics_info.name,
                        economics_info.category, economics_info.type))

                self.get_time_series_data_and_update(economics_info, self.update_history)
        finally:
            self.q.task_done()


def main():
    try:
        update_obj = UpdateBureauLaborStatistics(
                'mysql',
                Config.mysql_username,
                Config.mysql_password,
                Config.mysql_server,
                Config.mysql_database,
                update_history=False,
                api_version=2)
        update_obj.daemon = True
        update_obj.start()

        while True:
            time.sleep(1)
    except Exception as e:
        logger.Logger.log(logger.LogLevel.ERROR, e)


if __name__ == '__main__':
    main()
