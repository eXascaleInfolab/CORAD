import pandas as pd
import matplotlib.pyplot as plt
from datetime import timedelta
import numpy as np
import sys
from luminol.anomaly_detector import AnomalyDetector
from luminol.correlator import Correlator
from decimal import Decimal
from dictionary_learning import *


def getTrickletsTS(time_series, nbTS, nbweeks):
    # First  timestamp
    s1 = time_series.iloc[:, 0][0]

    # Segment length
    slength = timedelta(weeks=nbweeks)

    # Data segmentation
    i = 0
    ts = [[] for i in range(nbTS)]

    # Read two time series
    while ((s1 + i * slength < time_series.iloc[:, 0][-1])):
        d = time_series[time_series['date'] >= (s1 + i * slength)]
        d = d[d['date'] < (s1 + (i + 1) * slength)]
        # print(d)
        # print(d.iloc[:, 1])
        # print(d.iloc[:, 2])
        for k in range(nbTS):
            if (len(d.iloc[:, k + 1].tolist()) == nbweeks * 7):
                ts[k].append(d.iloc[:, k + 1].tolist())
        i += 1

    # print('ts1')
    # print(ts1)
    # print('ts2')
    # print(ts2)
    return ts


# def getTricklets(data, length, nbTS):
#     # First  timestamp
#     s1 = data.iloc[:, 0][0]
#
#     # Segment length
#     slength = timedelta(weeks=nbweeks)
#
#     # Data segmentation
#     i = 0
#     ts = [[] for i in range(nbTS)]
#
#     # Read two time series
#     while ((s1 + i * slength < time_series.iloc[:, 0][-1])):
#         d = time_series[time_series['date'] >= (s1 + i * slength)]
#         d = d[d['date'] < (s1 + (i + 1) * slength)]
#         # print(d)
#         # print(d.iloc[:, 1])
#         # print(d.iloc[:, 2])
#         for k in range(nbTS):
#             if (len(d.iloc[:, k + 1].tolist()) == nbweeks * 7):
#                 ts[k].append(d.iloc[:, k + 1].tolist())
#         i += 1
#
#     # print('ts1')
#     # print(ts1)
#     # print('ts2')
#     # print(ts2)
#     return ts


# def getTimeStamp(id_tricklet):
#     return id_tricklet * nbweeks * 7
#

def plotData(data):
    plt.plot(data)
    plt.show(block=True)


def plotManyData(data, x, xaxis, yaxiy):
    if xaxis > 1 and yaxiy > 1:
        fig, ax = plt.subplots(nrows=xaxis, ncols=yaxiy)
        i = 0
        for row in ax:
            for col in row:
                col.plot(x, data[i])
                i += 1
    else:
        plt.plot(data[0])

    plt.show(block=True)


def trickletIsIn(timeStamp, corr, length):
    return [item for item in corr if item[0] <= timeStamp and timeStamp + length <= item[1]]


def runSparseCoder(Dictionary, test_data, nonzero_coefs, transform_algorithm):
    from sklearn.decomposition import SparseCoder

    coder = SparseCoder(dictionary=Dictionary, transform_n_nonzero_coefs=nonzero_coefs,
                        transform_alpha=None, transform_algorithm=transform_algorithm)

    print('test_data')
    print(test_data)
    result = coder.transform(test_data)

    tricklets = []
    # tricklets = np.array([np.array([[i,e] for i, e in enumerate(result[t]) if e != 0 for t in range(result.shape[0])])])

    for t in range(result.shape[0]):
        x = []
        for i, e in enumerate(result[t]):
            if e != 0:
                x.append([i, e])

        # print(type(x))
        tricklets.append(x)
        # tricklets= np.append(tricklets, np.array([[i, e] for i, e in enumerate(result[t]) if e != 0]))

    # print(tricklets)
    # print("result size: " + str( *jnu9n *juuricklets.shape))
    # print("result")
    tricklets = np.array([np.array(xi) for xi in tricklets])
    # np.set_printoptions(threshold=np.inf)
    # print(tricklets)
    # print(result)
    # print(result.shape)
    return tricklets


def print_dictionary(dict):
    for key, val in dict.items():
        print(key, "=>", val)

#
# def runSparseCoder_new(Dictionary, test_data, nonzero_coefs, transform_algorithm, corr):
#     from sklearn.decomposition import SparseCoder
#
#     coder = SparseCoder(dictionary=Dictionary, transform_n_nonzero_coefs=nonzero_coefs,
#                         transform_alpha=None, transform_algorithm=transform_algorithm)
#
#     # test_data: list of lists
#     print('test_data000')
#     print(len(test_data))
#     print(type(test_data))
#     print(test_data)
#     code = coder.transform(test_data)
#     # code = coder.transform2Tricklets(test_data)
#     print(code.shape)
#     atoms_coded_tricklets = {}
#     corr_coded_tricklets = {}
#     # tricklets = np.array([np.array([[i,e] for i, e in enumerate(result[t]) if e != 0 for t in range(result.shape[0])])])
#     # print('result:')
#     # print(result)
#
#     for t in range(code.shape[0]):
#         if not trickletIsIn(getTimeStamp(t), corr, 7 * nbweeks):
#             x = []
#             for i, e in enumerate(code[t]):
#                 if e != 0:
#                     x.append([i, e])
#             # print(type(x))
#             atoms_coded_tricklets[t] = x
#         else:
#             corr_coded_tricklets[t] = 1
#
#     # atoms_coded_tricklets = np.array([np.array(xi) for xi in atoms_coded_tricklets])
#
#     # print()
#     # print(atoms_coded_tricklets)
#
#     return atoms_coded_tricklets, corr_coded_tricklets


def reconstructData(sparseData, Dictionary):
    # sparseData [n, m] : n = tricklets number; m: nb atoms
    # Dictionary [n, m] : n = tricklet length; m: nb atoms
    # print(result.shape)

    out = []
    # print(sparseData.shape)
    # print(Dictionary.T.shape)
    for t in range(sparseData.shape[0]):
        sum = np.zeros(Dictionary.T.shape[0])

        for i, e in sparseData[t]:
            # print(Dictionary.T[:,int(i)])
            # print(e)
            # print('\n')
            sum += Dictionary.T[:, int(i)] * e

        out.append(sum)
        # out.append(np.sum(Dictionary.T * sparseData[n], axis=1))

    # print(len(out))
    return out


def reconstructDataMulti_without_correlation(sparseData, Dictionary):
    # sparseData [n, m] : n = tricklets number; m: nb atoms
    # Dictionary [n, m] : n = tricklet length; m: nb atoms
    # print(result.shape)
    # print(sparseData.shape)
    # print(Dictionary.T.shape)
    result = []
    # result = [[] for i in range(len(sparseData))]
    # print(sparseData)
    for index in range(len(sparseData)):
        out = []
        # print(sparseData[index])
        # print()
        for t in range(sparseData[index].shape[0]):
            # print(t)
            sum = np.zeros(Dictionary.T.shape[0])

            for i, e in sparseData[index][t]:
                # print(Dictionary.T[:,int(i)])
                # print(e)
                # print('\n')
                sum += Dictionary.T[:, int(i)] * e

            out.append(sum.tolist())
            # print(out)
        # print(out)
        result.append(out)
        # print(result)

        # out.append(np.sum(Dictionary.T * sparseData[n], axis=1))

    # print(len(out))
    # print(len(result[0]))
    return result


def reconstructDataMulti_with_correlation(atoms_coded_tricklets, corr_coded_tricklets, Dictionary, ts):
    # result = [[] for i in range(len(sparseData))]
    # print(sparseData)

    result = {}

    # print(atoms_coded_tricklets)
    # input('')
    # start with reconstructing the atoms stored tricklets
    # for each time series
    for k, v in atoms_coded_tricklets.items():
        out = {}
        # print(sparseData[index])
        # print()
        for w in sorted(v.keys()):
            # print(t)
            sum = np.zeros(Dictionary.T.shape[0])

            for i, e in v[w]:
                # print(Dictionary.T[:,int(i)])
                # print(e)
                # print('\n')
                sum += Dictionary.T[:, int(i)] * e

            out[w] = sum.tolist()

            # print(out)
        # print(out)
        result[k] = out
        # print(result)

    # out.append(np.sum(Dictionary.T * sparseData[n], axis=1))
    # for k, v in result.items():
    #     # print(k, v.keys())
    #     for j in v.keys():
    #         try:
    #             print(ts[k][j])
    #             print(result[k][j])
    #
    #             plt.plot(ts[k][j])
    #             plt.plot(result[k][j])
    #             plt.title(str(i) + '_' + str(j))
    #             plt.show()
    #             print()
    #         except:
    #             print()
    #     print()

    # for each TS stored using correlation
    for k in corr_coded_tricklets.keys():
        # for each window and shift value
        for w in corr_coded_tricklets[k].keys():
            i_m = corr_coded_tricklets[k][w]
            # i_m, shift = corr_coded_tricklets[k][w]
            # print(shift)
            if k not in result.keys():
                result[k] = {}
            result[k][w] = [x  for x in result[i_m][w]]
            # result[k][w] = [x + shift for x in result[i_m][w]]

            # print(ts[k][w])
            # print(result[k][w])

            # plt.plot(ts[k][w])
            # plt.plot(result[k][w])
            # plt.plot(result[i_m][w])
            # plt.title(str(i) + '_' + str(w))
            # plt.show()
            # print('yep')

            # print()
            # try:
            #     # print(atoms_coded_tricklets[value][key])
            # print('a is ', a)
            # print(atoms_coded_tricklets[i_m][w] * a )
            # print(atoms_coded_tricklets[i_m][w] )

            # found_list, shift = find_corr_list(result, corr_coded_tricklets, i_m, w, shift)

            # corr_i = result[corr_coded_tricklets[value][w]][w]

            # print("XXXXXXX", index)
            # result[k][w] = [x + shift for x in result[i_m][w]]

            # try:
            #     result[index][w] = [x + shift for x in result[i_m][w]]
            # except:
            #     result[index][w] = [x + shift for x in result[corr_coded_tricklets[index][w]][w]]

            # except:
            #     result[index][w] = result[corr_coded_tricklets[value][w]][w]
            # not complete, it fixes a one way run, but not all cases
            # print(key)

    # print(len(out))
    # print(len(result[0]))

    resultList = []
    for i in range(len(result.values())):
        # li =
        # v = result[i]
        resultList.append([result[i][j] for j in sorted(result[i].keys())])

        # for j in range(len(result[i])):
        #     plt.plot(ts[i][j])
        #     plt.plot(resultList[i][j])
        #     plt.title(str(i) + '_' + str(j))
        #     plt.show()

        # resultList.append(li)

    # print(len(result))
    # for k in range(len(result.items())):
    #     w_list = [[] in range(len(result[k]))]
    #     print(w_list)
    #
    #     resultList[k] = [x for x in v.values()]
    #
    # for j in range(len(ts[k])):
    #     plt.plot(ts[k][j])
    #     plt.plot(resultList[k][j])
    #     plt.title(str(k) + '_'+str(j))
    #     plt.show()
    #
    #     print()

    return resultList


# def find_corr_list(result, corr_coded_tricklets, ts, window, shift):
def find_corr_list(result, corr_coded_tricklets, ts, window):
    try:
        return result[ts][window]
        # return result[ts][window], shift
    except:
        print(ts, window)
        raise

    # except:
    #     index, sh = corr_coded_tricklets[index][window]
    #     return find_corr_list(result, corr_coded_tricklets, index, window, shift + sh)


def pause():
    input("Press Enter to continue...")


def reconstructData_new(atoms_coded_tricklets, corr_coded_tricklets, otherTS, Dictionary):
    # sparseData [n, m] : n = tricklets number; m: nb atoms
    # Dictionary [n, m] : n = tricklet length; m: nb atoms
    # print(result.shape)

    out = []
    # print(Dictionary.T.shape)

    for t in corr_coded_tricklets:
        atoms_coded_tricklets[t] = otherTS[t] * corr_coded_tricklets[t]
        # atoms_coded_tricklets[t] = otherTS[t] * 0

    for t in sorted(atoms_coded_tricklets.keys()):
        # print(t)
        sum = np.zeros(Dictionary.T.shape[0])

        for i, e in atoms_coded_tricklets[t]:
            # print(Dictionary.T[:,int(i)])
            # print(e)
            # print('\n')
            sum += Dictionary.T[:, int(i)] * e

        out.append(sum)
    # out.append(np.sum(Dictionary.T * sparseData[n], axis=1))

    # for t in range(otherTS.shape[0]):
    #     if t in atoms_coded_tricklets:
    #         sum = np.zeros(Dictionary.T.shape[0])
    #         print(atoms_coded_tricklets[t])
    #         for i, e in atoms_coded_tricklets[t]:
    #             # print(Dictionary.T[:,int(i)])
    #             # print(e)
    #             # print('\n')
    #             sum += Dictionary.T[:, int(i)] * e
    #
    #         out.append(sum)
    #         # out.append(np.sum(Dictionary.T * sparseData[n], axis=1))
    #     else:
    #         out.append(corr_coded_tricklets[t])

    # print(len(out))
    return out


def localCorrelation(ts1, ts2, score_threshold, correlation_threshold, minLength):
    my_detector = AnomalyDetector(ts1, score_threshold=score_threshold)
    score = my_detector.get_all_scores()
    anomalies = my_detector.get_anomalies()

    list = []

    for a in anomalies:
        time_period = a.get_time_window()
        # print(time_period)
        if int(time_period[1]) - int(time_period[0]) >= minLength:
            # print(type(time_period))
            my_correlator = Correlator(ts1, ts2, time_period)
            if my_correlator.is_correlated(threshold=correlation_threshold):
                # print("ts2 correlate with ts1 at time period (%d, %d)" % time_period)
                list.append(time_period)
    return list


# def test_dictionary_building_old(ts1, ts2):
#     # Reading time series
#     # ts1, ts2 = read_time_series('SURF_CLI_CHN_MUL_DAY-TEM_50468-1960-2012-short.txt')
#
#     # Get sample 100 tricklets to reconstruct
#     test_data = np.array(ts2[20:120])
#
#     # Build the dictionary
#     print("Building the dictionary ... ", end='')
#     D = learnDictionary(ts1, 36, 1, 100)
#     print("done!")
#     # print(len(D))
#
#     # Transforming test data into sparse respresentation using the omp algorithm
#     print("Transforming test data into sparse respresentation ... ", end='')
#     sparseData = runSparseCoder(D, test_data, nbAtoms, "omp")
#     # np.set_printoptions(threshold=np.inf)
#     # print(sparseData)
#
#     sparseDataX = pd.DataFrame.from_records(sparseData)
#     # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     #     print(sparseDataX)
#     #     print(len(sparseDataX))
#
#     print("done!")
#
#     print("Reconstructing data...", end="")
#     out = reconstructData(sparseData, D)
#     print("done!")
#
#     print("Plotting.. ", end="")
#     plotManyData(test_data, range(len(D[0])), 2, 2)
#     plotManyData(D, range(len(D[0])), 6, 6)
#     plotManyData(out, range(len(D[0])), 2, 2)
#
#     plt.show(block=True)
#     print("done!")
#
#     print("Error's norm: ", end="")
#     print(np.linalg.norm(np.array(test_data) - np.array(out)))


def dict_to_array(dict):
    dictlist = []
    for key, value in dict.items():
        temp = [key, value]
        dictlist.append(temp)
    return dictlist


# def test_dictionary_building(ts1, ts2, corr):
#     # Reading time series
#     # ts1, ts2 = read_time_series('SURF_CLI_CHN_MUL_DAY-TEM_50468-1960-2012-short.txt')
#
#     # Build the dictionary
#     print("Building the dictionary ... ", end='')
#     D = learnDictionary(ts2, 400, 1, 100)
#     print("done!")
#     # print(len(D))
#
#     # Transforming test data into sparse respresentation using the omp algorithm
#     print("Transforming test data into sparse respresentation ... ", end='')
#     atoms_coded_tricklets1, corr_coded_tricklets1 = runSparseCoder_new(D, ts1, nbAtoms, "omp", corr)
#     # atoms_coded_tricklets1 = dict_to_array(atoms_coded_tricklets1)
#     # corr_coded_tricklets1 = dict_to_array(corr_coded_tricklets1)
#
#     atoms_coded_tricklets2 = runSparseCoder(D, ts1, nbAtoms, "omp")
#
#     # print(runSparseCoder(D, ts1, nbAtoms, "omp"))
#     # print(atoms_coded_tricklets1)
#     # print(corr_coded_tricklets1)
#     old_size = sys.getsizeof(atoms_coded_tricklets2)
#     new_size = sys.getsizeof(atoms_coded_tricklets1) + sys.getsizeof(corr_coded_tricklets1)
#     print('old size: ')
#     print(old_size)
#     print('new size: ')
#     print(new_size)
#
#     print('Compression rate:')
#     print("{0:.0%}".format(1. - float(new_size) / float(old_size)))
#     # # np.set_printoptions(threshold=np.inf)
#     # # print(sparseData)
#
#     # sparseDataX = pd.DataFrame.from_records(sparseData)
#     # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     #     print(sparseDataX)
#     #     print(len(sparseDataX))
#
#     print("done!")
#
#     print("Reconstructing data...", end="")
#
#     reconstruct1 = reconstructData_new(atoms_coded_tricklets1, corr_coded_tricklets1, atoms_coded_tricklets2, D)
#     reconstruct2 = reconstructData(atoms_coded_tricklets2, D)
#     # print(np.array(reconstruct1))
#     # print(np.array(reconstruct2))
#
#     # print(np.array(normalized(reconstruct1)).shape)
#     print("reconstruct1!")
#
#     # print(np.array(normalized(reconstruct2)).shape)
#     print("done!")
#
#     #
#     # # print("Plotting.. ", end="")
#     # # plotManyData(test_data, range(len(D[0])), 2, 2)
#     # # plotManyData(D, range(len(D[0])), 6, 6)
#     # # plotManyData(out, range(len(D[0])), 2, 2)
#     # #
#     # # plt.show(block=True)
#     # # print("done!")
#     # #
#
#     # print(np.array(normalized(ts1)))
#     # print(np.array(normalized(reconstruct1)))
#
#     # print(np.array(reconstruct1) - np.array(reconstruct2))
#
#     print("Error's norm of the correlation-aware method: ", end="")
#
#     # error1 = np.linalg.norm(np.array(normalized(ts1)) - np.array(normalized(reconstruct1)))
#     error1 = calculate_RMSE(ts1, reconstruct1)
#     # # error1 = ((np.array(normalized(ts1) - np.array(normalized(reconstruct1))) ** 2).mean(axis=None))
#     print('%.2E' % Decimal(error1))
#
#     print("Error's norm of the regular method: ", end="")
#     error2 = calculate_RMSE(ts1, reconstruct2)
#
#     # # error2 = ((np.array(normalized(ts2) - np.array(normalized(reconstruct1))) ** 2).mean(axis=None))
#     # print('%.2E' % Decimal(error2))
#
#     # error2 = np.linalg.norm(np.array(normalized(ts1)) - np.array(normalized(reconstruct2)))
#     print('%.2E' % Decimal(error2))
#
#     print('Lost precision: ' + str(error2 - error1))


def chunks(l, len_tricklet):
    """Yield successive n-sized chunks from l."""
    res = []
    for i in range(0, len(l), len_tricklet):
        if (len(l[i:i + len_tricklet]) == len_tricklet):
            res.append(l[i:i + len_tricklet])
    return res


def sparse_code_without_correlation(ts, Dictionary, nonzero_coefs, transform_algorithm):
    from sklearn.decomposition import SparseCoder

    coder = SparseCoder(dictionary=Dictionary, transform_n_nonzero_coefs=nonzero_coefs
                        , transform_algorithm=transform_algorithm)

    # For each time series, for each tricklet, transform the tricklet and store it
    result = []
    for t in ts:
        result.append(coder.transform(t))

    # transformation of result to [id_A, coef_A]
    tricklets = []
    for index in range(len(result)):
        temp = []
        for t in range(result[index].shape[0]):
            x = []
            for i, e in enumerate(result[index][t]):
                if e != 0:
                    x.append([i, e])
            temp.append(x)
        tricklets.append(temp)

    for index in range(len(result)):
        tricklets[index] = np.array([np.array(xi) for xi in tricklets[index]])

    return tricklets


def normalize_df(df):
    from scipy.signal import detrend
    from sklearn import preprocessing

    # x = df.values  # returns a numpy array
    # min_max_scaler = preprocessing.MinMaxScaler()
    # x_scaled = min_max_scaler.fit_transform(x)
    # df = pd.DataFrame(x_scaled)
    return detrend(df)

def mse(x, y):
    return ((np.array(x) - np.array(y)) ** 2).mean(axis=None)


def sparse_code_with_correlation(ts, correlation_matrix, Dictionary, nonzero_coefs, transform_algorithm, threshold):
    """

    :type correlation_matrix: object
    """

    from sklearn.decomposition import SparseCoder

    coder = SparseCoder(dictionary=Dictionary, transform_n_nonzero_coefs=nonzero_coefs,
                        transform_alpha=None, transform_algorithm=transform_algorithm)

    # For each time series, for each tricklet, transform the tricklet and store it
    result = []
    for t in ts:
        result.append(coder.transform(t))

    # tricklets sparsely coded
    tricklets = []

    # transform sparse matrix into sparse arrays
    for index in range(len(result)):
        temp = []
        for t in range(result[index].shape[0]):
            x = []
            for i, e in enumerate(result[index][t]):
                if e != 0:
                    x.append([i, e])
            temp.append(x)
        tricklets.append(temp)
    for index in range(len(result)):
        tricklets[index] = np.array([np.array(xi) for xi in tricklets[index]])

    atoms_coded_tricklets = {}
    # atoms_coded_tricklets = [{} for i in range(len(ts))
    corr_coded_tricklets = {}

    # print('corr size:', get_size(corr_coded_tricklets))

    # for each time window
    for w in range(result[0].shape[0]):
        # create dictionary to keep indices
        A = correlation_matrix[w].values.tolist()
        B = {i: A[i] for i in range(len(A))}
        # sort lines in a decent order by the sum of their elements
        C = dict(sorted(B.items(), key=lambda i: sum(i[1]), reverse=True))

        i_stored = []

        x_plotting = np.array([])
        y_plotting = np.array([])
        # for each line (TS)
        # print('shift reduced error?')

        # shift_works = []

        # for each time series
        for k, X in C.items():

            # Find the index maximizing the correlation
            # m =   list of indices of corr TS candidates AND
            #       already stored normally and different than itself
            m = {i: v for i, v in enumerate(X) if (
                    i in i_stored and v >= threshold and k != i)}
            m = dict(sorted(m.items(), key=lambda i: i[1], reverse=True))

            try:
                i_m = list(m.keys())[0]
            except:
                i_m = None

            # i_m = [i for i, v in enumerate(X) if m and v == max(m)]  # indice of the max
            # if k == 2 and w == 53:

            # print('m =', m, ', i_m=', i_m, ', i_stored=', i_stored)
            if i_m is not None:  # store corr
                # print('first in ')
                # i_m = i_m[0]
                x = ts[i_m][w]
                y = ts[k][w]
                if k not in corr_coded_tricklets.keys():
                    corr_coded_tricklets[k] = {}
                # corr_coded_tricklets[k][w] = i_m, shift_mean(x, y)
                corr_coded_tricklets[k][w] = i_m
                # print(shift_mean(x, y))

                # z = [v + shift_mean(x, y) for v in x]
                z = [v for v in x]
                # shift_works.append(mse(x, y) > mse(x, z))
                # plt.plot(x)
                # plt.plot(y)

                # plt.plot(z)
                # plt.savefig('outputs/shift_plots/shift_plots%d_%d.png' % (k, w))
                # plt.show()
                # plt.cla()
                # print(((np.array(x) - np.array(y)) ** 2).mean(axis=None))
                # np.append(x_plotting, shift_mean(x, y))
                # np.append(y_plotting, mse(x,y))
                # input('')
                # a, b = alpha_beta(x, y)
                # if a != 0 :
                #     corr_coded_tricklets[k][w] = i_m, a, b  # pick the first candidate maximizing the correlation
                # else:
                #     if k in atoms_coded_tricklets:
                #         atoms_coded_tricklets[k][w] = tricklets[k][w]
                #     else:
                #         atoms_coded_tricklets[k] = {}
                #         atoms_coded_tricklets[k][w] = tricklets[k][w]
                #     i_stored.append(k)
            else:  # store sparse
                # print('2nd in ')
                if k not in atoms_coded_tricklets:
                    atoms_coded_tricklets[k] = {}
                atoms_coded_tricklets[k][w] = tricklets[k][w]
                # add k to the list of elements stored in sparse way
                i_stored.append(k)

        #  plt.cla()
        #  plt.xlabel('shift mean')
        #  plt.ylabel('error')
        #  plt.title('shift mean vs mserror')
        #  plt.scatter(x, y)
        # # plt.show()
        #  plt.savefig('outputs/shift_error/shift_vs_error%d.png'%w)
        # print('yeah', any(item == True for item in shift_works))

    # print(atoms_coded_tricklets)
    # print(corr_coded_tricklets)
    return atoms_coded_tricklets, corr_coded_tricklets


def shift_median(x, y):
    av_x = sum(x) / len(x)
    av_y = sum(y) / len(y)

    # print(av_y - av_x)
    # plt.plot(x)
    # plt.plot(y)
    # plt.plot([i + av_y - av_x for i in x])
    # plt.show()

    plt.show(block=True)

    return av_y - av_x


def shift_mean(x, y):
    import statistics

    av_x = statistics.median(x)
    av_y = statistics.median(y)

    # print(av_y - av_x)
    # plt.plot(x)
    # plt.plot(y)
    # plt.plot([i + av_y - av_x for i in x])
    # plt.show()

    plt.show(block=True)

    return av_y - av_x


def alpha_beta(x, y):
    try:

        acc = (y[-1] - y[0]) / (x[-1] - x[0])
        print(x)
        print(y)
        print(acc)

        plt.plot(x)
        plt.plot(y)
        plt.plot([i * acc + x[0] * (1 - acc) for i in x])
        plt.show()

        plt.show(block=True)

    except:
        acc = 0
    # print(acc, x[0]*(1-acc))
    return acc, x[0] * (1 - acc)


# import sys
# from numbers import Number
# from collections import Set, Mapping, deque
#
# try: # Python 2
#     zero_depth_bases = (basestring, Number, xrange, bytearray)
#     iteritems = 'iteritems'
# except NameError: # Python 3
#     zero_depth_bases = (str, bytes, Number, range, bytearray)
#     iteritems = 'items'
#
# def get_size(obj_0):
#     """Recursively iterate to sum size of object & members."""
#     _seen_ids = set()
#     def inner(obj):
#         obj_id = id(obj)
#         if obj_id in _seen_ids:
#             return 0
#         _seen_ids.add(obj_id)
#         size = sys.getsizeof(obj)
#         if isinstance(obj, zero_depth_bases):
#             pass # bypass remaining control flow and return
#         elif isinstance(obj, (tuple, list, Set, deque)):
#             size += sum(inner(i) for i in obj)
#         elif isinstance(obj, Mapping) or hasattr(obj, iteritems):
#             size += sum(inner(k) + inner(v) for k, v in getattr(obj, iteritems)())
#         # Check for custom object instances - may subclass above too
#         if hasattr(obj, '__dict__'):
#             size += inner(vars(obj))
#         if hasattr(obj, '__slots__'): # can have __slots__ with __dict__
#             size += sum(inner(getattr(obj, s)) for s in obj.__slots__ if hasattr(obj, s))
#         return size
#     return inner(obj_0)


def get_size(obj, seen=None):
    """Recursively finds size of objects"""
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size


def compress_without_correlation(ts, Dictionary, nbAtoms, transform_algorithm):
    # Transforming test data into sparse respresentation using the transform algorithm
    print("Transforming test data into sparse respresentation without correlation ... ", end='')
    sparseData = sparse_code_without_correlation(ts, Dictionary, nbAtoms, transform_algorithm)
    # print(atoms_coded_tricklets)
    print("done!")

    print("Reconstructing data...", end="")
    recons = reconstructDataMulti_without_correlation(sparseData, Dictionary)
    print("done!")
    # print(recons)

    errors = []
    # print("Error's norm of the correlation-aware method: ", end="")
    for i in range(len(ts)):
        errors.append(calculate_RMSE(ts[i], recons[i]))
        # errors.append(np.square(np.array(normalized(ts[i]) - np.array(normalized(recons[i]))) ** 2).mean(axis=None))
        # for j in range(len(ts[i])):
        #     plt.plot(ts[i][j])
        #     plt.plot(recons[i][j])
        #     plt.title(str(i) + str(j))
        #     plt.show()

        # errors.append(calculate_RMSE(ts[i], np.array(recons[i])))
    # print(errors)
    # print(len(recons))
    return sparseData, errors

    # plt.plot(errors)
    # plt.ylabel('errors')
    # plt.show()


def compress_with_correlation(ts, correlation_matrix, Dictionary, corr_threshold, nbAtoms, transform_algorithm):
    # Transforming test data into sparse respresentation using the omp algorithm

    print("Transforming test data into correlation-aware sparse respresentation ... ", end='')
    atoms_coded_tricklets, corr_coded_tricklets = sparse_code_with_correlation(ts, correlation_matrix, Dictionary,
                                                                               nbAtoms, transform_algorithm,
                                                                               corr_threshold)

    # sparseData = sparse_code_without_correlation(ts, Dictionary, nbAtoms, "omp")
    # print(atoms_coded_tricklets)

    print("done!")

    print("Reconstructing data with correlation...", end="")

    # print(corr_coded_tricklets)

    # for k,v in corr_coded_tricklets.items():
    #     print(k, v)

    recons = reconstructDataMulti_with_correlation(atoms_coded_tricklets, corr_coded_tricklets, Dictionary, ts)
    print("done!")
    # # print(recons)

    # print(corr_coded_tricklets)

    import itertools

    errors = []
    result_before = []
    result_after = []
    # print("Error's norm of the correlation-aware method: ", end="")
    for i in range(len(ts)):
        errors.append(calculate_RMSE(ts[i], recons[i]))
        # print(i)
        result_before.append(list(itertools.chain.from_iterable(ts[i])))
        result_after.append(list(itertools.chain.from_iterable(recons[i])))
        #
        # print(len(result))
        # print(len(result[0]))

    result_after = pd.DataFrame(result_after)
    result_before = pd.DataFrame(result_before)
    result_before = result_before.T
    result_after = result_after.T
    print(result_before.shape)
    print(result_after.shape)
    print(result_before.head())
    print(result_after.head())


    result_after.to_csv('yoga_after.txt', float_format='%.6f', header=False, sep=' ', index=False)
    result_before.to_csv('yoga_before.txt', float_format='%.6f', header=False, sep=' ', index=False)

        # errors.append(np.square(np.array(normalized(ts[i]) - np.array(normalized(recons[i]))) ** 2).mean(axis=None))
        # for j in range(len(ts[i])):
        # try:
        # plt.plot(ts[i][j])
        # plt.plot(recons[i][j])
        # plt.title(str(i) + '_'+str(j))
        # plt.show()

        # except:
        #     print()
        #
        #     try:
        #         print(corr_coded_tricklets[i][j])
        #     except:
        #         print('in atoms')
        #     plt.show()

        # errors.append(calculate_RMSE(ts[i], np.array(recons[i])))
    # print(errors)

    return atoms_coded_tricklets, corr_coded_tricklets, errors

    # plt.plot(errors)
    # plt.ylabel('errors')
    # plt.show()


def normalized(ts):
    # pop = np.array([np.array(xi) for xi in ts])
    # return (pop - np.min(pop)) / (np.max(pop) - np.min(pop))
    from scipy import stats
    return stats.zscore(ts)


def calculate_RMSE(orig_sig, reconstructed_sig):
    orig_sig = normalized(orig_sig)
    reconstructed_sig = normalized(reconstructed_sig)
    return (np.square(np.array(orig_sig) - np.array(reconstructed_sig))).mean(axis=None)



def calculate_PRD(orig_sig, reconstructed_sig):
    orig_sig = normalized(orig_sig)
    reconstructed_sig = normalized(reconstructed_sig)
    num = np.sum((orig_sig - reconstructed_sig) ** 2)
    den = np.sum(orig_sig ** 2)

    PRD = np.sqrt(num / den)

    return PRD


def dataframeToTricklets(data, len_tricklet):
    ts = [[] for i in range(len(data.columns))]

    for column in data:
        # print(data[column].tolist())
        # pprint.pprint(list(chunks(data[column].tolist(), len_tricklet)))
        ts[data.columns.get_loc(column)].extend(chunks(data[column].tolist(), len_tricklet))

    return ts
