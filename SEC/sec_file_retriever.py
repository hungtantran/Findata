__author__ = 'hungtantran'

import datetime
import time
from ftplib import FTP

import logger
from constants_config import Config
from util import Util


class SecFileRetriever(object):
    MAX_TIME_FOR_REFRESH_IN_SECS = 60 * 30

    def __init__(self, link, full_index_path, xbrl_index_file=None):
        self.link = link
        self.full_index_path = full_index_path

        if xbrl_index_file is None:
            self.xbrl_index_file = Config.sec_xbrl_index_file
        else:
            self.xbrl_index_file = xbrl_index_file

        self.ftp = None
        self.last_refresh_time_in_sec = Util.get_current_time_in_second()

    def get_connection(self):
        current_time_in_secs = Util.get_current_time_in_second()
        if current_time_in_secs - self.last_refresh_time_in_sec > SecFileRetriever.MAX_TIME_FOR_REFRESH_IN_SECS:
            if self.ftp is not None:
                self.ftp.quit()
                self.ftp = None

        if self.ftp is None:
            self.ftp = FTP(self.link)
            self.ftp.login()
            self.last_refresh_time_in_sec = Util.get_current_time_in_second()

        return self.ftp

    def get_latest_xbrl_index(self, target_dir='.'):
        logger.Logger.log(logger.LogLevel.INFO, 'Downloading the latest xbrl index to directory %s' % target_dir)

        try:
            target_file_path = "%s/latest_%s" % (target_dir, self.xbrl_index_file)
            with open(target_file_path, 'wb') as file:
                ftp = self.get_connection()
                ftp.cwd(self.full_index_path)
                ftp.retrbinary("RETR " + self.xbrl_index_file, file.write)
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)
        finally:
            pass

    def get_past_xbrl_index(self, year, quarter, target_dir='.'):
        if quarter < 1 or quarter > 4:
            return

        now = datetime.datetime.now()
        if year < 1990 or year > now.year:
            return

        logger.Logger.log(logger.LogLevel.INFO, 'Downloading xbrl index of year %d, quarter %d to directory %s' % (
            year, quarter, target_dir))

        try:
            target_file_path = "%s/%d_qtr%d_%s" % (target_dir, year, quarter, self.xbrl_index_file)
            with open(target_file_path, 'wb') as file:
                ftp_target_directory = '%s/%d/QTR%d' % (self.full_index_path, year, quarter)
                ftp = self.get_connection()
                ftp.cwd(ftp_target_directory)
                ftp.retrbinary("RETR " + self.xbrl_index_file, file.write)
                return target_file_path
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)
        finally:
            pass

    def get_xbrl_zip_file(self, cik, accession, target_file_path=None):
        ftp_file_path = '%s/%d/%s/%s' % (Config.sec_xbrl_data_directory,
                                         cik,
                                         accession.replace('-', ''),
                                         accession + '-xbrl.zip')

        if target_file_path is None:
            target_file_path = './%d-%s-xbrl.zip' % (cik, accession)

        logger.Logger.log(logger.LogLevel.INFO, 'Downloading xbrl zip file for cik %d, accession %s to %s' % (
                cik, accession, target_file_path))
        return self.get_file(ftp_file_path=ftp_file_path,
                             target_file_path=target_file_path)

    def get_file(self, ftp_file_path, target_file_path):
        logger.Logger.log(logger.LogLevel.INFO, 'Downloading file %s to %s' % (ftp_file_path, target_file_path))

        try:
            with open(target_file_path, 'wb') as file:
                ftp_directory = ftp_file_path[:ftp_file_path.rfind('/')]
                ftp_file_name = ftp_file_path[(ftp_file_path.rfind('/') + 1):]
                ftp = self.get_connection()
                ftp.cwd(ftp_directory)
                ftp.retrbinary("RETR " + ftp_file_name, file.write)
                return target_file_path
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)
        finally:
            pass

