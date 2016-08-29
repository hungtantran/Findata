__author__ = 'hungtantran'

import sys
import datetime
import traceback

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
    # TODO move this to Config
    # TODO log rotation
    ERROR_FILE = open('error.txt', 'a')
    WARN_FILE = open('warn.txt', 'a')

    @staticmethod
    def log(level, msg, wrapper_layer=2):
        print_msg = ''
        if isinstance(msg, Exception):
            print_msg = str(msg)
        elif isinstance(msg, basestring):
            print_msg = msg

        traces = traceback.extract_stack()
        log_msg = "%s, %s, %s, *********** '%s'\n" % (datetime.datetime.now(), LogLevel.to_string(level), print_msg, traces[-wrapper_layer])

        if level == LogLevel.ERROR:
            Logger.ERROR_FILE.write(log_msg)
        elif level == LogLevel.WARN:
            Logger.WARN_FILE.write(log_msg)

        print(log_msg)

    @staticmethod
    def trace(msg):
        return Logger.log(LogLevel.TRACE, msg, wrapper_layer=3)

    @staticmethod
    def debug(msg):
        return Logger.log(LogLevel.DEBUG, msg, wrapper_layer=3)

    @staticmethod
    def info(msg):
        return Logger.log(LogLevel.INFO, msg, wrapper_layer=3)

    @staticmethod
    def warn(msg):
        return Logger.log(LogLevel.WARN, msg, wrapper_layer=3)

    @staticmethod
    def error(msg):
        return Logger.log(LogLevel.ERROR, msg, wrapper_layer=3)
