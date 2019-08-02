from library import *



if __name__ == "__main__":

    threshold = 0.99
    nbweeks = 2
    len_tricklet = nbweeks * 7
    nb_atoms = 6
    datasetPath = '../Datasets/archive_ics/gas-sensor-array-temperature-modulation/20160930_203718.csv'
    # datasetPath = '../Datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv'
    # datasetPath = '../Datasets/UCRArchive_2018/CinCECGTorso/CinCECGTorso_TEST.tsv'
    # datasetPath = '../Datasets/UCRArchive_2018/Yoga/Yoga_TRAIN.tsv'
    # len_tricklet = nbweeks * 7
    df_data = pd.read_csv(datasetPath, sep='\t')
    df_data = pd.read_csv(datasetPath)

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
    print(df_data.shape)
    # df.plot()
    # plt.show()

    # save_object(df_data, '../Datasets/df_Yoga_TRAIN.tsv')

    # np.savetxt('../Datasets/df_20ts_exactcorrelation.txt', df_data.values, fmt='%d')

    # print (df_data)

    import time

    ts = time.time()
    start = time.time()

    time_series_data = dataframeToTricklets(df_data, len_tricklet)
    save_object(time_series_data, 'outputs/compressed/originalData%s.out' % str(int(ts)))

    # print (len(time_series_data[0]))
    # df_data = df.iloc[:,0:53]
    # print(df_learning)
    # time_series_learning = [item for sublist in dataframeToTricklets(df_learning) for item in sublist]
    # print('len', len(time_series_learning))
    # print(time_series_learning)

    print("Computing correlation ... ", end='')
    correlation_matrix = []

    # compute the correlation for each segment
    for i in range(int(df_data.shape[0] / len_tricklet)):
        correlation_matrix.append(df_data[i * len_tricklet: (i + 1) * len_tricklet].corr())
    print("done!")

    # print(correlation_matrix)

    print("Building the dictionary ... ", end='')
    # data = read_time_series('../Datasets/../Datasets/UCRArchive_2018/Yoga/Yoga_TRAIN.tsv')
    # tricklets = getTrickletsTS(data, 2, nbweeks)
    # print(len(tricklets[0]))
    Dictionary = learnDictionary(time_series_data[0], 200, 1, 150, 'dict_100.pkl')
    # Dictionary = learnDictionary(time_series_learning, 20, 1, 100)
    print("done!")

    # print("Loading the dictionary ... ", end='')
    # Dictionary = load_object('dict1.pkl')
    # print("done!")

    old_atoms_coded_tricklets, errors_old = compress_without_correlation(time_series_data, Dictionary, nb_atoms, 'omp')
    atoms_coded_tricklets, corr_coded_tricklets, errors_new = compress_with_correlation(time_series_data,
                                                                                        correlation_matrix, Dictionary,
                                                                                        threshold, nb_atoms, 'omp')

    end = time.time()

    # print(corr_coded_tricklets)

    import statistics as s

    print('New error:', "{0:.5}".format(s.mean(errors_new)))
    print('Old error:', "{0:.5}".format(s.mean(errors_old)))

    # original_size = get_size(old_atoms_coded_tricklets)
    # new_size = get_size(atoms_coded_tricklets) + get_size(corr_coded_tricklets)

    # print(original_size, new_size)
    # print('size optimisation is: %f' % (new_size / original_size))
    import time

    # import sys
    # print()
    # print(type(old_atoms_coded_tricklets), type(old_atoms_coded_tricklets[0]))
    # print(type(atoms_coded_tricklets), type(corr_coded_tricklets))
    # print(sys.getsizeof(old_atoms_coded_tricklets), 'size of old_atoms_coded_tricklets')
    # print(sys.getsizeof(atoms_coded_tricklets) + sys.getsizeof(corr_coded_tricklets), 'size of atoms_coded_tricklets')

    # print('atoms_coded_tricklets + corr_coded_tricklets', total_size(atoms_coded_tricklets) + total_size(old_atoms_coded_tricklets))
    # print('old_atoms_coded_tricklets', total_size(old_atoms_coded_tricklets))
    # print('')

    save_object(old_atoms_coded_tricklets, 'outputs/compressed/old_out_pickle%s.out' % str(int(ts)))
    save_object((atoms_coded_tricklets, corr_coded_tricklets), 'outputs/compressed/new_out_pickle%s.out' % str(int(ts)))

    # f = open("old_atoms_coded_tricklets.txt", "a")
    # for item in old_atoms_coded_tricklets:
    #     print(item)
    # f.close()

    from decimal import Decimal

    print('Computation time: ', round(Decimal(end - start), 2), 's')
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
