#!/usr/bin/env python

from __future__ import division

import os
import numpy as np

from . import config as cfg
from . import files

DATASETS_DIR = cfg.DATASETS_DIR
# SYNTH_SAVE_PATH = os.path.join()

# _NBITS_TO_DTYPE = {8: np.uint8, 16: np.uint16}


def _create_synth_100M(nbits, ratio, size=int(100e6), save_path=None):
    # upper limit is set such that compression ratio should be ~2:1
    # dtype = _NBITS_TO_DTYPE[nbits]
    dtype = {8: np.uint8, 16: np.uint16}[nbits]
    target_ratio = {'low': cfg.SYNTH_LOW_COMPRESSION_RATIO,
                    'high': cfg.SYNTH_HIGH_COMPRESSION_RATIO}[ratio]
    # upper_lim = int((1 << (nbits) / target_ratio)
    upper_lim = int(2 ** (nbits / target_ratio))
    data = np.random.randint(0, upper_lim, size=size, dtype=dtype)

    if save_path is None:
        save_path = {(8, 'low'): cfg.SYNTH_100M_U8_LOW_PATH,
                     (16, 'low'): cfg.SYNTH_100M_U16_LOW_PATH,
                     (8, 'high'): cfg.SYNTH_100M_U8_HIGH_PATH,
                     (16, 'high'): cfg.SYNTH_100M_U16_HIGH_PATH}[(nbits, ratio)]

    files.ensure_dir_exists(os.path.dirname(save_path))
    # print "save_path", save_path
    # print "save_dir", os.path.dirname(save_path)
    data.tofile(save_path)


def create_synth_dense():
    _create_synth_100M(nbits=8, ratio='low')
    _create_synth_100M(nbits=16, ratio='low')
    _create_synth_100M(nbits=8, ratio='high')
    _create_synth_100M(nbits=16, ratio='high')


def main():
    create_synth_dense()


if __name__ == '__main__':
    main()
