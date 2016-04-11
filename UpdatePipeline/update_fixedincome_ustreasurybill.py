__author__ = 'hungtantran'


import datetime
import re
import urllib
import time
import threading
from bs4 import BeautifulSoup

import logger
import timeline_model
import timeline_model_database
from string_helper import StringHelper
from Common.constants_config import Config

class UpdateFixedincomeUstreasuryBill(threading.Thread):
    LINK_ALL = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yieldAll'
    LINK_YEAR = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yieldYear&year=%d'
    HEADER_TITLES = ['1 mo', '3 mo', '6 mo', '1 yr', '2 yr', '3 yr', '5 yr', '7 yr', '10 yr', '20 yr', '30 yr']

    def __init__(self, db_type, username, password, server, database):
        threading.Thread.__init__(self)
        # 12-hour update frequency
        self.update_frequency_seconds = 43200
        self.model_db = timeline_model_database.TimelineModelDatabase(db_type, username, password, server, database)
        self.data = {}
        for header_title in UpdateFixedincomeUstreasuryBill.HEADER_TITLES:
            self.data[header_title] = []

        self.tablename = {}
        for key in self.data:
            self.tablename[key] = 'fixedincome_ustreasurybill_' + key.replace(' ', '_')

    def run(self):
        while True:
            self.update_current_year()
            self.update_database()
            logger.Logger.log(logger.LogLevel.INFO, 'Sleep for %d secs before updating again' % self.update_frequency_seconds)
            time.sleep(self.update_frequency_seconds)

    def clear_data(self):
        for key in self.data:
            self.data[key] = []

    def update(self):
        logger.Logger.log(logger.LogLevel.INFO, 'Update now')
        response = urllib.urlopen(UpdateFixedincomeUstreasuryBill.LINK_ALL)
        html_string = response.read()
        return self.update_from_html_content(html_string)

    def update_year(self, year):
        logger.Logger.log(logger.LogLevel.INFO, 'Update year %d' % year)
        response = urllib.urlopen(UpdateFixedincomeUstreasuryBill.LINK_YEAR % year)
        html_string = response.read()
        return self.update_from_html_content(html_string)

    def update_current_year(self):
        logger.Logger.log(logger.LogLevel.INFO, 'Update current year')
        current_year = datetime.datetime.now().year
        return self.update_year(current_year)

    def _verify_header(self, header_titles):
        if len(header_titles) != (len(UpdateFixedincomeUstreasuryBill.HEADER_TITLES) + 1):
            logger.Logger.log(logger.LogLevel.WARN, 'There are %d header elements, %d expected' % (
                    len(header_titles), len(UpdateFixedincomeUstreasuryBill.HEADER_TITLES) + 1))
            return False

        if (header_titles[0] != 'Date'):
            logger.Logger.log(logger.LogLevel.WARN, 'The 1 title should be Date but is %s' % header_titles[0])
            return False

        for i in range(len(UpdateFixedincomeUstreasuryBill.HEADER_TITLES)):
            if header_titles[i + 1] != UpdateFixedincomeUstreasuryBill.HEADER_TITLES[i]:
                logger.Logger.log(logger.LogLevel.WARN, 'The %d title should be %s but is %s' % (
                        i + 1, UpdateFixedincomeUstreasuryBill.HEADER_TITLES[i], header_titles[i + 1]))
                return False

        return True

    def update_from_html_content(self, html_string):
        logger.Logger.log(logger.LogLevel.INFO, 'Update from html content')

        self.clear_data()

        html_elem = BeautifulSoup(html_string, 'html.parser')

        # Get the table html elem
        content_table_elems = html_elem.find_all('table', attrs={'class': 't-chart'})
        if len(content_table_elems) != 1:
            logger.Logger.log(logger.LogLevel.WARN, 'There are %d content table elements, 1 expected' % len(content_table_elems))
            return
        content_table_elem = content_table_elems[0]

        header_titles = []
        header_elems = content_table_elem.find_all('th', attrs={'scope': 'col'})
        for header_elem in header_elems:
            header_titles.append(header_elem.get_text())
        if not self._verify_header(header_titles):
            logger.Logger.log(logger.LogLevel.WARN, 'Failed to verify the correct header titles %s' % header_titles)
            return

        odd_row_elems = content_table_elem.find_all('tr', attrs={'class': 'oddrow'})
        even_row_elems = content_table_elem.find_all('tr', attrs={'class': 'evenrow'})
        data_row_elems = odd_row_elems + even_row_elems

        # Iterate through each row
        for data_row in data_row_elems:
            cell_elems = data_row.find_all('td')
            if len(cell_elems) != (len(UpdateFixedincomeUstreasuryBill.HEADER_TITLES) + 1):
                logger.Logger.log(logger.LogLevel.WARN, 'There are %d cell elements, %d expected' % (
                    len(cell_elems), len(UpdateFixedincomeUstreasuryBill.HEADER_TITLES) + 1))
                continue

            date = StringHelper.convert_string_to_datetime(cell_elems[0].get_text())
            if date is None:
                logger.Logger.log(logger.LogLevel.WARN, 'Cannot convert %s to date' % cell_elems[0].get_text())
                continue

            for i in range(1, len(cell_elems)):
                cell_text = cell_elems[i].get_text().strip()

                if cell_text == 'N/A':
                    continue

                cell_value = StringHelper.parse_value_string(cell_text)
                if cell_value is None:
                    logger.Logger.log(logger.LogLevel.WARN, 'Cannot convert %s to value' % cell_text)
                    continue

                value = timeline_model.TimelineModel(date, cell_value)
                self.data[UpdateFixedincomeUstreasuryBill.HEADER_TITLES[i - 1]].append(value)

    def update_database(self):
        logger.Logger.log(logger.LogLevel.INFO, 'Update database')
        current_latest_data = {}
        for key in self.data:
            latest_value = self.model_db.get_latest_model_data(self.tablename[key])
            current_latest_data[key] = latest_value

        self._update_database_with_given_data(self.data, current_latest_data)

    def _update_database_with_given_data(self, data, current_latest_data):
        logger.Logger.log(logger.LogLevel.INFO, 'Update database with given data')
        all_data = data

        num_value_update = {}
        for name in all_data:
            num_value_update[name] = 0
            data = all_data[name]
            for row in data:
                # Only insert value later than the current latest value
                # TODO make it more flexible than that
                if (current_latest_data[name] is not None) and (row.time > current_latest_data[name].time):
                    self.model_db.insert_row(self.tablename[name], row)
                    num_value_update[name] += 1

        for key in num_value_update:
            logger.Logger.log(logger.LogLevel.INFO, 'Update table %s with %d new values' % (self.tablename[key], num_value_update[key]))


def main():
    try:
        update_obj = UpdateFixedincomeUstreasuryBill('mysql',
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