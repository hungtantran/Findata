__author__ = 'hungtantran'

from mysqldaofactory import MysqlDAOFactory


class DAOFactoryRepository(object):
    dao_factory_dic = {'mysql': MysqlDAOFactory()}

    @staticmethod
    def getInstance(type):
        return DAOFactoryRepository.dao_factory_dic[type]

    @staticmethod
    def registerfactory(type, dao_factory):
        DAOFactoryRepository.dao_factory_dic[type] = dao_factory