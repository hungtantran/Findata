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
import ticker_info


class TickerInfoDatabase(object):
    TICKER_INFO_TABLE_NAME = 'ticker_info'
    max_num_reties = 1;

    def __init__(self, db_type, username, password, server, database, ticker_info_table_name=TICKER_INFO_TABLE_NAME):
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
        self.ticker_info_table_name = ticker_info_table_name
        self.table = self.get_ticker_info_table_object(ticker_info.TickerInfo)

    @staticmethod
    def copy_ticker_info_to_test():
        #TODO move this function somewhere else or make it more general
        dao_factory = DAOFactoryRepository.getInstance('mysql')
        with dao_factory.create(Config.test_mysql_username,
                                Config.test_mysql_password,
                                Config.test_mysql_server,
                                Config.test_mysql_database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                create_model_query_string = 'CREATE TABLE ticker_info LIKE models.ticker_info'
                insert_model_query_string = 'INSERT INTO ticker_info SELECT * FROM models.ticker_info'
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

    def get_ticker_info_table_object(self, class_map):
        metadata = sqlalchemy.MetaData(bind=self.engine)
        ticker_info_table = sqlalchemy.Table(self.ticker_info_table_name, metadata,
                                             sqlalchemy.Column('cik', sqlalchemy.INTEGER),
                                             sqlalchemy.Column('ticker', sqlalchemy.String(32), primary_key=True),
                                             sqlalchemy.Column('name', sqlalchemy.String(255)),
                                             sqlalchemy.Column('ipo_year', sqlalchemy.INTEGER),
                                             sqlalchemy.Column('sector', sqlalchemy.String(255)),
                                             sqlalchemy.Column('industry', sqlalchemy.String(255)),
                                             sqlalchemy.Column('exchange', sqlalchemy.String(32)),
                                             sqlalchemy.Column('sic', sqlalchemy.INTEGER),
                                             sqlalchemy.Column('naics', sqlalchemy.INTEGER))

        sqlalchemy.orm.clear_mappers()
        sqlalchemy.orm.mapper(class_map, ticker_info_table)
        return ticker_info_table

    def create_ticker_info_table(self, insert_to_data_store=False):
        logger.Logger.log(logger.LogLevel.INFO, 'Create ticker_info_table %s' % self.ticker_info_table_name)
        try:
            new_table = self.get_ticker_info_table_object(class_map=ticker_info.TickerInfo)
            new_table.create(self.engine, checkfirst=True)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)

    def insert_value(self, cik, ticker, name, ipo_year, sector, industry, exchange, sic, naics, ignore_duplicate=False):
        try:
            s = self.session()
            self.get_ticker_info_table_object(class_map=ticker_info.TickerInfo)
            new_value = ticker_info.TickerInfo(cik=cik,
                                               ticker=ticker,
                                               name=name,
                                               ipo_year=ipo_year,
                                               sector=sector,
                                               industry=industry,
                                               exchange=exchange,
                                               sic=sic,
                                               naics=naics)
            if ignore_duplicate:
                s.merge(new_value)
            else:
                s.add(new_value)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)
        finally:
            if s is not None:
                s.commit()
                s.close()

    def insert_row(self, ticker_info_obj):
        return self.insert_value(ticker_info_obj.cik,
                                 ticker_info_obj.ticker,
                                 ticker_info_obj.name,
                                 ticker_info_obj.ipo_year,
                                 ticker_info_obj.sector,
                                 ticker_info_obj.industry,
                                 ticker_info_obj.exchange,
                                 ticker_info_obj.sic,
                                 ticker_info_obj.naics)

    def update_row(self, ticker_info_obj):
        # TODO make this orm or remove all orm
        with self.dao_factory.create(
                self.username,
                self.password,
                self.server,
                self.database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                # TODO make the update clause to include more fields
                update_query = "UPDATE %s SET cik=%s, sic=%s, naics=%s WHERE ticker='%s'" % (
                    self.ticker_info_table_name,
                    ticker_info_obj.cik if ticker_info_obj.cik is not None else 'NULL',
                    ticker_info_obj.sic if ticker_info_obj.sic is not None else 'NULL',
                    ticker_info_obj.naics if ticker_info_obj.naics is not None else 'NULL',
                    ticker_info_obj.ticker)
                cursor.execute(update_query)
                connection.commit()
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    # TODO implement this
    def insert_values(self, ciks, tickers, names, ipo_years, sectors, industrys, exchanges, ignore_duplicate=False):
        pass

    def remove_ticker_info_table(self):
        logger.Logger.log(logger.LogLevel.INFO, 'Drop ticker_info_table %s' % self.ticker_info_table_name)
        try:
            drop_ticker_info_table = self.get_ticker_info_table_object(class_map=ticker_info.TickerInfo)
            drop_ticker_info_table.drop(self.engine, checkfirst=False)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)

    def get_ticker_info_data(self, lower_time_limit=None):
        try:
            s = self.session()
            data = s.query(ticker_info.TickerInfo).all()
            s.expunge_all()
            return data
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)
        finally:
            if s is not None:
                s.commit()
                s.close()

    def remove_ticker_info(self):
        logger.Logger.log(logger.LogLevel.INFO, 'Drop %s' % self.ticker_info_table_name)
        try:
            self.session.close_all()
            self.table.drop(self.engine, checkfirst=False)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)