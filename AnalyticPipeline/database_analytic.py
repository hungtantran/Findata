__author__ = 'hungtantran'


import Queue
import re
import threading

import logger
import ticker_info_database
from dao_factory_repo import DAOFactoryRepository
from string_helper import StringHelper
from Common.constants_config import Config


class DatabaseAnalytic(object):
    def __init__(self, db_type, username, password, server, database, max_num_threads=1):
        self.dao_factory = DAOFactoryRepository.getInstance(db_type)
        self.db_type = db_type
        self.username = username
        self.password = password
        self.server = server
        self.database = database
        self.max_num_threads = max_num_threads

        self.table_names = None
        self.tablename_regex = None
        self.max_result_per_table = None
        self.fields = None
        self.filter_clause = None
        self.orderby_clause = None
        self.analytic_func = None
        self.analytic_results = {}
        self.per_table_additional_data = {}
        self.q = Queue.Queue()

    def QueryTableName(self, tablename_regex):
        self.tablename_regex = tablename_regex
        return self

    def LimitTableNames(self, table_names):
        self.table_names = table_names
        return self

    def LimitResultPerTable(self, max_result_per_table):
        self.max_result_per_table = max_result_per_table
        return self

    # TODO make filter more generalizable instead of passing pure string here
    def Filter(self, filter_clause):
        self.filter_clause = filter_clause
        return self

    def OrderBy(self, orderby_clause):
        self.orderby_clause = orderby_clause
        return self

    def Fields(self, fields):
        self.fields = fields
        return self

    def AnalyticFunc(self, analytic_func):
        self.analytic_func = analytic_func
        return self

    def _GetTableNames(self):
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                cursor.execute('SHOW TABLES')
                data = cursor.fetchall()

                table_names = []
                for row in data:
                    table_names.append(row[0])
                return table_names
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

    def _FilterTableNames(self, table_names, tablename_regex):
        filtered_table_names = []
        for table_name in table_names:
            if re.search(tablename_regex, table_name):
                filtered_table_names.append(table_name)
        return filtered_table_names

    # TODO parametrize this instead of construct raw sql query
    def _ConstructPerTableQuery(self, table_name):
        query_string = 'SELECT '
        if self.fields is None or len(self.fields) == 0:
            query_string += '* '
        else:
            query_string += ', '.join(self.fields)
        query_string += ' FROM %s ' % table_name

        if self.filter_clause is not None:
            query_string += 'WHERE %s ' % self.filter_clause

        if self.orderby_clause is not None:
            query_string += 'ORDER BY %s ' % self.orderby_clause

        if self.max_result_per_table is not None:
            query_string += 'LIMIT %d' % self.max_result_per_table

        return query_string

    def _RunAnalyticPerTable(self):
        with self.dao_factory.create(self.username,
                                     self.password,
                                     self.server,
                                     self.database) as connection:
            # TODO need to make this general
            try:
                cursor = connection.cursor()
                while not self.q.empty():
                    table_name = self.q.get()
                    logger.Logger.log(logger.LogLevel.INFO, 'Run analytic for table %s' % table_name)

                    query_string = self._ConstructPerTableQuery(table_name)
                    print query_string
                    cursor.execute(query_string)
                    data = cursor.fetchall()

                    table_additional_data = None
                    if table_name in self.per_table_additional_data:
                        table_additional_data = self.per_table_additional_data[table_name]
                    result = self.analytic_func(data, table_additional_data)
                    self.analytic_results[table_name] = result
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
            finally:
                self.q.task_done()

    def RunAnalytic(self):
        if self.analytic_func is None:
            logger.Logger.log(logger.LogLevel.WARN, 'Need to provide analytic func')
            return

        if self.table_names is None:
            self.table_names = self._GetTableNames()

        if self.table_names is None:
            logger.Logger.log(logger.LogLevel.ERROR, 'Fail to get table names')
            return

        if self.tablename_regex is not None:
            self.table_names = self._FilterTableNames(self.table_names, self.tablename_regex)

        #TODO make this parallel or change it to spark or something
        logger.Logger.log(logger.LogLevel.INFO, 'Run analytic for %d tables' % len(self.table_names))
        self.analytic_results = {}

        for table_name in self.table_names:
            self.q.put(table_name)

        threads = []
        for i in range(self.max_num_threads):
            t = threading.Thread(target=self._RunAnalyticPerTable)
            threads.append(t)
            t.start()

        for i in range(len(threads)):
            wait_thread = threads[i]
            logger.Logger.log(logger.LogLevel.INFO, 'Wait for thread %s' % wait_thread.name)
            wait_thread.join()
            logger.Logger.log(logger.LogLevel.INFO, 'Thread %s done' % wait_thread.name)

    def GetAnalyticResults(self):
        return self.analytic_results


class UsEquityMetricsAnalytics(DatabaseAnalytic):
    def __init__(self, db_type, username, password, server, database, max_num_threads=5):
        super(UsEquityMetricsAnalytics, self).__init__(db_type, username, password, server, database, max_num_threads)
        self.orderby_clause = 'start_date desc'
        self.sector = None
        self.industry = None

    def RunAnalytic(self):
        try:
            ticker_info_db = ticker_info_database.TickerInfoDatabase(
                    self.db_type,
                    self.username,
                    self.password,
                    self.server,
                    self.database,
                    'ticker_info')
            data = ticker_info_db.get_ticker_info_data()

            self.table_names = []
            for ticker_info in data:
                if (ticker_info.ticker.isalnum() and
                    (self.sector is None or (ticker_info.sector is not None and self.sector.lower() in ticker_info.sector.lower())) and
                    (self.industry is None or (ticker_info.industry is not None and self.industry.lower() in ticker_info.industry.lower()))):
                    table_name = '%s_metrics' % ticker_info.ticker.lower()
                    self.table_names.append(table_name)
                    self.per_table_additional_data[table_name] = ticker_info
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
            raise e

        super(UsEquityMetricsAnalytics, self).RunAnalytic()

    def LimitSectorIndustry(self, sector, industry=None):
        self.sector = sector
        self.industry = industry
        return self

    def LimitTableNames(self, table_names):
        logger.Logger.log(logger.LogLevel.WARN, 'UsEquityMetricsAnalytics does not support LimitTableNames. Use '
                                                'QueryTableName if you need to limit tables')
        return self

    def CalculatePriceMovement(self, duration_in_days=10):
        def CalPriceMovement(data, ticker_info):
            price_movement = []
            for i in range(1, len(data)):
                price_change = (data[i - 1][0] - data[i][0]) / data[i][0] * 100
                price_movement.append(price_change)
            return price_movement


        self.Filter("metric_name = 'adj_close'")
        self.LimitResultPerTable(duration_in_days)
        self.Fields(['value, start_date'])
        self.AnalyticFunc(analytic_func=CalPriceMovement)
        self.RunAnalytic()
        results = self.GetAnalyticResults()
        return results

    def CalculateFundamentalMovement(self, fundamental, quarterly=True, yearly=False):
        def CalFundamentalMovement(data, ticker_info):
            fund_movement = []
            for i in range(1, len(data)):
                fund_change = (data[i - 1][0] - data[i][0]) / data[i][0] * 100
                fund_movement.append(fund_change)
            return fund_movement

        if ((quarterly and yearly) != False):
            logger.Logger.log(logger.LogLevel.WARN, 'Need to specify either quarterly or yearly')
            return None

        if ((quarterly or yearly) == False):
            logger.Logger.log(logger.LogLevel.WARN, 'Need to specify only one of quarterly or yearly')
            return None

        duration_filter = 'having duration < 100'
        if yearly:
            duration_filter = 'having duration > 100'
        self.Filter("metric_name = '%s' %s" % (fundamental, duration_filter))

        self.Fields(['value', 'DATEDIFF(end_date, start_date) as duration'])

        self.AnalyticFunc(analytic_func=CalFundamentalMovement)
        self.RunAnalytic()
        results = self.GetAnalyticResults()
        return results

    """def select *, DATEDIFF(end_date, start_date) as duration from msft_metrics where metric_name like 'grossprofit' having duration < 100 order by end_date desc;"""


if __name__ == '__main__':
    analytic_obj = UsEquityMetricsAnalytics(
            db_type='mysql',
            username=Config.mysql_username,
            password=Config.mysql_password,
            server=Config.mysql_server,
            database=Config.mysql_database).\
            LimitSectorIndustry(sector='Technology', industry='Software')
    """results = analytic_obj.CalculatePriceMovement(duration_in_days=2)"""
    results = analytic_obj.CalculateFundamentalMovement(fundamental='Revenues')
    with open('result.txt', 'w') as f:
        for table_name in results:
            results[table_name] = [str(value) for value in results[table_name]]
            line = table_name + ': ' + ','.join(results[table_name]) + '\n'
            f.write(line)

