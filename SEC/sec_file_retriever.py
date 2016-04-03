__author__ = 'hungtantran'


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

