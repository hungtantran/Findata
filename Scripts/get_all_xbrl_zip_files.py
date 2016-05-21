__author__ = 'hungtantran'


import re
from os import listdir, rename
from os.path import isfile, join
import datetime
from ftplib import FTP
import zipfile

import logger
import Queue
import threading
from constants_config import Config
from sec_xbrl_index_file_parser import SecXbrlIndexFileParser
from sec_file_retriever import SecFileRetriever


class Retrieve(object):
    XBRL_FILE_PATTERN = '^([a-zA-Z]+)-[0-9]+\.xml'
    XBRL_RAW_ZIP_PATTERN = '^[0-9]+-[0-9]+-qtr[0-9]-(10-Q|10-K)-[0-9]+-[0-9]+-[0-9]+-xbrl.zip'

    def __init__(self):
        self.q = Queue.Queue()

    def retrieve_file(self):
        file_retriever = SecFileRetriever(link=Config.sec_ftp_link,
                                          full_index_path=Config.sec_ftp_full_index_path,
                                          xbrl_index_file=Config.sec_xbrl_index_file)

        count = 0
        while not self.q.empty():
            try:
                cik, accession, target_file_path = self.q.get()
                count += 1
                print '(%s) Download file (%d): %s' % (threading.current_thread().name, count, target_file_path)
                file_retriever.get_xbrl_zip_file(cik=cik,
                                                 accession=accession,
                                                 target_file_path=target_file_path)
            finally:
                self.q.task_done()

    def retrieve_xbrl_zip_files(self, exclude_cik_list, cik_list, xbrl_index_dir, intermediate_file_dir='.'):
        xbrl_index_parser = SecXbrlIndexFileParser()

        xbrl_index_files = [join(xbrl_index_dir, f) for f in listdir(xbrl_index_dir) if (isfile(join(xbrl_index_dir, f)) and f.endswith('.idx'))]
        xbrl_zip_files = [f for f in listdir(intermediate_file_dir) if (isfile(join(intermediate_file_dir, f)) and f.endswith('.zip'))]

        count = 0
        for xbrl_index_file in xbrl_index_files:
            # xbrl_index_file should be like path/to/index/file/2011_qtr4_xbrl.idx so
            # file_parts should be like ['2011', 'qtr4', 'xbrl.idx]
            index = xbrl_index_file.rfind('/')
            if index > 0:
                xbrl_index_file_name = xbrl_index_file[(index + 1):]
            file_parts = xbrl_index_file_name.split('_')
            if len(file_parts) != 3 or (not xbrl_index_file_name.endswith('_xbrl.idx')):
                logger.Logger.log(logger.LogLevel.WARN, 'xbrl index file has to be in format {YYYY}_qtr{Q}_xbrl.idx')
                return

            xbrl_indices = xbrl_index_parser.parse(xbrl_index_file)

            # Expect there are 5 arrays of CIK, Company Name, Form Type, Date Filed and Accession
            if len(xbrl_indices) != 5:
                return

            # Get the xbrl zip file corresponding to the company
            for i in range(len(xbrl_indices[0])):
                # Only parse 10-Q and 10-K for now
                # TODO parse more form types
                if ((exclude_cik_list is None or xbrl_indices[0][i] not in exclude_cik_list) and
                    (cik_list is None or xbrl_indices[0][i] in cik_list) and
                    (xbrl_indices[2][i] == '10-Q' or xbrl_indices[2][i] == '10-K')):
                    target_file_name = '%d-%s-%s-%s-%s-xbrl.zip' % (xbrl_indices[0][i], file_parts[0],
                                                                    file_parts[1], xbrl_indices[2][i], xbrl_indices[4][i])
                    target_file_path = '%s/%s' % (intermediate_file_dir, target_file_name)

                    # The file already exists, skip it
                    if target_file_name in xbrl_zip_files:
                        continue

                    count += 1
                    self.q.put((xbrl_indices[0][i], xbrl_indices[4][i], target_file_path))

        # Start threads to download
        threads = []
        for i in range(4):
            t = threading.Thread(target=self.retrieve_file)
            threads.append(t)
            t.start()

        for i in range(len(threads)):
            wait_thread = threads[i]
            logger.Logger.log(logger.LogLevel.INFO, 'Wait for thread %s' % wait_thread.name)
            wait_thread.join()
            logger.Logger.log(logger.LogLevel.INFO, 'Thread %s done' % wait_thread.name)

    def rename_zip_file(self, xbrl_zip_dir):
        xbrl_zip_files = [join(xbrl_zip_dir, f) for f in listdir(xbrl_zip_dir) if (isfile(join(xbrl_zip_dir, f)) and f.endswith('.zip'))]

        for zip_file_path in xbrl_zip_files:
            index = zip_file_path.rfind('\\')
            directory = zip_file_path[:index]
            file_name = zip_file_path[index + 1:]
            if not re.search(Retrieve.XBRL_RAW_ZIP_PATTERN, file_name):
                print file_name
                continue

            if not zipfile.is_zipfile(zip_file_path):
                logger.Logger.log(logger.LogLevel.WARN, 'Give file %s is not zip file' % zip_file)
                continue

            ticker = None
            with zipfile.ZipFile(zip_file_path) as zip_file:
                files = zip_file.namelist()

                for file in files:
                    match = re.search(Retrieve.XBRL_FILE_PATTERN, file)
                    if not match:
                        continue
                    ticker = match.group(1)
                    break

            if ticker is None:
                logger.Logger.log(logger.LogLevel.WARN, 'Cannot find any xbrl file in zip %s. Found these files %s' % (
                        zip_file_path, files))
                continue

            new_zip_file_path = directory + '/' + ticker + '-' + file_name
            logger.Logger.log(logger.LogLevel.INFO, 'Rename %s to %s' % (zip_file_path, new_zip_file_path))
            rename(zip_file_path, new_zip_file_path)


#cik_list=[1800, 2969, 4127, 4281, 4447, 4904, 4962, 4977, 5272, 5513, 6201, 6281, 6769, 6951, 7084, 7332, 8670, 8818, 9389, 9892, 10456, 10795, 12659, 12927, 14272, 14693, 16732, 16918, 18230, 18926, 19617, 20286, 20520, 21076, 21344, 21665, 23217, 24545, 24741, 26172, 27419, 27904, 28412, 29534, 29905, 29915, 29989, 30554, 30625, 31462, 31791, 32604, 33185, 33213, 34088, 34903, 35527, 36104, 36270, 37785, 37996, 38777, 39899, 39911, 40533, 40545, 40704, 40987, 42582, 45012, 46080, 46765, 47111, 47217, 48465, 49071, 49196, 49826, 50104, 50863, 51253, 51434, 51644, 52988, 53669, 54480, 55067, 55785, 56873, 58492, 59478, 59558, 60086, 60667, 62709, 62996, 63276, 63754, 63908, 64040, 64670, 64803, 65984, 66740, 68505, 69499, 70318, 70858, 72207, 72333, 72741, 72903, 72971, 73124, 73309, 74208, 75362, 76334, 77360, 77476, 78003, 78239, 78814, 79879, 80424, 80661, 85961, 86312, 87347, 89800, 91419, 91440, 91576, 92122, 92230, 92380, 93410, 93556, 93751, 96021, 96223, 97476, 97745, 98246, 100493, 100517, 100885, 101778, 101829, 103379, 104169, 106040, 106535, 106640, 107263, 108772, 109198, 109380, 200406, 202058, 203077, 203527, 217346, 277135, 277948, 310158, 310764, 313616, 313927, 315189, 315213, 315293, 315852, 316206, 316709, 318154, 319201, 320187, 320335, 350563, 350698, 352915, 354908, 354950, 356028, 701221, 701985, 702165, 704051, 707549, 712515, 713676, 715957, 717423, 718877, 721371, 721683, 723125, 723254, 723531, 726728, 728535, 731766, 732712, 732717, 740260, 743988, 745732, 746515, 750556, 753308, 754737, 759944, 764180, 764478, 764622, 765880, 766704, 769397, 773840, 773910, 783325, 788784, 790070, 791519, 791907, 793952, 794323, 794367, 796343, 797468, 798354, 800459, 804212, 804328, 804753, 808362, 811156, 812074, 813828, 814453, 815097, 815556, 816284, 816761, 818479, 820027, 820313, 821189, 822416, 823768, 827052, 827054, 829224, 831001, 831259, 832988, 833444, 849399, 851968, 858470, 858877, 859737, 860730, 861878, 865436, 865752, 866787, 872589, 874761, 874766, 875045, 875159, 875320, 877890, 879101, 882095, 882184, 882835, 884629, 884887, 884905, 885639, 885725, 886158, 886982, 891024, 895126, 895421, 895648, 896159, 896878, 898173, 899051, 899689, 899866, 906107, 908255, 909832, 912242, 912615, 912750, 914208, 915389, 915912, 916076, 916365, 920148, 920522, 920760, 922224, 922864, 927066, 927628, 927653, 935703, 936340, 936468, 940944, 941548, 949039, 1000180, 1000228, 1000697, 1001039, 1001250, 1002047, 1002910, 1004155, 1004434, 1004980, 1011006, 1012100, 1013871, 1014473, 1015780, 1020569, 1021860, 1022079, 1024478, 1031296, 1032208, 1035002, 1035267, 1037038, 1037540, 1037868, 1038357, 1039684, 1040971, 1041061, 1043277, 1043604, 1045609, 1045810, 1047122, 1047862, 1048286, 1048695, 1048911, 1050915, 1051470, 1053112, 1053507, 1056239, 1058090, 1058290, 1059556, 1060391, 1063761, 1065088, 1065280, 1067701, 1067983, 1070750, 1071739, 1075531, 1086222, 1087423, 1090012, 1090727, 1090872, 1099219, 1099800, 1100962, 1101215, 1101239, 1103982, 1105705, 1109357, 1110783, 1110803, 1111711, 1113169, 1115222, 1116132, 1120193, 1121788, 1122304, 1124198, 1126328, 1130310, 1133421, 1135152, 1136869, 1136893, 1137411, 1137774, 1137789, 1138118, 1140536, 1140859, 1141391, 1156039, 1156375, 1158449, 1163165, 1164727, 1166691, 1168054, 1170010, 1174922, 1267238, 1274494, 1275283, 1281761, 1285785, 1289490, 1308161, 1308161, 1324404, 1324424, 1326160, 1326380, 1336917, 1339947, 1341439, 1358071, 1359841, 1361658, 1364742, 1365135, 1373835, 1377013, 1378946, 1385157, 1390777, 1393311, 1393612, 1396009, 1403161, 1410636, 1413329, 1418135, 1430602, 1437107, 1437107, 1441634, 1442145, 1451505, 1452575, 1466258, 1467373, 1467858, 1489393, 1491675, 1492633, 1506307, 1510295, 1521332, 1524472, 1526520, 1530721, 1532063, 1534701, 1545158, 1546640, 1551152, 1551182, 1555280, 1564708, 1564708, 1567892, 1571949, 1579241, 1585364, 1593538, 1601712, 1604778, 1618921, 1620546, 1629995, 1633917, 1636023, 1645590, 1646383]
#intermediate_file_dir='./SEC/xbrl_zip_files'
#xbrl_index_dir='./SEC/xbrl_index_files/'
#retrieve_xbrl_zip_files_from_cik_list_and_xbrl_index_file(cik_list, xbrl_index_dir, intermediate_file_dir)

exclude_cik_list=[1800, 2969, 4127, 4281, 4447, 4904, 4962, 4977, 5272, 5513, 6201, 6281, 6769, 6951, 7084, 7332, 8670, 8818, 9389, 9892, 10456, 10795, 12659, 12927, 14272, 14693, 16732, 16918, 18230, 18926, 19617, 20286, 20520, 21076, 21344, 21665, 23217, 24545, 24741, 26172, 27419, 27904, 28412, 29534, 29905, 29915, 29989, 30554, 30625, 31462, 31791, 32604, 33185, 33213, 34088, 34903, 35527, 36104, 36270, 37785, 37996, 38777, 39899, 39911, 40533, 40545, 40704, 40987, 42582, 45012, 46080, 46765, 47111, 47217, 48465, 49071, 49196, 49826, 50104, 50863, 51143, 51253, 51434, 51644, 52988, 53669, 54480, 55067, 55785, 56873, 58492, 59478, 59558, 60086, 60667, 62709, 62996, 63276, 63754, 63908, 64040, 64670, 64803, 65984, 66740, 68505, 69499, 70858, 72207, 72333, 72741, 72903, 72971, 73124, 73309, 74208, 75362, 76334, 77360, 77476, 78003, 78239, 78814, 79879, 80424, 80661, 85961, 86312, 87347, 89800, 91419, 91440, 91576, 92122, 92230, 92380, 93410, 93556, 93751, 96021, 96223, 97476, 97745, 98246, 100493, 100517, 100885, 101778, 101829, 103379, 104169, 106040, 106535, 106640, 107263, 108772, 109198, 109380, 200406, 202058, 203077, 203527, 217346, 277135, 277948, 310158, 310764, 313616, 313927, 315189, 315213, 315293, 315852, 316206, 316709, 318154, 319201, 320187, 320193, 320335, 350563, 350698, 352915, 354908, 354950, 356028, 701221, 701985, 702165, 704051, 707549, 712515, 713676, 715957, 717423, 718877, 721371, 721683, 723125, 723254, 723531, 726728, 728535, 731766, 732712, 732717, 740260, 743988, 745732, 746515, 750556, 753308, 754737, 759944, 764180, 764478, 764622, 765880, 766704, 769397, 773840, 773910, 783325, 788784, 789019, 790070, 791519, 791907, 793952, 794323, 794367, 796343, 797468, 798354, 800459, 804212, 804328, 804753, 808362, 811156, 812074, 813828, 814453, 815097, 815556, 816284, 816761, 818479, 820027, 820313, 821189, 822416, 823768, 827052, 827054, 829224, 831001, 831259, 832988, 833444, 849399, 850209, 851968, 858470, 858877, 859737, 860730, 861878, 865436, 865752, 866787, 872589, 874761, 874766, 875045, 875159, 875320, 877890, 879101, 882095, 882184, 882835, 884629, 884887, 884905, 885639, 885725, 886158, 886982, 891024, 895126, 895421, 895648, 896159, 896878, 898173, 899051, 899689, 899866, 906107, 908255, 909832, 912242, 912615, 912750, 914208, 915389, 915912, 916076, 916365, 920148, 920522, 920760, 922224, 922864, 927066, 927628, 927653, 935703, 936340, 936468, 940944, 949039, 1000180, 1000228, 1000697, 1001039, 1001250, 1002047, 1002910, 1004155, 1004434, 1004980, 1011006, 1012100, 1013871, 1014473, 1015780, 1018724, 1020569, 1021860, 1022079, 1024478, 1031296, 1032208, 1035002, 1035267, 1037038, 1037540, 1037868, 1038357, 1039684, 1040971, 1041061, 1043277, 1043604, 1045609, 1045810, 1047122, 1047862, 1048286, 1048695, 1048911, 1050915, 1051470, 1053112, 1053507, 1056239, 1058090, 1058290, 1059556, 1060391, 1063761, 1065088, 1065280, 1067701, 1067983, 1070750, 1071739, 1075531, 1086222, 1087423, 1090012, 1090727, 1090872, 1099219, 1099800, 1100962, 1101215, 1101239, 1103982, 1105705, 1108524, 1109357, 1110783, 1110803, 1111711, 1113169, 1115222, 1116132, 1120193, 1121788, 1122304, 1123360, 1124198, 1126328, 1130310, 1133421, 1135152, 1136869, 1136893, 1137411, 1137774, 1137789, 1138118, 1140536, 1140859, 1141391, 1156039, 1156375, 1158449, 1163165, 1164727, 1166691, 1168054, 1170010, 1174922, 1267238, 1274494, 1275283, 1281761, 1285785, 1288776, 1288776, 1289490, 1308161, 1308161, 1324404, 1324424, 1326160, 1326801, 1336917, 1339947, 1341439, 1358071, 1359841, 1361658, 1364742, 1365135, 1373835, 1377013, 1378946, 1385157, 1390777, 1393311, 1393612, 1396009, 1403161, 1403568, 1410636, 1413329, 1418135, 1430602, 1437107, 1437107, 1441634, 1442145, 1451505, 1452575, 1466258, 1467373, 1467858, 1489393, 1491675, 1492633, 1506307, 1510295, 1521332, 1524472, 1526520, 1530721, 1532063, 1534701, 1545158, 1546640, 1551152, 1551182, 1555280, 1564708, 1564708, 1567892, 1571949, 1579241, 1585364, 1593538, 1601712, 1604778, 1618921, 1620546, 1629995, 1633917, 1636023, 1645590, 1646383]
intermediate_file_dir='./SEC/xbrl_zip_files'
xbrl_index_dir='./SEC/xbrl_index_files/'
retrieve_obj = Retrieve()
#retrieve_obj.retrieve_xbrl_zip_files(exclude_cik_list, None, xbrl_index_dir, intermediate_file_dir)
retrieve_obj.rename_zip_file(xbrl_zip_dir=intermediate_file_dir)