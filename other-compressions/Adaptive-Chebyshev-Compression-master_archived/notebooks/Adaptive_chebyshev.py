from scipy.stats import kurtosis, kstest, wasserstein_distance, entropy
import numpy as np
import pandas as pd
from math import ceil
from PyAstronomy import pyasl
import sys

import Lempel_Ziv
import chebyshev_compression as cheb


def compress_coefs(coefs):
    # represent the compressed data https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20080009460.pdf
    ctrl = 0
    coefs_noZeros = np.array([])
    for coef in coefs:
        if coef:
            ctrl = (ctrl << 1) | 1  # mark existence of coef
            coefs_noZeros = np.append(coefs_noZeros , coef)
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


def hampel(vals_orig, t0=3):
    '''
    vals: pandas series of values from which to remove outliers
    k: size of window (including the sample; 7 is equal to 3 on either side of value)
    '''
    # Make copy so original not edited
    vals_orig = pd.DataFrame(vals_orig)
    vals=vals_orig.copy()
    # Hampel Filter
    L = 1.4826
    #rolling_median = vals.rolling(k).median() # don't need the rolling median cuz I've already create a window
    rolling_median = vals.median()
    difference = np.abs(rolling_median-vals)
    #median_abs_deviation=difference.rolling(k).median() # again no need for rolling
    median_abs_deviation = difference.median()
    threshold = t0 *L * median_abs_deviation
    outlier_idx = np.where(difference > threshold,1,0)
    vals = np.sum(outlier_idx)
    outlier_idx = list(np.where(outlier_idx==1)[0])
    return (vals,outlier_idx)


def outlier_detector(data):

    if kurtosis(data, fisher=False) < 3:  # minimize masking effective
        vals, val_idx = hampel(data)
        to_return = (vals, val_idx)

    else:  # k >3 # minimize swamping effect
        # apply Rosner filter for outlier detection based on (Extreme Studentized Deviate) ESD test
        r = pyasl.generalizedESD(data, maxOLs=10, alpha=0.05, fullOutput=True)  # ptasl.pointDistGESD(data,5)
        vals = r[0]
        val_idx = r[1]
        to_return = (vals, val_idx)

    return to_return


def outlier_detector_quasi(data, n=10):
    best_so_far_loc = np.array([])
    best_so_far_arr = np.array([])
    best_so_far = -1
    for idx, p in enumerate(data[:len(data)-n]):
        nearest_neighbor_dist = sys.maxsize
        for inner_idx, q in enumerate(data[:len(data)-n]):
            if np.abs(idx-inner_idx) > n:
                p_s = (data[idx:idx + n] - np.mean(data[idx:idx + n]))/np.std(data[idx:idx + n])
                q_s = (data[inner_idx:inner_idx + n] - np.mean(data[inner_idx:inner_idx + n]))/np.std(data[inner_idx:inner_idx + n]) #  q[idx:idx + n]
                if np.linalg.norm(p_s-q_s) < nearest_neighbor_dist:
                    nearest_neighbor_dist = np.linalg.norm(p_s-q_s)
        if nearest_neighbor_dist > best_so_far:
            best_so_far = nearest_neighbor_dist
            best_so_far_arr = np.append(nearest_neighbor_dist, best_so_far_arr)
            best_so_far_loc = np.append(idx, best_so_far_loc)
    return len(best_so_far_arr), best_so_far_loc.astype(int)


def entropy_custom(labels, base=None):
    _, counts = np.unique(labels, return_counts=True)
    return entropy(counts, base=base)


class ImportanceScore:
    def __init__(self, KS_alpha='0.05'):
        self.KS_alpha = float(KS_alpha)

    def derive_sensor_score(self, sample, isQuasi):
        # 2. find the importance score based on B_0
        if isQuasi:
            vals, out_list = outlier_detector_quasi(sample, 15)
        else:
            vals, out_list = outlier_detector(sample)

        values, histogram_sample = np.unique(sample, return_counts=True)
        values, histogram_outliers = np.unique(out_list, return_counts=True)
        raw_m = entropy(histogram_outliers)/entropy(histogram_sample)
        _, raw_s = kstest(histogram_sample/np.sum(histogram_sample), 'norm')
        if raw_s > self.KS_alpha or len(histogram_outliers) == 0:
            raw_s = 1
        else:
            raw_s = wasserstein_distance(histogram_sample/np.sum(histogram_sample),histogram_outliers/np.sum(histogram_outliers))
            #raw_s = wasserstein_distance(sample, out_list)

        raw_Q = 1+(raw_m * raw_s) * 5
        if raw_Q<1 or raw_Q>5:
            print('on no! range is not [1,5]', raw_Q, raw_m, raw_s)
        return raw_Q


class SensCompr:
    def __init__(self,block_Size):
        self.block_size_init = block_Size
        self.prev_importance_score = -1
        # self.threshold = 3
        self.cal_importance = ImportanceScore()
        self.PHI_MAX = 5

    def update_block_size(self, sample, l_index, block_size,isQuasi=False):

        curr_max_importance = self.cal_importance.derive_sensor_score(sample[l_index:l_index+block_size],isQuasi)
        if np.abs(curr_max_importance - self.prev_importance_score) > float('0.1'):
            # print (np.abs(curr_max_importance - self.prev_importance_score))
            self.prev_importance_score = curr_max_importance
            return self.update_block_size(sample, l_index,2 * block_size)
        else:
            self.prev_importance_score = 0
            #print (curr_max_importance)
            return l_index + block_size, curr_max_importance

    def sliding_compress(self, X, opt_block_size=False, threshold_value_idx=-1, isQuasi = False):
        coef_to_return = []
        compressed_to_return = []
        curr_score = 0

        i = 0
        l_index = i * self.block_size_init
        h_index = ((i + 1) * self.block_size_init) if (i + 1) * self.block_size_init < len(X) else len(X)
        while l_index < len(X) + 1:
            if l_index == h_index:
                break
            sample = X[l_index:h_index]
            block_size = h_index - l_index

            if opt_block_size:
                h_index, curr_score = self.update_block_size(X, l_index, self.block_size_init,isQuasi)
                print ("window bounderies:",l_index,h_index)
                sample = X[l_index:h_index]
                block_size = len(sample)

            # 1. calc c for B_0
            fano_factor = np.var(sample) / np.mean(sample)
            c = ceil(fano_factor)

            # 3. optimal Threshold
            Threshold_O = c * (2 ** (self.PHI_MAX - curr_score))

            # 4. perform Chebyshev transform
            coefs, sample_size = cheb.block_compress(sample)
            numZeros_before = np.size((np.where(coefs == 0)))
            if threshold_value_idx > -1:
                threshold = sorted(np.abs(coefs))[threshold_value_idx]
            else:
                threshold = Threshold_O
            coefs = np.where(np.abs(coefs) > threshold, coefs, 0)
            numZeros = np.size((np.where(coefs == 0)))

            coef_to_return.append({'coefs': coefs, 'block_size': block_size,'Thers': threshold_value_idx, 'NumZeros': numZeros, 'NumZeros_before': numZeros_before})
            compressed_to_return.append(compress_coefs(coefs))

            i += 1
            l_index = h_index
            h_index = (h_index + block_size) if (h_index + block_size) < len(X) else len(X)
        return compressed_to_return, coef_to_return

    def decompress(self,compressed):
        decompressed_full = np.array([])
        for idx, data_block in enumerate(compressed):
            coefs = decompress_coefs(data_block)
            reconstructed = cheb.block_decompress(coefs)
            decompressed_full = np.concatenate((decompressed_full, reconstructed ))
        return decompressed_full


