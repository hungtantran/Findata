__author__ = 'hungtantran'


from mysql_dao_factory import MysqlDAOFactory
from bigquery_dao_factory import BigQueryDAOFactory


class DAOFactoryRepository(object):
    dao_factory_dic = {'mysql': MysqlDAOFactory(),
                       'bigquery': BigQueryDAOFactory()}

    @staticmethod
    def getInstance(type):
        return DAOFactoryRepository.dao_factory_dic[type]

    @staticmethod
    def registerfactory(type, dao_factory):
        DAOFactoryRepository.dao_factory_dic[type] = dao_factory