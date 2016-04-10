__author__ = 'hungtantran'


import json
import urllib2


def backup_database_to_cloud_storage():
    data = {}
    data['exportContext'] = {}
    data['exportContext']['kind'] = "sqlobject"
    data['exportContext']['fileType'] = "CSV"
    data['exportContext']['uri'] = "gs://model_data/backup_csv"
    data['exportContext']['databases'] = ['models']
    data['exportContext']['csvExportOptions'] = {}
    data['exportContext']['csvExportOptions']['selectQuery'] = 'SELECT * FROM data_source'


    req = urllib2.Request('https://www.googleapis.com/sql/v1beta4/projects/model-1256/instances/models/export')
    req.add_header('Content-Type', 'application/json')

    response = urllib2.urlopen(req, json.dumps(data))
    print response

backup_database_to_cloud_storage()
