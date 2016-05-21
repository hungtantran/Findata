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
import timeline_model
from database_helper import DatabaseHelper


class TimelineModelDatabase(object):
    max_num_reties = 1;

    def __init__(self, db_type, username, password, server, database):
        self.dao_factory = DAOFactoryRepository.getInstance(db_type)
        self.username = username
        self.password = password
        self.server = server
        self.database = database
        self.engine = sqlalchemy.create_engine('%s://%s:%s@%s/%s?charset=utf8&use_unicode=0' %
                                               (db_type, username, password, server, database))
        self.session = sqlalchemy.orm.sessionmaker(bind=self.engine)

    @staticmethod
    def create_model_name(model):
        return model.replace(' ', '_')

    def get_timeline_table_object(self, model, class_map):
        model_name = TimelineModelDatabase.create_model_name(model)
        metadata = sqlalchemy.MetaData(bind=self.engine)
        timeline_table = sqlalchemy.Table(model_name, metadata,
                                          sqlalchemy.Column('time', sqlalchemy.DateTime, primary_key=True),
                                          sqlalchemy.Column('value', sqlalchemy.Float, nullable=False))
        sqlalchemy.orm.clear_mappers()
        sqlalchemy.orm.mapper(class_map, timeline_table)
        return timeline_table

    def create_model(self, model, insert_to_data_store=False):
        Common.logger.Logger.log(Common.logger.LogLevel.INFO, 'Create model %s' % model)
        try:
            new_table = self.get_timeline_table_object(model=model,
                                                       class_map=timeline_model.TimelineModel)
            new_table.create(self.engine, checkfirst=True)
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)

    def insert_value(self, model, time, value, ignore_duplicate=False):
        try:
            s = self.session()
            self.get_timeline_table_object(model=model,
                                           class_map=timeline_model.TimelineModel)
            new_value = timeline_model.TimelineModel(time=StringHelper.convert_string_to_datetime(time),
                                                     value=value)
            if ignore_duplicate:
                s.merge(new_value)
            else:
                s.add(new_value)
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)
        finally:
            if s is not None:
                s.commit()
                s.close()

    def insert_row(self, model, timeline_model_obj):
        print 'here ' + StringHelper.convert_datetime_to_string(timeline_model_obj.time)
        return self.insert_value(model,
                                 StringHelper.convert_datetime_to_string(timeline_model_obj.time),
                                 timeline_model_obj.value)

    def insert_values(self, model, times, values, ignore_duplicate=False):
        if len(times) != len(values):
            Common.logger.Logger.log(Common.logger.LogLevel.INFO, 'Mismatch number of times (%d) and values (%d)' %
                              (len(times), len(values)))
            return

        try:
            s = self.session()
            self.get_timeline_table_object(model=model,
                                           class_map=timeline_model.TimelineModel)
            new_value_arr = []
            for i in range(len(times)):
                new_value_arr.append(timeline_model.TimelineModel(time=StringHelper.convert_string_to_datetime(times[i]),
                                                                  value=values[i]))

            s.bulk_save_objects(new_value_arr)
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)
        finally:
            if s is not None:
                s.commit()
                s.close()

    def remove_model(self, model):
        Common.logger.Logger.log(Common.logger.LogLevel.INFO, 'Drop model %s' % model)

        Common.logger.Logger.log(Common.logger.LogLevel.INFO, 'Create model %s' % model)
        try:
            drop_model = self.get_timeline_table_object(model=model,
                                                        class_map=timeline_model.TimelineModel)
            drop_model.drop(self.engine, checkfirst=False)
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)

    def get_model_data(self, model, lower_time_limit=None):
        try:
            s = self.session()
            self.get_timeline_table_object(model=model,
                                           class_map=timeline_model.TimelineModel)
            data = s.query(timeline_model.TimelineModel).order_by(timeline_model.TimelineModel.time).all()
            s.expunge_all()
            return data
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)
        finally:
            if s is not None:
                s.commit()
                s.close()

    def get_latest_model_data(self, model):
        try:
            s = self.session()
            self.get_timeline_table_object(model=model,
                                           class_map=timeline_model.TimelineModel)
            data = s.query(timeline_model.TimelineModel).order_by(timeline_model.TimelineModel.time.desc()).first()
            s.expunge_all()
            return data
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)
        finally:
            if s is not None:
                s.commit()
                s.close()

    def get_join_models_data(self, model1, model2, class_map1, class_map2, lower_time_limit=None, upper_time_limit=None):
        try:
            s = self.session()
            self.get_timeline_table_object(model=model1,
                                           class_map=class_map1)
            self.get_timeline_table_object(model=model2,
                                           class_map=class_map2)
            lower_time_object, upper_time_object = DatabaseHelper.get_time_limit(lower_time_limit, upper_time_limit)
            q = session.query(lower_time_object).\
                join(User.addresses).filter(Address.email.like('q%'))

            lower_time_object, upper_time_object = self.get_time_limit(lower_time_limit, upper_time_limit)
            avg = s.query(sqlalchemy.sql.func.avg(class_map1.value).label('average')).filter(
                    class_map1.time >= lower_time_object).filter(class_map1.time <= upper_time_object)
            s.expunge_all()
            return avg[0][0]
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)
        finally:
            if s is not None:
                s.commit()
                s.close()

    def get_average_model_data(self, model, lower_time_limit=None, upper_time_limit=None):
        try:
            s = self.session()
            self.get_timeline_table_object(model=model,
                                           class_map=timeline_model.TimelineModel)
            lower_time_object, upper_time_object = DatabaseHelper.get_time_limit(lower_time_limit, upper_time_limit)
            avg = s.query(sqlalchemy.sql.func.avg(timeline_model.TimelineModel.value).label('average')).filter(
                    timeline_model.TimelineModel.time >= lower_time_object).filter(timeline_model.TimelineModel.time <= upper_time_object)
            s.expunge_all()
            return avg[0][0]
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)
        finally:
            if s is not None:
                s.commit()
                s.close()

    def get_std_model_data(self, model, lower_time_limit=None, upper_time_limit=None):
        try:
            s = self.session()
            self.get_timeline_table_object(model=model,
                                           class_map=timeline_model.TimelineModel)
            lower_time_object, upper_time_object = DatabaseHelper.get_time_limit(lower_time_limit, upper_time_limit)
            avg = s.query(sqlalchemy.sql.func.std(timeline_model.TimelineModel.value).label('std')).filter(
                    timeline_model.TimelineModel.time >= lower_time_object).filter(
                    timeline_model.TimelineModel.time <= upper_time_object)
            s.expunge_all()
            return avg[0][0]
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)
        finally:
            if s is not None:
                s.commit()
                s.close()

    def get_all_models_names(self):
        try:
            metadata = sqlalchemy.MetaData(bind=self.engine)
            return self.engine.table_names()
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, e)
