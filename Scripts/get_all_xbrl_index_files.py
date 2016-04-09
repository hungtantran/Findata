__author__ = 'hungtantran'

import datetime
from ftplib import FTP

import logger
from constants_config import Config


def get_past_xbrl_index(target_dir='.'):
    ftp = None

    try:
        ftp = FTP(Config.sec_ftp_link)
        ftp.login()

        for year in range(2015, 2017):
            for quarter in range(1, 5):
                logger.Logger.log(logger.LogLevel.INFO, 'Downloading xbrl index of year %d, quarter %d to directory %s' % (
                    year, quarter, target_dir))
                target_file_path = "%s/%d_qtr%d_%s" % (target_dir, year, quarter, Config.sec_xbrl_index_file)
                with open(target_file_path, 'wb') as file:
                    ftp_target_directory = '%s/%d/QTR%d' % (Config.sec_ftp_full_index_path, year, quarter)
                    ftp.cwd(ftp_target_directory)
                    ftp.retrbinary("RETR " + Config.sec_xbrl_index_file, file.write)
    except Exception as e:
        logger.Logger.log(logger.LogLevel.ERROR, e)
    finally:
        if ftp is not None:
            ftp.quit()

#get_past_xbrl_index('SEC/test_output_files')

