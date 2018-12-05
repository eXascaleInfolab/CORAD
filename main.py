from library import *

if __name__ == "__main__":

    threshold = 0.9


    df = read_multiple_ts('Datasets/Sales_Transactions_Dataset_Weekly.csv', 1, 53)


    df_data = df.iloc[:,0:39]
    df_learning = df.iloc[:,40:53]
    # print(df_learning)

    time_series_data = dataframeToTricklets(df_data)
    time_series_learning = [item for sublist in dataframeToTricklets(df_learning) for item in sublist]
    # print('len', len(time_series_learning))
    # print(time_series_learning)

    correlation_matrix = []


    for i in range(int(df_data.shape[0] / len_tricklet)):
        correlation_matrix.append(df_data[i * len_tricklet: (i + 1) * len_tricklet].corr())


    # print("Building the dictionary ... ", end='')
    # print(time_series_learning)
    # Dictionary = learnDictionary(time_series_learning, 10, 1, 100)
    # print("done!")

    print("Loading the dictionary ... ", end='')
    Dictionary = load_object('dict1.pkl')
    print("done!")


    old_sparse_size, errors1 = compress_without_correlation(time_series_data, Dictionary, 6, 'lasso_lars')
    new_sparse_size, errors2 = compress_with_correlation(time_series_data, correlation_matrix, Dictionary, threshold, 6, 'lasso_lars')
    original_size = get_size(time_series_data)
    import statistics as s
    print(s.mean(errors1))
    print(s.mean(errors2))

    print(old_sparse_size)
    print(new_sparse_size)

    print('Compression rate:')
    print("{0:.0%}".format(1. - float(new_sparse_size) / float(old_sparse_size)))
    print('Compression rate:')
    print("{0:.0%}".format(1. - float(new_sparse_size) / float(original_size)))


    plt.plot(errors1)
    plt.plot(errors2)
    plt.ylabel('errors')
    plt.xlabel('time series')
    plt.show()

    # plt.plot(data)
    # plt.show(block=True)

# if __name__ == "__main__":
#     # Reading time series
#     # data = read_time_series('Datasets/Sales_Transactions_Dataset_Weekly.csv')
#     # data = read_time_series('Datasets/drift6_normal.txt')
#     data = read_time_series('Datasets/SURF_CLI_CHN_MUL_DAY-TEM_50468-1960-2012-short.txt')
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
