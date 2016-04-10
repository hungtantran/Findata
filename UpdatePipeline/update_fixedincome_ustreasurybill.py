__author__ = 'hungtantran'


import datetime
import re
import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.sql
from time import sleep


class UpdateFixedincomeUstreasuryBill(object):
    def __init__(self, db_type, username, password, server, database):
        self.engine = sqlalchemy.create_engine('%s://%s:%s@%s/%s?charset=utf8&use_unicode=0' %
                                               (db_type, username, password, server, database))
        self.session = sqlalchemy.orm.sessionmaker(bind=self.engine)

            s = session()
            self.get_timeline_table_object(model=model,
                                           class_map=class_map)
            data = s.query(class_map).all()
            s.expunge_all()
            return data
        except Exception as e:
            Common.logger.Logger.log(Common.logger.LogLevel.ERROR, 'Exception = %s' % e)
        finally:
            if s is not None:
                s.commit()
                s.close()
        pass

    def update(self):
        pass