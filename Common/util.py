__author__ = 'hungtantran'


import time


class Util(object):
    @staticmethod
    def get_current_time_in_second():
        return time.time() * 1000 * 1000

    @staticmethod
    def get_current_time_in_millisec():
        return time.time() * 1000

    @staticmethod
    def get_current_time_in_nanosec():
        return time.time()
