from library import *
import time
from decimal import Decimal
import statistics as s
from scipy import stats


if __name__ == "__main__":

    # CONSTANTS
    # CORR_THRESHOLD = 0.95
    NBWEEKS = 2
    LEN_TRICKLET = 10
    # LEN_TRICKLET = NBWEEKS * 7
    NB_ATOMS = 6
    ERROR_THRES = 1
    TIMESTAMP = time.time()

    CORR_THRESHOLD = 1 - ERROR_THRES / 2

    # datasetPath = '../Datasets/archive_ics/gas-sensor-array-temperature-modulation/20160930_203718.csv'
    datasetPath = '../Datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv'
    # datasetPath = '../Datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv'
    # datasetPath = '../Datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv'
    # datasetPath = '../Datasets/UCRArchive_2018/ACSF1/ACSF1_TEST.tsv'

    datasetPathDictionary = '../Datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TRAIN.tsv'
    # datasetPathDictionary = '../Datasets/UCRArchive_2018/ACSF1/ACSF1_TRAIN.tsv'

    # READING THE DATASETS

    df_data = pd.read_csv(datasetPath, sep='\t')
    # df_data = pd.read_csv(datasetPath)

    df_data_learning = pd.read_csv(datasetPathDictionary, sep='\t')
    # df_data_learning = df_data_learning.iloc[:, 0:3]

    # z-score normalizing the data

    df_data = pd.DataFrame(stats.zscore(df_data))
    df_data_learning = pd.DataFrame(stats.zscore(df_data_learning))

    # CREATING TRICKLETS

    time_series_data = dataframeToTricklets(df_data, LEN_TRICKLET)
    time_series_data_dictionary = dataframeToTricklets(df_data_learning, LEN_TRICKLET)

    # CORRELATION COMPUTATION FOR EACH SEGMENT

    print("Computing correlation ... ", end='')
    correlation_matrix = []
    for i in range(int(df_data.shape[0] / LEN_TRICKLET)):
        correlation_matrix.append(df_data[i * LEN_TRICKLET: (i + 1) * LEN_TRICKLET].corr())
    print("done!")


    # DICTIONARY

    print("Building the dictionary ... ", end='')
    # for i in range(1, len(time_series_data_dictionary)):
    #     time_series_data_dictionary[0].extend(time_series_data_dictionary[i])
    Dictionary = learnDictionary(time_series_data_dictionary[0], 100, 1, 150, datasetPath + '.pkl')
    # data = read_time_series('../Datasets/../Datasets/UCRArchive_2018/Yoga/Yoga_TRAIN.tsv')
    # tricklets = getTrickletsTS(data, 2, NBWEEKS)
    # print(len(tricklets[0]))
    # Dictionary = learnDictionary(time_series_learning, 20, 1, 100)

    # print("Loading the dictionary ... ", end='')
    # Dictionary = load_object('dict_100.pkl')

    print("done!")

    # COMPRESSING THE DATA THE TRISTAN WAY
    start1 = time.time()
    old_atoms_coded_tricklets, errors_old = compress_without_correlation(time_series_data, Dictionary, NB_ATOMS, 'omp')
    end1 = time.time()

    # COMPRESSING THE DATA OUR WAY
    start2 = time.time()
    atoms_coded_tricklets, corr_coded_tricklets, errors_new = compress_with_correlation(time_series_data,
                                                                                        correlation_matrix, Dictionary,
                                                                                        CORR_THRESHOLD, NB_ATOMS, 'omp')
    end2 = time.time()

    # PRINTING COMPUTATION TIME
    print('Computation time without correlation: ', round(Decimal(end1 - start1), 2), 's')
    print('Computation time with correlation: ', round(Decimal(end2 - start2), 2), 's')

    # print(corr_coded_tricklets)

    # PRINTING ERRORS
    print('New error:', "{0:.5}".format(s.mean(errors_new)))
    print('Old error:', "{0:.5}".format(s.mean(errors_old)))

    # SAVE THE DATA FILES
    save_object(time_series_data, 'outputs/compressed/originalData%s.out' % str(int(TIMESTAMP)))
    save_object(old_atoms_coded_tricklets, 'outputs/compressed/old_out_pickle%s.out' % str(int(TIMESTAMP)))
    save_object((atoms_coded_tricklets, corr_coded_tricklets), 'outputs/compressed/new_out_pickle%s.out' % str(int(TIMESTAMP)))

    # # NORMALIZING DATA
    #
    # df_data= normalize_df(normalize_df)
    # df_data_learning= normalize_df(df_data_learning)

    # print(df_data.head())

    # original_size = get_size(old_atoms_coded_tricklets)
    # new_size = get_size(atoms_coded_tricklets) + get_size(corr_coded_tricklets)

    # print(original_size, new_size)
    # print('size optimisation is: %f' % (new_size / original_size))

    # import sys
    # print()
    # print(type(old_atoms_coded_tricklets), type(old_atoms_coded_tricklets[0]))
    # print(type(atoms_coded_tricklets), type(corr_coded_tricklets))
    # print(sys.getsizeof(old_atoms_coded_tricklets), 'size of old_atoms_coded_tricklets')
    # print(sys.getsizeof(atoms_coded_tricklets) + sys.getsizeof(corr_coded_tricklets), 'size of atoms_coded_tricklets')

    # print('atoms_coded_tricklets + corr_coded_tricklets', total_size(atoms_coded_tricklets) + total_size(old_atoms_coded_tricklets))
    # print('old_atoms_coded_tricklets', total_size(old_atoms_coded_tricklets))
    # print('')

    # f = open("old_atoms_coded_tricklets.txt", "a")
    # for item in old_atoms_coded_tricklets:
    #     print(item)
    # f.close()

    # print (len(time_series_data[0]))
    # df_data = df.iloc[:,0:53]
    # print(df_learning)
    # time_series_learning = [item for sublist in dataframeToTricklets(df_learning) for item in sublist]
    # print('len', len(time_series_learning))
    # print(time_series_learning)

    # df_data = pd.read_csv(datasetPath)

    # datasetPath = '../Datasets/archive_ics/gas-sensor-array-temperature-modulation/20160930_203718.csv'
    # datasetPath = '../Datasets/Sales_Transactions_Dataset_Weekly.csv'
    # df_data = read_multiple_ts(datasetPath, 1, 53)

    # df = pd.DataFrame(np.random.randint(0, 10, size=(100000, 1)), columns=list('A'))
    # from random import randrange
    #
    # for i in range(1):
    #     df[chr(ord('A') + i)] = df['A'] + randrange(-100, 100)
    #
    # # df.plot()
    # # plt.show()
    # # print(df)
    #
    # df_data = df

    # df_data = pd.read_csv('../Datasets/UCRArchive_2018/Yoga/Yoga_TRAIN.tsv', sep='\t')
    # df.plot()
    # plt.show()

    # save_object(df_data, '../Datasets/df_Yoga_TRAIN.tsv')

    # np.savetxt('../Datasets/df_20ts_exactcorrelation.txt', df_data.values, fmt='%d')

    # print (df_data)

    # plt.plot(errors_new)
    # plt.plot(errors_old)
    # plt.ylabel('errors')
    # plt.xlabel('time series')
    # plt.show()
    #
    # plt.plot(data)
    # plt.show(block=True)

# if __name__ == "__main__":
#     # Reading time series
#     # data = read_time_series('../Datasets/Sales_Transactions_Dataset_Weekly.csv')
#     # data = read_time_series('../Datasets/drift6_normal.txt')
#     data = read_time_series('../Datasets/SURF_CLI_CHN_MUL_DAY-TEM_50468-1960-2012-short.txt')
#
#     tricklets = getTrickletsTS(data, 2)
#     tricklets1 = tricklets[0]
#     tricklets2 = tricklets[1]
#
#     # print(len(tricklets1))
#
#     # ts1 = dict(zip(data.index, data.t1))
#     # ts2 = dict(zip(data.index, data.t2))
#
#     ts1 = {int(k): v for k, v in dict(zip(data.index, data.t1)).items()}
#     ts2 = {int(k): v for k, v in dict(zip(data.index, data.t2)).items()}
#
#     # print(data['t1'])
#     # print(data.to_dict('t1'))
#
#     print(ts1)
#     print(ts2)
#
#     print(tricklets1)
#     print(tricklets2)
#
#     corr = localCorrelation(ts1, ts2, 0.1, 0.9, 28)
#     print(corr)
#
#     test_dictionary_building(tricklets1, tricklets2, corr)
#     #
#
#     # plt.plot(ts1.values())
#     # plt.plot(ts2.values())
#     # plt.show(block=True)


#
# # Normalize time series data
# from pandas import Series
# import pandas as pd
# from sklearn.preprocessing import MinMaxScaler
# from scipy import stats
#
#
# # load the dataset and print the first 5 rows
# df = pd.read_csv('data.txt', header=0)
# print(df.head())
#
#
# mean_std={}
# for var in df.columns:
#     mean_std[var]=(df[var].mean(), df[var].std())
#
# def reverse_zscore(pandas_series, mean, std):
#     '''Mean and standard deviation should be of original variable before standardization'''
#     yis=pandas_series*std+mean
#     return yis
#
# df_z = stats.zscore(df)
#
# print(mean_std)
#
# original_mean, original_std = mean_std['Temp']
# original_var_series = reverse_zscore(df_z['Temp'], original_mean, original_std)
#
# print(original_var_series.head)