__author__ = 'hungtantran'

import pprint
import datetime
import logger
import re
import time
from httplib2 import Http

from constants_config import Config
from googleapiclient import discovery
from googleapiclient import http
from googleapiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from oauth2client.service_account import ServiceAccountCredentials


class CloudStorageBucket(object):
    def __init__(self, name, time_created, time_updated):
        self.name = name
        self.time_created = time_created
        self.time_updated = time_updated


class CloudStorageObject(object):
    def __init__(self, name, directory, bucket, is_directory, size):
        self.name = name
        self.directory = directory
        self.bucket = bucket
        self.is_directory = is_directory
        self.size = size


class CloudStorageHelper(object):
    # Read more at https://developers.google.com/resources/api-libraries/documentation/storage/v1/python/latest/
    SCOPES = ['https://www.googleapis.com/auth/cloud-platform']

    def __init__(self, project_id, client_secret):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
                client_secret, scopes=CloudStorageHelper.SCOPES)

        http_auth = self.credentials.authorize(Http())

        self.storage_service = discovery.build(
                'storage', 'v1', http=http_auth)

        self.project_id = project_id
        self.client_secret = client_secret

    def list_buckets(self):
        # List all buckets
        try:
            buckets_json = self.storage_service.buckets().list(
                    project=self.project_id).execute()

            buckets = []
            for bucket_json in buckets_json['items']:
                buckets.append(CloudStorageBucket(
                        name=bucket_json['name'],
                        time_created=bucket_json['timeCreated'],
                        time_updated=bucket_json['updated']))
            return buckets
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

        return None

    def list_objects(self, bucket, directory):
        # List all objects under a directory in a bucket
        try:
            objects_json = self.storage_service.objects().list(
                    bucket=bucket,
                    prefix=directory).execute()

            objects = []
            for object_json in objects_json['items']:
                name = object_json['name']
                is_directory = (name[-1:] == "/")
                if is_directory:
                    name = name[:-1]

                index = name.rfind("/")
                object_directory = ""
                if not is_directory:
                    object_directory = name[:index+1]
                    name = name[index+1:]

                objects.append(CloudStorageObject(
                        name=name,
                        directory=object_directory,
                        bucket=bucket,
                        is_directory=is_directory,
                        size=int(object_json['size'])))
            return objects
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

        return None

    def get_object(self, bucket, filename, out_file):
        req = self.storage_service.objects().get_media(
                bucket=bucket, object=filename)
        downloader = http.MediaIoBaseDownload(out_file, req)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download {}%.".format(int(status.progress() * 100)))
        return out_file

    def delete_object(self, bucket, filename):
        req = self.storage_service.objects().delete(
                bucket=bucket, object=filename)
        resp = req.execute()
        return resp

    def upload_object(self, bucket, filename, readers, owners):
        body = {'name': filename}

        if readers or owners:
            body['acl'] = []

        for r in readers:
            body['acl'].append({
                'entity': 'user-%s' % r,
                'role': 'READER',
                'email': r
            })

        for o in owners:
            body['acl'].append({
                'entity': 'user-%s' % o,
                'role': 'OWNER',
                'email': o
            })

        with open(filename, 'rb') as f:
            req = self.storage_service.objects().insert(
                bucket=bucket, body=body,
                media_body=http.MediaIoBaseUpload(
                        f, 'application/octet-stream'))
            resp = req.execute()

        return resp

