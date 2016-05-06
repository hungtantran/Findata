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


class BigQueryClient(object):
    SCOPES = ['https://www.googleapis.com/auth/bigquery']
    CLIENT_SECRETS = 'Key/model-5798ace788b3.json'
    PROJECT_ID = 'model-1256'

    def __init__(self, project_id, dataset_id):
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            BigQueryClient.CLIENT_SECRETS, scopes=BigQueryClient.SCOPES)

        # Create a BigQuery client using the credentials.
        self.bigquery_service = discovery.build(
            'bigquery', 'v2', credentials=self.credentials)

        self.project_id = project_id
        self.dataset_id = dataset_id

    def list_dataset(self):
        # List all datasets in BigQuery
        try:
            datasets = self.bigquery_service.datasets()
            listReply = datasets.list(projectId=self.project_id).execute()
            return listReply
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def create_table(self, tablename, column_names, types):
        if len(column_names) != len(types):
            logger.Logger.log(logger.LogLevel.WARN, 'Mismatch number of column names (%d) and types (%d)' %
                              (len(column_names), len(types)))
            return

        # Since bigquery doesn't support delete, we implement delete by append a column indicate delete or not
        column_names.append('deleted')
        types.append('BOOLEAN')

        try:
            fields = []
            for i, column_name in enumerate(column_names):
                column = {'type': types[i], 'name': column_name}
                fields.append(column)

            schema = {}
            schema['fields'] = fields
            table_ref = {'tableId': tablename,
                         'datasetId': self.dataset_id,
                         'projectId': self.project_id}
            table = {'tableReference': table_ref,
                     'schema': schema}
            logger.Logger.log(logger.LogLevel.INFO, 'Create table %s with column names %s, type %s' % (tablename, column_names, types))
            self.bigquery_service.tables().insert(projectId=self.project_id,
                                                  datasetId=self.dataset_id,
                                                  body=table).execute()
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def delete_table(self, tablename):
        try:
            self.bigquery_service.tables().delete(projectId=self.project_id,
                                                  datasetId=self.dataset_id,
                                                  tableId=tablename).execute()
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def list_table(self):
        try:
            results = self.bigquery_service.tables().list(projectId=self.project_id,
                                                          datasetId=self.dataset_id).execute()
            # Sample results:
            # {u'totalItems': 1, u'tables': [{u'kind': u'bigquery#table', u'type': u'TABLE', u'id': u'model-1256:test_models.TEST1', u'tableReference': {u'projectId': u'model-1256', u'tableId': u'TEST1', u'datasetId': u'test_models'}}], u'kind': u'bigquery#tableList', u'etag': u'"oGMCLvGjZO7RB3oFjn17umMEDU4/dMsP55IY4G3Dzk4m2IL7cRkp9SY"'}
            tables_json = results['tables']
            table_names = []
            for table_json in tables_json:
                table_names.append(table_json['tableReference']['tableId'])
            return table_names
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def _extract_schema_from_json(self, json):
        fields = json['schema']['fields']
        column_names = []
        types = []
        for field in fields:
            column_names.append(field['name'])
            types.append(field['type'])
        return column_names, types

    def describe_table(self, tablename):
        try:
            results = self.bigquery_service.tables().get(projectId=self.project_id,
                                                         datasetId=self.dataset_id,
                                                         tableId=tablename).execute()
            return self._extract_schema_from_json(results)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def insert(self, tablename, values):
        column_names, types = self.describe_table(tablename)
        return self.insert_with_schema(tablename, column_names, values)

    def insert_with_schema(self, tablename, column_names, values):
        try:
            rows = []
            for value in values:
                json = {}
                # The last column of a table is always 'deleted', mark new row as not deleted
                value.append(False)
                for i, column_name in enumerate(column_names):
                    json[column_name] = value[i]

                row = {}
                row['json'] = json
                rows.append(row)
            body = {"rows": rows}

            logger.Logger.log(logger.LogLevel.INFO, 'Insert %d rows into table %s' % (len(rows), tablename))
            response = self.bigquery_service.tabledata().insertAll(projectId=self.project_id,
                                                                   datasetId=self.dataset_id,
                                                                   tableId=tablename,
                                                                   body=body).execute()
            print response
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def query(self, query_string):
        try:
            pattern = 'select .+ from ([^ ]+)'
            match = re.search(pattern, query_string, re.IGNORECASE)
            if match:
                tablename = match.group(1)
                full_tablename = '[%s.%s]' % (self.dataset_id, tablename)
                query_string = query_string.replace(tablename, full_tablename, 1)
            else:
                logger.Logger.log(logger.LogLevel.WARN, 'Cannot find table name from query %s' % query_string)
                return None

            query_data = {'query': query_string}
            query_response = self.bigquery_service.jobs().query(projectId=self.project_id,
                                                                body=query_data).execute()
            print query_response
            # Empty result set
            if 'rows' not in query_response:
                return []

            column_names, types = self._extract_schema_from_json(query_response)
            if column_names[-1] != 'deleted' or types[-1] != 'BOOLEAN':
                print 'here % %' % (column_names[-1], types[-1])
                logger.Logger.log(logger.LogLevel.WARN, 'Unrecognize table format column names %s types %s' % (column_names, types))
                return []

            rows = query_response['rows']
            results = []
            # Each row look like this {u'f': [{u'v': u'test1'}, {u'v': u'2'}, {u'v': u'3.0'}, {u'v': u'1.4573088E9'}, {u'v': u'false'}]}
            for row in rows:
                result = []
                for i, field in enumerate(row['f']):
                    if (types[i] == 'INTEGER'):
                        result.append(int(field['v']))
                    elif (types[i] == 'FLOAT'):
                        result.append(float(field['v']))
                    elif (types[i] == 'TIMESTAMP'):
                        # We convert timestamp to float first because of scientific notation like 1.4573088E9
                        result.append(datetime.datetime.fromtimestamp(int(float(field['v']))))
                    elif (types[i] == 'BOOLEAN'):
                        if field['v'] == 'false':
                            result.append(False)
                        else:
                            result.append(True)
                    else:
                        result.append(field['v'])

                # If the last column is True, it mean the row is deleted
                print result
                if result[-1]:
                    continue
                else:
                    result = result[:-1]
                results.append(result)
            print results
            return results
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def cursor(self):
        return self

    def _parse_create_query(self, query_string):
        pattern = 'create table (.+) \((.+)\)'
        match = re.search(pattern, query_string, re.IGNORECASE)
        if match:
            tablename = match.group(1)

            type_string = match.group(2) + ','
            type_pattern = '(\w+) (\w+).*?,'
            regex = re.compile(pattern=type_pattern)
            column_names = []
            types = []
            for type_match in regex.finditer(type_string):
                column_names.append(type_match.group(1))
                type = type_match.group(2)
                if ('char' in type.lower() or 'string' in type.lower()):
                    type = 'STRING'
                elif 'float' in type.lower():
                    type = 'FLOAT'
                elif 'int' in type.lower():
                    type = 'INTEGER'
                elif 'time' in type.lower():
                    type = 'TIMESTAMP'
                else:
                    logger.Logger.log(logger.LogLevel.WARN, 'Cannot recognize type %s' % type)
                    return None, None, None
                types.append(type)

            return tablename, column_names, types
        return None, None, None

    def execute(self, query_string):
        # TODO parse this into query, insert, delete, update, etc...
        query_string_lower = query_string.lower()
        if query_string_lower.startswith('select'):
            return self.query(query_string)
        elif query_string_lower.startswith('create table'):
            tablename, column_names, types = self._parse_create_query(query_string)
            if (tablename is None or
                column_names is None or
                types is None):
                return None

            return self.create_table(tablename=tablename,
                                     column_names=column_names,
                                     types=types)

        logger.Logger.log(logger.LogLevel.WARN, 'Cannot recognize query %s' % query_string)
        return None