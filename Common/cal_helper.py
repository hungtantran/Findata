__author__ = 'hungtantran'

from math import sqrt

from constants_config import Config
from Database.timeline_model_database import TimelineModelDatabase


class CalHelper(object):
    @staticmethod
    def mean(data_list):
        """calculates mean"""
        sum = 0
        for i in range(len(data_list)):
            sum += data_list[i]
        return (sum / len(data_list))

    @staticmethod
    def standard_deviation(data_list):
        """calculates standard deviation"""
        sum = 0
        mean = CalHelper.mean(data_list)
        for i in range(len(data_list)):
            sum += pow((data_list[i] - mean), 2)
        return sqrt(sum/(len(data_list)-1))

    @staticmethod
    def covariance(model1_data, model2_data, avg_model1, avg_model2):
        num_data_point = len(model1_data)
        if num_data_point != len(model2_data):
            return None

        covariance = 0
        for i in range(num_data_point):
            covariance += (model1_data[i] - avg_model1) * (model2_data[i] - avg_model2)
        covariance = covariance / (num_data_point - 1)
        return covariance

    @staticmethod
    def correlation(model1_data, model2_data, avg_model1, avg_model2, std_model1, std_model2):
        coverance = CalHelper.covariance(model1_data, model2_data, avg_model1, avg_model2)
        correlation = coverance / (std_model1 * std_model2)
        return correlation

    @staticmethod
    def rsquare(model_data, predict_model_data, avg_model):
        if len(model_data) != len(predict_model_data):
            return None

        total_sum_of_square = 0
        for i in range(len(model_data)):
            total_sum_of_square += (model_data[i] - avg_model) * (model_data[i] - avg_model)

        sum_of_square_of_residuals = 0
        for i in range(len(model_data)):
            sum_of_square_of_residuals += (model_data[i] - predict_model_data[i]) * (model_data[i][1] - predict_model_data[i])

        rsquare = 1 - sum_of_square_of_residuals / total_sum_of_square
        return rsquare

    @staticmethod
    def covariance_and_correlation_two_models(model1, model2, lower_time_limit=None, upper_time_limit=None):
        model_db = TimelineModelDatabase('mysql',
                                         Config.mysql_username,
                                         Config.mysql_password,
                                         Config.mysql_server,
                                         Config.mysql_database)
        join_data = model_db.get_join_models_data(model1, model2)
        num_data_point = len(join_data)

        model1_data = [data[1] for data in join_data]
        model2_data = [data[2] for data in join_data]
        avg_model1 = CalHelper.mean(model1_data)
        avg_model2 = CalHelper.mean(model2_data)
        std_model1 = CalHelper.standard_deviation(model1_data)
        std_model2 = CalHelper.standard_deviation(model2_data)
        print "%f %f %f %f" % (avg_model1, avg_model2, std_model1, std_model2)

        covariance = 0
        for i in range(num_data_point):
            val = join_data[i]
            covariance += (val[1] - avg_model1) * (val[2] - avg_model2)
        covariance /= (num_data_point - 1)
        correlation = covariance / (std_model1 * std_model2)
        return (covariance, correlation, join_data[0][0], join_data[-1][0])

    @staticmethod
    def rsquare_model(model, predict_model, lower_time_limit=None, upper_time_limit=None):
        model_db = TimelineModelDatabase('mysql',
                                         Config.mysql_username,
                                         Config.mysql_password,
                                         Config.mysql_server,
                                         Config.mysql_database)
        join_data = model_db.get_join_models_data(model, predict_model)
        avg_model = model_db.get_average_model_data(model)

        total_sum_of_square = 0
        for i in range(len(join_data)):
            total_sum_of_square += (join_data[i][1] - avg_model) * (join_data[i][1] - avg_model)

        sum_of_square_of_residuals = 0
        for i in range(len(join_data)):
            sum_of_square_of_residuals += (join_data[i][1] - join_data[i][2]) * (join_data[i][1] - join_data[i][2])

        rsquare = 1 - sum_of_square_of_residuals / total_sum_of_square
        return rsquare

    @staticmethod
    def cal_stat_matrix(models_list, lower_time_limit=None, upper_time_limit=None):
        matrix = []
        for i in range(len(models_list)):
            matrix.append([0] * len(models_list))

        for i in range(len(models_list)):
            for j in range(i + 1, len(models_list)):
                print '%d %d' % (i, j)
                matrix[i][j] = CalHelper.covariance_and_correlation_two_models(models_list[i], models_list[j])

        return matrix


if __name__ == '__main__':
    model_db = TimelineModelDatabase('mysql',
                                         Config.mysql_username,
                                         Config.mysql_password,
                                         Config.mysql_server,
                                         Config.mysql_database)
    #model_list = model_db.get_all_models_names()
    #models_names_list = [model[0] for model in model_list]
    #models_name_close = []
    #for name in models_names_list:
    #    if name.endswith('close') and (not name.endswith('adj_close')):
    #        models_name_close.append(name)
    #print len(models_name_close)

    model_list = ['NASDAQ_FB_close', 'NASDAQ_AAPL_close']
    matrix = CalHelper.cal_stat_matrix(model_list)
    for i in range(len(matrix)):
        print matrix[i]