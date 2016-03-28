__author__ = 'hungtantran'

from os import remove
from os import listdir
from os import rename
from os.path import isfile, join
import re

import sys

class SanitizeFile(object):
    def __init__(self):
        pass

    @staticmethod
    def rename_files_extention_in_dir(dir_path, new_extension, old_extension):
        file_names = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
        for file_name in file_names:
            if file_name.endswith(old_extension):
                new_file_name = file_name[:-len(old_extension)] + new_extension
                old_path = join(dir_path, file_name)
                new_path = join(dir_path, new_file_name)
                print 'Rename %s to %s' % (old_path, new_path)
                rename(old_path, new_path)

    @staticmethod
    def remove_files_match_regex(dir_path, regex):
        prog = re.compile(regex)

        file_names = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
        for file_name in file_names:
            if prog.match(file_name):
                full_path = join(dir_path, file_name)
                print 'Remove file %s' % full_path
                remove(full_path)

    @staticmethod
    def append_to_files_name(dir_path, append_string, front=True):
        file_names = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
        for file_name in file_names:
            if front:
                new_file_name = append_string + file_name
            else:
                new_file_name = file_name + append_string
            old_path = join(dir_path, file_name)
            new_path = join(dir_path, new_file_name)
            print 'Rename %s to %s' % (old_path, new_path)
            rename(old_path, new_path)

    @staticmethod
    def append_file_name_to_header(dir_path):
        file_names = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
        for file_name in file_names:
            file_name_append = file_name.replace('.csv', '')
            path = join(dir_path, file_name)

            try:
                f = open(path, 'r')
                content = f.read()
                content_lines = content.split('\n')
                header_titles = content_lines[0].split(',')
                if header_titles[0] != 'Date':
                    continue

                for i in range(1, len(header_titles)):
                    header_titles[i] = file_name_append + '_' + header_titles[i].lower().replace(' ', '_')
                header_string = ','.join(header_titles)
                content_lines[0] = header_string
                new_content = '\n'.join(content_lines)

                print 'Write new content for file %s' % path
                print header_string

                w = open(path, 'w')
                w.write(new_content)
            except Exception as e:
                print e
            finally:
                w.flush()
                w.close()



if __name__ == '__main__':
    # SanitizeFile.rename_files_extention_in_dir('E:\OneDrive\Issues\Finance\Stock Prices\\nyse', '.csv', '.txt')
    # SanitizeFile.remove_files_match_regex('E:\OneDrive\Issues\Finance\Stock Prices\\nasdaq', '^[A-Z]+\.[1-9]\.csv$')
    # SanitizeFile.append_to_files_name('E:\OneDrive\Issues\Finance\Stock Prices\\nyse', 'NYSE_')
    # SanitizeFile.append_file_name_to_header('E:\Stock Prices\\nyse')
    pass