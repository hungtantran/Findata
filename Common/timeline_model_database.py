__author__ = 'hungtantran'


import datetime
import re
import time

import logger
from dao_factory_repo import DAOFactoryRepository


class TimelineModelDatabase(object):
    max_num_reties = 3;

    def __init__(self, db_type, username, password, server, database):
        self.dao_factory = DAOFactoryRepository.getInstance(db_type)
        self.username = username
        self.password = password
        self.server = server
        self.database = database

    @staticmethod
    def convert_time(time_str):
        patterns = {}
        # 3/1/2016
        patterns['^[0-9][0-9]?/[0-9][0-9]?/[0-9][0-9][0-9][0-9]$'] = '%m/%d/%Y'
        # 2016/03/03
        patterns['^[0-9][0-9][0-9][0-9]/[0-9][0-9]?/[0-9][0-9]?$'] = '%Y/%m/%d'
        # 03/04/16
        patterns['^[0-9][0-9]?/[0-9][0-9]?/[0-9][0-9]$'] = '%m/%d/%y'
        # 2016-03-02
        patterns['^[0-9][0-9][0-9][0-9]-[0-9]+-[0-9]+$'] = '%Y-%m-%d'
        # Mar 06 2016
        patterns['^[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]? [0-9][0-9]? [0-9][0-9][0-9][0-9]$'] = '%b %d %Y'
        # Mar 06, 2016
        patterns['^[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]? [0-9][0-9]?, [0-9][0-9][0-9][0-9]$'] = '%b %d, %Y'
        # 07-Mar-2016
        patterns['^[0-9][0-9]?-[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]?-[0-9][0-9][0-9][0-9]$'] = '%d-%b-%Y'
        # 08-Mar-16
        patterns['^[0-9][0-9]?-[a-zA-Z][a-zA-Z][a-zA-Z][a-zA-Z]?-[0-9][0-9]$'] = '%d-%b-%y'

        for pattern in patterns:
            prog = re.compile(pattern)
            if prog.match(time_str):
                return datetime.datetime.strptime(time_str, patterns[pattern])

    @staticmethod
    def create_model_name(model):
        return model.replace(' ', '_')

    def create_model(self, model):
        model_name = TimelineModelDatabase.create_model_name(model)
        logger.Logger.log(logger.LogLevel.INFO, 'Create model %s' % model_name)
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS %s (time DATETIME NOT NULL, value FLOAT NOT NULL, PRIMARY KEY(time))" % model_name)
                connection.commit()
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
                connection.rollback()

    def insert_value(self, model, time, value):
        model_name = TimelineModelDatabase.create_model_name(model)
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                datetime_obj = TimelineModelDatabase.convert_time(time)
                if datetime_obj is not None:
                    cursor.execute("INSERT INTO %s (time, value) VALUES ('%s', %f)" %
                                   (model_name, datetime_obj.strftime("%Y-%m-%d %H:%M:%S"), value))
                    connection.commit()
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
                connection.rollback()

    def insert_values(self, model, times, values):
        if len(times) != len(values):
            logger.Logger.log(logger.LogLevel.INFO, 'Mismatch number of times (%d) and values (%d)' %
                              (len(times), len(values)))
            return

        num_retries = 0
        while num_retries < TimelineModelDatabase.max_num_reties:
            num_retries += 1
            try:
                model_name = TimelineModelDatabase.create_model_name(model)
                with self.dao_factory.create(self.username,
                                             self.password,
                                             self.server,
                                             self.database) as connection:
                    # TODO need to make this general
                    cursor = connection.cursor()

                    values_arr = []
                    for i in range(len(times)):
                        time = times[i]
                        value = values[i]

                        datetime_obj = TimelineModelDatabase.convert_time(time)
                        if datetime_obj is not None:
                            value_string = "('%s', %f)" % (datetime_obj.strftime("%Y-%m-%d %H:%M:%S"), value)
                            values_arr.append(value_string)

                    if len(values_arr) > 0:
                        query_string = "INSERT INTO %s (time, value) VALUES %s" % (model_name, ','.join(values_arr))
                        cursor.execute(query_string)
                        connection.commit()
                break;
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
                connection.rollback()
                time.sleep(2)

    def remove_model(self, model):
        model_name = TimelineModelDatabase.create_model_name(model)
        logger.Logger.log(logger.LogLevel.INFO, 'Drop model %s' % model)
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                cursor.execute("DROP TABLE IF EXISTS %s" % model_name)
                connection.commit()
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
                connection.rollback()

    def get_model_data(self, model):
        model_name = TimelineModelDatabase.create_model_name(model)
        logger.Logger.log(logger.LogLevel.INFO, 'Get %s model data' % model_name)
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            try:
                # TODO need to make this general
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM %s ORDER BY time" % model_name)
                return cursor.fetchall()
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

