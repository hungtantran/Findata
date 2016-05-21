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
import economics_info


class EconomicsInfoDatabase(object):
    ECONOMICS_INFO_TABLE_NAME = 'economics_info'

    def __init__(self, db_type, username, password, server, database, economics_info_table_name=ECONOMICS_INFO_TABLE_NAME):
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
        self.economics_info_table_name = economics_info_table_name

    def get_economics_info_table_object(self):
        metadata = sqlalchemy.MetaData(bind=self.engine)
        economics_info_table = sqlalchemy.Table(
                self.economics_info_table_name, metadata,
                sqlalchemy.Column('id', sqlalchemy.INTEGER, primary_key=True, autoincrement=True),
                sqlalchemy.Column('name', sqlalchemy.String(255)),
                sqlalchemy.Column('location', sqlalchemy.String(255)),
                sqlalchemy.Column('category', sqlalchemy.String(255)),
                sqlalchemy.Column('type', sqlalchemy.String(255)),
                sqlalchemy.Column('source', sqlalchemy.String(255)),
                sqlalchemy.Column('metadata', sqlalchemy.TEXT),
                sqlalchemy.UniqueConstraint('name', 'location', 'category', 'type'))
        return economics_info_table

    def create_economics_info_table(self, insert_to_data_store=False):
        logger.Logger.log(logger.LogLevel.INFO, 'Create economics_info_table %s' % self.economics_info_table_name)
        try:
            new_table = self.get_economics_info_table_object()
            new_table.create(self.engine, checkfirst=True)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)

    def insert_row(self, economics_info_obj):
        try:
            with self.dao_factory.create(
                    self.username,
                    self.password,
                    self.server,
                    self.database) as connection:
                query_string = 'INSERT IGNORE INTO %s (name, location, category, type, source, metadata)' % self.economics_info_table_name
                query_string += r' VALUES (%s, %s, %s, %s, %s, %s)'

                cursor = connection.cursor()
                cursor.execute(query_string, (
                    economics_info_obj.name,
                    economics_info_obj.location,
                    economics_info_obj.category,
                    economics_info_obj.type,
                    economics_info_obj.source,
                    economics_info_obj.metadata))
                connection.commit()
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)

    def remove_economics_info_table(self):
        logger.Logger.log(logger.LogLevel.INFO, 'Drop economics_info_table %s' % self.economics_info_table_name)
        try:
            drop_economics_info_table = self.get_economics_info_table_object()
            drop_economics_info_table.drop(self.engine, checkfirst=False)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)

    def get_economics_info_data(self):
        try:
            with self.dao_factory.create(
                    self.username,
                    self.password,
                    self.server,
                    self.database) as connection:
                query_string = 'SELECT * FROM %s' % self.economics_info_table_name

                cursor = connection.cursor()
                cursor.execute(query_string)
                data = cursor.fetchall()
                economics_info_list = [economics_info.EconomicsInfo(
                        id=row[0],
                        name=row[1],
                        location=row[2],
                        category=row[3],
                        type=row[4],
                        source=row[5],
                        metadata=row[6]) for row in data]
                return economics_info_list
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)


if __name__ == '__main__':
    economics_info_db = EconomicsInfoDatabase(
            'mysql',
            Config.mysql_username,
            Config.mysql_password,
            Config.mysql_server,
            Config.mysql_database)
    economics_info_db.create_economics_info_table()