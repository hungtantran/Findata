__author__ = 'hungtantran'

import datetime

class LogLevel(object):
    TRACE = 1
    DEBUG = 2
    INFO = 3
    WARN = 4
    ERROR = 5

    dic = {
        TRACE : 'TRACE',
        DEBUG : 'DEBUG',
        INFO : 'INFO',
        WARN : 'WARN',
        ERROR : 'ERROR',
    }

    @staticmethod
    def to_string(level):
        return LogLevel.dic[level]

class Logger(object):
    @staticmethod
    def log(level, msg):
        print("%s,%s,'%s'\n" % (datetime.datetime.now(), LogLevel.to_string(level), msg))