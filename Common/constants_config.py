__author__ = 'hungtantran'


class Config(object):
    # https://developers.google.com/api-client-library/python/apis/
    # Google cloud project id
    cloud_projectid = 'model-1256'
    cloud_clientsecret = 'Key/model-5798ace788b3.json'

    # Mysql config
    test_mysql_username = 'root'
    test_mysql_password = 'test'
    test_mysql_server = '104.154.40.63'
    test_mysql_database = 'test_models'

    mysql_username = 'root'
    mysql_password = 'test'
    mysql_server = '104.154.40.63'
    mysql_database = 'models'

    # Cloud Sql config
    cloudsql_instanceid = 'models'
    cloudsql_secret_json = 'Key/model-5798ace788b3.json'

    # Cloud Storage config
    cloudstorage_secret_json = 'Key/model-5798ace788b3.json'
    cloudstorage_bucket = 'market_data_analysis'
    cloudstorage_bucket_test = 'market_data_analysis_test'

    # Bigquery config
    test_bigquery_username = None
    test_bigquery_password = None
    test_bigquery_server = 'model-1256'
    test_bigquery_database = 'test_models'

    bigquery_username = None
    bigquery_password = None
    bigquery_server = 'model-1256'
    bigquery_database = 'models'

    # Gmail config
    gmail_client_userid = 'hungtantran@gmail.com'
    gmail_secret_json = 'Key/client_secret_292129338715-tqmce99o5ejkehi7fpm59skmg81hvoh3.apps.googleusercontent.com.json'

    sec_ftp_link = 'ftp.sec.gov'
    sec_ftp_full_index_path = '/edgar/full-index'
    sec_xbrl_index_file = 'xbrl.idx'
    sec_xbrl_data_directory = '/edgar/data'

    sec_field_tags = ['us-gaap:GrossProfit', 'us-gaap:Liabilities', 'us-gaap:Assets', 'us-gaap:EarningsPerShareBasic',
                      'us-gaap:EarningsPerShareDiluted']
