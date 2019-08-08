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

#include "coding.h"

#include "bitpacking.h"
#include "bitstream.h"
#include "coding_helpers.h"

static inline uint32_t calc_offset_start(Block_Coder_Data *b)
{
  uint32_t start;

  assert(b->offset >= BBP_ALIGNMENT);

  start = RU_N(b->offset, BBP_ALIGNMENT);

  if (start > b->len)
    start = b->len;

  return start;
}

void code_offset(Block_Coder_Data *b, uint8_t *stream, int len, uint8_t last, const int block_size)
{
  int i;
  int remain;
  int start;
  int bits_long[CHUNK_SIZE/block_size] __attribute__((aligned(BBP_ALIGNMENT)));
  uint8_t diff[CHUNK_SIZE] __attribute__((aligned(BBP_ALIGNMENT)));

  comp_coder_reset(b);

  //16byte aligned and >= offset
  start = calc_offset_start(b);

  assert(b->offset);

  if (start+block_size > len) {
    memcpy(b->cur_block, stream, len);
    //align up
    b->cur_block += RU_N(len, BBP_ALIGNMENT);
    b->len_c = RU_N(len, BBP_ALIGNMENT);
    return;
  }

  memcpy(b->cur_block, stream, start);
  i = start;
  //cur_block  is now BBP_ALIGNMENT aligned but may not be block aligned!
  b->cur_block += start;
  memset(b->cur_block, 0, block_size);

  //compress in CHUNK_SIZE chunks for performance (unrolling, cache locality etc.)
  for(;i<len-CHUNK_SIZE;i+=CHUNK_SIZE) {
    _code_diff_offset(stream+i,diff,b->offset,CHUNK_SIZE);
    _code_max_chunk(diff, bits_long, block_size, CHUNK_SIZE);
    push_block_chunk(b, bits_long, diff, block_size, CHUNK_SIZE);
  }

  //do coding for remaining blocks (<CHUNK_SIZE && >=16B)
  //TODO document: may be inlined+unrolled if user compiles with lto and len is constant!
  remain = (len-i)/(block_size*4)*(block_size*4)/BBP_ALIGNMENT*BBP_ALIGNMENT;
  _code_diff_offset(stream+i,diff,b->offset,remain);
  _code_max_chunk(diff, bits_long, block_size, remain);
  push_block_chunk(b, bits_long, diff, block_size, remain);
  i += remain;

  //if cur block is not empty - push it out
  if (b->cur_block_free_bits != 8) {
    next_block(b, block_size);
    b->cur_block_free_bits = 8;
  }

  //do memcpy for remaining bytes (<block_size || <16B)
  remain = len-i;
  memcpy(b->cur_block, stream+i, remain);
  b->cur_block += remain;
  i += remain;

  //align output up to BBP_ALIGNMENT bytes (small blocks or odd input len)
  //TODO set unused bytes to zero?
  if ((b->cur_block-b->block_buf) % BBP_ALIGNMENT)
    b->cur_block += BBP_ALIGNMENT - ((b->cur_block-b->block_buf) % BBP_ALIGNMENT);

  b->len_c = b->cur_block-b->block_buf;
  assert(i==len);
}

int offset_calc_signal_len(Block_Coder_Data *b)
{
  int len = b->len;
  int signal_len = 0;
  int i;
  int remain;
  int start;

  start = calc_offset_start(b);

  if (start+b->block_size > len)
    return 0;

  i = start;

  for(;i<len-CHUNK_SIZE;i+=CHUNK_SIZE)
    signal_len += CHUNK_SIZE/b->block_size;

  remain = (len-i)/(b->block_size*4)*(b->block_size*4)/16*16;
  signal_len += remain/b->block_size;

  return signal_len;
}

static void decode_offset(Block_Coder_Data *b, const int block_size)
{
  int remain;
  int i, n;
  uint8_t diff[CHUNK_SIZE] __attribute__((aligned(BBP_ALIGNMENT)));
  int start;

  printf("about to call comp_decoder_reset\n");

  comp_decoder_reset(b);

  //16byte aligned and >= offset
  start = calc_offset_start(b);

  printf("about to call memcpy some stuff\n");

  if (start+block_size > b->len) {
    memcpy(b->cur_data, b->cur_block, b->len);
    b->cur_data += b->len;
    b->len_c = b->len;
    return;
  }

  memcpy(b->cur_data, b->cur_block, start);
  i = start;
  //cur_block  is now BBP_ALIGNMENT bytes aligned but may not be block aligned!
  b->cur_data += start;
  b->cur_block += start;

  for(;i<b->len-CHUNK_SIZE;i+=CHUNK_SIZE) {
    printf("about to call pull_block a lot\n");
    for(n=0;n<CHUNK_SIZE;n+=block_size) {
      pull_block(b, diff+n, block_size);
    }
    printf("about to _decode_lut_inv_diff\n");
    _decode_lut_inv_diff(b->cur_data, diff, b->data_buf+i-b->offset, CHUNK_SIZE);
    b->cur_data+= CHUNK_SIZE;
  }

  remain = (b->len-i)/(b->block_size*4)*(b->block_size*4)/BBP_ALIGNMENT*BBP_ALIGNMENT;
  printf("about to pull block at end\n");
  for(n=0;n<remain;n+=block_size) {
    pull_block(b, diff+n, block_size);
  }
  printf("about to _decode_lut_inv_diff\n");
  _decode_lut_inv_diff(b->cur_data, diff, b->cur_data-b->offset, remain);
  b->cur_data += remain;
  i+= remain;

  //we already pulled the partially free block, need to point to next one
  if (b->cur_block_free_bits != 8) {
    b->cur_block += block_size;
    b->cur_block_free_bits = 8;
  }

  remain = b->len-i;
  memcpy(b->cur_data, b->cur_block, remain);
  b->cur_data += remain;
  b->cur_block += remain;
  i += remain;

  b->len_c = i;
  assert(b->cur_data-b->data_buf==b->len);
}

void decode(Block_Coder_Data *b)
{
  if (b->coder == CODER_OFFSET) {
    switch (b->block_size)
    {
      case 4 : decode_offset(b, 4); break;
      case 8 : decode_offset(b, 8); break;
      case 16 : decode_offset(b, 16); break;
      case 32 : decode_offset(b, 32); break;
      case 64 : decode_offset(b, 64); break;
      case 128 : decode_offset(b, 128); break;
      case 256 : decode_offset(b, 256); break;
      case 512 : decode_offset(b, 512); break;
      case 1024 : decode_offset(b, 1024); break;
      case 2048 : decode_offset(b, 2048); break;
      case 4096 : decode_offset(b, 4096); break;
      default :
	abort();
    }
  }
  else
    abort();
}

void code(Block_Coder_Data *b, uint8_t *in, int len)
{
  if (b->coder == CODER_OFFSET) {
    switch (b->block_size)
    {
      case 4 : code_offset(b, in, len, 0, 4); break;
      case 8 : code_offset(b, in, len, 0, 8); break;
      case 16 : code_offset(b, in, len, 0, 16); break;
      case 32 : code_offset(b, in, len, 0, 32); break;
      case 64 : code_offset(b, in, len, 0, 64); break;
      case 128 : code_offset(b, in, len, 0, 128); break;
      case 256 : code_offset(b, in, len, 0, 256); break;
      case 512 : code_offset(b, in, len, 0, 512); break;
      case 1024 : code_offset(b, in, len, 0, 1024); break;
      case 2048 : code_offset(b, in, len, 0, 2048); break;
      case 4096 : code_offset(b, in, len, 0, 4096); break;
      default :
	abort();
    }
  }
  else
    abort();
}
