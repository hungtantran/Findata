__author__ = 'hungtantran'

import bigquery_client
from dao_factory import DAOFactory


class BigQueryDAOFactory(DAOFactory):
    @staticmethod
    def create(username, password, server, database):
        return bigquery_client.BigQueryClient(project_id=server, dataset_id=database)