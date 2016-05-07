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

    def get_ticker_info_table_object(self):
        metadata = sqlalchemy.MetaData(bind=self.engine)
        ticker_info_table = sqlalchemy.Table(
                self.ticker_info_table_name, metadata,
                sqlalchemy.Column('id', sqlalchemy.INTEGER, primary_key=True, autoincrement=True),
                sqlalchemy.Column('ticker', sqlalchemy.String(32)),
                sqlalchemy.Column('ticker_type', sqlalchemy.String(255)),
                sqlalchemy.Column('name', sqlalchemy.String(255)),
                sqlalchemy.Column('location', sqlalchemy.String(255)),
                sqlalchemy.Column('cik', sqlalchemy.String(255)),
                sqlalchemy.Column('ipo_year', sqlalchemy.INTEGER),
                sqlalchemy.Column('sector', sqlalchemy.String(255)),
                sqlalchemy.Column('industry', sqlalchemy.String(255)),
                sqlalchemy.Column('exchange', sqlalchemy.String(255)),
                sqlalchemy.Column('sic', sqlalchemy.INTEGER),
                sqlalchemy.Column('naics', sqlalchemy.INTEGER),
                sqlalchemy.Column('class_share', sqlalchemy.String(255)),
                sqlalchemy.Column('fund_type', sqlalchemy.String(255)),
                sqlalchemy.Column('fund_family', sqlalchemy.String(255)),
                sqlalchemy.Column('asset_class', sqlalchemy.String(255)),
                sqlalchemy.Column('active', sqlalchemy.INTEGER),
                sqlalchemy.Column('MetaData', sqlalchemy.TEXT),
                sqlalchemy.UniqueConstraint('ticker', 'location'))
        return ticker_info_table

    def create_ticker_info_table(self, insert_to_data_store=False):
        logger.Logger.log(logger.LogLevel.INFO, 'Create ticker_info_table %s' % self.ticker_info_table_name)
        try:
            new_table = self.get_ticker_info_table_object()
            new_table.create(self.engine, checkfirst=True)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)

    def insert_row(self, ticker_info_obj):
        raise NotImplementedError('Need to implement insert_row')

    def remove_ticker_info_table(self):
        logger.Logger.log(logger.LogLevel.INFO, 'Drop ticker_info_table %s' % self.ticker_info_table_name)
        try:
            drop_ticker_info_table = self.get_ticker_info_table_object(class_map=ticker_info.TickerInfo)
            drop_ticker_info_table.drop(self.engine, checkfirst=False)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)

    def get_ticker_info_data(self, ticker_type=None, lower_time_limit=None):
        try:
            with self.dao_factory.create(
                    self.username,
                    self.password,
                    self.server,
                    self.database) as connection:
                query_string = 'SELECT * FROM %s' % self.ticker_info_table_name
                if ticker_type is not None:
                    query_string += ' WHERE ticker_type = \'%s\'' % ticker_type

                cursor = connection.cursor()
                cursor.execute(query_string)
                data = cursor.fetchall()
                ticker_list = [ticker_info.TickerInfo(
                        id=row[0],
                        ticker=row[1],
                        ticker_type=row[2],
                        name=row[3],
                        location=row[4],
                        cik=row[5],
                        ipo_year=row[6],
                        sector=row[7],
                        industry=row[8],
                        exchange=row[9],
                        sic=row[10],
                        naics=row[11],
                        class_share=row[12],
                        fund_type=row[13],
                        fund_family=row[14],
                        asset_class=row[15],
                        active=row[16],
                        metadata=row[17]) for row in data]
                return ticker_list
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)