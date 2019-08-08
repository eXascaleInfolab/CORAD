import Adaptive_chebyshev as adp_cheb
import numpy as np
import pandas as pd
from os import getcwd
from os.path import join
import matplotlib as plt


def print_lot_statistics(coefs, orignal, reconstrcuted):
    # statistics
    dict_to_return = calc_stats(coefs, orignal, reconstrcuted)
    print(dict_to_return)

    # plot
    plt.plot(orignal)
    plt.plot(reconstrcuted)
    plt.legend(('original', 'decompressed'))
    plt.title('Compressed vs decompressed block_size {0}'.format(i))
    plt.show()

    plt.plot(coefs)
    plt.title('coeficient. count={0}'.format(len(coefs)))
    plt.show()
    return dict_to_return


def calc_stats(coefs, orignal, reconstrcuted):
    if type(coefs[0]) == float or type(coefs[0]) == int:
        dict_to_return = {
            "block_size:": len(orignal),
            "num of zeros in coefs": np.size((np.where(coefs == 0))),
            "loss norm2": np.linalg.norm(reconstrcuted - orignal),
            "loss factor": ((np.std(reconstrcuted) - np.std(orignal)) / np.std(orignal))*100,
            "compression gain": float(len(orignal)) / (len(orignal) - np.size((np.where(coefs == 0))))
        }
    else:
        compressed_length = np.sum([len(x[0]) for x in coefs[0]])
        dict_to_return = {
            "block_size:": len(orignal),
            "percentage of zeros in coefs": np.mean([(float(x['NumZeros']) / len(x['coefs'])) for x in coefs[1]]) * 100,
            #"num of zeros in coefs": np.mean([(float(x['NumZeros'])) for x in coefs[1]]) * 100,
            "loss norm2": np.linalg.norm(reconstrcuted - orignal),
            "loss factor": ((np.std(reconstrcuted) - np.std(orignal)) / np.std(orignal))*100,
            "compression gain": len(np.array(orignal).tobytes()) / compressed_length
        }
    return dict_to_return


def Sens_Evaluate(data, sc, threshold_idx):
    compressed = sc.sliding_compress(data, threshold_value_idx=threshold_idx,opt_block_size=True,isQuasi=False)
    decompressed_data = sc.decompress(compressed[0])
    return calc_stats(compressed, data, decompressed_data)


def Sens_Test_params():

    company_path_csv = join(getcwd(), r'..\\..\\Data\\ecg_temp.csv')
    data_np = np.array(pd.read_csv(company_path_csv)['0'])
    results = {}
    for i in range(500,502):
        for j in range(i-20,i):
            sc = adp_cheb.SensCompr(i)
            data = list(data_np)[:(int(len(data_np) / i) * i)]
            temp = Sens_Evaluate(data, sc, j)
            results[(i, j)] = temp
            # if distance <50000 and compression_ratio > 3:# and numZeros <100:
            #     results[(i, j)] = (compression_ratio, distance,distance_std, numZeros, numZeros_before)
        if i % 20 == 0:
            print ("itereation: ", i)
    # Print out results.

    for blockSize, ThresholdValue in sorted(results):
        block_size,numZeros, loss_norm2,distance_std, CR = results[(blockSize,ThresholdValue)].values()
        print('CR {0} loss: {1},loss_std: {2} numZeros {3}  blockSize: {4} ThresholdIDX: {5}'.format(
            CR, loss_norm2,distance_std,numZeros , blockSize, ThresholdValue))

def Sens_Test_Automatic(path = ""):

    if path == "":
        company_path_csv = join(getcwd(), r'..\\..\\Data\\data.csv')
    else:
        company_path_csv = path

    data_np = np.array(pd.read_csv(company_path_csv)['0'])
    print ("length of data", len(data_np))
    # results = {}
    sc = adp_cheb.SensCompr(512)
    temp = Sens_Evaluate(data_np, sc, -1)
    print (temp)

def coef_compress_test():
    data = np.array([0,0,0,0])
    compressed = compress_coefs(data)
    coefs=decompress_coefs(compressed)
    print(coefs)
    print(data)
    if np.array_equal(data, coefs):
        print ('yes!')


if __name__ == "__main__":
    # Sens_Test_params()
    Sens_Test_Automatic()