__author__ = 'hungtantran'


import pprint

from googleapiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client.client import AccessTokenRefreshError
from oauth2client.service_account import ServiceAccountCredentials

SCOPES = ['https://www.googleapis.com/auth/bigquery']
CLIENT_SECRETS = 'Key/model-5798ace788b3.json'


def main():
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CLIENT_SECRETS, scopes=SCOPES)

    # Create a BigQuery client using the credentials.
    bigquery_service = discovery.build(
        'bigquery', 'v2', credentials=credentials)

    # List all datasets in BigQuery
    try:
        datasets = bigquery_service.datasets()
        listReply = datasets.list(projectId='model-1256').execute()
        print('Dataset list:')
        print listReply

    except HttpError as err:
        print('Error in listDatasets:')
        pprint.pprint(err.content)

    except AccessTokenRefreshError:
        print('Credentials have been revoked or expired, please re-run'
              'the application to re-authorize')


if __name__ == '__main__':
    main()
