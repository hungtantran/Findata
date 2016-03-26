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
        patterns['[0-9]+/[0-9]+/[0-9][0-9][0-9][0-9]'] = '%m/%d/%Y'
        patterns['[0-9][0-9][0-9][0-9]-[0-9]+-[0-9]+'] = '%Y-%m-%d'
        for pattern in patterns:
            prog = re.compile(pattern)
            if prog.match(time_str):
                return datetime.datetime.strptime(time_str, patterns[pattern])

    def create_model(self, model):
        logger.Logger.log(logger.LogLevel.INFO, 'Create model %s' % model)
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                cursor.execute("CREATE TABLE IF NOT EXISTS %s (time DATETIME NOT NULL, value FLOAT NOT NULL, PRIMARY KEY(time))" % model)
                connection.commit()
            except:
                connection.rollback()

    def insert_value(self, model, time, value):
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                datetime_obj = TimelineModelDatabase.convert_time(time)
                if datetime_obj is not None:
                    cursor.execute("INSERT INTO %s (time, value) VALUES ('%s', %f)" % (model, datetime_obj.strftime("%Y-%m-%d %H:%M:%S"), value))
                    connection.commit()
            except:
                connection.rollback()

    def remove_model(self, model):
        logger.Logger.log(logger.LogLevel.INFO, 'Drop model %s' % model)
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                cursor.execute("DROP TABLE IF EXISTS %s" % model)
                connection.commit()
            except:
                connection.rollback()

    def get_model_data(self, model):
        logger.Logger.log(logger.LogLevel.INFO, 'Get %s model data' % model)
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            # TODO need to make this general
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM %s" % model)
            return cursor.fetchall()

