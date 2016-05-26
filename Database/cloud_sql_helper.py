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
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

        return None

    def export_table_to_cloud_storage(self, sql_database, sql_table,
                                      storage_bucket, storage_filename):
        try:
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
            return result
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
