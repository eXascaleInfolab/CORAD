/*
 *
 *  BBP - high speed image compressor using block-wise bitpacking
 *
 *  Copyright (C) 2014-2015 Hendrik Siedelmann <hendrik.siedelmann@googlemail.com>
 *
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 */

#ifndef _COMP_CODING_HELPERS_H
#define _COMP_CODING_HELPERS_H

#include "common.h"
#include "bitpacking.h"

CFINLINE void _code_intra_max(uint8_t *diff, int *bits, const int block_size);
CFINLINE void _code_intra_diff(uint8_t *n, uint8_t *diff, v16qi *n_vec, const int block_size);
CFINLINE void _diff_pred_jpegls(uint8_t *n, uint8_t *diff, int stride, int block_size);
CFINLINE void _diff_chunk_prefetch(uint8_t *n, uint8_t *diff, v16qi *n_vec, int len);
CFINLINE void _diff_chunk(uint8_t *n, uint8_t *diff, v16qi *n_vec, int len);
CFINLINE void _code_diff_offset(uint8_t *n, uint8_t *diff, int off, int block_size);
CFINLINE void _code_max(uint8_t *diff, int *bits, const int block_size);
CFINLINE void _code_max_chunk(uint8_t *diff, int *bits, const int block_size, const int chunk_size);
CFINLINE void _decode_lut_inv_diff(uint8_t *dec, uint8_t *diff, uint8_t *off, int block_size);

#endif