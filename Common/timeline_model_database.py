__author__ = 'hungtantran'


import datetime
import re
from time import sleep

import logger
from dao_factory_repo import DAOFactoryRepository
from string_helper import StringHelper


class TimelineModelDatabase(object):
    max_num_reties = 3;

    def __init__(self, db_type, username, password, server, database):
        self.dao_factory = DAOFactoryRepository.getInstance(db_type)
        self.username = username
        self.password = password
        self.server = server
        self.database = database

    @staticmethod
    def create_model_name(model):
        return model.replace(' ', '_')

    @staticmethod
    def get_time_limit(lower_time_limit, upper_time_limit):
        lower_time_object = datetime.datetime(1900, 1, 1, 0, 0)
        if lower_time_limit is not None:
            if type(lower_time_limit) is datetime.datetime:
                lower_time_object = lower_time_limit
            elif type(lower_time_limit) is str:
                lower_time_object = StringHelper.convert_string_to_datetime(lower_time_limit)

        upper_time_object = datetime.datetime(9999, 12, 31, 0, 0)
        if upper_time_limit is not None:
            if type(upper_time_limit) is datetime.datetime:
                upper_time_object = upper_time_limit
            elif type(upper_time_object) is str:
                upper_time_object = StringHelper.convert_string_to_datetime(upper_time_limit)

        return (lower_time_object, upper_time_object)

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

    def insert_value(self, model, time, value):
        model_name = TimelineModelDatabase.create_model_name(model)
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                datetime_obj = StringHelper.convert_string_to_datetime(time)
                if datetime_obj is not None:
                    cursor.execute("INSERT INTO %s (time, value) VALUES ('%s', %f)" %
                                   (model_name, StringHelper.convert_datetime_to_string(datetime_obj), value))
                    connection.commit()
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

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

                        datetime_obj = StringHelper.convert_string_to_datetime(time)
                        if datetime_obj is not None:
                            value_string = "('%s', %f)" %  (StringHelper.convert_datetime_to_string(datetime_obj), value)
                            values_arr.append(value_string)

                    if len(values_arr) > 0:
                        query_string = "INSERT INTO %s (time, value) VALUES %s" % (model_name, ','.join(values_arr))
                        cursor.execute(query_string)
                        connection.commit()
                break;
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
                sleep(2)

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

    def get_model_data(self, model, lower_time_limit=None):
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

    def get_join_models_data(self, model1, model2, lower_time_limit=None, upper_time_limit=None):
        model1_name = TimelineModelDatabase.create_model_name(model1)
        model2_name = TimelineModelDatabase.create_model_name(model2)
        logger.Logger.log(logger.LogLevel.INFO, 'Get join model1 %s, model2 %s data' % (model1_name, model2_name))
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            try:
                # TODO need to make this general
                cursor = connection.cursor()
                cursor.execute("SELECT A.time as time, A.value, B.value FROM %s as A INNER JOIN %s as B on A.time = B.time ORDER BY A.time" %
                               (model1_name, model2_name))
                return cursor.fetchall()
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def get_average_model_data(self, model, lower_time_limit=None, upper_time_limit=None):
        model_name = TimelineModelDatabase.create_model_name(model)
        logger.Logger.log(logger.LogLevel.INFO, 'Get average model %s' % model_name)
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            try:
                # TODO need to make this general
                cursor = connection.cursor()

                (lower_time_object, upper_time_object) = TimelineModelDatabase.get_time_limit(
                        lower_time_limit, upper_time_limit)

                execute_query =  "SELECT AVG(value) FROM %s WHERE time >= '%s' and time <= '%s'" % (
                        model_name,
                        StringHelper.convert_datetime_to_string(lower_time_object),
                        StringHelper.convert_datetime_to_string(upper_time_object))

                cursor.execute(execute_query)
                avg_arrs = cursor.fetchall()
                if len(avg_arrs) == 1 and len(avg_arrs[0]) == 1:
                    return avg_arrs[0][0]

                return None
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def get_std_model_data(self, model, lower_time_limit=None, upper_time_limit=None):
        model_name = TimelineModelDatabase.create_model_name(model)
        logger.Logger.log(logger.LogLevel.INFO, 'Get standard deviation model %s' % model_name)
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            try:
                # TODO need to make this general
                cursor = connection.cursor()

                (lower_time_object, upper_time_object) = TimelineModelDatabase.get_time_limit(
                        lower_time_limit, upper_time_limit)

                execute_query =  "SELECT STDDEV(value) FROM %s WHERE time >= '%s' and time <= '%s'" % (
                        model_name,
                        StringHelper.convert_datetime_to_string(lower_time_object),
                        StringHelper.convert_datetime_to_string(upper_time_object))

                cursor.execute(execute_query)
                avg_arrs = cursor.fetchall()
                if len(avg_arrs) == 1 and len(avg_arrs[0]) == 1:
                    return avg_arrs[0][0]

                return None
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def get_all_models_names(self):
        logger.Logger.log(logger.LogLevel.INFO, 'Get all model names')
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            try:
                # TODO need to make this general
                cursor = connection.cursor()
                cursor.execute("SHOW TABLES")
                all_models = cursor.fetchall()
                return all_models
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    @staticmethod
    def query_result_to_file(query_result, output_file_name, delimiter=','):
        f = None
        try:
            logger.Logger.log(logger.LogLevel.INFO, 'Start writing to file %s' % output_file_name)
            f = open(output_file_name, 'w')

            # Write each row for each date
            for i in range(len(query_result)):
                values_arr = query_result[i]
                string_values_arr = []
                for value in values_arr:
                    if type(value) is datetime.datetime:
                        string_values_arr.append(StringHelper.convert_datetime_to_string(value))
                    elif type(value) is float:
                        string_values_arr.append(str(value))

                values_string = delimiter.join(string_values_arr)
                values_string += '\n'
                f.write(values_string)

            logger.Logger.log(logger.LogLevel.INFO, 'Finish writing to file %s' % output_file_name)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception %s' % e)
        finally:
            if f is not None:
                f.flush()
                f.close()

