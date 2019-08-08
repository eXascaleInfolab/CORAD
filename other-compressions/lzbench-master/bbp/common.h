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

#ifndef _COMP_COMMON_H
#define _COMP_COMMON_H

#include "globals.h"

//TODO shifting on v16qi will use arithmetic shift (but we are always using unsigned!)
//FIXME dont use!
//typedef unsigned char block_vec __attribute__ ((vector_size (BLOCK_SIZE)));
typedef char v16qi __attribute__ ((vector_size (16)));
typedef long long v2di __attribute__ ((vector_size (16)));
typedef float v4sf __attribute__ ((vector_size (16)));
typedef uint32_t v4qi __attribute__ ((vector_size (16)));
typedef int16_t v8hi __attribute__ ((vector_size (16)));
typedef uint16_t v8qi __attribute__ ((vector_size (16)));
typedef int32_t v4si __attribute__ ((vector_size (16)));

//from http://burtleburtle.net/bob/rand/smallprng.html
typedef unsigned long int  u4;
typedef struct ranctx { u4 a; u4 b; u4 c; u4 d; } ranctx;

typedef struct {
  uint8_t count;
  uint8_t symbol;
} Sort_Data;

typedef struct {
  uint8_t *cur_data; //pointer to current data (only used for decoding atm
  uint8_t *block_buf; //block buffer
  uint8_t *signal_buf; //signal buffer
  uint8_t *cur_block; //pointer to current block
  uint8_t *cur_signal; //pointer to current(actually next unused) signal byte
  int cur_block_free_bits; //free bits left in cur_block (1-8)
  uint32_t block_byte_count; //FIXME remove
  uint32_t signal_byte_count; //FIXME remove
  uint8_t *data_buf;
  uint8_t last;
  int coder;
  int block_size;
  int text_coder_pos;
  int offset;
  int len, len_c;
} Block_Coder_Data;

typedef struct {
  int in_fd, out_fd;
  int decompress; //compress or decompress
  uint64_t compressed_size;
  uint64_t uncompressed_size;
  uint8_t *tmp_data;
  uint32_t inter_blocks;
  uint32_t intra_blocks;
  uint8_t *in_map;
  uint8_t *in_cur;
  uint64_t in_len;
  uint8_t *out_map;
  uint8_t *out_cur;
#ifdef USE_TEXT_COMP
  /*uint8_t order_1_lut[65536];
  uint32_t stats_order_1[65536];
  Sort_Data stat_sort_order_1[65536];*/
  uint8_t stats_order_2[HASH_MAX*256];
  int sum_order_2[HASH_MAX];
  //uint16_t *order_2_ind; //idx of 256b luts
  uint8_t *order_2_data;
  uint8_t *order_2_data_inv;
  int last_bucket;
#endif
  Block_Coder_Data block_coder_ctx;
  Block_Coder_Data signal_coder_ctx;
  int block_size;
  int block_size_r;
  ranctx rng_st;
} Comp_Context;

uint8_t *lut; //lut for wrapped delta mapping
uint8_t *lut_inv; //lut for wrapped delta mapping
uint8_t *clz_lut; //lut to count max bit usage
extern int inits_count;

#ifdef CALC_STATS
  uint32_t hist[9];
  uint32_t hist_ext[256];
#endif

u4 ranval( ranctx *x );
void raninit( ranctx *x, u4 seed );
uint8_t *get_wrap_lut(void);
uint8_t *get_wrap_lut_inv(void);
uint8_t *get_clz_lut(void);

#endif
