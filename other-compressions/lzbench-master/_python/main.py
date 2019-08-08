#!/usr/bin/env python

# here's what we want:
#   option to do everything 8b or 16b
#   option to do rowmajor or colmajor (although only colmajor for now)
#   option to pick dataset[s] (defaults to all of them)
#   option to pick algorithm[s] (defaults to all of them)
#       -and note that all these names are some canonical form
#   option to pick memory limit in KB (defaults to no limit)
#   option to pick how many seconds of compression/decompression (-t arg)
#   for selected combo of (nbits, order, algos, dsets)
#       figure out which dset to actually use (eg, faspfor needs u32 versions)
#           -and other stuff needs deltas
#       figure out which algo to actually use
#           -eg, 'bitshuf' needs to get turned into 'blosc_bitshuf8b' or 16b
#       figure out cmd line name for selected algo
#       figure out cmd line params for selected algo based on orig name
#       figure out path for selected dset
#       figure out path for file in which to dump the df
#           -maybe just one giant df we can query later (so timestamp the versions)
#       figure out path for file in which to dump the fig(s)
#
#   code to generate scatterplots for speed vs ratio
#   code to read in our stored data and generate real plots via this func

# some queries I like: TODO put these somewhere sensible
#
# profile raw bitpacking speed
#   ./lzbench -r -asprJustBitpack/sprFixedBitpack -t0,0 -i25,25 -j synthetic/100M_randint_0_1.dat
#
# run everything and create figure for one dataset (here, uci_gas):
#   python -m _python.main --sweep algos=SprintzDelta,SprintzDelta_16b,
#       SprintzDelta_HUF,SprintzDelta_HUF_16b,Zstd,Brotli,LZ4,Huffman,
#       FastPFOR,SIMDBP128 --dsets=uci_gas --miniters=10 --create_fig

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools
import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# import seaborn as sb

import sys
from . import files
from . import pyience
from . import config as cfg

# import gflags   # google's command line lib; pip install python-gflags
# FLAGS = gflags.FLAGS

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

# gflags.DEFINE_

DEBUG = False

# hack for specifying path directly, not based on algorithm requirements
RAW_DSET_PATH_PREFIX = 'RAW_PATH:'


# ================================================================ experiments

def _clean_algorithm_name(algo_name):
    algo_name = algo_name.strip()
    # print("cleaning algo name: '{}'".format(algo_name))
    tokens = algo_name.split(' ')
    algo_name = cfg.BENCH_NAME_TO_PRETTY_NAME[tokens[0]]
    if tokens[-1][0] == '-':  # if compression level given; eg, '-5'
        algo_name += ' ' + tokens[-1]
    # print("cleaned algo name: '{}'".format(algo_name))
    return algo_name


def _df_from_string(s, **kwargs):
    # print('>>>>>>>>>>>> got df string:\n', s)
    # print('<<<<<<<<<<<<')
    return pd.read_csv(StringIO(s), **kwargs)


def _dset_path(nbits, dset, algos, order, deltas):
    algos = pyience.ensure_list_or_tuple(algos)

    if dset.startswith(RAW_DSET_PATH_PREFIX):  # hack for specifying path directly
        return dset[len(RAW_DSET_PATH_PREFIX):]

    join = os.path.join
    path = cfg.DATASETS_DIR

    # storage order
    assert order in ('c', 'f')  # rowmajor, colmajor order (C, Fortran order)
    path = join(path, 'colmajor') if order == 'f' else join(path, 'rowmajor')

    # storage format (number of bits, whether delta-encoded)
    assert nbits in (8, 16)

    # algos = _canonical_algo_names(algos)
    want_32b = np.array([cfg.ALGO_INFO[algo].needs_32b for algo in algos])
    if np.sum(want_32b) not in (0, len(algos)):
        raise ValueError('Some algorithms require 32-bit input, while '
                         'others do not; requires separate commands. Requested'
                         ' algorithms:\n'.format(', '.join(algos)))
    want_32b = np.sum(want_32b) > 0

    if deltas and want_32b:
        # also zigzag encode since fastpfor and company assume nonnegative ints
        subdir = 'uint{}-as-uint32_deltas_zigzag'.format(nbits)
    # elif deltas:
        # subdir = 'int{}_deltas'.format(nbits)
    elif want_32b:
        subdir = 'uint{}-as-uint32'.format(nbits)
    else:
        subdir = 'uint{}'.format(nbits)

    return join(path, subdir, dset)


def _generate_cmd(nbits, algos, dset_path, preprocs=None, memlimit=None,
                  miniters=1, use_u32=False, ndims=None, dset_name=None,
                  custom_levels=None, inject_str=None, min_comp_iters=0,
                  query_id=-1, nthreads=0, order=None,
                  **sink):
    algos = pyience.ensure_list_or_tuple(algos)
    inject_str = inject_str if inject_str is not None else ''

    if ndims is None:
        ndims = int(cfg.NAME_2_DSET[dset_name].ndims)

    # cmd = './lzbench -r -j -o4 -e'  # o4 is csv
    cmd = './lzbench -r -o4 -t0,0'  # o4 is csv
    cmd += inject_str
    cmd += ' -i{},{}'.format(int(min_comp_iters), int(miniters))
    # cmd += ' -i{},{}'.format(2, int(miniters))  # XXX compress full number of trials
    cmd += ' -a'
    algo_strs = []
    for algo in algos:
        algo = algo.split('-')[0]  # rm possible '-Delta' suffix
        info = cfg.ALGO_INFO[algo]
        s = info.lzbench_name
        # s = s.replace(NEEDS_NBITS, str(nbits))
        if custom_levels is None:
            if info.levels is not None:
                s += ',' + ','.join([str(lvl) for lvl in info.levels])
            if info.needs_ndims:
                s += ',{}'.format(int(ndims))
        else:
            s += ',' + ','.join([str(lvl) for lvl in custom_levels])
        algo_strs.append(s)

    cmd += '/'.join(algo_strs)
    if memlimit is not None and int(memlimit) > 0:
        cmd += ' -b{}'.format(int(memlimit))
    if preprocs is not None:
        preprocs = pyience.ensure_list_or_tuple(preprocs)
        for preproc in preprocs:
            # EDIT: this is handled by feeding it delta + zigzag
            # version of the data, which is really optimistic but lets
            # us get meaningful results since relevant algos can't
            # bitpack negative numbers at all (in provided impls)
            #
            # preproc_const = PREPROC_TO_INT[preproc.lower()]
            # if preproc_const == 1 and use_u32:
            #     # use FastPFOR vectorized delta impl instead of regular
            #     # scalar delta for FastPFOR 32b funcs
            #     preproc_const = 4
            # cmd += ' -d{}'.format(preproc_const)
            # cmd += ' -d{}'.format(cfg.PREPROC_TO_INT[preproc.lower()])

            cmd += ' ' + cfg.cmd_line_arg_for_preproc(preproc)

    # if (not use_u32):
    if (not use_u32) or (nthreads > 0):  # not sure first clause is good?
        cmd += ' -e{}'.format(int(nbits / 8))
    if query_id is not None and query_id >= 0:
        cmd += ' -q{}'.format(query_id)
        assert ndims > 0  # running query requires specifying ndims
    if nthreads > 0:
        cmd += ' -T{}'.format(nthreads)
    if order is not None:
        cmd += ' -S{}'.format(cfg.id_for_order(order))
    if ndims is not None:
        effective_ndims = int(ndims)
        if use_u32:
            effective_ndims = effective_ndims * 32 // nbits
        cmd += ' -c{}'.format(effective_ndims)

    cmd += ' {}'.format(dset_path)
    return cmd


def _run_cmd(cmd, verbose=0):
    # print("------------------------")
    # print("actually about to run it...")
    output = os.popen(cmd).read()
    # trimmed = output[output.find('\n') + 1:output.find('\ndone...')]
    # print("here's the start of the raw output: \n")
    # print output[:1000]
    # print("about to trim output...")
    trimmed = output[:output.find('\ndone...')]
    # trimmed = trimmed[:]

    if not os.path.exists('./lzbench'):
        os.system('make')

    if verbose > 1:
        # print("------------------------")
        print("raw output:\n" + output)
        print("trimmed output:\n", trimmed)

    # print("about to turn string into df")
    try:
        return _df_from_string(trimmed[:])
    except:  # noqa
        print("ERROR: couldn't parse dataframe from output: '{}'".format(output))
        sys.exit(1)


def _clean_results(results, dset, memlimit, miniters, nbits, order,
                   preprocs, nthreads, query_id):
    # print("==== results df:\n", results)
    # print results_dicts
    results_dicts = results.to_dict('records')
    for i, d in enumerate(results_dicts):
        d['Dataset'] = dset
        d['Memlimit'] = memlimit
        d['MinIters'] = miniters
        d['Nbits'] = nbits
        d['Order'] = order
        # d['Deltas'] = deltas
        d['Preprocs'] = preprocs
        d['Nthreads'] = nthreads
        d['Query'] = query_id
        d['Algorithm'] = _clean_algorithm_name(d['Compressor name'])
        # if deltas and algo != 'Memcpy':
        #     d['Algorithm'] = d['Algorithm'] + '-Delta'
        d.pop('Compressor name')
        # d['Filename'] = d['Filename'].replace(os.path.expanduser('~'), '~')
        d['Filename'] = d['Filename'].replace(
            os.path.expanduser(cfg.DATASETS_DIR), '')
        # d.pop('Filename')  # not useful because of -j
    results = pd.DataFrame.from_records(results_dicts)
    return results


def _run_experiment(nbits, algos, dsets=None, memlimit=-1, miniters=0, order='f',
                    preprocs=None, create_fig=False, verbose=1, dry_run=DEBUG,
                    save_path=None, nthreads=0, query_id=None, **cmd_kwargs):
    dsets = cfg.ALL_DSET_NAMES if dsets is None else dsets
    dsets = pyience.ensure_list_or_tuple(dsets)
    algos = pyience.ensure_list_or_tuple(algos)

    # print("using nthreads, query: ", nthreads, query_id)
    # return

    for dset in dsets:
        # if verbose > 0:
        #     print("================================ {}".format(dset))

        # don't tell dset_path about delta encoding; we'll use the benchmark's
        # preprocessing abilities for that, so that the time gets taken into
        # account
        dset_path = _dset_path(nbits=nbits, dset=dset, algos=algos,
                               order=order, deltas=False)
        # use_u32 = 'zigzag' in dset_path  # TODO this is hacky
        use_u32 = 'uint32' in dset_path  # TODO this is hacky
        # preprocs = 'delta' if (deltas and not use_u32) else None
        cmd = _generate_cmd(nbits=nbits, dset_path=dset_path, algos=algos,
                            preprocs=preprocs, memlimit=memlimit,
                            miniters=miniters, use_u32=use_u32, dset_name=dset,
                            order=order, nthreads=nthreads, query_id=query_id,
                            **cmd_kwargs)

        if verbose > 0 or dry_run:
            print('------------------------')
            print(cmd)

            if dry_run:
                print("Warning: abandoning early for debugging!")
                continue

        # print("about to run command:")
        results = _run_cmd(cmd, verbose=verbose)
        # print("...command successful")
        results = _clean_results(
            results, dset=dset, memlimit=memlimit, miniters=miniters,
            nbits=nbits, order=order, preprocs=preprocs,
            nthreads=nthreads, query_id=query_id)

        if verbose > 1:
            print("==== Results")
            print(results)

        # dump raw results with a timestamp for archival purposes
        pyience.save_data_frame(results, cfg.RESULTS_BACKUP_DIR,
                                name='results', timestamp=True)

        # add these results to master set of results, overwriting previous
        # results where relevant
        if save_path is None:
            save_path = cfg.ALL_RESULTS_PATH

        if os.path.exists(save_path):
            existing_results = pd.read_csv(save_path)
            all_results = pd.concat([existing_results, results], axis=0)
            all_results.drop_duplicates(  # add filename since not doing '-j'
                subset=(cfg.INDEPENDENT_VARS + ['Filename']), inplace=True)
        else:
            all_results = results

        all_results.to_csv(save_path, index=False)
        # print("all results ever:\n", all_results)

    if create_fig and not dry_run:
        for dset in dsets:
            fig_for_dset(dset, save=True, df=all_results, nbits=nbits)
            # fig_for_dset(dset, algos=algos, save=True, df=all_results)

    if not dry_run:
        return all_results


# ================================================================ plotting


# def _pretty_scatterplot(x, y):
#     sb.set_context('talk')
#     _, ax = plt.subplots(figsize=(7, 7))
#     ax.scatter(x, y)
#     ax.set_title('Compression Speed vs Ratio')
#     ax.set_xlabel('Compression Speed (MB/s)')
#     ax.set_ylabel('Compression Ratio')

#     plt.show()


def fig_for_dset(dset, algos=None, save=True, df=None, nbits=None,
                 exclude_algos=None, exclude_preprocs=False,
                 memlimit=-1, avg_across_files=True, order=None, **sink):

    fig, axes = plt.subplots(2, figsize=(9, 9))
    dset_name = cfg.PRETTY_DSET_NAMES[dset] if dset in cfg.PRETTY_DSET_NAMES else dset
    fig.suptitle(dset_name)

    axes[0].set_title('Compression Speed vs Ratio')
    axes[0].set_xlabel('Compression Speed (MB/s)')
    axes[0].set_ylabel('Compression Ratio')
    axes[1].set_title('Decompression Speed vs Compression Ratio')
    axes[1].set_xlabel('Decompression Speed (MB/s)')
    axes[1].set_ylabel('Compression Ratio')

    if df is None:
        df = pd.read_csv(cfg.ALL_RESULTS_PATH)
    # print("read back df")
    # print df

    df = df[df['Dataset'] == dset]

    if order is not None:
        df = df[df['Order'] == order]
    # df = df[df['Algorithm'] != 'Memcpy']

    # print("using algos before exlude deltas: ", sorted(list(df['Algorithm'])))
    # return

    if exclude_preprocs:
        # df = df[~df['Deltas']]
        df = df[df['Preprocs'].isin([cfg.Preproc.NONE])]

    # print("using algos before memlimit: ", sorted(list(df['Algorithm'])))

    if memlimit is not None:  # can use -1 for runs without a mem limit
        df = df[df['Memlimit'] == memlimit]

    if avg_across_files:
        df = df.groupby(
            cfg.INDEPENDENT_VARS, as_index=False)[cfg.DEPENDENT_VARS].mean()
        # print("means: ")
        # print df
        # return

    if nbits is not None:
        df = df[df['Nbits'] == nbits]
    else:
        raise ValueError("must specify nbits!")

    # if algos is None:
        # algos = list(df['Algorithm'])
    # else:
    if algos is not None:
        algos_set = set(pyience.ensure_list_or_tuple(algos))
        mask = [algo.split()[0] in algos_set for algo in df['Algorithm']]
        df = df[mask]

    if exclude_algos is not None:
        exclude_set = set(pyience.ensure_list_or_tuple(exclude_algos))
        # print("exclude algos set:", exclude_set)
        mask = [algo.split()[0] not in exclude_set for algo in df['Algorithm']]
        df = df[mask]

    algos = list(df['Algorithm'])
    used_preprocs = list(df['Preprocs'])

    print("fig_for_dset: using algos: ", sorted(list(df['Algorithm'])))
    # return

    # print("pruned df to:")
    # print df; return

    # # munge algorithm names
    # new_algos = []
    # for algo, delta in zip(algos, df['Deltas']):
    #     new_algos.append(algo + '-Delta' if delta else algo)
    # algos = new_algos

    # print df

    # df['Algorithm'] = raw_algos
    compress_speeds = df['Compression speed'].as_matrix()
    decompress_speeds = df['Decompression speed'].as_matrix()
    ratios = (100. / df['Ratio']).as_matrix()

    for i, algo in enumerate(algos):  # undo artificial boost from 0 padding
        name = algo.split()[0]  # ignore level
        if cfg.ALGO_INFO[name].needs_32b:
            nbits = df['Nbits'].iloc[i]
            ratios[i] *= nbits / 32.

    # compute colors for each algorithm in scatterplot
    # ignore level (eg, '-3') and deltas (eg, Zstd-Delta)
    # base_algos = [algo.split()[0].split('-')[0] for algo in algos]
    base_algos = [algo.split()[0] for algo in algos]
    infos = [cfg.ALGO_INFO[algo] for algo in base_algos]
    colors = [info.color for info in infos]

    # ratios = 100. / ratios
    # df['Ratio'] = 100. / df['Ratio']
    # print("algos: ", algos)
    # print("compress_speeds: ", compress_speeds)
    # print("ratios: ", ratios)

    # option 1: annotate each point with the algorithm name
    def scatter_plot(ax, x, y, colors=None):
        ax.scatter(x, y, c=colors)

        # annotations
        xscale = ax.get_xlim()[1] - ax.get_xlim()[0]
        yscale = ax.get_ylim()[1] - ax.get_ylim()[0]
        perturb_x = .01 * xscale
        perturb_y = .01 * yscale
        for i, algo in enumerate(algos):
            # algo = algo + '-Delta' if used_delta[i] else algo
            if used_preprocs[i] != cfg.Preproc.NONE:
                algo += '-'.join(used_preprocs[i].split(','))
            ax.annotate(algo, (x[i] + perturb_x, y[i] + perturb_y))
        ax.margins(0.2)

    scatter_plot(axes[0], compress_speeds, ratios, colors=colors)
    scatter_plot(axes[1], decompress_speeds, ratios, colors=colors)

    for ax in axes:
        # ax.set_xscale('log')
        ax.set_ylim([.95, ax.get_ylim()[1]])

    plt.tight_layout()
    plt.subplots_adjust(top=.88)
    save_dir = cfg.FIG_SAVE_DIR
    if nbits is not None:
        save_dir = os.path.join(save_dir, '{}b'.format(nbits))
    if exclude_preprocs:
        save_dir += '_nopreprocs'
    if memlimit is not None and memlimit > 0:
        save_dir += '_{}KB'.format(memlimit)
    if order is not None:
        save_dir += '_{}'.format(order)
    if save:
        files.ensure_dir_exists(save_dir)
        plt.savefig(os.path.join(save_dir, dset))
    else:
        plt.show()


def fig_for_dsets(dsets=None, **kwargs):
    if dsets is None:
        dsets = cfg.ALL_DSET_NAMES
    for dset in pyience.ensure_list_or_tuple(dsets):
        fig_for_dset(dset, **kwargs)


# ================================================================ main

def run_sweep(algos=None, create_fig=False, nbits=None, all_use_u32=None,
              preprocs=None, miniters=0, memlimit=-1,
              orders=['c', 'f'], dsets=None, nthreads=[0],
              queries=[cfg.Queries.NONE], **kwargs):
    # TODO I should just rename these vars
    all_nbits = nbits
    all_preprocs = preprocs  # 'deltas' was a more intuitive kwarg
    all_dsets = dsets  # rename kwarg for consistency
    all_algos = algos
    all_orders = orders
    all_nthreads = nthreads
    all_queries = queries

    if all_nbits is None:
        # all_nbits = [16]
        all_nbits = [8, 16]
    if all_use_u32 is None:
        # all_use_u32 = [True]
        all_use_u32 = [True, False]
    if all_preprocs is None:
        all_preprocs = [cfg.Preproc.NONE]
    if all_orders is None:
        all_orders = ['c', 'f']
    if all_dsets is None:
        all_dsets = cfg.ALL_DSET_NAMES
    if all_algos is None:
        all_algos = cfg.USE_WHICH_ALGOS
    # if all_queries is None:
        # all_queries = [None]
        # all_algos = ('Zstd LZ4 LZ4HC Snappy FSE Huffman FastPFOR Delta ' +
        #              'DoubleDelta DeltaRLE_HUF DeltaRLE BitShuffle8b ' +
        #              'ByteShuffle8b').split()

    all_nbits = pyience.ensure_list_or_tuple(all_nbits)
    all_use_u32 = pyience.ensure_list_or_tuple(all_use_u32)
    all_preprocs = pyience.ensure_list_or_tuple(all_preprocs)
    all_orders = pyience.ensure_list_or_tuple(all_orders)
    all_dsets = pyience.ensure_list_or_tuple(all_dsets)
    all_algos = pyience.ensure_list_or_tuple(all_algos)

    # all_algorithms = ('BitShuffle8b ByteShuffle8b').split()
    # all_dsets = ['PAMAP']

    # delta_algos = [algo for algo in algos if ALGO_INFO[algo].allow_delta]
    # delta_u32_algos = [algo for algo in delta_algos if ALGO_INFO[algo].needs_32b]

    all_combos = itertools.product(
        all_nbits, all_use_u32, all_preprocs, all_orders,
        all_nthreads, all_queries)
    for (use_nbits, use_u32, use_preproc, use_order, use_nthreads, use_query) in all_combos:  # noqa

        # print("considering preproc: '{}'".format(use_preproc))

        # filter algorithms with incompatible requirements
        algos = []
        for algo in all_algos:
            info = cfg.ALGO_INFO[algo]

            # print("algo {} allows preprocs: {}".format(info.lzbench_name, info.allowed_preprocs))

            if use_nbits not in info.allowed_nbits:
                continue
            if use_u32 != info.needs_32b:
                continue
            # print("{} passed all non-preproc checks".format(info.lzbench_name))
            if use_preproc not in info.allowed_preprocs:
                continue
            # print("{} passed preproc check".format(info.lzbench_name))
            if use_order not in info.allowed_orders:
                continue
            algos.append(algo)

        # print("eligible algos: ", algos)

        if len(algos) == 0:
            continue

        # print("using nthreads, query: ", use_nthreads, use_query)
        # continue

        _run_experiment(algos=algos, dsets=all_dsets, nbits=use_nbits,
                        preprocs=use_preproc, memlimit=memlimit,
                        miniters=miniters, order=use_order,
                        create_fig=create_fig, nthreads=use_nthreads,
                        query_id=use_query, **kwargs)


def run_ucr():
    run_sweep(dsets='ucr', algos=cfg.USE_WHICH_ALGOS, miniters=0,
              save_path=cfg.UCR_RESULTS_PATH)


def run_memlimit_ucr():
    run_sweep(dsets='ucr', algos=cfg.USE_WHICH_ALGOS, miniters=0,
              memlimit=1, save_path=cfg.UCR_MEMLIMIT_RESULTS_PATH)
    run_sweep(dsets='ucr', algos=cfg.USE_WHICH_ALGOS, miniters=0,
              memlimit=10, save_path=cfg.UCR_MEMLIMIT_RESULTS_PATH)
    run_sweep(dsets='ucr', algos=cfg.USE_WHICH_ALGOS, miniters=0,
              memlimit=2, nbits=16, save_path=cfg.UCR_MEMLIMIT_RESULTS_PATH)
    run_sweep(dsets='ucr', algos=cfg.USE_WHICH_ALGOS, miniters=0,
              memlimit=20, nbits=16, save_path=cfg.UCR_MEMLIMIT_RESULTS_PATH)


def run_preprocs_ucr():
    # TODO higher miniters once working
    # run_sweep(dsets='ucr', algos=cfg.PREPROC_EFFECTS_ALGOS, miniters=10,
    # run_sweep(dsets='ucr', algos=['Huffman', 'Snappy', 'LZ4'], miniters=0,
    run_sweep(dsets='ucr', algos=['Zstd', 'Zlib'], miniters=0,
              preprocs=cfg.ALL_PREPROCS,
              save_path=cfg.PREPROC_UCR_RESULTS_PATH)


def run_speed_vs_ndims():

    # TODO uncomment to run on all dsets
    # dsets = [cfg.SYNTH_100M_U8_LOW_PATH, cfg.SYNTH_100M_U16_LOW_PATH,
    dsets = [
             cfg.SYNTH_100M_U8_HIGH_PATH, cfg.SYNTH_100M_U16_HIGH_PATH]
    dsets = [RAW_DSET_PATH_PREFIX + dset for dset in dsets]
    # run_sweep(dsets=dsets, algos=['SprintzDelta', 'SprintzXff'],
    #           miniters=10, save_path=cfg.NDIMS_SPEED_RESULTS_PATH,
    #           custom_levels=np.arange(8, 10))

    # split into two sweeps so we get some intermediate results
    run_sweep(dsets=dsets, algos=cfg.SPRINTZ_ALGOS,
              miniters=10, save_path=cfg.NDIMS_SPEED_RESULTS_PATH,
              custom_levels=np.arange(1, 40))
    run_sweep(dsets=dsets, algos=cfg.SPRINTZ_ALGOS,
              miniters=10, save_path=cfg.NDIMS_SPEED_RESULTS_PATH,
              custom_levels=np.arange(40, 80 + 1))


def run_speed_vs_ndims_preprocs():
    # dsets = [cfg.SYNTH_100M_U8_LOW_PATH, cfg.SYNTH_100M_U16_LOW_PATH]
    # dsets = [RAW_DSET_PATH_PREFIX + dset for dset in dsets]

    # algos = 'Delta DoubleDelta FIRE Delta_16b DoubleDelta_16b FIRE_16b'.split()
    # algos = 'Delta DoubleDelta FIRE'.split()
    algos = ['FIRE']

    # split into multiple sweeps so we get some intermediate results
    dset = RAW_DSET_PATH_PREFIX + cfg.SYNTH_100M_U8_LOW_PATH
    for interval in ([1, 20], [20, 40], [40, 60], [60, 81]):
        run_sweep(dsets=[dset], algos=algos,
                  miniters=10, save_path=cfg.PREPROC_SPEED_RESULTS_PATH,
                  custom_levels=np.arange(interval[0], interval[1]))

    algos = [algo + '_16b' for algo in algos]
    dset = RAW_DSET_PATH_PREFIX + cfg.SYNTH_100M_U16_LOW_PATH
    for interval in ([1, 20], [20, 40], [40, 60], [60, 81]):
        run_sweep(dsets=[dset], algos=algos,
                  miniters=10, min_comp_iters=10,
                  save_path=cfg.PREPROC_SPEED_RESULTS_PATH,
                  custom_levels=np.arange(interval[0], interval[1]))

    # run_sweep(dsets=dsets, algos=algos,
    #           miniters=10, save_path=cfg.NDIMS_SPEED_RESULTS_PATH,
    #           custom_levels=np.arange(1, 40))
    # run_sweep(dsets=dsets, algos=algos,
    #           miniters=10, save_path=cfg.NDIMS_SPEED_RESULTS_PATH,
    #           custom_levels=np.arange(40, 80 + 1))


def run_multidim():
    run_sweep(dsets=cfg.USE_WHICH_MULTIDIM_DSETS, algos=cfg.USE_WHICH_ALGOS,
              miniters=20, min_comp_iters=10,
              save_path=cfg.MULTIDIM_RESULTS_PATH)


def run_queries():
    pass
    # a couple examples:
    # export D=18; make && ./lzbench -r -S1 -c$D -e2 -q1 -asnappy/zstd,1,7 -t0,0 -i0,0 -j ~/Desktop/datasets/compress/colmajor/uint16/uci_gas # noqa
    # export D=80; make && ./lzbench -r -S0 -c$D -e2 -q0 -amaterialized/snappy/zstd,1,7 -t0,0 -i0,0 -j ~/Desktop/datasets/compress/rowmajor/uint16/msrc # noqa


def run_multicore_queries():

    use_nthreads = np.arange(1, 17)
    # use_nthreads = [1, 2]
    query_ids = [cfg.Queries.NONE, cfg.Queries.SUM, cfg.Queries.MAX]
    algos = cfg.USE_WHICH_ALGOS
    algos.remove('FastPFOR')  # makes queries segfault for unclear reasons
    # print("algos: ", algos)
    # return

    # run_sweep(dsets=['msrc_split'], algos=cfg.USE_WHICH_ALGOS,
    run_sweep(dsets=['msrc_split'], algos=algos,
              miniters=0, min_comp_iters=0,
              nthreads=use_nthreads, queries=query_ids,
              save_path=cfg.MULTICORE_RESULTS_PATH, inject_str=' -j')
    # dry_run=True) # TODO rm


def main():
    # _run_experiment(nbits=8, dsets=['ampd_gas'], algos=['Zstd', 'FSE'])
    # _run_experiment(nbits=8, dsets=['ampd_gas'], algos=['FSE'])
    # _run_experiment(nbits=8, dsets=['ampd_gas'], algos=['Huffman'])

    kwargs = pyience.parse_cmd_line()

    if kwargs.get('run_ucr', False):
        run_ucr()
        return

    if kwargs.get('memlimit_ucr', False):
        run_memlimit_ucr()
        return

    if kwargs.get('speed_vs_ndims', False):
        run_speed_vs_ndims()
        print("ran speed vs ndims...")
        return

    if kwargs.get('preproc_speeds', False):
        run_speed_vs_ndims_preprocs()
        print("ran preproc speed vs ndims...")
        return

    if kwargs.get('preproc_ucr', False):
        run_preprocs_ucr()
        print("ran preproc + ucr")
        return

    if kwargs.get('multidim', False):
        run_multidim()
        print("ran multidim")
        return

    if kwargs.get('multicore', False):
        run_multicore_queries()
        print("ran multicore queries")
        return

    if kwargs is not None and kwargs.get('sweep', False):
        run_sweep(**kwargs)
        return

    if kwargs.get('dsets') == 'all':
        kwargs['dsets'] = cfg.ALL_DSET_NAMES

    # print kwargs; return

    if kwargs and 'fig' not in kwargs:
        _run_experiment(**kwargs)
    elif 'fig' in kwargs:
        fig_for_dsets(**kwargs)

    # fig_for_dset('ampd_gas')

    # gradient = np.linspace(0, 1, 256)
    # gradient = np.vstack((gradient, gradient))
    # # plt.imshow(gradient, aspect='auto', cmap=plt.get_cmap('Dark2'))
    # # plt.imshow(gradient, aspect='auto', cmap=plt.get_cmap('tab10'))
    # plt.imshow(gradient, aspect='auto', cmap=plt.get_cmap('tab20'))
    # plt.show()

    # # this is how you get the colors out of a cmap; vals in (0, 1)
    # cmap = plt.get_cmap('tab20')
    # print cmap(0)
    # print cmap(.1)
    # print cmap(.11)
    # print cmap(.2)
    # print cmap(.3)
    # # print cmap(26)
    # # print cmap(27)
    # # print cmap(255)


if __name__ == '__main__':
    main()
