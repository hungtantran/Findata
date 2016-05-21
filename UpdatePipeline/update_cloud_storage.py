__author__ = 'hungtantran'


import time
import logger
import threading

from constants_config import Config
from cloud_sql_helper import CloudSqlHelper
from metrics_database import MetricsDatabase


class UpdateCloudStorage(threading.Thread):
    UPDATE_FREQUENCY_SECONDS = 43200

    def __init__(self, db_type, username, password, server, database, cloud_projectid, cloudsql_instanceid, cloudstorage_bucket,
                 client_secret, update_frequency_seconds=None):
        threading.Thread.__init__(self)

        self.db_type = db_type
        self.username = username
        self.password = password
        self.server = server
        self.database = database
        self.cloudstorage_bucket = cloudstorage_bucket

        self.sql_helper = CloudSqlHelper(
                project_id=cloud_projectid,
                instance_id=cloudsql_instanceid,
                client_secret=client_secret)

        self.update_frequency_seconds = update_frequency_seconds or UpdateCloudStorage.UPDATE_FREQUENCY_SECONDS

    def run(self):
        SUCCESS_RESULTS = [u'PENDING', u'RUNNING', u'DONE']

        while True:
            try:
                metrics_db = MetricsDatabase(
                        self.db_type,
                        self.username,
                        self.password,
                        self.server,
                        self.database,
                        metric=None)
                metrics_table_list = metrics_db.get_all_metrics_tables()

                for metrics_table in metrics_table_list:
                    # Try a few time because multiple operations can't be parallel
                    for _ in range(3):
                        try:
                            result = self.sql_helper.export_table_to_cloud_storage(
                                    sql_database=self.database,
                                    sql_table=metrics_table,
                                    storage_bucket=self.cloudstorage_bucket,
                                    storage_filename=metrics_table)

                            result_success = False
                            if result['status'] in SUCCESS_RESULTS:
                                logger.Logger.info('Update table %s to cloud storage succeed with result code: %s' % (metrics_table, result['status']))
                            else:
                                logger.Logger.error('Update table %s to cloud storage fail with result: %s' % (metrics_table, result))
                            break
                        except Exception as e:
                            pass
                        finally:
                            time.sleep(5)

                logger.Logger.info('Sleep for %d secs before updating again' % self.update_frequency_seconds)
                # TODO make it sleep through weekend
            except Exception as e:
                logger.Logger.error(e)
            finally:
                time.sleep(self.update_frequency_seconds)


def main():
    try:
        update_obj = UpdateCloudStorage(
                db_type='mysql',
                username=Config.mysql_username,
                password=Config.mysql_password,
                server=Config.mysql_server,
                database=Config.mysql_database,
                cloud_projectid=Config.cloud_projectid,
                cloudsql_instanceid=Config.cloudsql_instanceid,
                cloudstorage_bucket=Config.cloudstorage_bucket,
                client_secret=Config.cloud_clientsecret)
        update_obj.daemon = True
        update_obj.start()

        while True:
            time.sleep(1)
    except Exception as e:
        logger.Logger.log(logger.LogLevel.ERROR, e)


if __name__ == '__main__':
    main()
