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
    @staticmethod
    def log(level, msg):
        print_msg = ''
        if type(msg) is Exception:
            print_msg = msg.__str__
        elif type(msg) is str:
            print_msg = msg

        traces = traceback.extract_stack()
        print("%s, %s, %s, '%s'\n" % (datetime.datetime.now(), LogLevel.to_string(level), print_msg, traces[-2]))