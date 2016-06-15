__author__ = 'hungtantran'

import init_app

import datetime

import logger
from Database.cloud_sql_helper import CloudSqlHelper
from Common.constants_config import Config
from UpdatePipeline.Flow import Flow
from UpdatePipeline.Flow import FlowStatus


class BackupCloudSqlFlow(Flow):
    cloud_sql_client = None
    mysql_database = None
    storage_bucket = None

    def __init__(self, cloud_sql_client, mysql_database, storage_bucket):
        super(BackupCloudSqlFlow, self).__init__("BackupCloudSqlFlow")
        self.cloud_sql_client = cloud_sql_client
        self.mysql_database = mysql_database
        self.storage_bucket = storage_bucket

    def status(self):
        # TODO: implement async and return real status here
        return self.status

    def start(self):
        if self.status != FlowStatus.NOT_START:
            return

        now = datetime.datetime.now()
        storage_filename = '%s/%s/%s/total' % (now.year, now.month, now.day)

        self.cloud_sql_client.export_sql_to_cloud_storage(
            sql_database=self.mysql_database,
            storage_bucket=self.storage_bucket,
            storage_filename=storage_filename,
            wait_until_complete=True)

        # TODO: return error in case export fail
        self.status = FlowStatus.SUCCESS

    def rollback(self):
        raise NotImplementedError


if __name__ == '__main__':
    cloud_sql_client = CloudSqlHelper(
            project_id=Config.cloud_projectid,
            instance_id=Config.cloudsql_instanceid,
            client_secret=Config.cloudsql_secret_json)
    backup_cloudsql_flow = BackupCloudSqlFlow(
            cloud_sql_client=cloud_sql_client,
            mysql_database=Config.mysql_database,
            storage_bucket=Config.cloudstorage_bucket)
    backup_cloudsql_flow.start()
    print backup_cloudsql_flow.status()