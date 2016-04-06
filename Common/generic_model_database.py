__author__ = 'hungtantran'


import datetime
import re
from time import sleep

import logger
from dao_factory_repo import DAOFactoryRepository
from string_helper import StringHelper


class GenericModelDatabase(object):
    MAX_NUM_RETRIES = 3

    def __init__(self, db_type, username, password, server, database):
        self.dao_factory = DAOFactoryRepository.getInstance(db_type)
        self.username = username
        self.password = password
        self.server = server
        self.database = database

    @staticmethod
    def create_model_name(model):
        return model.replace(' ', '_')

    def create_model(self, model, column_names, column_types, primary_key_column=None):
        if len(column_names) == 0:
            logger.Logger.log(logger.LogLevel.WARN, 'There is no column name')

        if len(column_types) != len(column_names):
            logger.Logger.log(logger.LogLevel.WARN, 'Given %d names and %d types, not match!' %
                              (len(column_names), len(column_types)))

        if (primary_key_column is not None) and (primary_key_column not in column_names):
            logger.Logger.log(logger.LogLevel.WARN, 'Primary column %s not in the list of colum names %s' %
                              (primary_key_column, column_names))

        model_name = GenericModelDatabase.create_model_name(model)
        logger.Logger.log(logger.LogLevel.INFO, 'Create model %s with name %s, type %s, primary key %s' %
                          (model_name, column_names, column_types, primary_key_column))

        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                query_string = 'CREATE TABLE IF NOT EXISTS %s (%s %s' % (model_name, column_names[0], column_types[0])
                for i in range(1, len(column_names)):
                    query_string += ', %s %s' % (column_names[i], column_types[i])
                if primary_key_column is not None:
                    query_string += ', PRIMARY KEY(%s)' % primary_key_column
                query_string += ')'

                cursor.execute(query_string)
                connection.commit()
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def insert_values(self, model, values):
        num_retries = 0
        while num_retries < GenericModelDatabase.MAX_NUM_RETRIES:
            num_retries += 1
            try:
                model_name = GenericModelDatabase.create_model_name(model)
                with self.dao_factory.create(self.username,
                                             self.password,
                                             self.server,
                                             self.database) as connection:
                    # TODO need to make this general
                    cursor = connection.cursor()
                    values_arr = []
                    for row in values:
                        value_string = '('
                        for cell in row:
                            if type(cell) is str:
                                value_string += "'%s'," % cell
                            elif type(cell) is datetime.datetime:
                                value_string += "'%s'," % StringHelper.convert_datetime_to_string(cell)
                            else:
                                value_string += "%s," % cell
                        # Remove the last comma
                        value_string = value_string[:-1]
                        value_string += ')'
                        values_arr.append(value_string)

                    if len(values_arr) > 0:
                        query_string = "INSERT INTO %s VALUES %s" % (model_name, ','.join(values_arr))
                        cursor.execute(query_string)
                        connection.commit()
                break;
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
                sleep(2)

    def get_model_data(self, model, lower_time_limit=None):
        model_name = GenericModelDatabase.create_model_name(model)
        logger.Logger.log(logger.LogLevel.INFO, 'Get %s model data' % model_name)
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            try:
                # TODO need to make this general
                cursor = connection.cursor()
                cursor.execute("SELECT * FROM %s" % model_name)
                return cursor.fetchall()
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def remove_model(self, model):
        model_name = GenericModelDatabase.create_model_name(model)
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