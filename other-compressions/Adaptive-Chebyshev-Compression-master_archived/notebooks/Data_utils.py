import numpy as np
SAMPLE_SIZE = 127


def split_data(data_arr, window_size = SAMPLE_SIZE):
    num_blocks = len(data_arr) // window_size
    throw = (len(data_arr) % window_size)
    X = np.array(np.split(data_arr[0:-throw], num_blocks))

    # print ("Trowed {0} samples".format(throw))
    # print ("Ttal blocks {0} samples, and actually {1}".format(num_blocks,len(X)))
    return X
