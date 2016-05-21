__author__ = 'hungtantran'


import logger
from dao_factory_repo import DAOFactoryRepository
from constants_config import Config


class DatabaseHelper(object):
    @staticmethod
    def copy_table_from_test_to_prd(table):
        #TODO move this function somewhere else or make it more general
        dao_factory = DAOFactoryRepository.getInstance('mysql')
        with dao_factory.create(Config.test_mysql_username,
                                Config.test_mysql_password,
                                Config.test_mysql_server,
                                Config.test_mysql_database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                create_model_query_string = 'CREATE TABLE %s LIKE models.%s' % table
                insert_model_query_string = 'INSERT INTO %s SELECT * FROM models.%s' % table
                cursor.execute(create_model_query_string)
                connection.commit()
                cursor.execute(insert_model_query_string)
                connection.commit()
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

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