import pandas as pd
import numpy as np
from os import listdir
from os.path import isfile,join
import Data_utils

bit_per_sample = 11  # not used
freq = 360  # samples in sec - not used
SAMPLE_SIZE = 127
default_path_company = r'..\..\Data\MIT_BIH_CSV'


def load_data(data__dir_path):
    onlyfiles = [join(data__dir_path ,f) for f in listdir(data__dir_path) if isfile(join(data__dir_path ,f))]
    data_arr = np.array([])
    for idx, file_path in enumerate(onlyfiles):
        mit_data = pd.read_csv(file_path)
        # print (mit_data.head())
        data_file = np.array(mit_data[mit_data.columns[1]])  # ['\'V5\''] another option
        data_arr = np.concatenate((data_arr, data_file))
        if idx%10==0 and idx>0:
            print((0.0+idx)/len(onlyfiles))

    return data_arr


if __name__ == '__main__':
    data = load_data(default_path_company)
    X = Data_utils.split_data(data, window_size=200)
    print(X.shape)
