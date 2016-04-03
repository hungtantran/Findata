__author__ = 'hungtantran'

import datetime
from ftplib import FTP

import logger
from constants_config import Config


class SecFileRetriever(object):
    def __init__(self, link, full_index_path, xbrl_index_file=None):
        self.link = link
        self.full_index_path = full_index_path

        if xbrl_index_file is None:
            self.xbrl_index_file = Config.sec_xbrl_index_file
        else:
            self.xbrl_index_file = xbrl_index_file

    def get_latest_xbrl_index(self, target_dir='.'):
        ftp = None

        try:
            target_file_path = "%s/latest_%s" % (target_dir, self.xbrl_index_file)
            with open(target_file_path, 'wb') as file:
                ftp = FTP(self.link)
                ftp.login()
                ftp.cwd(self.full_index_path)
                ftp.retrbinary("RETR " + self.xbrl_index_file, file.write)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)
        finally:
            if ftp is not None:
                ftp.quit()

    def get_past_xbrl_index(self, year, quarter, target_dir='.'):
        if quarter < 1 or quarter > 4:
            return

        now = datetime.datetime.now()
        if year < 1990 or year > now.year:
            return

        ftp = None

        try:
            target_file_path = "%s/%d_qtr%d_%s" % (target_dir, year, quarter, self.xbrl_index_file)
            with open(target_file_path, 'wb') as file:
                ftp = FTP(self.link)
                ftp.login()

                ftp_target_directory = '%s/%d/QTR%d' % (self.full_index_path, year, quarter)
                ftp.cwd(ftp_target_directory)
                ftp.retrbinary("RETR " + self.xbrl_index_file, file.write)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)
        finally:
            if ftp is not None:
                ftp.quit()

    def get_xbrl_zip_file(self, cik, accession, target_file_path):
        ftp_file_path = '%s/%d/%s/%s' % (Config.sec_xbrl_data_directory,
                                         cik,
                                         accession.replace('-', ''),
                                         accession + '-xbrl.zip')
        return self.get_file(ftp_file_path=ftp_file_path,
                             target_file_path=target_file_path)

    def get_file(self, ftp_file_path, target_file_path):
        ftp = None

        try:
            with open(target_file_path, 'wb') as file:
                ftp = FTP(self.link)
                ftp.login()

                ftp_directory = ftp_file_path[:ftp_file_path.rfind('/')]
                ftp_file_name = ftp_file_path[(ftp_file_path.rfind('/') + 1):]

                ftp.cwd(ftp_directory)
                ftp.retrbinary("RETR " + ftp_file_name, file.write)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)
        finally:
            if ftp is not None:
                ftp.quit()

