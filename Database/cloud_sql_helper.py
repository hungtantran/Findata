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
            # {u'items': [{u'kind': u'sql#instance', u'name': u'models', u'settings': {u'kind': u'sql#settings', u'dataDiskType': u'PD_SSD', u'authorizedGaeApplications': [], u'activationPolicy': u'ALWAYS', u'backupConfiguration': {u'kind': u'sql#backupConfiguration', u'enabled': True, u'binaryLogEnabled': False, u'startTime': u'17:00'}, u'ipConfiguration': {u'ipv4Enabled': True, u'authorizedNetworks': [{u'kind': u'sql#aclEntry', u'name': u'All', u'value': u'0.0.0.0/0'}]}, u'pricingPlan': u'PER_USE', u'replicationType': u'SYNCHRONOUS', u'tier': u'db-f1-micro', u'settingsVersion': u'40', u'dataDiskSizeGb': u'100'}, u'region': u'us-central1', u'backendType': u'SECOND_GEN', u'project': u'model-1256', u'state': u'RUNNABLE', u'etag': u'"6k1naR9M9ROxjLCQwitIXBJ8XUk/7j1PzNO4U1-McviSnwvzLCJdMPQ"', u'serviceAccountEmailAddress': u'7vr5vqerzvblvdo2g4bjhxwuji@cloudsql.gserviceaccount.com', u'serverCaCert': {u'certSerialNumber': u'0', u'kind': u'sql#sslCert', u'sha1Fingerprint': u'15917b04d8fc9203b1e358b1cfb6bf7cd2114801', u'commonName': u'C=US,O=Google\\, Inc,CN=Google Cloud SQL Server CA', u'instance': u'models', u'cert': u'-----BEGIN CERTIFICATE-----\nMIIDITCCAgmgAwIBAgIBADANBgkqhkiG9w0BAQUFADBIMSMwIQYDVQQDExpHb29n\nbGUgQ2xvdWQgU1FMIFNlcnZlciBDQTEUMBIGA1UEChMLR29vZ2xlLCBJbmMxCzAJ\nBgNVBAYTAlVTMB4XDTE2MDMyMzA2NDczOVoXDTE4MDMyMzA2NDgzOVowSDEjMCEG\nA1UEAxMaR29vZ2xlIENsb3VkIFNRTCBTZXJ2ZXIgQ0ExFDASBgNVBAoTC0dvb2ds\nZSwgSW5jMQswCQYDVQQGEwJVUzCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC\nggEBAIFHne2ugiE2ZzrmV/eRbprAZ5pjCucPHcBK6R9ZkhbpkgIY3qk/xztLLzGl\nn8IHBAd4KBd21mmPMIPhbq+voYNfN11IuV2R4Uy0Tl4Lm85qMkfp5lsvCKSVS+OZ\nF5lXRpgYMFRq9LIxdSNAGxjh+HwFsgq+Gr7dB9kUiGT/9hfLYfw/rYw/6LsUCylm\niGL9wWtVJ6hyi9z+/pQx8mFUGouKw5xUfNt+HOctPq3OTH5mp4IHRQh6DFKJALrV\nNeWjSEQZRjevtiW/EMvklWRTGJ+6jWrljFdPrO1eeh8/uIlu9AxK78/3XIzOnjr4\nBvpeNK772FRhmH28Srx9LLK0rsUCAwEAAaMWMBQwEgYDVR0TAQH/BAgwBgEB/wIB\nADANBgkqhkiG9w0BAQUFAAOCAQEAPpJ4pyrdrONak0ygCfhZxlyHRXEdvXLWZSNR\nwR5JTEr1GmdJA6Hf43CKLp8xXE9JJNrnlGHbaBCnuCAIQlMupSb77vBroLE5kv+R\n4m2pXz+os6WpPzooMQ/0o2ud1OozCrc5+t3jB1viOe/rSlcuARBRXVlZWeB+zKbV\nuzJ7IQfbwdfUJJfcYPnZS7VBgn6+n1i/82//TRwIh33X5ZDChFkX6i1GcagbxBVi\nbchp4gmwa3ODTkVu3pyU+dFfu/RckTDnDzQBTiXfxOZ/JSUmgIXvQM7wABaNjY2/\nT3npw/0r8vNaoMVPiNDvc43JTN7dU3ZOtDNeY6PRzW+1Zn/OLg==\n-----END CERTIFICATE-----', u'expirationTime': u'2018-03-23T06:48:39.900Z', u'createTime': u'2016-03-23T06:47:39.900Z'}, u'ipAddresses': [{u'ipAddress': u'104.154.40.63'}], u'databaseVersion': u'MYSQL_5_6', u'instanceType': u'CLOUD_SQL_INSTANCE', u'selfLink': u'https://www.googleapis.com/sql/v1beta4/projects/model-1256/instances/models'}], u'kind': u'sql#instancesList'}
            instances = self.cloudsqlapi_service.instances().list(project=self.project_id).execute()
            return instances
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

        return None

    def export_table_to_cloud_storage(self, sql_database, sql_table, storage_bucket, storage_filename):
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
