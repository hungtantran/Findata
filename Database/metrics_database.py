__author__ = 'hungtantran'

import datetime
import re
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql
from time import sleep

import logger
from dao_factory_repo import DAOFactoryRepository
from Common.string_helper import StringHelper
import metrics


class MetricsDatabase(object):
    max_num_reties = 1;

    def __init__(self, db_type, username, password, server, database, metric, use_orm=True):
        self.dao_factory = DAOFactoryRepository.getInstance(db_type)
        self.username = username
        self.password = password
        self.server = server
        self.database = database
        self.metric = metric

        if use_orm and metric is not None:
            self.engine = sqlalchemy.create_engine('%s://%s:%s@%s/%s?charset=utf8&use_unicode=0' %
                                                   (db_type, username, password, server, database),
                                                   pool_recycle=3600)
            self.session = sqlalchemy.orm.sessionmaker(bind=self.engine, expire_on_commit=False)
            self.table = self.get_metrics_table_object(
                    metric=metric,
                    class_map=metrics.Metrics)

    @staticmethod
    def create_metric_name(metric):
        return metric.replace(' ', '_')

    def get_metrics_table_object(self, metric, class_map):
        metric_name = MetricsDatabase.create_metric_name(metric)
        metadata = sqlalchemy.MetaData(bind=self.engine)
        metrics_table = sqlalchemy.Table(
                metric_name, metadata,
                sqlalchemy.Column('id', sqlalchemy.INTEGER, primary_key=True, autoincrement=True),
                sqlalchemy.Column('metric_name', sqlalchemy.String(255), nullable=False),
                sqlalchemy.Column('value', sqlalchemy.Float),
                sqlalchemy.Column('unit', sqlalchemy.String(32)),
                sqlalchemy.Column('start_date', sqlalchemy.DateTime),
                sqlalchemy.Column('end_date', sqlalchemy.DateTime),
                sqlalchemy.Column('metadata', sqlalchemy.TEXT),
                sqlalchemy.UniqueConstraint('metric_name', 'start_date', 'end_date'))
        return metrics_table

    def create_metric(self, insert_to_data_store=False):
        logger.Logger.log(logger.LogLevel.INFO, 'Create metric %s' % self.metric)
        try:
            self.table.create(self.engine, checkfirst=True)
        except Exception as e:
            logger.Logger.error('Exception = %s' % e)

    def insert_metric(self, new_metric, ignore_duplicate=False):
    	return self.insert_metrics([new_metric])

    def insert_metrics(self, new_metrics, ignore_duplicate=True):
        try:
            with self.dao_factory.create(self.username,
                                         self.password,
                                         self.server,
                                         self.database) as connection:
                # TODO need to make this general
                # TODO seriously need to make this parametrized
                cursor = connection.cursor()
                values_arr = []

                for metric in new_metrics:
                    value_string = '('
                    value_string += "'%s'," % metric.metric_name
                    value_string += "%s," % metric.value
                    value_string += "'%s'," % metric.unit
                    value_string += "'%s'," % StringHelper.convert_datetime_to_string(metric.start_date)
                    value_string += "'%s'," % StringHelper.convert_datetime_to_string(metric.end_date)

                    if metric.metadata is None:
                        value_string += "NULL"
                    else:
                        value_string += "'%s'" % metric.metadata

                    value_string += ')'
                    values_arr.append(value_string)

                if len(values_arr) > 0:
                    query_string = "INSERT "
                    if ignore_duplicate:
                        query_string += "IGNORE "
                    query_string += "INTO %s (metric_name, value, unit, start_date, end_date, metadata) VALUES %s" % (self.metric, ','.join(values_arr))
                    cursor.execute(query_string)
                    connection.commit()
        except Exception as e:
            logger.Logger.error('Exception = %s' % e)

    def remove_metric(self):
        logger.Logger.log(logger.LogLevel.INFO, 'Drop metric %s' % self.metric)
        # TODO figure out why this make update_exchange_stockprice_test deadlock
        try:
            self.session.close_all()
            self.table.drop(self.engine, checkfirst=False)
        except Exception as e:
            logger.Logger.error('Exception = %s' % e)

    def get_metrics(self, metric_name=None, max_num_results=None, reverse_order=False):
        try:
            with self.dao_factory.create(
                    self.username,
                    self.password,
                    self.server,
                    self.database) as connection:
                query_string = 'SELECT * FROM %s' % self.metric
                if metric_name is not None:
                    query_string += ' WHERE metric_name = \'%s\'' % metric_name
                if reverse_order:
                    query_string += ' ORDER BY start_date'
                else:
                    query_string += ' ORDER BY start_date DESC'
                if max_num_results is not None:
                    query_string += ' LIMIT %d' % max_num_results 

                cursor = connection.cursor()
                cursor.execute(query_string)
                data = cursor.fetchall()
                metric_list = [metrics.Metrics(
                        id=row[0],
                        metric_name=row[1],
                        value=row[2],
                        unit=row[3],
                        start_date=row[4],
                        end_date=row[5],
                        metadata=row[6]) for row in data]
                return metric_list
        except Exception as e:
            logger.Logger.error('Exception = %s' % e)

    def get_all_metrics_tables(self):
        try:
            with self.dao_factory.create(
                    self.username,
                    self.password,
                    self.server,
                    self.database) as connection:
                cursor = connection.cursor()
                query_string = r"SHOW TABLES LIKE '%metrics'"
                cursor.execute(query_string)
                data = cursor.fetchall()
                metrics_table_list = [row[0] for row in data]
                return metrics_table_list
        except Exception as e:
            logger.Logger.error('Exception = %s' % e)

    def get_earliest_time(self, metric_name=None):
        earliest_rows = self.get_metrics(metric_name=metric_name, max_num_results=1, reverse_order=True)
        earliest_time = None
        try:
            earliest_time = earliest_rows[0].start_date
        except Exception as e:
            logger.Logger.error('Exception = %s' % e)
            earliest_time = None
        return earliest_time

    def get_latest_time(self, metric_name=None):
        latest_rows = self.get_metrics(metric_name=metric_name, max_num_results=1)
        latest_time = None
        try:
            latest_time = latest_rows[0].start_date
        except Exception as e:
            logger.Logger.error('Exception = %s' % e)
            latest_time = None
        return latest_time

    def get_earliest_and_latest_time(self, metric_name=None):
        # Find the latest and earliest time
        latest_time = self.get_latest_time(metric_name=metric_name)
        earliest_time = self.get_earliest_time(metric_name=metric_name)

        return latest_time, earliest_time

    def update_database_with_given_data(self, data, latest_time, earliest_time):
        num_value_update = 0
        for row in data:
            insert_rows = []
            # Only insert value later than the current latest value
            # TODO make it more flexible than that
            if ((latest_time is None or row.start_date > latest_time) or 
                (earliest_time is None or row.start_date < earliest_time)):
                insert_rows.append(row)
                num_value_update += 1

            if len(insert_rows) > 0:
                self.insert_metrics(insert_rows)

        logger.Logger.info('Update table %s with %d new values' % (self.metric, num_value_update))
        return num_value_update
