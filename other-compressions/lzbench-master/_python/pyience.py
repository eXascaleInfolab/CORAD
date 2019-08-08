#!/bin/env/python

"""utility functions for running experiments"""

from __future__ import print_function

import datetime
import os
import itertools
# import warnings
import numpy as np
import pandas as pd
import sys

import sklearn

try:
    from joblib import Memory
    memory = Memory('.', verbose=0)
    cache = memory.cache
except Exception:
    def cache(f):
        return f

# ================================================================ Constants

KEY_FINISHED_UPDATING = '__pyn_finished_updating__'
KEY_NEW_KEYS = '__pyn_newkeys__'


# ================================================================ Types

class UsageError(Exception):
    pass


class Options(object):
    """Wrapper for a collection to signify that each element is one possible
    parameter value"""

    def __init__(self, *args):
        if args is None or len(args) < 1:
            raise ValueError("No options given!")

        if len(args) == 1 and hasattr(args, '__len__'):
            self.values = args[0]  # given a list
        else:
            self.values = args  # given individual objects

    def __len__(self):
        return len(self.values)

    # deliberately don't act like a collection so that we fail fast if
    # code doesn't know that this is supposed to represent Options, rather
    # than a collection of values. This is mostly to ensure that Options
    # are always expanded out when generating sets of parameters.
    def __getitem__(self, idx):
        self._raise()

    def __setitem__(self, idx, item):
        self._raise()

    def _raise(self):
        raise TypeError("Options object is not a collection; use options.values"
                        " to access the collection of individual options")


# ================================================================ Funcs

# ------------------------------------------------ misc utils

def ensure_list_or_tuple(x):
    if not isinstance(x, (list, tuple)):
        return [x]
    return x


def make_immutable(x):
    """
    >>> make_immutable(5) == 5
    True
    >>> make_immutable('a') == 'a'
    True
    >>> make_immutable((1, 2)) == (1, 2)
    True
    >>> make_immutable([1, 2]) == [1, 2]
    False
    """
    # must either be not a collections or immutable
    try:
        {}[x] = 0   # dicts require immutability
        return x
    except TypeError:
        # so it's mutable; either a collection or a
        # mutable class; if a class, we're hosed, so
        # assume it's a collection
        try:
            # if it's a singleton collection, try returning
            # first element; this will jump to except
            # unless x is a collection
            if len(x) == 1:
                return make_immutable(x[0])

            # not a singleton collection, but still a collection,
            # so make it a tuple
            return tuple(x)
        except TypeError:
            return x    # not a collection


def as_key(x):
    return make_immutable(x)


# ------------------------------------------------ IO / saving results

def now_as_string():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H_%M_%S")


def ensure_dir_exists(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def save_data_frame(df, save_dir, name=None, timestamp=False):
    ensure_dir_exists(save_dir)
    timestamp_str = ("_" + now_as_string()) if timestamp else ""
    name = name if name else ""
    fileName = "{}{}.csv".format(name, timestamp_str)
    df = df.sort_index(axis=1)
    df.to_csv(os.path.join(save_dir, fileName), index=False)


def save_dicts_as_data_frame(d, save_dir, name=None, timestamp=False):
    if not isinstance(d, dict):
        try:
            df = pd.DataFrame.from_records(d)
        except Exception:
            dfs = [pd.DataFrame.from_records(dd, index=[0]) for dd in d]
            df = pd.concat(dfs, axis=0, ignore_index=True)
    else:
        df = pd.DataFrame.from_records(d, index=[0])
    save_data_frame(df, save_dir, name=name, timestamp=timestamp)


def generate_save_path(params, savedir, subdir_keys=None):
    # create nested subdirectories with names specified by
    # the values for the keys in subdir_keys
    if subdir_keys is not None:
        subdir_keys = list(subdir_keys)
        subdir_names = ["{}={}".format(str(key), str(params[key]))
                        for key in subdir_keys]
        savedir = os.path.join(savedir, *subdir_names)

    return savedir


# ------------------------------------------------ cross validation

def stratified_split_train_test(X, Y, train_frac=.8):
    """Returns X_train, X_test, y_train, y_test"""
    return sklearn.model_selection.train_test_split(
        X, Y, train_size=train_frac, stratify=Y)


def split_train_test(X, Y, train_frac=.8):
    """Returns X_train, X_test, y_train, y_test"""
    return sklearn.model_selection.train_test_split(
        X, Y, train_size=train_frac)

    # n_folds = int(train_frac / (2. - train_frac))
    # split = StratifiedKFold(Y, n_folds=n_folds, random_state=12345)
    # train_index, test_index = next(iter(split))
    # X, Xtest = X[train_index], X[test_index]
    # Y, Ytest = Y[train_index], Y[test_index]
    # return X, Xtest, Y, Ytest


# ------------------------------------------------ Command line

def _split_kv_arg(arg):
    key, val = arg.split('=')
    return key.strip('-'), val


def _is_kv_arg(arg):
    return len(arg.split('=')) == 2


def _clean_flag_arg(arg):
    return arg.strip('-')


def _is_flag_arg(arg):
    return arg[0] == '-'


def _to_appropriate_type(s):
    """convert string `s` to an int, bool, or float, as appropriate. Returns
    the original string if it does not appear to be any of these types."""

    if "," in s:
        return [_to_appropriate_type(tok) for tok in s.split(',')]

    if s == 'True' or s == 'T':
        return True
    elif s == 'False' or s == 'F':
        return False
    elif s == 'None':
        return None
    try:
        return int(s)
    except Exception:
        pass
    try:
        return float(s)
    except Exception:
        pass
    return s


def parse_cmd_line(argv=None, positional_keys=None, allow_flags=True,
                   infer_types=True):
    """Parses the list of command line arguments into a dictionary of
    key-value pairs

    Parameters
    ----------
    argv : iterable of strings
        This should be sys.argv if supplied. Otherwise, sys.argv is read.

    positional_keys : iterable of strings, optional
        If k strings are specified, the up to the first k arguments will
        be treated as values to be paired with these keys. Arguments of the
        form foo=bar will never be treated this way.

    allow_flags : bool, optional
        If True, allows arguments of the form --myArg. When passed, this will
        add {'myArg': True} to the returned dictionary. This is equivalent to
        myArg=True

    infer_types : bool, optional
        If True, attempts to infer the type of each value in the returned
        dictionary. E.g., instead of returning {'height': '72'}, it will
        return {'height': 72}.

    Returns
    -------
    argKV : dict: string -> inferred type or string
        A dictionary whose keys and values are specified by the command line
        arguments

    >>> # ------------------------ positional args only
    >>> argv = ['pyience.py', 'fooVal', 'barVal']
    >>> d = parse_cmd_line(argv, positional_keys=['fooKey', 'barKey'])
    >>> len(d)
    2
    >>> d['fooKey']
    'fooVal'
    >>> d['barKey']
    'barVal'
    >>> # ------------------------ key-value args
    >>> argv = ['pyience.py', 'fooVal', 'bletchKey=bletchVal', 'blahKey=blahVal']
    >>> d = parse_cmd_line(argv, positional_keys=['fooKey', 'barKey'])
    >>> len(d)
    3
    >>> d['fooKey']
    'fooVal'
    >>> d.get('barKey', 'notHere')
    'notHere'
    >>> d['bletchKey']
    'bletchVal'
    >>> d['blahKey']
    'blahVal'
    >>> # ------------------------ flags
    >>> argv = ['pyience.py', 'fooVal', 'bletchKey=bletchVal', '--myFlag']
    >>> d = parse_cmd_line(argv, positional_keys=['fooKey', 'barKey'])
    >>> d['myFlag']
    True
    >>> # ------------------------ type inference
    >>> argv = ['pyience.py', '--myFlag', 'foo=1.1', 'bar=7', 'baz=T']
    >>> d = parse_cmd_line(argv, positional_keys=['fooKey', 'barKey'])
    >>> len(d)
    4
    >>> d['myFlag']
    True
    >>> d['foo']
    1.1
    >>> d['bar']
    7
    >>> d['baz']
    True
    >>> # ------------------------ no positional args
    >>> d = parse_cmd_line(argv)
    >>> len(d)
    4
    >>> d['myFlag']
    True
    >>> d['foo']
    1.1
    """

    if argv is None:
        argv = sys.argv

    args = argv[1:]  # ignore file name

    num_positional_keys = 0
    if positional_keys is not None and len(positional_keys):
        num_positional_keys = len(positional_keys)

    # validate input; keyword arguments must come after positional
    # arguments, and there must be no more positional arguments than
    # we have keys to associate with them
    kwargs_started = False
    flags_started = False
    for i, arg in enumerate(args):
        if _is_kv_arg(arg):  # it's a keyword argument
            kwargs_started = True
        elif _is_flag_arg(arg):
            flags_started = True
        else:  # it's not a keyword argument
            if kwargs_started:
                raise UsageError("key=value arguments must come after"
                                 "positional arguments!")

            if flags_started:
                raise UsageError("flag (e.g., --myFlag) arguments must come"
                                 "after positional arguments!")

            arg_num = i + 1
            if arg_num > num_positional_keys:
                raise UsageError("only expecting "
                                 "{} positional arguments!".format(
                                    num_positional_keys))

    argKV = {}
    for i, arg in enumerate(args):
        if _is_kv_arg(arg):
            key, val = _split_kv_arg(arg)
            argKV[key] = val
        elif _is_flag_arg(arg):
            key = _clean_flag_arg(arg)
            argKV[key] = 'True'  # string so that all vals are strings
        elif i < num_positional_keys:
            key = positional_keys[i]
            argKV[key] = arg
        else:
            raise UsageError("couldn't parse argument '{}'".format(arg))

    if infer_types:
        for k, v in argKV.items():
            argKV[k] = _to_appropriate_type(v)

    return argKV


# ------------------------------------------------ parameter generation

def expand_params(params):
    """dict of kv pairs -> list of dicts with one option selected for
    each key whose value is an instance of Options."""

    # keys with values that are Options; try all combos of these
    options_keys = [key for key in params if isinstance(params[key], Options)]
    options_keys = sorted(options_keys)  # sort for reproducibility
    options_vals = [params[key].values for key in options_keys]

    # keys with values that aren't Options; these are the same every time
    no_options_keys = [key for key in params if not isinstance(params[key], Options)]
    no_options_vals = [params[key] for key in no_options_keys]
    no_options_params = dict(zip(no_options_keys, no_options_vals))

    # make a list of all possible combos of values for each key with Options
    expanded_params_list = []
    for v in itertools.product(*options_vals):
        expanded_params = dict(zip(options_keys, v))  # pick one option for each
        expanded_params.update(no_options_params)  # add in fixed params
        expanded_params_list.append(expanded_params)

    return expanded_params_list


def update_func_from_dict(d):
    def f(params, new_keys):
        for k, v in d.items():
            if k in new_keys:
                for kk, vv in v.items():
                    params.setdefault(kk, vv)
    return f


def generate_params_combinations(params_list, update_func):
    """Uses update_func to update each dict based on its values (e.g., to
    add SVM kernel params if it contains "classifier": "SVM")"""
    if not isinstance(params_list, (list, set, frozenset, tuple)):
        params_list = [params_list]

    for params in params_list:
        params[KEY_NEW_KEYS] = set(params.keys())

    if isinstance(update_func, dict):
        update_func = update_func_from_dict(update_func)

    while True:
        new_list = []
        for params in params_list:
            expanded = expand_params(params)
            new_list += expanded

        if not update_func:
            params_list = new_list
            break

        allFinished = True
        for params in new_list:
            # if these params aren't fully updated, update them; keep
            # track of which keys are added along the way so we can
            # pass this set to the update function next time
            if not params.get(KEY_FINISHED_UPDATING, False):
                # read which keys were added last time and which keys
                # are currently present
                new_keys = params[KEY_NEW_KEYS]
                existing_keys = frozenset(params.keys())
                params.pop(KEY_NEW_KEYS)

                unfinished = update_func(params, new_keys)

                # compute and store which keys were added this time
                new_keys = frozenset(params.keys()) - existing_keys
                params[KEY_NEW_KEYS] = new_keys

                if unfinished:
                    allFinished = False
                params[KEY_FINISHED_UPDATING] = not unfinished

        params_list = new_list

        if allFinished:
            break

    for p in params_list:
        p.pop(KEY_FINISHED_UPDATING)
        p.pop(KEY_NEW_KEYS)

    return params_list


# ================================================================ Main

def update(params, new_keys):
    if 'classifier' in new_keys:
        params['kernel'] = Options('rbf', 'linear')

    # we use setdefault here so that we don't overwrite values
    # passed in at the top level
    if 'kernel' in new_keys:
        kernel = params['kernel']
        params.setdefault('C', Options(10. ** np.arange(-5, 3)))
        if kernel == 'rbf':
            params.setdefault('gamma', Options([1, 10]))

    return True if new_keys else False


def main():
    cVals = 10. ** np.arange(-3, 3)
    d = {"classifier": "SVM", 'C': Options(cVals)}
    # generate_params_combinations(d, update)
    combos = generate_params_combinations(d, update)

    # add a fake outcome variable
    for combo in combos:
        combo['runtime'] = np.random.rand() * 10

    # print out a dataframe so we can see that this worked
    import pandas as pd
    print(pd.DataFrame.from_records(combos))  # woot; it worked


if __name__ == '__main__':
    from doctest import testmod
    testmod()

    main()
