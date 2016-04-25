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
    def __init__(self, db_type, username, password, server, database, max_num_threads=20):
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
                    cursor.execute(query_string)
                    data = cursor.fetchall()

                    table_additional_data = None
                    if table_name in self.per_table_additional_data:
                        table_additional_data = self.per_table_additional_data[table_name]
                    result = self.analytic_func(data, table_additional_data)
                    self.analytic_results[table_name] = result
            except Exception as e:
                logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)

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
    def __init__(self, db_type, username, password, server, database, max_num_threads=20):
        super(UsEquityMetricsAnalytics, self).__init__(db_type, username, password, server, database, max_num_threads)
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
                if ticker_info.ticker.isalnum():
                    table_name = '%s_metrics' % ticker_info.ticker.lower()
                    self.table_names.append(table_name)
                    self.per_table_additional_data[table_name] = ticker_info
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, 'Exception = %s' % e)
            raise e

        self.orderby_clause = 'start_date desc'

    def LimitTableNames(self, table_names):
        logger.Logger.log(logger.LogLevel.WARN, 'UsEquityMetricsAnalytics does not support LimitTableNames. Use '
                                                'QueryTableName if you need to limit tables')
        return self

    @staticmethod
    def CalculatePriceMovement(db_type, username, password, server, database, duration_in_days=10, max_num_threads=20):
        def CalPriceMovement(data, ticker_info):
            price_movement = []
            for i in range(1, len(data)):
                price_change = (data[i - 1][0] - data[i][0]) / data[i][0] * 100
                price_movement.append(price_change)
            return price_movement

        analytics = UsEquityMetricsAnalytics(
                db_type=db_type,
                username=username,
                password=password,
                server=server,
                database=database,
                max_num_threads=max_num_threads).\
                Filter("metric_name = 'adj_close'").\
                LimitResultPerTable(duration_in_days).\
                Fields(['value, start_date']).\
                AnalyticFunc(analytic_func=CalPriceMovement)
        analytics.RunAnalytic()
        results = analytics.GetAnalyticResults()
        return results


if __name__ == '__main__':
    results = UsEquityMetricsAnalytics.CalculatePriceMovement(
            db_type='mysql',
            username=Config.mysql_username,
            password=Config.mysql_password,
            server=Config.mysql_server,
            database=Config.mysql_database,
            duration_in_days=10,
            max_num_threads=20)
    with open('result2.txt', 'w') as f:
        for table_name in results:
            results[table_name] = [str(value) for value in results[table_name]]
            line = table_name + ': ' + ','.join(results[table_name]) + '\n'
            f.write(line)

