from lib.lib import *
import time
from decimal import Decimal
import statistics as s
from scipy import stats
from tqdm import tqdm
import argparse
import sys
import ntpath
import os

def exportResults(name, dic):
    download_dir = name + ".csv"  # where you want the file to be downloaded to

    if not os.path.exists(os.path.dirname(download_dir)):
        try:
            os.makedirs(os.path.dirname(download_dir))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    csv = open(download_dir, "w")
    # "w" indicates that you're writing strings to the file

    columnTitleRow = "title, CORAD, TRISTAN\n"
    csv.write(columnTitleRow)

    for key in dic.keys():
        title = key
        value1, value2 = dic[key]
        row = title + "," + str(value1) + "," + str(value2) + "\n"
        csv.write(row)


if __name__ == "__main__":
    

    print("Number of arguments:", len(sys.argv), "arguments.")
    print("Argument List:", str(sys.argv))

    for i in range(len(sys.argv)):
        print(i, sys.argv[i])

    parser = argparse.ArgumentParser(description = 'Script for running the compression')
    parser.add_argument('--dataset', nargs = '?', type = str, help = 'Dataset path', default = 'datasets/20160930_203718-2.csv')
    # parser.add_argument('--datasetPathDictionary', nargs = '?', type = str, help = 'Dataset path of the dictionary', default = '../datasets/archive_ics/gas-sensor-array-temperature-modulation/20160930_203718-2.csv')
    parser.add_argument('--trick', nargs = '?', type = int, help = 'Length of a tricklet', default = 40)
    parser.add_argument('--err', nargs = '?', type = float, help = 'Maximum level of threshold', default = 0.4)
    parser.add_argument('--atoms', nargs = '?', type = int, help = 'Number of atoms', default = 4)
    #parser.add_argument('--export', nargs = '*', type = str, help = 'Path to file where to export the results', default = 'results.txt')
    parser.add_argument('--additional_arguments', nargs = '?', type = str, help = 'Additional arguments to be passed to the scripts', default = '')
    args = parser.parse_args()


    dataset = args.dataset

    
        # datasetPathDictionary = args.datasetPathDictionary
    trick = args.trick
    err = args.err
    atoms = args.atoms


    # dataset = sys.argv[1]
    # datasetPath = sys.argv[2]
    # datasetPathDictionary = sys.argv[3]
    # # NBWEEKS = sys.argv[2]
    # trick = int(sys.argv[4])
    # err = float(sys.argv[5])
    # # trick = NBWEEKS * 7
    # atoms = int(sys.argv[6])
    

    TIMESTAMP = time.time()
    CORR_THRESHOLD = 1 - err / 2

    # READING THE DATASETS

    # df_data = pd.read_csv(datasetPath, sep='\t|;|:|,| ')
    # df_data = df_data.T
    df_data = pd.read_csv(dataset, header=None, sep='\t|;|:|,| ')

    print(df_data.shape)
    print(df_data.head())

    # df_data_learning = pd.read_csv(datasetPathDictionary, sep='\t|;|:|,| ')
    # df_data_learning = df_data_learning.T
    df_data = pd.DataFrame(stats.zscore(df_data))

    df_data_learning = df_data.iloc[:, 1:8]

    # z-score normalizing the data

    # df_data.round(6)
    # print(df_data.head())
    # df_data.to_csv('yoga_before.txt', header=False, float_format='%.6f', sep='\t|;|:|,| ', index=False)
    # df_data.plot()
    # plt.draw()

    # df_data_learning = pd.DataFrame(stats.zscore(df_data_learning))

    # CREATING TRICKLETS

    time_series_data = dataframeToTricklets(df_data, trick)
    time_series_data_dictionary = dataframeToTricklets(df_data_learning, trick)

    # CORRELATION COMPUTATION FOR EACH SEGMENT

    print("Computing correlation ... ", end="")
    correlation_matrix = []
    for i in tqdm(range(int(df_data.shape[0] / trick))):
        correlation_matrix.append(
            df_data[i * trick : (i + 1) * trick].corr()
        )
    print("done!")

    # DICTIONARY

    print("Building the dictionary ... ", end="")
    for i in tqdm(range(1, int(len(time_series_data_dictionary)))):
        time_series_data_dictionary[0].extend(time_series_data_dictionary[i])
    print("Learning dictionary")
    Dictionary = learnDictionary(
        time_series_data_dictionary[0], 200, 1, 150, dataset + ".pkl"
    )
    # data = read_time_series('../datasets/../datasets/UCRArchive_2018/Yoga/Yoga_TRAIN.tsv')
    # tricklets = getTrickletsTS(data, 2, NBWEEKS)
    # print(len(tricklets[0]))
    # Dictionary = learnDictionary(time_series_learning, 20, 1, 100)

    # print("Loading the dictionary ... ", end='')
    # Dictionary = load_object('dict_100.pkl')

    print("done!")

    # COMPRESSING THE DATA THE TRISTAN WAY
    start1 = time.time()
    old_atoms_coded_tricklets, errors_old = compress_without_correlation(
        time_series_data, Dictionary, atoms, "omp"
    )
    end1 = time.time()

    # COMPRESSING THE DATA OUR WAY
    start2 = time.time()
    atoms_coded_tricklets, corr_coded_tricklets, errors_new = compress_with_correlation(
        time_series_data,
        correlation_matrix,
        Dictionary,
        CORR_THRESHOLD,
        atoms,
        "omp",
    )
    end2 = time.time()
    
    save_object(
        time_series_data, "results/compressed/originalData%s.out" % str(int(TIMESTAMP))
    )
    save_object(
        old_atoms_coded_tricklets,
        "results/compressed/old_out_pickle%s.out" % str(int(TIMESTAMP)),
    )
    save_object(
        (atoms_coded_tricklets, corr_coded_tricklets),
        "results/compressed/new_out_pickle%s.out" % str(int(TIMESTAMP)),
    )


    # SAVE THE DATA FILES
    save_object(
        time_series_data, "results/compressed/originalData.out"
    )
    save_object(
        old_atoms_coded_tricklets,
        "results/compressed/old_out_pickle.out",
    )
    save_object(
        (atoms_coded_tricklets, corr_coded_tricklets),
        "results/compressed/new_out_pickle.out",
    )

    dic = {}

    # PRINTING COMPUTATION TIME
    print(
        "Computation time without correlation: ", round(Decimal(end1 - start1), 2), "s"
    )
    print("Computation time with correlation: ", round(Decimal(end2 - start2), 2), "s")

    # dic['compression_time_without_correltion']= round(Decimal(end1 - start1), 2)
    # dic['compression_time_with_correltion']= round(Decimal(end2 - start2), 2)
    dic["compression_time"] = (
        round(Decimal(end2 - start2), 2),
        round(Decimal(end1 - start1), 2),
    )

    # print(corr_coded_tricklets)

    # PRINTING ERRORS
    print("New error:", "{0:.5}".format(s.mean(errors_new)))
    print("Old error:", "{0:.5}".format(s.mean(errors_old)))

    # dic['error_new'] = "{0:.5}".format(s.mean(errors_new))
    # dic['error_old'] = "{0:.5}".format(s.mean(errors_old))
    dic["error"] = (
        "{0:.5}".format(s.mean(errors_new)),
        "{0:.5}".format(s.mean(errors_old)),
    )

    # COMPUTING COMPRESSION RATIOS

    import os

    statinfo_old = os.stat(
        "results/compressed/old_out_pickle%s.out" % str(int(TIMESTAMP))
    )
    statinfo_old = statinfo_old.st_size
    # dic['size_old'] = statinfo.st_size
    statinfo_new = os.stat(
        "results/compressed/new_out_pickle%s.out" % str(int(TIMESTAMP))
    )
    statinfo_new = statinfo_new.st_size

    # dic['size_new'] = statinfo.st_size
    statinfo = os.stat("results/compressed/originalData%s.out" % str(int(TIMESTAMP)))
    statinfo = statinfo.st_size

    dic["size_original"] = (statinfo, statinfo)
    dic["compressed size"] = (statinfo_new, statinfo_old)

    dic["compression_ratio"] = (
        dic["size_original"][0] / (statinfo_new),
        dic["size_original"][0] / statinfo_old,
    )



    exportResults(
        "results/stats_"
        + str(ntpath.basename(dataset))
        + "_"
        + str(trick)
        + "_"
        + str(err)
        + "_"
        + str(atoms)
        + ".txt",
        dic,
    )


