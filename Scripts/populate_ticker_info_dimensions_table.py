__author__ = 'hungtantran'


import init_app
import filecmp
import os
from os import listdir, rename
from os.path import isfile, join
import re
import unittest
import zipfile

import logger
from constants_config import Config
from dao_factory_repo import DAOFactoryRepository
from string_helper import StringHelper


def populate_ticker_info_dimensions_table():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    all_metrics = []
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()
            cursor.execute('SELECT id from ticker_info ORDER BY id')
            data = cursor.fetchall()

            cursor2 = connection.cursor()
            cursor3 = connection.cursor()
            for row in data:
                try:
                    id = row[0]
                    table_name = 'ticker_info_' + str(id) + '_metrics'

                    cursor2.execute('SELECT DISTINCT metric_name, TIMESTAMPDIFF(DAY, start_date, end_date) as duration from ' + table_name)
                    data2 = cursor2.fetchall()
                    for row2 in data2:
                        metric_abbrv = row2[0]
                        metric_name = metric_abbrv
                        if metric_abbrv == 'open':
                            metric_name = 'Open'
                        elif metric_abbrv == 'high':
                            metric_name = 'High'
                        elif metric_abbrv == 'low':
                            metric_name = 'Low'
                        elif metric_abbrv == 'close':
                            metric_name = 'Close'
                        elif metric_abbrv == 'volume':
                            metric_name = 'Volume'
                        elif metric_abbrv == 'adj_close':
                            metric_name = 'Adjusted Close'

                        duration_day = row2[1]
                        if duration_day >= 25 and duration_day <= 35:
                            metric_abbrv = 'Monthly ' + metric_abbrv
                            metric_name = 'Monthly ' + metric_name
                        elif duration_day >= 80 and duration_day <= 100:
                            metric_abbrv = 'Quarterly ' + metric_abbrv
                            metric_name = 'Quarterly ' + metric_name
                        elif duration_day >= 160 and duration_day <= 200:
                            metric_abbrv = '6-month ' + metric_abbrv
                            metric_name = '6-month ' + metric_name
                        elif duration_day >= 320 and duration_day <= 400:
                            metric_abbrv = 'Annual ' + metric_abbrv
                            metric_name = 'Annual ' + metric_name
                        elif duration_day > 0:
                            duration_month = int(duration_day / 30)
                            if duration_day % 30 >= 15:
                                duration_month += 1;
                            metric_abbrv = '%d-month ' % duration_month + metric_abbrv
                            metric_name = '%d-month ' % duration_month + metric_name

                        if metric_name not in all_metrics:
                            try:
                                update_query = "INSERT INTO ticker_info_dimensions (abbrv, name, name_hash) VALUES ('%s', '%s', MD5('%s'))" % (metric_abbrv, metric_name, metric_name)
                                print update_query

                                cursor3.execute(update_query)
                                connection.commit()
                                all_metrics.append(metric_name)
                            except Exception as e:
                                print e
                except Exception as e:
                    print e

        except Exception as e:
            print e


def rename_ticker_info_financial_metric_name():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()
            all_metrics = []
            cursor.execute('SELECT name from ticker_info_dimensions')
            data = cursor.fetchall()
            for row in data:
                try:
                    name = row[0]
                    all_metrics.append(name)
                except Exception as e:
                    print e

            cursor.execute('SELECT id from ticker_info ORDER BY id')
            data = cursor.fetchall()

            cursor2 = connection.cursor()
            cursor3 = connection.cursor()
            for row in data:
                try:
                    id = row[0]
                    table_name = 'ticker_info_' + str(id) + '_metrics'

                    cursor2.execute('SELECT id, metric_name, TIMESTAMPDIFF(DAY, start_date, end_date) as duration from ' + table_name)
                    data2 = cursor2.fetchall()
                    for row2 in data2:
                        id2 = row2[0]
                        metric_abbrv = row2[1]
                        if metric_abbrv == 'open':
                            metric_abbrv = 'Open'
                        elif metric_abbrv == 'high':
                            metric_abbrv = 'High'
                        elif metric_abbrv == 'low':
                            metric_abbrv = 'Low'
                        elif metric_abbrv == 'close':
                            metric_abbrv = 'Close'
                        elif metric_abbrv == 'volume':
                            metric_abbrv = 'Volume'
                        elif metric_abbrv == 'adj_close':
                            metric_abbrv = 'Adjusted Close'

                        duration_day = row2[2]
                        if duration_day > 0:
                            if duration_day >= 25 and duration_day <= 35:
                                metric_abbrv = 'Monthly ' + metric_abbrv
                            elif duration_day >= 80 and duration_day <= 100:
                                metric_abbrv = 'Quarterly ' + metric_abbrv
                            elif duration_day >= 160 and duration_day <= 200:
                                metric_abbrv = '6-month ' + metric_abbrv
                            elif duration_day >= 320 and duration_day <= 400:
                                metric_abbrv = 'Annual ' + metric_abbrv
                            elif duration_day > 0:
                                duration_month = int(duration_day / 30)
                                if duration_day % 30 >= 15:
                                    duration_month += 1;
                                metric_abbrv = '%d-month ' % duration_month + metric_abbrv

                            if metric_abbrv in all_metrics:
                                try:
                                    update_query = "UPDATE %s SET metric_name = '%s' where id = %d" % (table_name, metric_abbrv, id2)
                                    print update_query

                                    cursor3.execute(update_query)
                                    connection.commit()
                                except Exception as e:
                                    print e
                except Exception as e:
                    print e

        except Exception as e:
            print e


def rename_ticker_info_metric_name():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()
            all_metrics = []
            cursor.execute('SELECT name from ticker_info_dimensions')
            data = cursor.fetchall()
            for row in data:
                try:
                    name = row[0]
                    all_metrics.append(name)
                except Exception as e:
                    print e

            cursor.execute('SELECT id from ticker_info ORDER BY id')
            data = cursor.fetchall()

            cursor2 = connection.cursor()
            cursor3 = connection.cursor()
            for row in data:
                try:
                    id = row[0]
                    table_name = 'ticker_info_' + str(id) + '_metrics'
                    try:
                        update_query = "UPDATE %s SET metric_name = 'Open' where metric_name = 'open'" % (table_name)
                        print update_query
                        cursor3.execute(update_query)
                        update_query = "UPDATE %s SET metric_name = 'High' where metric_name = 'high'" % (table_name)
                        print update_query
                        cursor3.execute(update_query)
                        update_query = "UPDATE %s SET metric_name = 'Low' where metric_name = 'low'" % (table_name)
                        print update_query
                        cursor3.execute(update_query)
                        update_query = "UPDATE %s SET metric_name = 'Close' where metric_name = 'close'" % (table_name)
                        print update_query
                        cursor3.execute(update_query)
                        update_query = "UPDATE %s SET metric_name = 'Volume' where metric_name = 'volume'" % (table_name)
                        print update_query
                        cursor3.execute(update_query)
                        update_query = "UPDATE %s SET metric_name = 'Adjusted Close' where metric_name = 'adj_close'" % (table_name)
                        print update_query
                        cursor3.execute(update_query)
                        connection.commit()
                    except Exception as e:
                        print e
                except Exception as e:
                    print e

        except Exception as e:
            print e


if __name__ == '__main__':
    #populate_ticker_info_dimensions_table()
    #rename_ticker_info_financial_metric_name
    rename_ticker_info_metric_name()
