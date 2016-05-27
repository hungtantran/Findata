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

    def full_path(self):
        full_path = '%s/%s' % (self.directory, self.name)
        if full_path[0] == '/':
            full_path = full_path[1:]
        return full_path


class CloudStorageDataflowObject(object):
    def __init__(self, name, size, cloud_storage_objects):
        self.name = name
        self.size = size
        self.cloud_storage_objects = cloud_storage_objects


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

    def list_objects(self, bucket, prefix):
        # List all objects under a prefix in a bucket
        try:
            objects_json = self.storage_service.objects().list(
                    bucket=bucket,
                    prefix=prefix).execute()
            objects = []
            for object_json in objects_json['items']:
                name = object_json['name']
                is_directory = (name[-1:] == "/")
                if is_directory:
                    name = name[:-1]

                index = name.rfind("/")
                object_directory = ""
                if (not is_directory) and (index != -1):
                    object_directory = name[:index]
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

        return []

    def list_dataflow_result(self, bucket, prefix):
        objects = self.list_objects(bucket, prefix)
        dataflow_obj_map = {}

        for obj in objects:
            full_path = obj.full_path()
            if prefix not in full_path:
                continue

            # result.1464158881.07.txt-00000-of-00006
            match = re.search(r"(result.*)-([0-9]+)-of-([0-9]+)", obj.name)
            if match:
                # Return file name and part number
                file_name = match.group(1)
                part_number = int(match.group(2))
                total_parts = int(match.group(3))
                if file_name not in dataflow_obj_map:
                    dataflow_obj_map[file_name] = CloudStorageDataflowObject(
                            name=file_name,
                            size=total_parts,
                            cloud_storage_objects=[obj])
                else:
                    dataflow_obj_map[file_name].cloud_storage_objects.append(
                            obj)
            else:
                continue

        results = []
        for file_name in dataflow_obj_map:
            results.append(dataflow_obj_map[file_name])
        return results

    def get_object(self, bucket, filename, out_filename):
        with open(out_filename, "w") as out_file:
            req = self.storage_service.objects().get_media(
                    bucket=bucket, object=filename)
            downloader = http.MediaIoBaseDownload(out_file, req)

            done = False
            while done is False:
                status, done = downloader.next_chunk()
                logger.Logger.info("Download %d%% to %s" % (
                        int(status.progress() * 100),
                        out_filename))

    def get_dataflow_file(self, bucket, dataflow_filename, out_filename):
        dataflow_objs = self.list_dataflow_result(bucket, dataflow_filename)
        if len(dataflow_objs) != 1:
            logger.Logger.error("Find %d dataflow obj" % len(dataflow_objs)) 
            return
        return self.get_dataflow_object(bucket, dataflow_objs[0], out_filename)

    def get_dataflow_object(self, bucket, dataflow_obj, out_filename):
        with open(out_filename, "a") as out_file:
            for obj in dataflow_obj.cloud_storage_objects:
                filename = obj.full_path()
                req = self.storage_service.objects().get_media(
                        bucket=bucket, object=filename)
                downloader = http.MediaIoBaseDownload(out_file, req)

                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    logger.Logger.info("Download %d%% to %s" % (
                        int(status.progress() * 100),
                        out_filename))

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

