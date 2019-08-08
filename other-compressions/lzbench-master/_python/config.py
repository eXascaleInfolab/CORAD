#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import matplotlib.pyplot as plt
import matplotlib as mpl

from . import files

# change this if you aren't me
DATASETS_DIR = os.path.expanduser('~/Desktop/datasets/compress')

FIG_SAVE_DIR = 'figs'
RESULTS_SAVE_DIR = 'results'


def _results_path(*args):
    return os.path.join(RESULTS_SAVE_DIR, *args)


RESULTS_BACKUP_DIR          = _results_path('backups')  # noqa
ALL_RESULTS_PATH            = _results_path('all_results.csv') # noqa
UCR_RESULTS_PATH            = _results_path('ucr', 'ucr_results.csv') # noqa
UCR_MEMLIMIT_RESULTS_PATH   = _results_path('ucr_memlimit', 'ucr_memlimit_results.csv') # noqa
MULTIDIM_RESULTS_PATH       = _results_path('multidim_results', 'multidim_results.csv') # noqa
NDIMS_SPEED_RESULTS_PATH    = _results_path('ndims_speed', 'ndims_speed_results.csv') # noqa
PREPROC_SPEED_RESULTS_PATH  = _results_path('preproc_speed', 'preproc_speed_results.csv') # noqa
PREPROC_UCR_RESULTS_PATH    = _results_path('preproc_ucr', 'preproc_ucr_results.csv') # noqa
MULTICORE_RESULTS_PATH      = _results_path('multicore', 'multicore_queries.csv') # noqa

files.ensure_dir_exists(RESULTS_BACKUP_DIR)
files.ensure_dir_exists(os.path.dirname(ALL_RESULTS_PATH))
files.ensure_dir_exists(os.path.dirname(UCR_RESULTS_PATH))
files.ensure_dir_exists(os.path.dirname(UCR_MEMLIMIT_RESULTS_PATH))
files.ensure_dir_exists(os.path.dirname(NDIMS_SPEED_RESULTS_PATH))
files.ensure_dir_exists(os.path.dirname(MULTIDIM_RESULTS_PATH))
files.ensure_dir_exists(os.path.dirname(NDIMS_SPEED_RESULTS_PATH))
files.ensure_dir_exists(os.path.dirname(PREPROC_SPEED_RESULTS_PATH))
files.ensure_dir_exists(os.path.dirname(PREPROC_UCR_RESULTS_PATH))
files.ensure_dir_exists(os.path.dirname(MULTICORE_RESULTS_PATH))

SYNTH_LOW_COMPRESSION_RATIO = 1
SYNTH_HIGH_COMPRESSION_RATIO = 8
SYNTH_DATASETS_DIR = os.path.join(DATASETS_DIR, 'synthetic')
SYNTH_100M_U8_LOW_PATH = os.path.join(SYNTH_DATASETS_DIR,
    'synth_100M_u8_ratio={}.dat'.format(SYNTH_LOW_COMPRESSION_RATIO))    # noqa
SYNTH_100M_U16_LOW_PATH = os.path.join(SYNTH_DATASETS_DIR,
    'synth_100M_u16_ratio={}.dat'.format(SYNTH_LOW_COMPRESSION_RATIO))   # noqa
SYNTH_100M_U8_HIGH_PATH = os.path.join(SYNTH_DATASETS_DIR,
    'synth_100M_u8_ratio={}.dat'.format(SYNTH_HIGH_COMPRESSION_RATIO))   # noqa
SYNTH_100M_U16_HIGH_PATH = os.path.join(SYNTH_DATASETS_DIR,
    'synth_100M_u16_ratio={}.dat'.format(SYNTH_HIGH_COMPRESSION_RATIO))  # noqa

# DEFAULT_LEVELS = [1, 5, 9]  # many compressors have levels 1-9
DEFAULT_LEVELS = [1, 9]  # many compressors have levels 1-9

CAMERA_READY_FONT = 'DejaVu Sans'


class Queries:  # needs to match cpp query enum
    NONE = 0
    MAX = 1
    SUM = 2
    ALL_QUERIES = [NONE, MAX, SUM]


def query_name(query_id):
    return {
        Queries.NONE: "None",
        Queries.MEAN: "Mean",
        Queries.MAX: "Max",
        Queries.MIN: "Min",
        Queries.SUM: "Sum"
        }[query_id]


class StorageOrder:  # needs to match cpp enum
    ROWMAJOR = 0
    COLMAJOR = 1


def id_for_order(order_char):
    return {'c': StorageOrder.ROWMAJOR, 'f': StorageOrder.COLMAJOR}[
        order_char.lower()]


class Preproc:
    NONE = 'None'
    DELTA = 'Delta'
    DBL_DELTA = 'DoubleDelta'
    FIRE = 'FIRE'
    ALL = 'ALL_PREPROCS'


ALL_PREPROCS = (Preproc.NONE, Preproc.DELTA, Preproc.DBL_DELTA, Preproc.FIRE)


def cmd_line_arg_for_preproc(preproc, ndims=1):
    return {Preproc.DELTA: '-d{}'.format(ndims),
            Preproc.DBL_DELTA: '-D{}'.format(ndims),
            Preproc.FIRE: '-f{}'.format(ndims),
            Preproc.NONE: ''}[preproc]


class AlgoInfo(object):

    def __init__(self, lzbench_name, levels=None, allowed_preprocs=Preproc.ALL,
                 allowed_nbits=[8, 16], needs_32b=False, group=None,
                 allowed_orders=['f'], needs_ndims=False):
        self.lzbench_name = lzbench_name
        self.levels = levels
        self.allowed_nbits = allowed_nbits
        self.needs_32b = needs_32b
        self.group = group
        self.allowed_orders = allowed_orders
        self.needs_ndims = needs_ndims

        if allowed_preprocs == Preproc.ALL:
            self.allowed_preprocs = ALL_PREPROCS[:]
        elif allowed_preprocs:
            self.allowed_preprocs = allowed_preprocs
        else:
            self.allowed_preprocs = Preproc.NONE


class DsetInfo(object):

    def __init__(self, pretty_name, bench_name, ndims):
        self.pretty_name = pretty_name
        self.bench_name = bench_name
        self.ndims = ndims


ALL_DSETS = [
    DsetInfo('AMPD Gas', 'ampd_gas', 3),
    DsetInfo('AMPD Water', 'ampd_water', 2),
    DsetInfo('AMPD Power', 'ampd_power', 23),
    DsetInfo('AMPD Weather', 'ampd_weather', 7),
    DsetInfo('MSRC-12', 'msrc', 80),
    DsetInfo('MSRC-Split', 'msrc_split', 80),
    DsetInfo('PAMAP', 'pamap', 31),
    DsetInfo('UCI Gas', 'uci_gas', 18),
    DsetInfo('UCR', 'ucr', 1)
]
NAME_2_DSET = {ds.bench_name: ds for ds in ALL_DSETS}
PRETTY_DSET_NAMES = {ds.bench_name: ds.pretty_name for ds in ALL_DSETS}

SUCCESS_DSETS = 'msrc pamap uci_gas'.split()
FAILURE_DSETS = ['ampd_gas', 'ampd_water', 'ampd_power']
USE_WHICH_MULTIDIM_DSETS = SUCCESS_DSETS + FAILURE_DSETS

# for i in range(81):
#     NAME_2_DSET

# PRETTY_DSET_NAMES = {
#     'ucr':          'UCR',
#     'ampd_gas':     'AMPD Gas',
#     'ampd_water':   'AMPD Water',
#     'ampd_power':   'AMPD Power',
#     'ampd_weather': 'AMPD Weather',
#     'uci_gas':      'UCI Gas',
#     'pamap':        'PAMAP',
#     'msrc':         'MSRC-12',
# }


# def _sprintz_algo_info(name, nbits=8, **kwargs):
def _sprintz_algo_info(name, nbits=8):
    # kwargs.set_default('allowed_orders', 'c')
    return AlgoInfo(name, allowed_preprocs=None, allowed_nbits=[nbits],
                    allowed_orders=['c'], group='Sprintz', needs_ndims=True)
                    # group='Sprintz', needs_ndims=True, **kwargs)


ALGO_INFO = {
    'Memcpy':           AlgoInfo('memcpy'),
    # general-purpose compressors
    'Zlib':             AlgoInfo('zlib', levels=DEFAULT_LEVELS),
    'Zstd':             AlgoInfo('zstd', levels=DEFAULT_LEVELS),
    'LZ4':              AlgoInfo('lz4'),
    'Huffman':          AlgoInfo('huff0'),
    'Snappy':           AlgoInfo('snappy'),
    'LZ4HC':            AlgoInfo('lz4hc', levels=DEFAULT_LEVELS),
    'LZO':              AlgoInfo('lzo1x', levels=DEFAULT_LEVELS),
    'Simple8B':         AlgoInfo('simple8b', needs_32b=True),
    'SIMDBP128':        AlgoInfo('binarypacking', needs_32b=True),
    'FastPFOR':         AlgoInfo('fastpfor', needs_32b=True),
    'SprintzDelta':     _sprintz_algo_info('sprintzDelta'),
    'SprintzXff':       _sprintz_algo_info('sprintzXff'),
    'SprintzDelta_Huf': _sprintz_algo_info('sprintzDelta_HUF'),
    'SprintzXff_Huf':   _sprintz_algo_info('sprintzXff_HUF'),
    'SprintzDelta_16b':     _sprintz_algo_info('sprintzDelta_16b', nbits=16),
    'SprintzXff_16b':       _sprintz_algo_info('sprintzXff_16b', nbits=16),
    'SprintzDelta_Huf_16b': _sprintz_algo_info('sprintzDelta_HUF_16b', nbits=16),
    'SprintzXff_Huf_16b':   _sprintz_algo_info('sprintzXff_HUF_16b', nbits=16),
    'Gipfeli':          AlgoInfo('gipfeli'),
    'Brotli':           AlgoInfo('brotli', levels=DEFAULT_LEVELS),
    'FSE':              AlgoInfo('fse'),
    'Delta':            _sprintz_algo_info('sprJustDelta', nbits=8),
    'DoubleDelta':      _sprintz_algo_info('sprJustDblDelta', nbits=8),
    'FIRE':             _sprintz_algo_info('sprJustXff', nbits=8),
    'Delta_16b':        _sprintz_algo_info('sprJustDelta_16b', nbits=16),
    'DoubleDelta_16b':  _sprintz_algo_info('sprJustDblDelta_16b', nbits=16),
    'FIRE_16b':         _sprintz_algo_info('sprJustXff_16b', nbits=16),
    'OptPFOR':          AlgoInfo('optpfor', needs_32b=True),
    'SIMDGroupSimple':  AlgoInfo('simdgroupsimple', needs_32b=True),
    'BitShuffle8b':     AlgoInfo('blosc_bitshuf8b', allowed_nbits=[8],
                                 levels=DEFAULT_LEVELS),
    'ByteShuffle8b':    AlgoInfo('blosc_byteshuf8b', allowed_nbits=[8],
                                 levels=DEFAULT_LEVELS),
    'BitShuffle16b':    AlgoInfo('blosc_bitshuf16b', allowed_nbits=[16],
                                 levels=DEFAULT_LEVELS),
    'ByteShuffle16b':   AlgoInfo('blosc_byteshuf16b', allowed_nbits=[16],
                                 levels=DEFAULT_LEVELS),
}

import matplotlib.lines as lines
ALL_SCATTER_MARKERS = [".", ",", "v", "^", "<", ">", "1", "2", "3", "4", "8",
                       "s", "p", "P", "*", "h", "H", "+", "x", "X", "D", "d",
                       "|", "_", "o", lines.TICKLEFT, lines.TICKRIGHT,
                       lines.TICKUP, lines.TICKDOWN, lines.CARETLEFT,
                       lines.CARETRIGHT, lines.CARETUP, lines.CARETDOWN,
                       lines.CARETLEFTBASE, lines.CARETRIGHTBASE,
                       lines.CARETUPBASE]
# ALL_NOT_HIDEOUS_MARKERS = ALL_SCATTER_MARKERS
# ALL_NOT_HIDEOUS_MARKERS = [".", "v", "^", "<", ">", "1", "2", "3", "4",
ALL_NOT_HIDEOUS_MARKERS = [".", ",", "v", "^", "<", ">", "1", "2", "3", "4",
                           "h", "s", "p", "*", "+", "x", "X", "D", "o"]

# associate each algorithm with a color
# cmap = plt.get_cmap('tab20')
# SPRINTZ_MARKER = '*'
SPRINTZ_MARKER = '*'
cmap = plt.get_cmap('tab10')
for i, (name, info) in enumerate(sorted(ALGO_INFO.items())):
    if info.group == 'Sprintz':
        # info.color = 'r'
        info.color = plt.get_cmap('tab20')(4 * 20. / 256)  # red
        info.marker = SPRINTZ_MARKER
        continue
        # print "set info color to red for algorithm {} (group {})".format(name, info.group)

    if i >= 6:
        i += 1  # don't let anything be red (which is color6 in tab20)
    frac = (i * (13 / 256.)) % 1.
    # frac = float(i) / len(ALGO_INFO)

    info.color = cmap(frac)
    eligible_markers = ALL_NOT_HIDEOUS_MARKERS[:]
    eligible_markers.remove(SPRINTZ_MARKER)
    info.marker = eligible_markers[i % len(eligible_markers)]

    # print("{}) frac={}; setting color {} for algo {}".format(
    #     i, frac, info.color, info.lzbench_name))


def get_algo_info(name_and_level, nbits=8):
    name = name_and_level.split()[0]

    # TODO this whole thing is a terrible hack because our figures rename
    # algos to make them pretty
    if name.lower().startswith('sprintz'):
        if name == 'Sprintz':
            level = -int(name_and_level.split()[1])
            name = {(1, 8): 'SprintzDelta',
                    (2, 8): 'SprintzXff',
                    (3, 8): 'SprintzXff_Huf',
                    (1, 16): 'SprintzDelta_16b',
                    (2, 16): 'SprintzXff_16b',
                    (3, 16): 'SprintzXff_Huf_16b'}[level, nbits]

        elif name in ('SprintzDelta', 'SprintzFIRE', 'SprintzFIRE+Huf'):
            name = {('SprintzDelta', 8): 'SprintzDelta',
                    ('SprintzDelta', 16): 'SprintzDelta_16b',
                    ('SprintzFIRE', 8): 'SprintzXff',
                    ('SprintzFIRE', 16): 'SprintzXff_16b',
                    ('SprintzFIRE+Huf', 8): 'SprintzXff_Huf',
                    ('SprintzFIRE+Huf', 16): 'SprintzXff_Huf_16b'
                    }[(name, nbits)]

            print("mapped old name and level '{}' to new name: '{}'".format(name_and_level, name))

        info = ALGO_INFO[name]

        if name in ('SprintzXff', 'SprintzXff_16b'):
            # print "using new marker!"
            new_marker = mpl.markers.MarkerStyle(SPRINTZ_MARKER, fillstyle='none')
            # new_marker = mpl.markers.MarkerStyle(SPRINTZ_MARKER, fillstyle='left')
            info.marker = new_marker
            # info.marker = '+'

        return info

    return ALGO_INFO[name]

    # return info
    # if name.lower().startswith('sprintz'):
    #     new_marker = mpl.markers.MarkerStyle(SPRINTZ_MARKER, fillstyle='none')
    #     if name == 'Sprintz':  # name already cleaned
    #         level = -int(name_and_level.split()[1])
    #         if level == 1:
    #             info = ALGO_INFO['Sprintz']
    #     try:  # name already cleaned

    #         if level == 2:
    #             info.marker = new_marker
    #         # if level == 1:
    #             # info.marker = '*'
    #         # elif level == 2:
    #             # info.marker
    #     except IndexError:
    #         if name in ('SprintzXff', 'SprintzXff_16b'):
    #             info.marker = new_marker

    #     return info

    # return ALGO_INFO[name]


BENCH_NAME_TO_PRETTY_NAME = dict([(info.lzbench_name, key)
                                 for (key, info) in ALGO_INFO.items()])

USE_WHICH_ALGOS = 'SprintzDelta SprintzXff SprintzDelta_Huf SprintzXff_Huf ' \
    'SprintzDelta_16b SprintzXff_16b SprintzDelta_Huf_16b SprintzXff_Huf_16b '\
    'SIMDBP128 FastPFOR Simple8B ' \
    'Zstd Snappy LZ4 Zlib Huffman'.split()
    # 'Zstd Snappy LZO LZ4 Zlib Huffman'.split()
SPRINTZ_ALGOS = [algo for algo in ALGO_INFO if algo.lower().startswith('sprintz')]

PREPROC_EFFECTS_ALGOS = 'Zstd Snappy LZO LZ4 Zlib Huffman'.split()


ALL_DSET_NAMES = PRETTY_DSET_NAMES.keys()

# XXX might actually want to vary Order as an independent var, but for
# now, this is a hack to not have two different memcpy results
# INDEPENDENT_VARS = 'Algorithm Dataset Memlimit Nbits Order Deltas'.split()
# INDEPENDENT_VARS = 'Algorithm Dataset Memlimit Nbits Deltas'.split()
# INDEPENDENT_VARS = 'Algorithm Dataset Memlimit Nbits Preprocs'.split()
INDEPENDENT_VARS = 'Algorithm Dataset Memlimit Nbits Preprocs Nthreads Query'.split()
DEPENDENT_VARS = ['Ratio', 'Compression speed', 'Decompression speed']
