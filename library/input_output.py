import pandas as pd
import os

def save_object(obj, filename):
    try:
        import cPickle as pickle
    except ModuleNotFoundError:
        import pickle

    # dirname = os.path.dirname(filename)
    # if not os.path.exists(dirname):
    #     os.makedirs(dirname)
    
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(obj, output, pickle.HIGHEST_PROTOCOL)


def load_object(filename):
    try:
        import cPickle as pickle
    except ModuleNotFoundError:
        import pickle
    with open(filename, 'rb') as input:  # Overwrites any existing file.
        obj = pickle.load(input)
        return obj



def read_time_series(fname):
    headers = ['col0', 'col1', 'col2', 'col3', 't1', 't2', 't3']
    parse_dates = [['col1', 'col2', 'col3']]

    data = pd.read_csv(fname, sep=" ", header=None, parse_dates=parse_dates,
                       names=headers)

    data = data.iloc[:, [0, 2, 3, 4]]
    data = data.rename(index=str, columns={"col1_col2_col3": "date"})

    return data



def read_multiple_ts(fname, first_column, last_column):

    data = pd.read_csv(fname, header=0)
    data = data.iloc[:, first_column:last_column]
    # print(data)

    # ts = read_time_series('Datasets/SURF_CLI_CHN_MUL_DAY-TEM_50468-1960-2012-short.txt')
    # tricklets = getTrickletsTS(ts, 2)
    # tricklets1 = tricklets[0]

    return data
