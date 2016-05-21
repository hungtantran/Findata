__author__ = 'hungtantran'


import sys

from constants_config import Config
from dao_factory_repo import DAOFactoryRepository
from company_metrics_database import CompanyMetricsDatabase
from company_metrics import CompanyMetrics
from string_helper import StringHelper


def migrate_multiple_stock_metrics_into_one(tickername):

    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        cursor = connection.cursor()
        query_string = "show tables like 'exchange\_stockprice\_%s\_%%'" % tickername
        print query_string
        cursor.execute(query_string)
        data = cursor.fetchall()
        print data

        metric_table_name = '%s_metrics' % tickername
        metrics_db = CompanyMetricsDatabase(
                'mysql',
                 Config.mysql_username,
                 Config.mysql_password,
                 Config.mysql_server,
                 Config.mysql_database,
                 metric_table_name)
        #metrics_db.remove_metric()
        metrics_db.create_metric()

        metrics = []
        prefix = "exchange_stockprice_%s_" % tickername
        tablenames = []
        for table in data:
            tablename = table[0]
            tablenames.append(tablename)
            if not tablename.startswith(prefix):
                print 'Table %s does not start with' % (tablename, prefix)
                sys.exit()

            metric_name = tablename[len(prefix):]

            print "process metric %s for ticker %s" % (metric_name, tickername)
            cursor.execute("insert %s (metric_name, value, unit, start_date, end_date) select '%s' as metric_name, value, 'usd' as unit, time as start_date, time as end_date from %s" % (metric_table_name, metric_name, tablename))

        try:
            fundamental_table_name = 'company_fundamentals_%s_metrics' % tickername
            tablenames.append(fundamental_table_name)
            #cursor.execute('select * from company_fundamentals_%s_metrics' % tickername)

            cursor.execute("insert %s (metric_name, value, unit, start_date, end_date) select metrics_name as metric_name, value_float as value, metrics_unit as unit, start_date, end_date from %s" % (metric_table_name, fundamental_table_name))
        except Exception as e:
            print e

        print "Start inserting into table %s_metrics" % tickername
        connection.commit()

        # Clean old data
        for table in tablenames:
            try:
                cursor.execute('DROP TABLE %s' % table)
            except Exception as e:
                print e


def migrate_all():
    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        cursor = connection.cursor()
        query_string = "select ticker from ticker_info"
        print query_string
        cursor.execute(query_string)
        data = cursor.fetchall()
        index = 0
        for row in data:
            ticker = row[0].lower()
            index += 1
            print 'Process %d' % index
            if not ticker.isalnum():
                continue
            if ticker <= 'zyne':
                continue
            migrate_multiple_stock_metrics_into_one(ticker)

migrate_all()
#migrate_multiple_stock_metrics_into_one('msft')
