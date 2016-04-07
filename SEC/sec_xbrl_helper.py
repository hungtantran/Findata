__author__ = 'hungtantran'


from os import listdir
from os.path import isfile, join


class SecXbrlHelper(object):
    # TODO write unit test for this method
    @staticmethod
    def get_all_xbrl_zip_files_from_directory(directory):
        return [join(directory, f) for f in listdir(directory) if (isfile(join(directory, f)) and f.endswith('xbrl.zip'))]
