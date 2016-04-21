__author__ = 'hungtantran'

import datetime
import re
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql
from time import sleep

import Common.logger
from dao_factory_repo import DAOFactoryRepository
from Common.string_helper import StringHelper
import metrics


class MetricsDatabase(object):
    max_num_reties = 1;

    def __init__(self, db_type, username, password, server, database, metric):
        self.dao_factory = DAOFactoryRepository.getInstance(db_type)
        self.username = username
        self.password = password
        self.server = server
        self.database = database
        self.engine = sqlalchemy.create_engine('%s://%s:%s@%s/%s?charset=utf8&use_unicode=0' %
                                               (db_type, username, password, server, database),
                                               pool_recycle=3600)
        self.session = sqlalchemy.orm.sessionmaker(bind=self.engine, expire_on_commit=False)
        self.metric = metric
        self.table = self.get_metrics_table_object(
                metric=metric,
                class_map=metrics.Metrics)

    @staticmethod
    def create_metric_name(metric):
        return metric.replace(' ', '_')

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
                sqlalchemy.Column('metadata', sqlalchemy.TEXT))
        sqlalchemy.orm.clear_mappers()
        sqlalchemy.orm.mapper(class_map, metrics_table)
        return metrics_table

    def create_metric(self, insert_to_data_store=False):
        Common.logger.Logger.log(Common.logger.LogLevel.INFO, 'Create metric %s' % self.metric)
        try:
            self.table.create(self.engine, checkfirst=True)
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)

    def insert_metric(self, new_metric, ignore_duplicate=False):
        try:
            self.session.close_all()
            s = self.session()
            if ignore_duplicate:
                s.merge(new_metric)
            else:
                s.add(new_metric)
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)
        finally:
            if s is not None:
                s.commit()
                s.close()

    def insert_metrics(self, new_metrics, ignore_duplicate=False):
        try:
            self.session.close_all()
            s = self.session()
            s.bulk_save_objects(new_metrics)
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)
        finally:
            if s is not None:
                s.commit()
                s.close()

    def remove_metric(self):
        Common.logger.Logger.log(Common.logger.LogLevel.INFO, 'Drop metric %s' % self.metric)
        # TODO figure out why this make update_exchange_stockprice_test deadlock
        try:
            self.session.close_all()
            self.table.drop(self.engine, checkfirst=False)
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)

    def get_metrics(self, metric_name=None, max_num_results=None):
        try:
            s = self.session()
            query = s.query(metrics.Metrics)
            if metric_name:
                query = query.filter_by(metric_name=metric_name)
            query = query.order_by(sqlalchemy.desc(metrics.Metrics.start_date))

            if max_num_results:
                data = query.limit(max_num_results)
            else:
                data = query.all()
            s.expunge_all()
            return data
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)
        finally:
            if s is not None:
                s.commit()
                s.close()
