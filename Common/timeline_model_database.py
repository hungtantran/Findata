__author__ = 'hungtantran'


import datetime
import re

import logger
from dao_factory_repo import DAOFactoryRepository


class TimelineModelDatabase(object):
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
            except:
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
            except:
                connection.rollback()

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
            except:
                connection.rollback()

    def get_model_data(self, model):
        model_name = TimelineModelDatabase.create_model_name(model)
        logger.Logger.log(logger.LogLevel.INFO, 'Get %s model data' % model_name)
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            # TODO need to make this general
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM %s ORDER BY time" % model_name)
            return cursor.fetchall()

