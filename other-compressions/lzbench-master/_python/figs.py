#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

import numpy as np
import os
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sb  # pip install seaborn

from joblib import Memory  # pip install joblib

from _python import config as cfg
from _python import pyience
from _python import files

_memory = Memory('./', verbose=1)

DSETS_POSITIONS = {'uci_gas': (0, 0), 'ampd_gas': (0, 1),
                   'msrc':    (1, 0), 'ampd_power': (1, 1),
                   'pamap': (2, 0), 'ampd_water': (2, 1)}
# dsets_plot_shape = (len(DSETS_POSITIONS) // 2, 2)

# USE_WHICH_DSETS = DSETS_POSITIONS.keys()
# USE_WHICH_DSETS = [cfg.NAME_2_DSET[name] for name in USE_WHICH_DSETS]

FIG_SAVE_DIR = os.path.join(cfg.FIG_SAVE_DIR, 'paper')

CAMERA_READY_FONT = 'DejaVu Sans'


def save_fig(name, save_dir=FIG_SAVE_DIR):
    plt.savefig(os.path.join(save_dir, name + '.pdf'), bbox_inches='tight')


def save_fig_png(name, save_dir=FIG_SAVE_DIR):
    plt.savefig(os.path.join(save_dir, name + '.png'), bbox_inches='tight',
                dpi=300)


def add_ylabel_on_right(ax, label, **ylabel_kwargs):
    ax2 = ax.twinx()
    sb.despine(ax=ax2, top=True, left=True, bottom=True, right=True)
    ax2.get_xaxis().set_visible(False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax2.get_yticklabels(), visible=False)
    ax2.yaxis.set_label_position('right')
    ax2.set_ylabel(label, labelpad=10, fontsize=14, family=CAMERA_READY_FONT)


def vertical_line(x, ymin=None, ymax=None, ax=None, **plot_kwargs):
    if ax and (not ymin or not ymax):
        ymin, ymax = ax.get_ylim()
    if not ax:
        ax = plt

    plot_kwargs.setdefault('color', 'k')
    plot_kwargs.setdefault('linestyle', '--')
    if 'linewidth' not in plot_kwargs:
        plot_kwargs.setdefault('lw', 2)

    ax.plot([x, x], [ymin, ymax], **plot_kwargs)


def _clean_algo_name(s):
    name = s.split()[0]
    if name.endswith('_16b'):
        name = name[:-4]
    # return {'SprintzDelta': 'Sprintz -1',
    #         'SprintzXff':   'Sprintz -2',
    #         # 'LZO': 'LZO'}.get(name, s)  # replaces 'LZO -1' with LZO
    #         'SprintzXff_Huf': 'Sprintz -3'}.get(name, s)

    # #
    # if s[-2:] == '-9':
    #     return name

    return {'SprintzDelta': 'SprintzDelta',
            'SprintzXff':   'SprintzFIRE',
            # 'LZO': 'LZO'}.get(name, s)  # replaces 'LZO -1' with LZO
            'SprintzXff_Huf': 'SprintzFIRE+Huf',
            'Delta': 'Delta',
            'DoubleDelta': 'DoubleDelta',
            'FIRE': 'FIRE'}.get(name, s)


def _fix_algo_col_names(df):
    colnames = list(df.columns)
    new_colnames = [_clean_algo_name(name) for name in colnames]
    rename_dict = dict(zip(colnames, new_colnames))
    return df.rename(columns=rename_dict)


def _apply_filters(df, nbits=None, order=None, preproc=cfg.Preproc.NONE,
                   memlimit=None, avg_across_files=False, algos=None,
                   exclude_algos=None):

    if nbits is not None:
        df = df[df['Nbits'] == nbits]
    else:
        raise ValueError("must specify nbits!")

    if order is not None:
        df = df[df['Order'] == order]

    # if deltas is not None and deltas:
    #     df = df[df['Deltas'] == deltas]

    if preproc is not None:
        df = df[df['Preprocs'] == preproc]

    if memlimit is not None:  # can use -1 for runs without a mem limit
        df = df[df['Memlimit'] == memlimit]

    if avg_across_files:
        df = df.groupby(
            cfg.INDEPENDENT_VARS, as_index=False)[cfg.DEPENDENT_VARS].mean()

    if algos is not None:
        algos_set = set(pyience.ensure_list_or_tuple(algos))
        mask = [algo.split()[0] in algos_set for algo in df['Algorithm']]
        df = df[mask]

    if exclude_algos is not None:
        exclude_set = set(pyience.ensure_list_or_tuple(exclude_algos))
        # print "exclude algos set:", exclude_set
        mask = [algo.split()[0] not in exclude_set for algo in df['Algorithm']]
        df = df[mask]

    return df


def _scatter_plot(ax, x, y, algos, labels, annotate=False,
                  scales=None, colors=None, markers=None):

    print("labels: ", labels)
    print("labels type: ", type(labels))

    print("labels dtype: ", np.array(labels, dtype=np.object).dtype)
    # ax.scatter(x, y, s=scales, c=colors, label=np.array(labels))
    # for xx, yy, ss, label
    for i in range(len(x)):
        s = scales[i] if scales is not None else None
        c = colors[i] if colors is not None else None
        m = markers[i] if markers is not None else 'o'
        z = 99 if labels[i].startswith('Sprintz') else None
        ax.scatter(x[i], y[i], s=s, c=c, label=labels[i], marker=m, zorder=z)

    # ax.margins(x=.05, y=0.19)
    ax.margins(x=.05, y=0.22)
    ax.set_ylim([.75, ax.get_ylim()[1]])

    # annotations
    xscale = ax.get_xlim()[1] - ax.get_xlim()[0]
    yscale = ax.get_ylim()[1] - ax.get_ylim()[0]
    # perturb_x = .01 * xscale
    # perturb_y = .01 * yscale
    perturb_x = .03 * xscale
    perturb_y = -.03 * yscale
    if annotate:
        for i, algo in enumerate(algos):
            # allow only annotating certain algorithms by specifying a
            # prefix instead of just True
            if isinstance(annotate, str) and not algo.lower().startswith(annotate):
                continue

            # algo = algo + '-Delta' if used_delta[i] else algo
            ax.annotate(algo, (x[i] + perturb_x, y[i] + perturb_y),
                        # rotation=30, rotation_mode='anchor')
                        # rotation=10, rotation_mode='anchor')
                        rotation=7, rotation_mode='anchor')
    # ax.margins(0.2)


def _decomp_vs_ratio_plot(dset, ax, df):
    # dset_name = dset.pretty_name
    # dset_name = cfg.PRETTY_DSET_NAMES[dset] if dset in cfg.PRETTY_DSET_NAMES else dset

    # print("using dset ", dset)
    # print "df"
    # print df

    rm_algos = ('SprintzDelta_Huf', 'SprintzDelta_Huf_16b',
                'SprintzXff', 'SprintzXff_16b')
    df = df[df['Dataset'] == dset.bench_name]
    rm_mask = df['Algorithm'].apply(lambda s: s.split()[0]).isin(rm_algos)
    df = df[~rm_mask]

    # algos = list(df['Algorithm'])
    ratios = (100. / df['Ratio']).as_matrix()

    # for i, algo in enumerate(list(df['Algorithm'])):  # undo artificial boost from 0 padding
    for i, algo in enumerate(list(df['Algorithm'])):  # undo artificial boost from 0 padding
        name = algo.split()[0]  # ignore level
        if cfg.get_algo_info(name).needs_32b:
            nbits = df['Nbits'].iloc[i]
            ratios[i] *= nbits / 32.
    # df['Ratio'] = ratios

    df['Algorithm'] = df['Algorithm'].apply(_clean_algo_name)
    algos = list(df['Algorithm'])

    comp_speeds = df['Compression speed'].as_matrix()
    # ratios = df['Ratio']
    # used_delta = list(df['Deltas'])

    # compress_speeds = df['Compression speed'].as_matrix()
    decompress_speeds = df['Decompression speed'].as_matrix()
    # ratios = (100. / df['Ratio']).as_matrix()

    # compute colors for each algorithm in scatterplot
    # ignore level (eg, '-3') and deltas (eg, Zstd-Delta)
    # base_algos = [algo.split()[0] for algo in algos]
    # infos = [cfg.ALGO_INFO[algo] for algo in base_algos]
    infos = [cfg.get_algo_info(algo) for algo in algos]
    colors = [info.color for info in infos]
    # scales = [36 if info.group != 'Sprintz' else 64 for info in infos]
    # scales = np.log2(comp_speeds)**(3./2)
    # scales = np.log2(comp_speeds)**2 / 2
    scales = np.log2(np.minimum(1000, comp_speeds))**(1.9) / 2
    markers = [info.marker for info in infos]

    # print "algos: ", algos
    # print "decompress_speeds", decompress_speeds
    # print "ratios", ratios
    _scatter_plot(ax, decompress_speeds, ratios, algos, markers=markers,
                  labels=algos, colors=colors, scales=scales, annotate='sprintz')


def _decomp_vs_ratio_fig(suptitle, nbits=None, preprocs=cfg.Preproc.NONE,
                         memlimit=None, order=None, save=False, dsets=None,
                         save_as=None):

    # if dsets_positions is None:
        # dsets_positions = DSETS_POSITIONS

    if dsets is None:
        dsets = cfg.SUCCESS_DSETS

    dsets = [cfg.NAME_2_DSET[name] for name in dsets]
    # dsets_plot_shape = (len(dsets) // 2, 2)
    dsets_plot_shape = (len(dsets), 2)

    figsize = (6, 7) if len(dsets) == 3 else (6, 5.2)

    fig, axes = plt.subplots(*dsets_plot_shape, figsize=figsize, sharex=True)
    axes = axes.reshape(dsets_plot_shape)

    for ax in axes[-1, :]:
        ax.set_xlabel('Decompression Speed (MB/s)')
    for ax in axes[:, 0]:
        ax.set_ylabel('Compression Ratio')

    # print "axes.shape", axes.shape

    # dsets = USE_WHICH_DSETS
    # df = pd.read_csv(cfg.UCR_RESULTS_PATH)
    df = pd.read_csv(cfg.MULTIDIM_RESULTS_PATH)
    df = df[df['Algorithm'] != 'Memcpy']   # TODO only 1 memcpy instead?
    df = df[~df['Algorithm'].isin(['LZO -1', 'LZO -9'])]

    df['__sort_key__'] = \
        df['Algorithm'].apply(lambda name_and_level: 'AAA' + name_and_level
                              if name_and_level.lower().startswith('sprintz')
                              else name_and_level)
    df = df.sort_values(['__sort_key__']).drop('__sort_key__', 1)

    # all_nbits = (8, 16)
    # dfs_for_nbits = []
    # for nbits in all_nbits:
    #     dfs_for_nbits.append(_apply_filters(df, nbits=nbits, memlimit=memlimit,
    #                                         order=order, preproc=preprocs))

    # print("filtered df: ")
    # print(df)
    # print("using dsets: ", dsets)
    # return

    for j, nbits in enumerate((8, 16)):
        # position = dsets_positions[dset.bench_name]
        # ax = axes[position[0], position[1]]
        # use_df = df[df['Nbits'] == nbits]
        # use_df = dfs_for_nbits[j]
        use_df = _apply_filters(df, nbits=nbits, memlimit=memlimit,
                                order=order, preproc=preprocs)
        for i, dset in enumerate(dsets):
            ax = axes[i, j]
            ax.set_title("{}, {}bit".format(dset.pretty_name, nbits))
            _decomp_vs_ratio_plot(dset=dset, ax=ax, df=use_df)

    leg_lines, leg_labels = axes.ravel()[0].get_legend_handles_labels()
    plt.figlegend(leg_lines, leg_labels, loc='lower center',
                  ncol=3, labelspacing=0)

    # plt.suptitle('Decompression Speed vs Compression Ratio', fontweight='bold')
    plt.suptitle(suptitle, fontweight='bold')
    plt.tight_layout()
    if len(dsets) == 3:
        # plt.subplots_adjust(top=.91, bottom=.2)
        plt.subplots_adjust(top=.91, bottom=.18)
    elif len(dsets) == 2:
        # plt.subplots_adjust(top=.89, bottom=.28)
        plt.subplots_adjust(top=.89, bottom=.25)

    # if save and not isinstance(save, str):
    #     save_dir = cfg.FIG_SAVE_DIR
    #     if nbits is not None:
    #         save_dir = os.path.join(save_dir, '{}b'.format(nbits))
    #     if preprocs is not None:
    #         save_dir += '_{}'.format(''.join(preprocs))
    #     if memlimit is not None and memlimit > 0:
    #         save_dir += '_{}KB'.format(memlimit)
    #     if order is not None:
    #         save_dir += '_{}'.format(order)
    #     files.ensure_dir_exists(save_dir)
    # elif save:
    #     save_dir = save

    if save_as:
        save_fig_png(save_as)
        # plt.savefig(os.path.join(save_dir, dset.bench_name))
    else:
        plt.show()


def decomp_vs_ratio_fig_success(save=True):
    _decomp_vs_ratio_fig(
        suptitle='Decompression Speed vs Compression Ratio, Success Cases',
        dsets=cfg.SUCCESS_DSETS, save_as='tradeoff_success')
    # _decomp_vs_ratio_fig(*args, **kwargs)


def decomp_vs_ratio_fig_failure(save=True):
    _decomp_vs_ratio_fig(
        suptitle='Decompression Speed vs Compression Ratio, Failure Cases',
        dsets=['ampd_gas', 'ampd_water'], save_as='tradeoff_fail')
        # dsets=cfg.FAILURE_DSETS, save_as='tradeoff_fail')


def _compute_ranks(df, lower_better=True):
    """assumes each row of X is a dataset and each col is an algorithm"""
    # return df.rank(axis=1, numeric_only=True, ascending=lower_better)
    return df.rank(axis=1, numeric_only=True, ascending=lower_better, method='min')


def cd_diagram(df, lower_better=True, verbose=1):
    import Orange as orn  # requires py3.4 or greater environment

    ranks = _compute_ranks(df, lower_better=lower_better)
    names = [s.strip() for s in ranks.columns]
    mean_ranks = ranks.mean(axis=0)
    ndatasets = df.shape[0]

    if verbose > 1:
        print("--- raw ranks:")
        print(ranks)

    if verbose > 0:
        print("--- mean ranks:")
        print("\n".join(["{}: {}".format(name, rank)
                         for (name, rank) in zip(names, mean_ranks)]))

    # alpha must be one of {'0.1', '0.05', '0.01'}
    # cd = orn.evaluation.compute_CD(mean_ranks, ndatasets, alpha='0.1')
    cd = orn.evaluation.compute_CD(mean_ranks, ndatasets, alpha='0.05', test='nemenyi')
    # cd = orn.evaluation.compute_CD(mean_ranks, ndatasets, alpha='0.05', test='bonferroni-dunn')
    orn.evaluation.graph_ranks(mean_ranks, names, cd=cd, reverse=True)
    if verbose > 0:
        print("\nNemenyi critical difference: ", cd)


# def _read_and_clean_ucr_results(others_deltas=False):

# @_memory.cache
def _read_and_clean_ucr_results(no_preprocs, memlimit=-1, results_path=cfg.UCR_RESULTS_PATH):
    df = pd.read_csv(results_path)

    # df = df[df['Order'] == 'c']
    df['Filename'] = df['Filename'].apply(lambda s: os.path.basename(s).split('.')[0])
    df = df.sort_values(['Filename', 'Algorithm'])
    # if others_deltas:
    #     df = df[df['Deltas'] | df['Algorithm'].str.startswith('Sprintz')]
    # else:
    #     df = df[~df['Deltas']]

    # uniq_memlimits = df['Memlimit'].unique()
    # print("uniq memlimts: ", uniq_memlimits)
    # return

    df = df[df['Memlimit'] == memlimit]
    ignore_algos = ['SprintzDelta_Huf -1', 'SprintzDelta_Huf_16b -1',
                    'LZO -1', 'LZO -9', 'Zstd -1', 'Zlib -1']
    df = df[~df['Algorithm'].isin(ignore_algos)]

    if no_preprocs:
        df = df[df['Preprocs'] == cfg.Preproc.NONE]
        df = df[['Nbits', 'Algorithm', 'Filename', 'Order', 'Ratio']]
    else:
        df = df[['Nbits', 'Algorithm', 'Filename', 'Order', 'Preprocs', 'Ratio']]
    df = df[df['Algorithm'] != 'Memcpy']
    df['Ratio'] = 100. / df['Ratio']  # bench reports % of original size
    return df
    # full_df = df


# def boxplot_ucr(others_deltas=False, save=True):
def boxplot_ucr(save=True, preproc_plot=False, memlimit=-1, results_path=None):
    # df = pd.read_csv(cfg.UCR_RESULTS_PATH)

    # if preproc_plot:
        # assert not no_preprocs  # preproc plot can't filter out all the preprocs

    # # df = df[df['Order'] == 'c']
    # df['Filename'] = df['Filename'].apply(lambda s: os.path.basename(s).split('.')[0])
    # df = df.sort_values(['Filename', 'Algorithm'])
    # if others_deltas:
    #     df = df[df['Deltas'] | df['Algorithm'].str.startswith('Sprintz')]
    # else:
    #     df = df[~df['Deltas']]
    # df = df[df['Algorithm'] != 'Memcpy']
    # df = df[['Nbits', 'Algorithm', 'Filename', 'Ratio', 'Order']]
    # df['Ratio'] = 100. / df['Ratio']  # bench reports % of original size
    # df = _read_and_clean_ucr_results(others_deltas=others_deltas)
    if results_path is None:
        results_path = cfg.PREPROC_UCR_RESULTS_PATH \
            if preproc_plot else cfg.UCR_RESULTS_PATH
    df = _read_and_clean_ucr_results(
        no_preprocs=not preproc_plot, memlimit=memlimit, results_path=results_path)

    df['Algorithm'] = df['Algorithm'].apply(lambda s: s if s[-2:] != '-9' else s.split()[0])

    # print("got filenames: "), df['Filename']

    # fnames = list(df['Filename'])
    # algos = list(df['Algorithm'])
    # nbitss = list(df['Nbits'])
    # fname_and_algo = [f + a + '_' + str(b) for f, a, b in zip(fnames, algos, nbitss)]
    # print("got initial ivar combos: ", "\n".join(fname_and_algo[:50]))
    # return

    # sb.set_context("talk")
    figsize = (10, 6) if preproc_plot else (5, 7)
    _, axes = plt.subplots(2, 1, figsize=figsize, sharex=True, sharey=True)

    full_df = df
    # for nbits in [8]:
    for i, nbits in enumerate((8, 16)):
        ax = axes[i]
        if i != len(axes) - 1:
            plt.setp(ax.get_xticklabels(), visible=False)
            ax.get_xaxis().set_visible(False)

        df = full_df[full_df['Nbits'] == nbits]
        df = df.drop('Nbits', axis=1)

        if len(df) == 0:
            print("WARNING: No results for nbits = {}".format(nbits))
            continue

        # if it complains about duplicate entries here, might be because
        # memcpy ran on some stuff (but not everything for some reason)
        if preproc_plot:
            # XXX this case just assumes we didn't run with any u32 codecs,
            # since we don't carry out the u32 correction below

            # print("df we're plotting: ")
            # print(df[:20])

            # df[df['Algorithm'] == 'Huffman'].sort_values(['Filename', 'Preprocs']).to_csv('~/Desktop/tmp_{}bit.csv'.format(nbits))

            df['Algorithm'] = df['Algorithm'].apply(_clean_algo_name)

            sb.boxplot(ax=ax, data=df, x='Algorithm', y='Ratio', hue='Preprocs')
            # sb.violinplot(ax=ax, data=df, x='Algorithm', y='Ratio', hue='Preprocs')
        else:
            df = df.pivot(index='Filename', columns='Algorithm', values='Ratio')

            for col in df:
                info = cfg.ALGO_INFO.get(col)
                if info is not None and info.needs_32b:
                    print("scaling comp ratio for col: {}".format(col))
                    # print("old df col:")
                    # print(df[col][:10])

                    # df[col] = df[col] * (32 / nbits)  # if using % of orig
                    df[col] = df[col] * (nbits / 32)    # if using orig/compressed

            # ax = sb.violinplot(data=df, figsize=(8, 8))
            # ax = sb.boxplot(data=df)
            # ax = sb.boxplot(data=df.apply(np.log))

            # df['Algorithm'] = df['Algorithm'].apply(_clean_algo_name)

            # df.drop('SprintzDelta_Huf -1', axis=1, inplace=True)  # not using this
            # df.drop('SprintzDelta_Huf_16b -1', axis=1, inplace=True)  # not using this

            # rename_dict = {name: _clean_algo_name(name) for name in cfg.USE_WHICH_ALGOS}
            # rename_dict = {name: 'fred' for name in cfg.USE_WHICH_ALGOS}

            # print("colnames: ", colnames)
            # print("new colnames: ", new_colnames)

            df = _fix_algo_col_names(df)

            # ratios1 = df['Sprintz -1'].as_matrix()
            # ratios2 = df['Sprintz -2'].as_matrix()
            ratios1 = df['SprintzDelta'].as_matrix()
            ratios2 = df['SprintzFIRE'].as_matrix()
            num_wins = np.sum(ratios2 > ratios1)
            rel_improvements = (ratios2 - ratios1) / ratios1
            from scipy import stats
            _, pvalue = stats.wilcoxon(ratios1, ratios2)
            print("FIRE wins {} / {} datasets (p={}); mean, std of rel improvement = {}, {}".format(
                num_wins, len(ratios1), pvalue,
                np.mean(rel_improvements), np.std(rel_improvements)))

            # print("colnames: ", colnames)
            # print("new colnames: ", new_colnames)

            # order = ['Sprintz -1', 'Sprintz -2', 'Sprintz -3',
            #          'Zlib -1', 'Zlib -9', 'Zstd -1', 'Zstd -9',
            order = ['SprintzDelta', 'SprintzFIRE', 'SprintzFIRE+Huf',
                     'Zlib', 'Zstd',
                     'FastPFOR', 'Huffman', 'LZ4',
                     'SIMDBP128', 'Simple8B', 'Snappy']
                     # 'FastPFOR', 'Huffman', 'LZ4', 'LZO -1', 'LZO -9',

            sb.boxplot(data=df, ax=ax, order=order)

        ax.semilogy()

        # print("xticklabels: ", ax.get_xticklabels())
        # xticklabels = ax.get_xticklabels()
        # ax.set_xticklabels(ax.get_xticklabels(), rotation=70)  # rotate labels
        # ax.set_xticklabels(["\n" + lbl.get_text() for lbl in ax.get_xticklabels()], rotation=70)
        add_ylabel_on_right(ax, "{}-bit Data".format(nbits))

    # for ax in axes:
    # for really unclear reasons, the second line is necessary when we
    # use rotation_mode='anchor' to avoid ticklabels ending up the plot
    xlabels = list(ax.get_xticklabels())
    # print("WTF are these xticklabels?: ", xlabels)
    for i in range(3):
        # xlabels[i].weight = 'bold'
        xlabels[i].set_weight('bold')
    ax.set_xticklabels(xlabels, rotation=70, rotation_mode='anchor')
    plt.setp(ax.xaxis.get_majorticklabels(), ha='right')  # align xticklabels nicely?

    for ax in axes:
        ax.set_ylabel("Compression Ratio", fontsize=14)

        # # ymin, ymax = np.array(ax.get_ylim()) * 1./ax.get_margin()[1]
        # ymin, ymax = np.array(ax.get_ylim()) * 1.25
        # ymin, ymax = np.array(ax.get_ylim()) + np.array([.5, 0])
        # # ymin, ymax = -1, np.array(ax.get_ylim())[1] * 2
        # vertical_line(x=.235 * ax.get_xlim()[1], ax=ax, lw=.75, color='gray')
        # ax.margins(y=.02)

    # axes[0].set_title("Compression Ratios on UCR Archive, {}-bit".format(nbits),
    title = "Compression Ratios on UCR Datasets"
    if memlimit > 0:
        title += '\nBlock Size = {}KB'.format(memlimit)
    axes[0].set_title(title, fontsize=16)

    plt.tight_layout()
    figname = 'boxplot_preproc_ucr' if preproc_plot else 'boxplot_ucr'
    figname += '' if memlimit <= 0 else "_{}KB".format(memlimit)
    if save:
        save_fig_png(figname)
    else:
        plt.show()


def preproc_boxplot_ucr():
    boxplot_ucr(preproc_plot=True)


def memlimit_boxplot_ucr():
    boxplot_ucr(preproc_plot=False, results_path=cfg.UCR_MEMLIMIT_RESULTS_PATH,
                memlimit=1)
    boxplot_ucr(preproc_plot=False, results_path=cfg.UCR_MEMLIMIT_RESULTS_PATH,
                memlimit=10)


def _cd_diagram_ours_vs_others(save=True, preproc_plot=False):
    # df = pd.read_csv(cfg.UCR_RESULTS_PATH)

    # # df = df[df['Order'] == 'c']
    # df['Filename'] = df['Filename'].apply(lambda s: os.path.basename(s).split('.')[0])
    # df = df.sort_values(['Filename', 'Algorithm'])
    # if others_deltas:
    #     df = df[df['Deltas'] | df['Algorithm'].str.startswith('Sprintz')]
    # else:
    #     df = df[~df['Deltas']]
    # df = df[df['Algorithm'] != 'Memcpy']
    # df = df[['Nbits', 'Algorithm', 'Filename', 'Ratio', 'Order']]
    # df['Ratio'] = 100. / df['Ratio']  # bench reports % of original size
    # df = _read_and_clean_ucr_results(others_deltas=others_deltas)
    results_path = cfg.PREPROC_UCR_RESULTS_PATH \
        if preproc_plot else cfg.UCR_RESULTS_PATH
    df = _read_and_clean_ucr_results(
        no_preprocs=not preproc_plot, results_path=results_path)

    df['Algorithm'] = df['Algorithm'].apply(lambda s: s if s[-2:] != '-9' else s.split()[0])

    full_df = df
    # for nbits in [8]:
    for nbits in (8, 16):
        df = full_df[full_df['Nbits'] == nbits]
        df = df.drop('Nbits', axis=1)
        # df = df.sort_values('Filename')

        # # counts = df.groupby(['Filename', 'Algorithm']).count()
        # counts = df.groupby(['Algorithm']).count()
        # print("fname, algo counts: ")
        # print(counts)
        # print(counts.min())
        # print(counts.max())
        # # print(df[:560].groupby('Filename').count())
        # # print(df[560:1120].groupby('Filename').count())
        # # print(df[-560:].groupby('Filename').count())

        # # return

        # df.to_csv('df_ucr.csv')

        # print("df8 algos", df8['Algorithm'])

        # if if complains about duplicate entries here, might because
        # memcpy ran on some stuff (but not everything for some reason)
        df = df.pivot(index='Filename', columns='Algorithm', values='Ratio')

        # print("df8", df8[:20])
        # print("df8", df8)
        # print("df8 cols", df8.columns.names)

        for col in df:
            info = cfg.ALGO_INFO.get(col)
            if info is not None and info.needs_32b:
                print("scaling comp ratio for col: {}".format(col))
                # print("old df col:")
                # print(df[col][:10])

                # df[col] = df[col] * (32 / nbits)  # if using % of orig
                df[col] = df[col] * (nbits / 32)    # if using orig/compressed

                # print("new df col:")
                # print(df[col][:10])

        df = _fix_algo_col_names(df)
        # df = df.drop(['LZO -1', 'LZO -9'], axis=1)

        cd_diagram(df)  # if using % of orig
        cd_diagram(df, lower_better=False)

        ax = plt.gca()
        ax.set_title("Mean Ranks on UCR Archive, {}-bit".format(nbits), fontsize=16)
        plt.tight_layout()

        if save:
            fmt_str = 'preproc_cd_diagram_{}b' if preproc_plot else 'cd_diagram_{}b'
            save_fig_png(fmt_str.format(nbits))
            # save_fig_png('cd_diagram_{}b_deltas={}'.format(
            #     nbits, int(others_deltas)))
        else:
            plt.show()


def cd_diagram_ours_vs_others():
    _cd_diagram_ours_vs_others()


# def cd_diagram_ours_vs_others_delta():
#     _cd_diagram_ours_vs_others(others_deltas=True)


def _speed_vs_ndims_fig(ycol, ylabel, suptitle, use_ratios=(1,), savepath=None):
    df = pd.read_csv(cfg.NDIMS_SPEED_RESULTS_PATH)
    sb.set_context("talk")

    # INCLUDE_HIGH_COMP = False

    figsize = (8, 8) if len(use_ratios) == 2 else (8, 4.5)
    fig, axes = plt.subplots(len(use_ratios), 2, figsize=figsize, sharey=True)
    axes = axes.reshape(len(use_ratios), 2)

    # df = df[df['Order'] == 'c']
    # df['Filename'] = df['Filename'].apply(lambda s: os.path.basename(s).split('.')[0])
    # df = df.sort_values(['Filename', 'Algorithm'])
    # df = df[df['Algorithm'] != 'Memcpy']
    rm_algos = ('Memcpy', 'SprintzDelta_Huf', 'SprintzDelta_Huf_16b')
    # df = df[df['Algorithm'].apply(lambda s: s.split()[0]).isin(ignore_algos)]
    rm_mask = df['Algorithm'].apply(lambda s: s.split()[0]).isin(rm_algos)
    df = df[~rm_mask]

    df['Ratio'] = 100. / df['Ratio']  # bench reports % of original size

    # Y_VAR_COL = 'Decompression speed'
    Y_VAR_COL = ycol

    # extract ndims from algo name; eg: "SprintzDelta -9" -> 9
    df['Ndims'] = df['Algorithm'].apply(lambda algo: -int(algo.split()[1]))
    # df['Algorithm'] = df['Algorithm'].apply(lambda algo: algo.split()[0])
    df['Algorithm'] = df['Algorithm'].apply(_clean_algo_name)
    df['TrueRatio'] = df['Filename'].apply(
        lambda path: int(path.split("ratio=")[1].split('.')[0]))
    df = df[['Ndims', 'Nbits', 'Algorithm', Y_VAR_COL, 'TrueRatio']]

    full_df = df
    # for nbits in [8]:
    # use_ratios = df['TrueRatio'].unique()
    uniq_algos = sorted(df['Algorithm'].unique())
    all_nbits = (8, 16)

    print("using ratios: ", use_ratios)

    for i, rat in enumerate(use_ratios):
        axes_row = axes[i]
        df_for_ratio = full_df[full_df['TrueRatio'] == rat]

        for ax, nbits in zip(axes_row, all_nbits):
            df = df_for_ratio[df_for_ratio['Nbits'] == nbits]
            df = df.drop('Nbits', axis=1)
            df = df.sort_values(['Algorithm', 'Ndims'])

            for algo in uniq_algos:
                subdf = df[df['Algorithm'] == algo]
                x = subdf['Ndims']
                y = subdf[Y_VAR_COL]

                print("plotting algo: ", algo)

                ax.plot(x, y, label=algo, lw=1)

    for ax, nbits in zip(axes[0, :], all_nbits):
        ax.set_title("{}-bit Values".format(nbits), fontsize=16)
    for ax in axes[:, 0]:
        # ax.set_ylabel("Decompression Speed\n(MB/s)", fontsize=14)
        ax.set_ylabel(ylabel, fontsize=14)
    for ax in axes[-1, :]:
        ax.set_xlabel("Number of columns", fontsize=14)
    for ax in axes.ravel():
        ax.set_ylim([0, ax.get_ylim()[1]])

    # add byte counts on the right
    # fmt_str = "{}B Encodings"
    sb.set_style("white")  # adds border (spines) we have to remove
    if len(use_ratios) > 1:
        for i, ax in enumerate(axes[:, -1]):
            ax2 = ax.twinx()
            sb.despine(ax=ax2, top=True, left=True, bottom=True, right=True)
            ax2.get_xaxis().set_visible(False)
            # ax2.get_yaxis().set_visible(False)  # nope, removes ylabel
            plt.setp(ax2.get_xticklabels(), visible=False)
            plt.setp(ax2.get_yticklabels(), visible=False)
            ax2.yaxis.set_label_position('right')
            if len(use_ratios) == 2:
                lbl = "Incompressible Data" if i == 0 else "Highly Compressible Data"
            else:
                lbl = "Compression Ratio = %d".format(int(use_ratios[i]))
            ax2.set_ylabel(lbl, labelpad=10, fontsize=14, family=CAMERA_READY_FONT)

    leg_lines, leg_labels = axes.ravel()[-1].get_legend_handles_labels()
    plt.figlegend(leg_lines, leg_labels, loc='lower center',
                  ncol=len(uniq_algos), labelspacing=0)

    # plt.suptitle("Decompression Speed vs Number of Columns", fontweight='bold')
    plt.suptitle(suptitle, fontweight='bold')
    plt.tight_layout()
    if len(use_ratios) == 2:
        plt.subplots_adjust(top=.9, bottom=.14)
    else:
        plt.subplots_adjust(top=.85, bottom=.24)

    if savepath is not None:
        save_fig_png(savepath)
    else:
        plt.show()


# this version plots compression and decompression in one fig
def _speed_vs_ndims_fig_v2(results_path, ylabel, top_quantity, bottom_quantity,
                           suptitle, savepath=None):
    df = pd.read_csv(results_path)
    sb.set_context("talk")

    fig, axes = plt.subplots(2, 2, figsize=(8, 8), sharey=True)

    # rm_algos = ('Memcpy', 'SprintzDelta_Huf', 'SprintzDelta_Huf_16b')
    # # df = df[df['Algorithm'].apply(lambda s: s.split()[0]).isin(ignore_algos)]
    # rm_mask = df['Algorithm'].apply(lambda s: s.split()[0]).isin(rm_algos)
    # df = df[~rm_mask]

    # print("here are the uniq algos at the start: ")
    # print(df['Algorithm'].unique())
    # return

    df = df[df['Algorithm'] != 'Memcpy']
    df['Ratio'] = 100. / df['Ratio']  # bench reports % of original size

    # df = df['Algorithm'].apply(lambda s: s.split()[0])
    # df = df['Algorithm'].apply(_clean_algo_name)

    ycols = ['Compression speed', 'Decompression speed']

    # extract ndims from algo name; eg: "SprintzDelta -9" -> 9
    df['Ndims'] = df['Algorithm'].apply(lambda algo: -int(algo.split()[1]))
    # df['Algorithm'] = df['Algorithm'].apply(lambda algo: algo.split()[0])
    df['Algorithm'] = df['Algorithm'].apply(_clean_algo_name)
    df['TrueRatio'] = df['Filename'].apply(
        lambda path: int(path.split("ratio=")[1].split('.')[0]))
    df = df[['Ndims', 'Nbits', 'Algorithm', 'TrueRatio'] + ycols]

    full_df = df
    # for nbits in [8]:
    # use_ratios = df['TrueRatio'].unique()
    uniq_algos = sorted(df['Algorithm'].unique())
    all_nbits = (8, 16)

    for i, ycol in enumerate(ycols):
        axes_row = axes[i]
        # df_for_ratio = full_df[full_df['TrueRatio'] == rat]

        for ax, nbits in zip(axes_row, all_nbits):
            df = full_df[full_df['Nbits'] == nbits]
            df = df.drop('Nbits', axis=1)
            df = df.sort_values(['Algorithm', 'Ndims'])

            for algo in uniq_algos:
                subdf = df[df['Algorithm'] == algo]
                x = subdf['Ndims']
                y = subdf[ycol]

                print("plotting algo: ", algo)

                ax.plot(x, y, label=algo, lw=1)

    y = y.as_matrix()
    y[:] = 7500  # from repeated measurements across many experiments...
    for ax in axes.ravel():
        ax.plot(x, y, '--', label='Memcpy', lw=1)

    # for ax, nbits in zip(axes[0, :], all_nbits):
        # ax.set_title("{}-bit Values".format(nbits), fontsize=16)
    # for ax in axes[:, 0]:
        # ax.set_ylabel("Decompression Speed\n(MB/s)", fontsize=14)
        # ax.set_ylabel(ylabel, fontsize=14)

    # SELF: pick up here

    axes[0, 0].set_title("8-bit {}".format(top_quantity))
    axes[0, 1].set_title("16-bit {}".format(top_quantity))
    axes[1, 0].set_title("8-bit {}".format(bottom_quantity))
    axes[1, 1].set_title("16-bit {}".format(bottom_quantity))

    for ax in axes[-1, :]:
        ax.set_xlabel("Number of columns", fontsize=14)
    for ax in axes.ravel():
        ax.set_ylim([0, ax.get_ylim()[1]])
    for ax in axes[:, 0]:
        ax.set_ylabel(ylabel)

    leg_lines, leg_labels = axes.ravel()[-1].get_legend_handles_labels()
    plt.figlegend(leg_lines, leg_labels, loc='lower center',
                  ncol=len(uniq_algos) + 1, labelspacing=0)
                  # ncol=len(uniq_algos), labelspacing=0)

    # plt.suptitle("Decompression Speed vs Number of Columns", fontweight='bold')
    plt.suptitle(suptitle, fontweight='bold')
    plt.tight_layout()
    plt.subplots_adjust(top=.9, bottom=.14)

    if savepath is not None:
        save_fig_png(savepath)
    else:
        plt.show()
    # plt.show()


def decomp_vs_ndims_results(save=True):
    # _speed_vs_ndims_fig_v2(ycol='Decompression speed',
    _speed_vs_ndims_fig(ycol='Decompression speed',
                        # ylabel='Decompression Speed\n(MB/s)',
                        ylabel='Decompression Speed (MB/s)',
                        suptitle='Decompression Speed vs Number of Columns',
                        savepath=('ndims_vs_decomp_speed' if save else None))


def comp_vs_ndims_results(save=True):
    # _speed_vs_ndims_fig_v2(ycol='Compression speed',
    _speed_vs_ndims_fig(ycol='Compression speed',
                        # ylabel='Compression Speed\n(MB/s)',
                        ylabel='Compression Speed (MB/s)',
                        suptitle='Compression Speed vs Number of Columns',
                        savepath=('ndims_vs_comp_speed' if save else None))


def preproc_vs_ndims_results(save=True):
    _speed_vs_ndims_fig_v2(
        results_path=cfg.PREPROC_SPEED_RESULTS_PATH,
        ylabel='Throughput (MB/s)',
        top_quantity='Encoding',
        bottom_quantity='Decoding',
        suptitle='Forecaster Speed vs Number of Columns',
        savepath=('ndims_vs_preproc_speed' if save else None))


@_memory.cache
def _compute_ucr_snrs():
    from _python.datasets import ucr
    dsets = ucr.allUCRDatasets()

    snrs = {}

    for dset in dsets:
        X = dset.X
        minval, maxval = np.min(X), np.max(X)
        spread = maxval - minval
        for nbits in (8, 16):
            dtype = {8: np.uint8, 16: np.uint16}[nbits]
            scale = (1 << nbits) / spread
            X_quant = np.array((X - minval) * scale, dtype=dtype)
            # X_quant = np.array((X - minval) * scale + .5, dtype=dtype)

            X_hat = (X_quant.astype(np.float64) / scale) + minval

            diffs = X - X_hat

            # snr = np.var(X.ravel()) / np.var(diffs.ravel())
            snr = np.var(X.ravel()) / np.mean(diffs.ravel() * diffs.ravel())
            snrs[(dset.name, nbits)] = snr

    return snrs


def quantize_err_results(save=True):
    # from _python.datasets import ucr
    # dsets = ucr.allUCRDatasets()

    # snrs = {}

    # for dset in dsets:
    #     X = dset.X
    #     minval, maxval = np.min(X), np.max(X)
    #     spread = maxval - minval
    #     for nbits in (8, 16):
    #         dtype = {8: np.uint8, 16: np.uint16}[nbits]
    #         scale = (1 << nbits) / spread
    #         X_quant = np.array((X - minval) * scale, dtype=dtype)

    #         X_hat = (X_quant.astype(np.float64) / scale) + minval

    #         diffs = X - X_hat

    #         snr = np.var(X.ravel()) / np.var(diffs.ravel())
    #         snrs[(dset.name, nbits)] = snr

    snrs = _compute_ucr_snrs()  # note that these aren't log scale

    # convert snrs dict to a dataframe
    snrs_list = []
    for k, v in snrs.items():
        snrs_list.append({'Dataset': k[0], 'Nbits': k[1],
                          'Ratio': np.log10(v)})
                          # 'Ratio': 10 * np.log10(v)})
    df = pd.DataFrame.from_records(snrs_list)

    sb.set_context('talk')
    fig, axes = plt.subplots(1, 2, figsize=(8, 4), sharey=True)
    axes[0].set_title('8 Bit Quantization')
    axes[1].set_title('16 Bit Quantization')

    vals8 = df['Ratio'][df['Nbits'] == 8]
    vals16 = df['Ratio'][df['Nbits'] == 16]

    # sb.distplot(vals8, ax=axes[0], norm_hist=False, kde=False, rug=True, bins=13)
    sb.distplot(vals8, ax=axes[0], norm_hist=False, kde=False, rug=True, bins=25)
    sb.distplot(vals16, ax=axes[1], norm_hist=False, kde=False, rug=True, bins=25)

    # axes[0].semilogx()
    # axes[1].semilogx()

    for ax in axes:
        ax.set_xlabel('Log10(Data Variance / \nMean Quantization Error)')
        # ax.set_xlabel('Variance / \nMean Quantization Error')
        # ax.set_xlabel('Signal-to-Noise Ratio (dB)')
        # ax.set_xlabel('Orders of magnitude le')
        ax.set_xlim([0, ax.get_xlim()[1]])
        # cur_labels = ax.get_xticklabels()
        # new_labels = []
        # for lbl in cur_labels:
        #     try:
        #         # print("got text: ", lbl.get_text())
        #         print("got text: ", str(lbl))
        #         new_labels.append(10**float(lbl.get_text()))
        #     except ValueError:
        #         new_labels.append('')
        # ax.set_xticklabels(new_labels)

        # ax.set_xticklabels([10**float(lbl.get_text()) for lbl in ax.get_xticklabels()])
    # axes[0].set_ylabel('Relative Frequency')
    axes[0].set_ylabel('Number of Datasets')
    # axes[0].set_xlim(axes[1].get_xlim())

    output = ["{}: {}".format(k, v) for k, v in snrs.items()]
    print("\n".join(output[:10]))

    plt.suptitle("Distribution of Quantization Errors\nOn UCR Datasets")
    plt.tight_layout()
    plt.subplots_adjust(top=.75, bottom=.1)
    if save:
        save_fig_png('quantize_errs')
    else:
        plt.show()


def theoretical_thruput(save=True):
    # relevant variables:
    #   -number of cores
    #   -thruput of each core
    #   -memory bw
    #   -compression ratio
    #
    # suppose 20GB/s DDR4 RAM
    # then limiting thruput is 20GB/s * ratio
    # and until this point, thruput is ncores * thruput/core

    ratios = [1.5, 2, 4]
    thruputs = [1200, 800, 3000]
    algos = ['Snappy', 'Zstd', 'Sprintz']

    MEM_BANDWIDTH_MBPS = 20*1000
    ncores = np.arange(1, 64 + 1)

    fig, ax = plt.subplots(1)
    plt.title("Expected Read Throughput vs Number of Cores")
    for ratio, thruput, name in zip(ratios, thruputs, algos):
        total_thruputs = ncores * thruput
        limit_thruput = MEM_BANDWIDTH_MBPS * ratio
        total_thruputs = np.minimum(total_thruputs, limit_thruput)
        ax.plot(ncores, total_thruputs, label=name)

    plt.legend()
    ax.set_xlabel("Number of Cores")
    ax.set_xlabel("Total Read Throughput")
    if save:
        save_fig_png('expected_thruput')
    else:
        plt.show()

# def decomp_vs_ratio_success(save=True):
#     pass


@_memory.cache
def _cached_read_csv(path):
    return pd.read_csv(path)


def ncores_vs_thruput(save=False):
    df = _cached_read_csv("results/multicore/multicore_queries.csv")
    sb.set_context("talk")

    # print(df)
    # return

    fig, axes = plt.subplots(2, 2, figsize=(7, 8), sharey=True)

    # df = df[df['Algorithm'] != 'Memcpy']

    ycols = ['Compression speed', 'Decompression speed']

    rm_algos = ('Memcpy', 'SprintzDelta_Huf', 'SprintzDelta_Huf_16b')
    rm_mask = df['Algorithm'].apply(lambda s: s.split()[0]).isin(rm_algos)
    df = df[~rm_mask]

    # df['Ndims'] = df['Algorithm'].apply(lambda algo: -int(algo.split()[1]))
    df['Algorithm'] = df['Algorithm'].apply(_clean_algo_name)

    full_df = df
    uniq_algos = sorted(df['Algorithm'].unique())
    all_nbits = (8, 16)

    df = df['Query'] == 0

    # TODO plot max on left, sum on right, instead of comp and decomp
    for i, nbits in enumerate(all_nbits):
        df = full_df[full_df['Nbits'] == nbits]
        for j, col in enumerate(['Compression speed', 'Decompression speed']):
            ax = axes[i, j]
            for algo in uniq_algos:
                subdf = df[df['Algorithm'] == algo]
                x = subdf['Nthreads']
                y = subdf[col]
                ax.plot(x, y, label=algo, lw=1)

    # for ax, nbits in zip(axes[0, :], all_nbits):
    #     ax.set_title("{}-bit Values".format(nbits), fontsize=16)
    for ax in axes[:, 0]:
        # ax.set_ylabel("Decompression Speed\n(MB/s)", fontsize=14)
        ax.set_ylabel('Throughput (MB/s)', fontsize=14)
    for ax in axes[-1, :]:
        ax.set_xlabel("Number of Threads", fontsize=14)
    for ax in axes.ravel():
        ax.set_ylim([0, ax.get_ylim()[1]])

    # add byte counts on the right
    # fmt_str = "{}B Encodings"
    sb.set_style("white")  # adds border (spines) we have to remove
    # if len(use_ratios) > 1:
    #     for i, ax in enumerate(axes[:, -1]):
    #         ax2 = ax.twinx()
    #         sb.despine(ax=ax2, top=True, left=True, bottom=True, right=True)
    #         ax2.get_xaxis().set_visible(False)
    #         # ax2.get_yaxis().set_visible(False)  # nope, removes ylabel
    #         plt.setp(ax2.get_xticklabels(), visible=False)
    #         plt.setp(ax2.get_yticklabels(), visible=False)
    #         ax2.yaxis.set_label_position('right')
    #         # if len(use_ratios) == 2:
    #         #     lbl = "Incompressible Data" if i == 0 else "Highly Compressible Data"
    #         # else:
    #         #     lbl = "Compression Ratio = %d".format(int(use_ratios[i]))
    #         ax2.set_ylabel(lbl, labelpad=10, fontsize=14, family=CAMERA_READY_FONT)

    leg_lines, leg_labels = axes.ravel()[-1].get_legend_handles_labels()
    plt.figlegend(leg_lines, leg_labels, loc='lower center',
                  ncol=2, labelspacing=0)

    # plt.suptitle("Decompression Speed vs Number of Columns", fontweight='bold')
    plt.suptitle("Query Throughput vs Nthreads", fontweight='bold')
    plt.tight_layout()
    plt.subplots_adjust(top=.9, bottom=.26)

    if save:
        save_fig_png('multicore_queries')
    else:
        plt.show()


def main():
    # camera-ready can't have Type 3 fonts, which are what matplotlib
    # uses by default; 42 is apparently TrueType fonts
    mpl.rcParams['pdf.fonttype'] = 42
    mpl.rcParams['font.family'] = cfg.CAMERA_READY_FONT

    # print("USE_WHICH_ALGOS: ", cfg.USE_WHICH_ALGOS)

    # decomp_vs_ratio_fig(nbits=8)
    # decomp_vs_ratio_fig_success()
    # decomp_vs_ratio_fig_failure()
    # cd_diagram_ours_vs_others()
    # boxplot_ucr()
    # preproc_boxplot_ucr()
    # memlimit_boxplot_ucr()
    # decomp_vs_ndims_results()
    # comp_vs_ndims_results()
    # preproc_vs_ndims_results()
    quantize_err_results()
    # theoretical_thruput(save=False)
    # ncores_vs_thruput()


if __name__ == '__main__':
    main()
