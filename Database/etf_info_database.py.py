__author__ = 'hungtantran'

import datetime
import re
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql
from time import sleep

import logger
from dao_factory_repo import DAOFactoryRepository
from string_helper import StringHelper
from constants_config import Config
import fund_info


class FundInfoDatabase(object):
    FUND_INFO_TABLE_NAME = 'fund_info'
    max_num_reties = 1;

    def __init__(self, db_type, username, password, server, database, fund_info_table_name=FUND_INFO_TABLE_NAME):
        self.dao_factory = DAOFactoryRepository.getInstance(db_type)
        self.username = username
        self.password = password
        self.server = server
        self.database = database
        self.db_type = db_type

        self.engine = sqlalchemy.create_engine('%s://%s:%s@%s/%s?charset=utf8&use_unicode=0' %
                                               (db_type, username, password, server, database),
                                               pool_recycle=3600)
        self.session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.fund_info_table_name = fund_info_table_name

    @staticmethod
    def copy_fund_info_to_test():
        #TODO move this function somewhere else or make it more general
        dao_factory = DAOFactoryRepository.getInstance('mysql')
        with dao_factory.create(Config.test_mysql_username,
                                Config.test_mysql_password,
                                Config.test_mysql_server,
                                Config.test_mysql_database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                create_model_query_string = 'CREATE TABLE fund_info LIKE models.fund_info'
                insert_model_query_string = 'INSERT INTO fund_info SELECT * FROM models.fund_info'
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

    def get_fund_info_table_object(self, class_map):
        metadata = sqlalchemy.MetaData(bind=self.engine)
        fund_info_table = sqlalchemy.Table(
                self.fund_info_table_name, metadata,
                sqlalchemy.Column('id', sqlalchemy.INTEGER, primary_key=True, autoincrement=True),
                sqlalchemy.Column('ticker', sqlalchemy.String(32), primary_key=True),
                sqlalchemy.Column('name', sqlalchemy.String(255)),
                sqlalchemy.Column('family', sqlalchemy.String(255)),
                sqlalchemy.Column('class_share', sqlalchemy.String(255)),
                sqlalchemy.Column('fund_type', sqlalchemy.String(255)),
                sqlalchemy.Column('metadata', sqlalchemy.TEXT),
                sqlalchemy.UniqueConstraint('ticker', name='ticker'))
        return fund_info_table

    def create_fund_info_table(self, insert_to_data_store=False):
        logger.Logger.log(logger.LogLevel.INFO, 'Create fund_info_table %s' % self.fund_info_table_name)
        try:
            new_table = self.get_fund_info_table_object(class_map=fund_info.FundInfo)
            new_table.create(self.engine, checkfirst=True)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)

    def insert_value(self, tickers, names, families, class_shares, fund_types, metadatas, ignore_duplicate=False):
        try:
            with self.dao_factory.create(
                    self.username,
                    self.password,
                    self.server,
                    self.database) as connection:
                cursor = connection.cursor()
                for i in range(len(tickers)):
                    query_string = 'INSERT IGNORE INTO %s (ticker, name, family, class_share, fund_type, metadata) VALUES ' % self.fund_info_table_name
                    query_string += r'(%s, %s, %s, %s, %s, %s)'
                    cursor.execute(query_string, (tickers[i], names[i], families[i], class_shares[i], fund_types[i], metadatas[i]))
                    if i % 100 == 0:
                        connection.commit()
                connection.commit()
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)

    def insert_row(self, fund_info_obj, ignore_duplicate=False):
        return self.insert_value(tickers=[fund_info_obj.ticker],
                                 names=[fund_info_obj.name],
                                 families=[fund_info_obj.family],
                                 class_shares=[fund_info_obj.class_share],
                                 fund_types=[fund_info_obj.fund_type],
                                 metadatas=[fund_info_obj.metadata],
                                 ignore_duplicate=ignore_duplicate)

    def insert_rows(self, fund_info_objs, ignore_duplicate=False):
        tickers = [obj.ticker for obj in fund_info_objs]
        names = [obj.name for obj in fund_info_objs]
        families = [obj.family for obj in fund_info_objs]
        class_shares = [obj.class_share for obj in fund_info_objs]
        fund_types = [obj.fund_type for obj in fund_info_objs]
        metadatas = [obj.metadata for obj in fund_info_objs]

        return self.insert_value(tickers=tickers,
                                 names=names,
                                 families=families,
                                 class_shares=class_shares,
                                 fund_types=fund_types,
                                 metadatas=metadatas,
                                 ignore_duplicate=ignore_duplicate)

    def remove_fund_info_table(self):
        logger.Logger.log(logger.LogLevel.INFO, 'Drop fund_info_table %s' % self.fund_info_table_name)
        try:
            drop_fund_info_table = self.get_fund_info_table_object(class_map=fund_info.FundInfo)
            drop_fund_info_table.drop(self.engine, checkfirst=False)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)

    def get_fund_info_data(self):
        try:
            with self.dao_factory.create(
                    self.username,
                    self.password,
                    self.server,
                    self.database) as connection:
                query_string = 'SELECT * FROM %s' % self.fund_info_table_name
                cursor = connection.cursor()
                cursor.execute(query_string)
                data = cursor.fetchall()
                fund_list = [fund_info.FundInfo(
                        id=row[0],
                        ticker=row[1],
                        name=row[2],
                        family=row[3],
                        class_share=row[4],
                        fund_type=row[5],
                        metadata=row[6]) for row in data]
                return fund_list
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)