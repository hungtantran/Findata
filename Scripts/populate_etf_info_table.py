__author__ = 'hungtantran'


import logger
from constants_config import Config
from dao_factory_repo import DAOFactoryRepository
from etf_info_database import ETFInfoDatabase


def populate_etf_info_table(company_info_file):
    etf_db = ETFInfoDatabase(
            'mysql',
            Config.mysql_username,
            Config.mysql_password,
            Config.mysql_server,
            Config.mysql_database)
    etf_db.create_etf_info_table()

    dao_factory = DAOFactoryRepository.getInstance('mysql')
    with dao_factory.create(Config.mysql_username,
                            Config.mysql_password,
                            Config.mysql_server,
                            Config.mysql_database) as connection:
        try:
            # TODO need to make this general
            cursor = connection.cursor()

            with open(company_info_file) as f:
                lines = f.read().split('\n')
                for i in range(1, len(lines)):
                    line = lines[i]
                    cells = line.split('",')
                    cells = [cell.replace('"', '') for cell in cells]

                    ticker = cells[0]
                    name = cells[1]

                    print '%s, %s' % (ticker, name)
                    cursor.execute("INSERT INTO etf_info (ticker, name, asset_class, sector, location, metadata) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE "
                                   "KEY UPDATE name=%s, asset_class=%s, sector=%s, location=%s, metadata=%s", (ticker, name, None, None, None, None, name, None, None, None, None))
                    connection.commit()

        except Exception as e:
            print e


if __name__ == '__main__':
    populate_etf_info_table('Data/etf_list.csv')