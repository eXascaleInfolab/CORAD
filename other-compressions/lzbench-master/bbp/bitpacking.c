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

#include "bitpacking.h"
#include "intrinsics.h"
#include "intrinsics_c.h"

uint32_t mask_l[9] = { 0xFF, 0xFE, 0xFC, 0xF8, 0xF0, 0xE0, 0xC0, 0x80, 0x00};
uint32_t mask_r[9] = { 0xFF, 0x7F, 0x3F, 0x1F, 0x0F, 0x07, 0x03, 0x01, 0x00};

uint32_t mask4_l[9];
uint32_t mask4_r[9];
uint64_t mask8_l[9];
uint64_t mask8_r[9];

#ifdef BBP_USE_SSE
unsigned __int128 mask16_l[9];
unsigned __int128 mask16_r[9];
#endif

#ifdef BBP_USE_AVX2
__m256i mask32_l[9];
__m256i mask32_r[9];
#endif

v2di shift_precalc[9] = { {0, 0}, {1, 1}, {2, 2}, {3, 3}, {4, 4}, {5, 5}, {6, 6}, {7, 7}, {8, 8} };

#ifdef BBP_USE_NEON
v16qi shift_precalc_u8[9];
v16qi shift_precalc_neg_u8[9];
#endif

void init_masks(void)
{
  int i;

 for(i=0;i<9;i++) {
    memset(&mask4_l[i], mask_l[i], 4);
    memset(&mask4_r[i], mask_r[i], 4);
    memset(&mask8_l[i], mask_l[i], 8);
    memset(&mask8_r[i], mask_r[i], 8);
#ifdef BBP_USE_SSE
    memset(&mask16_l[i], mask_l[i], 16);
    memset(&mask16_r[i], mask_r[i], 16);
#endif
#ifdef BBP_USE_AVX2
    memset(&mask32_l[i], mask_l[i], 32);
    memset(&mask32_r[i], mask_r[i], 32);
#endif
  }

#ifdef BBP_USE_NEON
  int j;
  for(i=0;i<9;i++)
    for(j=0;j<16;j++) {
      (shift_precalc_u8[i])[j] = i;
      (shift_precalc_neg_u8[i])[j] = -i;
    }
#endif
}

/*
 * push current block to buf
 */
void next_block(Block_Coder_Data *b, const int block_size)
{
  b->cur_block += block_size;
}

/*
 * push current block to buf and write out if necessary
 */
void get_next_block(Block_Coder_Data *b, const int block_size)
{
  b->cur_block += block_size;
}

/*
 * push current block to buf and write out if necessary
 */
CFINLINE void next_signal(Block_Coder_Data *b, uint8_t signal)
{
  *b->cur_signal = signal;
  b->cur_signal++;
}

/*
 * get next signal
 */
uint8_t get_next_signal(Block_Coder_Data *b)
{
  uint8_t signal = *b->cur_signal;

  b->cur_signal++;

  return signal;
}


CFINLINE void push_block_1(Block_Coder_Data *b, uint8_t bits, uint8_t *block, const int block_size)
{
  int i;
  int shift;

  next_signal(b, bits);

  if (!bits)
    return;

  if (b->cur_block_free_bits >= bits) {
    //push block in the remaining free bits
    b->cur_block_free_bits -= bits;

    for(i=0;i<block_size;i++)
      b->cur_block[i] |= block[i] << b->cur_block_free_bits;

  }
  else {
    //first use up remaining free bits
    shift = bits - b->cur_block_free_bits;
    for(i=0;i<block_size;i++)
      b->cur_block[i] |= block[i] >> shift;
    next_block(b, block_size);
    //then write remaining bits into new block
    b->cur_block_free_bits = 8 + b->cur_block_free_bits - bits;
    for(i=0;i<block_size;i++)
      b->cur_block[i] = block[i] << b->cur_block_free_bits;
  }
}


void pull_block_1(Block_Coder_Data *b, uint8_t *block, const int block_size)
{
  int i;
  int shift;

  uint8_t bits = get_next_signal(b);

  if (!bits) {
    for(i=0;i<block_size;i++)
      block[i] = 0;

    return;
  }

  if (b->cur_block_free_bits >= bits) {
    b->cur_block_free_bits -= bits;

    if (b->cur_block_free_bits) {
      for(i=0;i<block_size;i++)
	block[i] = (b->cur_block[i] >> b->cur_block_free_bits) & mask_r[8-bits];
    }
    else {
      for(i=0;i<block_size;i++)
	block[i] = b->cur_block[i] & mask_r[8-bits];
      get_next_block(b, block_size);
      b->cur_block_free_bits = 8;
    }
  }
  else {
    //first use up remaining free bits
    shift = bits - b->cur_block_free_bits;
    for(i=0;i<block_size;i++)
      block[i] = (b->cur_block[i] & mask_r[8-b->cur_block_free_bits]) << shift;
    get_next_block(b, block_size);
    //then write remaining bits into new block
    b->cur_block_free_bits = 8 + b->cur_block_free_bits - bits;
    for(i=0;i<block_size;i++)
      block[i] |= b->cur_block[i] >> b->cur_block_free_bits;
  }
}

#ifdef BBP_USE_SSE
CFINLINE void pull_block_8(Block_Coder_Data *b, uint8_t *block, const int block_size)
{
  int i;
  int shift;
  uint64_t mask;
  uint8_t bits = get_next_signal(b);

  if (!bits) {
    for(i=0;i<block_size;i++)
      block[i] = 0;

    return;
  }

  if (b->cur_block_free_bits >= bits) {
    b->cur_block_free_bits -= bits;
    mask = mask8_r[8-bits];

    for(i=0;i<block_size/8;i++)
      ((uint64_t*)block)[i] = (((uint64_t*)b->cur_block)[i] >> b->cur_block_free_bits) & mask;
  }
  else {
    //first use up remaining free bits
    shift = bits - b->cur_block_free_bits;
    mask = mask8_r[8-b->cur_block_free_bits];
    for(i=0;i<block_size/8;i++)
      ((uint64_t*)block)[i] = (((uint64_t*)b->cur_block)[i] & mask) << shift;
    get_next_block(b, block_size);
    //then write remaining bits into new block
    b->cur_block_free_bits = 8 + b->cur_block_free_bits - bits;
    mask = mask8_l[b->cur_block_free_bits];
    for(i=0;i<block_size/8;i++)
      ((uint64_t*)block)[i] |= (((uint64_t*)b->cur_block)[i] & mask) >> b->cur_block_free_bits;
  }
}

CFINLINE void pull_block_16(Block_Coder_Data *b, uint8_t *block, int block_size)
{
  int i;
  int shift;
  v2di tmp_vec;
  v2di mask;
  v2di shift_vec;

  uint8_t bits = get_next_signal(b);

  if (!bits) {
    for(i=0;i<block_size;i++)
      block[i] = 0;

    return;
  }

  if (b->cur_block_free_bits >= bits) {
    b->cur_block_free_bits -= bits;
    mask = (v2di)mask16_r[8-bits];
    shift_vec =  shift_precalc[b->cur_block_free_bits];
    for(i=0;i<block_size/16;i++) {
      tmp_vec = __builtin_ia32_psrlq128(*(v2di*)(b->cur_block+i*16), shift_vec);
      *(v2di*)(block+i*16) = pand(tmp_vec, mask);
    }
  }
  else {
    //first use up remaining free bits
    shift = bits - b->cur_block_free_bits;
    mask = (v2di)mask16_r[8-b->cur_block_free_bits];
    shift_vec =  shift_precalc[shift];
    for(i=0;i<block_size/16;i++) {
      tmp_vec = pand(*(v2di*)(b->cur_block+i*16), mask);
      *(v2di*)(block+i*16) = __builtin_ia32_psllq128(tmp_vec, shift_vec);
    }
    get_next_block(b, block_size);
    //then write remaining bits into new block
    b->cur_block_free_bits = 8 + b->cur_block_free_bits - bits;
    mask = (v2di)mask16_l[b->cur_block_free_bits];
    shift_vec =  shift_precalc[b->cur_block_free_bits];
    for(i=0;i<block_size/16;i++) {
      tmp_vec = pand(*(v2di*)(b->cur_block+i*16), mask);
      tmp_vec = __builtin_ia32_psrlq128(tmp_vec, shift_vec);
      *(v2di*)(block+i*16) = por(*(v2di*)(block+i*16), tmp_vec);
    }
  }
}
#endif

CFINLINE void pull_block(Block_Coder_Data *b, uint8_t *block, const int block_size)
{
#ifdef BBP_USE_SSE
  if (block_size >= 16)
    pull_block_16(b, block, block_size);
   else if (block_size >= 8)
     pull_block_8(b, block, block_size);
  else
  // printf("pulling block with block_sz %d\n", block_size);
#endif
//TODO implement pull_block_4!
    pull_block_1(b, block, block_size);
}

CFINLINE void push_block_4(Block_Coder_Data *b, uint8_t bits, uint8_t *block, const int block_size)
{
  int i;
  int shift;
  uint32_t *block_4 = (uint32_t *)block;
  uint32_t *cur_block_4 = (uint32_t *)b->cur_block;
  uint32_t mask;

  next_signal(b, bits);

  //if (!bits)
    //return;

  if (b->cur_block_free_bits >= bits) {
    //push block in the remaining free bits
    b->cur_block_free_bits -= bits;

    for(i=0;i<block_size/4;i++)
      cur_block_4[i] |= block_4[i] << b->cur_block_free_bits;
  }
  else {
    //first use up remaining free bits
    shift = bits - b->cur_block_free_bits;
    mask = mask4_l[shift];
    for(i=0;i<block_size/4;i++)
      cur_block_4[i] |= (block_4[i] & mask) >> shift;
    next_block(b, block_size);
    cur_block_4 = (uint32_t *)b->cur_block;
    //then write remaining bits into new block
    b->cur_block_free_bits = 8 + b->cur_block_free_bits - bits;
    mask = mask4_r[b->cur_block_free_bits];
    for(i=0;i<block_size/4;i++)
      cur_block_4[i] = (block_4[i] & mask) << b->cur_block_free_bits;
  }
}

#ifdef BBP_USE_SSE

CFINLINE void push_block_8(Block_Coder_Data *b, uint8_t bits, uint8_t *block, const int block_size)
{
  int i;
  int shift;
  uint64_t *block_8 = (uint64_t *)block;
  uint64_t *cur_block_8 = (uint64_t *)b->cur_block;
  uint64_t mask;

  next_signal(b, bits);

  //if (!bits)
    //return;

  if (b->cur_block_free_bits >= bits) {
    //push block in the remaining free bits
    b->cur_block_free_bits -= bits;

    for(i=0;i<block_size/8;i++)
      cur_block_8[i] |= block_8[i] << b->cur_block_free_bits;
  }
  else {
    //first use up remaining free bits
    shift = bits - b->cur_block_free_bits;
    mask = mask8_l[shift];
    for(i=0;i<block_size/8;i++)
      cur_block_8[i] |= (block_8[i] & mask) >> shift;
    next_block(b, block_size);
    cur_block_8 = (uint64_t *)b->cur_block;
    //then write remaining bits into new block
    b->cur_block_free_bits = 8 + b->cur_block_free_bits - bits;
    mask = mask8_r[b->cur_block_free_bits];
    for(i=0;i<block_size/8;i++)
      cur_block_8[i] = (block_8[i] & mask) << b->cur_block_free_bits;
  }
}
#endif

#ifdef BBP_USE_SSE
CFINLINE void push_block_16(Block_Coder_Data *b, uint8_t bits, uint8_t *block, const int block_size)
{
  int i;
  int shift;
  unsigned __int128 *block_16 = (unsigned __int128 *)block;
  unsigned __int128 mask;
  v2di tmp_vec;
  v2di shift_vec;

  next_signal(b, bits);

  //NOTE on very compressible input this may improve performance
  //if (!bits)
    //return;

  if (b->cur_block_free_bits >= bits) {
    //push block in the remaining free bits
    b->cur_block_free_bits -= bits;

    shift_vec =  shift_precalc[b->cur_block_free_bits];
    for(i=0;i<block_size/16;i++) {
      tmp_vec = __builtin_ia32_psllq128((v2di)block_16[i], shift_vec);
      *(v2di*)(b->cur_block+i*16) = por(*(v2di*)(b->cur_block+i*16), tmp_vec);
    }
  }
  else {
    //first use up remaining free bits
    shift = bits - b->cur_block_free_bits;
    mask = mask16_l[shift];
    shift_vec =  shift_precalc[shift];
    for(i=0;i<block_size/16;i++) {
      tmp_vec = pand((v2di)block_16[i], (v2di)mask);
      tmp_vec = __builtin_ia32_psrlq128(tmp_vec, shift_vec);
      *(v2di*)(b->cur_block+i*16) = por(*(v2di*)(b->cur_block+i*16), tmp_vec);
    }
    next_block(b, block_size);
    //then write remaining bits into new block
    b->cur_block_free_bits = 8 + b->cur_block_free_bits - bits;
    mask = mask16_r[b->cur_block_free_bits];
    shift_vec =  shift_precalc[b->cur_block_free_bits];
    for(i=0;i<block_size/16;i++) {
      tmp_vec = pand((v2di)block_16[i], (v2di)mask);
      *(v2di*)(b->cur_block+i*16) = __builtin_ia32_psllq128(tmp_vec, shift_vec);
    }
  }
}
#endif


#ifdef BBP_USE_AVX2
CFINLINE void push_block_32(Block_Coder_Data *b, uint8_t bits, uint8_t *block_u8, const int block_size)
{
  int i;
  int shift;
  __m256i *block = (__m256i *)block_u8;
  __m256i mask;
  __m256i tmp_vec;
  v2di shift_vec;

  next_signal(b, bits);

  //NOTE on very compressible input this may improve performance
  //if (!bits)
    //return;

  if (b->cur_block_free_bits >= bits) {
    //push block in the remaining free bits
    b->cur_block_free_bits -= bits;

    shift_vec =  shift_precalc[b->cur_block_free_bits];
    for(i=0;i<block_size/32;i++) {
      tmp_vec = sll_4_32(block[i], shift_vec);
      *(__m256i*)(b->cur_block+i*32) = or_32(*(__m256*)(b->cur_block+i*32), tmp_vec);
    }
  }
  else {
    //first use up remaining free bits
    shift = bits - b->cur_block_free_bits;
    mask = mask32_l[shift];
    shift_vec =  shift_precalc[shift];
    for(i=0;i<block_size/32;i++) {
      tmp_vec = and_32(block[i], mask);
      tmp_vec = srl_4_32(tmp_vec, shift_vec);
      *(__m256i*)(b->cur_block+i*32) = or_32(*(__m256*)(b->cur_block+i*32), tmp_vec);
    }
    next_block(b, block_size);
    //then write remaining bits into new block
    b->cur_block_free_bits = 8 + b->cur_block_free_bits - bits;
    mask = mask32_r[b->cur_block_free_bits];
    shift_vec =  shift_precalc[b->cur_block_free_bits];
    for(i=0;i<block_size/32;i++) {
      tmp_vec = and_32(block[i], mask);
      *(__m256i*)(b->cur_block+i*32) = sll_4_32(tmp_vec, shift_vec);
    }
  }
}

#endif

#ifdef BBP_USE_NEON
CFINLINE void push_block_16(Block_Coder_Data *b, uint8_t bits, uint8_t *block, const int block_size)
{
  int i;
  int shift;
  v2di tmp_vec;
  v16qi shift_vec;

  next_signal(b, bits);

  //NOTE on very compressible input this may improve performance
  //if (!bits)
    //return;

  if (b->cur_block_free_bits >= bits) {
    //push block in the remaining free bits
    b->cur_block_free_bits -= bits;

    shift_vec =  shift_precalc_u8[b->cur_block_free_bits];
    for(i=0;i<block_size/16;i++) {
      tmp_vec = shl_u8x16(*(v2di*)(block+i*16), shift_vec);
      *(v2di*)(b->cur_block+i*16) = por(*(v2di*)(b->cur_block+i*16), tmp_vec);
    }
  }
  else {
    //first use up remaining free bits
    shift = bits - b->cur_block_free_bits;
    shift_vec =  shift_precalc_neg_u8[shift];
    for(i=0;i<block_size/16;i++) {
      tmp_vec = *(v2di*)(block+i*16);
      tmp_vec = shl_u8x16(tmp_vec, shift_vec);
      *(v2di*)(b->cur_block+i*16) = por(*(v2di*)(b->cur_block+i*16), tmp_vec);
    }
    next_block(b, block_size);
    //then write remaining bits into new block
    b->cur_block_free_bits = 8 + b->cur_block_free_bits - bits;
    shift_vec =  shift_precalc_u8[b->cur_block_free_bits];
    for(i=0;i<block_size/16;i++) {
      tmp_vec = *(v2di*)(block+i*16);
      *(v2di*)(b->cur_block+i*16) = shl_u8x16(tmp_vec, shift_vec);
    }
  }
}
#endif
/*
CFINLINE void push_block(Block_Coder_Data *b, int bits, uint8_t *diff, const int block_size)
{
#ifdef BBP_USE_NEON
  if (block_size >= 16)
    push_block_16(b, bits, diff, block_size);
  else
#elif BBP_USE_SSE
  if (block_size >= 16)
    push_block_16(b, bits, diff, block_size);
  else if (block_size >= 8) {
    printf("bp8\n");
    push_block_8(b, bits, diff, block_size);
  }
  else
#endif
  if (block_size >= 4) {
    printf("bp4\n");
    push_block_4(b, bits, diff, block_size);
  }
  else {
    printf("bp1\n");
    push_block_1(b, bits, diff, block_size);
  }
}*/

void push_block_chunk_dynamic(Block_Coder_Data *b, int *bits, uint8_t *diff, const int block_size, const int chunk_size)
{
  int i;

#ifdef BBP_USE_NEON
  if (block_size >= 16)
    for(i=0;i<chunk_size/block_size;i++)
      push_block_16(b, bits[i], diff+block_size*i, block_size);
  else
#endif
#if BBP_USE_AVX2
  if (block_size >= 32)
    for(i=0;i<chunk_size/block_size;i++)
      push_block_32(b, bits[i], diff+block_size*i, block_size);
  else
#endif
#if BBP_USE_SSE
  if (block_size >= 16)
    for(i=0;i<chunk_size/block_size;i++)
      push_block_16(b, bits[i], diff+block_size*i, block_size);
   else if (block_size == 8)
     for(i=0;i<chunk_size/block_size;i++)
       push_block_8(b, bits[i], diff+block_size*i, block_size);
  else
#endif
  if (block_size == 4)
    for(i=0;i<chunk_size/block_size;i++)
      push_block_4(b, bits[i], diff+block_size*i, block_size);
  else
    for(i=0;i<chunk_size/block_size;i++)
      push_block_1(b, bits[i], diff+block_size*i, block_size);
}


void push_block_chunk(Block_Coder_Data *b, int *bits, uint8_t *diff, const int block_size, const int chunk_size)
{

  switch (block_size) {
    case 4 : push_block_chunk_dynamic(b,bits,diff, 4, chunk_size); break;
    case 8 : push_block_chunk_dynamic(b,bits,diff, 8, chunk_size); break;
    case 16 : push_block_chunk_dynamic(b,bits,diff, 16, chunk_size); break;
    case 32 : push_block_chunk_dynamic(b,bits,diff, 32, chunk_size); break;
    case 64 : push_block_chunk_dynamic(b,bits,diff, 64, chunk_size); break;
    case 128 : push_block_chunk_dynamic(b,bits,diff, 128, chunk_size); break;
    case 256 : push_block_chunk_dynamic(b,bits,diff, 256, chunk_size); break;
    case 512 : push_block_chunk_dynamic(b,bits,diff, 512, chunk_size); break;
    case 1024 : push_block_chunk_dynamic(b,bits,diff, 1024, chunk_size); break;
    case 2048 : push_block_chunk_dynamic(b,bits,diff, 2048, chunk_size); break;
    case 4096 : push_block_chunk_dynamic(b,bits,diff, 4096, chunk_size); break;
    default : abort();
  }
}
