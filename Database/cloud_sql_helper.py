__author__ = 'hungtantran'

import pprint
import datetime
import logger
import re
import time

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from oauth2client.service_account import ServiceAccountCredentials


class CloudSqlHelper(object):
    SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
    CLIENT_SECRETS = 'Key/model-5798ace788b3.json'
    PROJECT_ID = 'model-1256'

    def __init__(self, project_id, dataset_id):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            CloudSqlHelper.CLIENT_SECRETS, scopes=CloudSqlHelper.SCOPES)

        # Create a BigQuery client using the credentials.
        self.bigquery_service = discovery.build(
            'bigquery', 'v2', credentials=self.credentials)

        self.project_id = project_id
        self.dataset_id = dataset_id

    def dump_sql_to_datastore(self):
        # List all datasets in BigQuery
        try:
            datasets = self.bigquery_service.datasets()
            listReply = datasets.list(projectId=self.project_id).execute()
            return listReply
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

        logger.Logger.log(logger.LogLevel.WARN, 'Cannot recognize query %s' % query_string)
        return None