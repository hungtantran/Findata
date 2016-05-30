__author__ = 'hungtantran'

import pprint
import datetime
import logger
import re
import time
from httplib2 import Http

from constants_config import Config
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from oauth2client.service_account import ServiceAccountCredentials


class CloudSqlHelper(object):
    # Read more at https://developers.google.com/resources/api-libraries/documentation/sqladmin/v1beta4/python/latest/
    SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

    def __init__(self, project_id, instance_id, client_secret):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                client_secret, scopes=CloudSqlHelper.SCOPES)

        http_auth = self.credentials.authorize(Http())

        # Create a CloudSql client using the credentials.
        self.cloudsqlapi_service = discovery.build(
                'sqladmin', 'v1beta4', http=http_auth)
        self.storage_service = discovery.build(
                'storage', 'v1', http=http_auth)

        self.project_id = project_id
        self.instance_id = instance_id
        self.client_secret = client_secret

    def list_instances(self):
        # List all datasets in CloudSql
        try:
            # TODO parse result like this
            instances = self.cloudsqlapi_service.instances().list(
                    project=self.project_id).execute()
            return instances
        except Exception as e:
            logger.Logger.error('Exception = %s' % e)

        return None

    def export_table_to_cloud_storage(self, sql_database, sql_table,
                                      storage_bucket, storage_filename):
        try:
            logger.Logger.info('Export table %s from database %s to %s/%s' % (
                    sql_table, sql_database, storage_bucket, storage_filename))
            request_body = {
                'exportContext': {
                    'kind': 'sql#exportContext',
                    'fileType': 'CSV',
                    'uri': 'gs://%s/%s' % (storage_bucket, storage_filename),
                    'csvExportOptions': {
                        'selectQuery': 'SELECT * FROM %s' % sql_table
                    },
                    'databases': [
                        '%s' % sql_database
                    ]
                }
            }
            result = self.cloudsqlapi_service.instances().export(
                    project=self.project_id,
                    instance=self.instance_id,
                    body=request_body).execute()
            logger.Logger.info('Export result %s' % result)
            return result
        except Exception as e:
            logger.Logger.error('Exception = %s' % e)

    def export_sql_to_cloud_storage(self, sql_database, storage_bucket,
                                    storage_filename, wait_until_complete=True):
        try:
            logger.Logger.info('Export sql database %s to %s/%s' % (
                    sql_database, storage_bucket, storage_filename))
            request_body = {
                'exportContext': {
                    'kind': 'sql#exportContext',
                    'fileType': 'SQL',
                    'uri': 'gs://%s/%s' % (storage_bucket, storage_filename),
                    'databases': [
                        '%s' % sql_database
                    ]
                }
            }
            result = self.cloudsqlapi_service.instances().export(
                    project=self.project_id,
                    instance=self.instance_id,
                    body=request_body).execute()
            logger.Logger.info('Export result %s' % result)

            if wait_until_complete:
                self.poll_job(result)

            return result
        except Exception as e:
            logger.Logger.error('Exception = %s' % e)

    def poll_job(self, job, polling_frequency_in_sec=60):
        """Waits for a job to complete."""
        logger.Logger.info('Waiting for job to finish...')
        request = self.cloudsqlapi_service.operations().get(
                project=job['targetProject'],
                operation=job['name'])

        num_wait_sec = 0
        while True:
            result = request.execute(num_retries=2)
            if result['status'] == 'DONE':
                logger.Logger.info('Job complete.')
                return
            else:
                logger.Logger.info(
                        'Wait %d secs for project %s, wait more. Jobs: %s' % (
                                num_wait_sec, job['targetProject'], result))
            time.sleep(polling_frequency_in_sec)
            num_wait_sec += polling_frequency_in_sec


if __name__ == '__main__':
    cloud_sql_client = CloudSqlHelper(
            project_id=Config.cloud_projectid,
            instance_id=Config.cloudsql_instanceid,
            client_secret=Config.cloudsql_secret_json)

    now = datetime.datetime.now()
    storage_filename = '%s/%s/%s/total' % (
            now.year, now.month, now.day)
    cloud_sql_client.export_sql_to_cloud_storage(
            sql_database=Config.mysql_database,
            storage_bucket='market_data_analysis',
            storage_filename=storage_filename)
