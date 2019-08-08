import numpy as np
import pandas as pd
import Lempel_Ziv
import scipy.fftpack as fft


def coefs_compress(coefs):
    # represent the compressed data https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20080009460.pdf
    ctrl = 0
    coefs_noZeros = np.array([])
    for coef in coefs:
        if coef:
            ctrl = (ctrl << 1) | 1  # mark existence of coef
            coefs_noZeros = np.append(coefs_noZeros, coef)
        else:
            ctrl = (ctrl << 1)  # mark no existence of coef

    temp = np.append(coefs_noZeros, len(coefs))
    data = temp.tobytes()
    compressed_data = (Lempel_Ziv.compress(data))
    return compressed_data, ctrl


def decompress_coefs(compressed_data):
    decompressed = np.frombuffer(Lempel_Ziv.decompress(compressed_data[0]), dtype='float')

    ctrl = compressed_data[1]  # int(decompressed[-2])
    block_size = int(decompressed[-1])
    coefs = np.zeros(block_size)
    idx_decompressed = len(decompressed)-2  # -3 cuz we don't count the ctrl and then all coefs are located
    idx_coefs = 0  # -3 cuz we don't count the ctrl and then all coefs are located
    # TODO - turn it to for loop!!
    while ctrl:
        ctrl_bit = ctrl & 1
        if ctrl_bit: # coef exist
            coefs[idx_coefs] = decompressed[idx_decompressed]
            idx_decompressed -= 1
        else:
            coefs[idx_coefs] = 0
        idx_coefs += 1
        ctrl = ctrl >> 1

    return np.flip(coefs)


def block_compress(sample):
    coefs = fft.dct(sample, norm='ortho')
    return coefs, len(sample)


def block_decompress(coefs):
    sample = fft.idct(coefs, norm='ortho')
    return sample


if __name__ == '__main__':
    data = pd.read_csv('../../ecg_temp.csv',header=None)[1]
    coefs,sample_size= block_compress(data,len(data)+40)
    recovered = block_decompress(coefs, sample_size)
    print (np.linalg.norm(recovered-data))


