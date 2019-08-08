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

#include "coding_helpers.h"

#include "intrinsics.h"

void _code_diff_offset(uint8_t *n, uint8_t *diff, int off, int block_size)
{

#ifdef BBP_USE_AVX2
  __m256i p_vec, diff_vec, vec_a, vec_b, n_vec;
  __m256i vec128 = set1_1_32(128);;
  int j;

  for(j=0;j<block_size/32;j++) {
    LOAD_UA_32(p_vec, n-off+j*32)
    //TODO maybe add extra version for aligned offsets? But seems to be slower...
    //p_vec = *(v16qi*)(n-off+j*16);
    n_vec = *(__m256i*)(n+j*32);
    diff_vec = (__m256i)sub_u1_32(p_vec, n_vec);
    vec_a = (__m256i)add_sat_u1_32(diff_vec, diff_vec);
    vec_b = (__m256i)sub_sat_u1_32(diff_vec, vec128);
    vec_b = (__m256i)add_sat_u1_32(vec_b, vec_b);
    vec_b = ~vec_b;
    *(__m256i*)(diff+j*32) = min_u1_32(vec_a, vec_b);
  }
#else
  // #error "why is BBP_USE_AVX2 not defined?"
  v16qi p_vec, diff_vec, vec_a, vec_b, n_vec;
  v16qi vec128 = {128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128, 128};
  int j;

  for(j=0;j<block_size/16;j++) {
    LOAD_UA(p_vec, n-off+j*16)
    //TODO maybe add extra version for aligned offsets? But seems to be slower...
    //p_vec = *(v16qi*)(n-off+j*16);
    n_vec = *(v16qi*)(n+j*16);
    diff_vec = p_vec - n_vec;
    vec_a = paddusb(diff_vec, diff_vec);
    vec_b = psubusb(diff_vec, vec128);
    vec_b = paddusb(vec_b, vec_b);
    vec_b = ~vec_b;
    *(v16qi*)(diff+j*16) = pminub(vec_a, vec_b);
  }
#endif
}

void _decode_lut_inv_diff(uint8_t *dec, uint8_t *diff, uint8_t *off, int block_size)
{
  int j;
  v2di mask_odd = {0x0101010101010101, 0x0101010101010101};
  v2di mask_shift = {0xFEFEFEFEFEFEFEFE, 0xFEFEFEFEFEFEFEFE};
  v16qi v_0 = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
  v16qi val, odd_mask2;
  v16qi off_v, dec_v;

  for(j=0;j<block_size;j+=16) {
    val = *(v16qi*)(diff+j);
    odd_mask2 = (v16qi)pand(mask_odd, (v2di)val);
    odd_mask2 = pcmpgtb(odd_mask2, v_0);
    val = (v16qi)pand(mask_shift, (v2di)val);
    val = (v16qi)psrldi((v4si)val, 1);
    val = (v16qi)pxor((v2di)odd_mask2, (v2di)val);
    LOAD_UA(off_v, off+j)
    dec_v= off_v - val;
    memcpy(dec+j, &dec_v, 16);
  }
}

void _code_max(uint8_t *diff, int *bits, const int block_size)
{
  if (block_size >= 16) {
    int j;
    uint64_t max_l;
    uint8_t max;
    v2di max_v;

    max_v = *(v2di*)diff;
    for(j=1;j<block_size/16;j++)
      max_v = por((v2di)max_v, *(v2di*)(diff+j*16));
    max_l = max_v[0] | max_v[1];
    max_l |= max_l >> 32;
    max_l |= max_l >> 16;
    max_l |= max_l >> 8;
    max = max_l;

    *bits = clz_lut[max];
  }
  else if (block_size >= 8) {
    uint64_t max_l;
    uint8_t max;

    max_l = *(uint64_t*)diff;
    max_l |= max_l >> 32;
    max_l |= max_l >> 16;
    max_l |= max_l >> 8;
    max = max_l;

    *bits = clz_lut[max];
  }
  else if (block_size >= 4) {
    uint32_t max_l;
    uint8_t max;

    max_l = *(uint32_t*)diff;
    max_l |= max_l >> 16;
    max_l |= max_l >> 8;
    max = max_l;

    *bits = clz_lut[max];
  }
  else {
    int i;
    uint8_t max = 0;

    for(i=0;i<block_size;i++)
      max |= diff[i];
    *bits = clz_lut[max];
  }
}


void _code_max_chunk(uint8_t *diff, int *bits, const int block_size, const int chunk_size)
{
  assert(chunk_size % 16 == 0);

#ifdef BBP_USE_SSSE
  if (block_size >= 16) {
    int i;
    int j;
    v4si mask1 =  {0x000000FF,0x000000FF,0x000000FF,0x000000FF};
    v4si max_v[chunk_size/block_size];
    v4si tmp_v1, tmp_v2, tmp_max1, tmp_max2, tmp1, tmp2;

    for(i=0;i<chunk_size/block_size;i++) {
      max_v[i] = *(v4si*)(diff+i*block_size);
      for(j=1;j<block_size/16;j++)
	max_v[i] = (v4si)por((v2di)max_v[i], *(v2di*)(diff+i*block_size+j*16));
    }

    //process 4 blocks at the same time
    for(i=0;i<chunk_size/block_size;i+=4) {
      tmp_v1 = (v4si)punpckldq(max_v[i], max_v[i+1]);
      tmp_v2 = (v4si)punpckhdq(max_v[i], max_v[i+1]);
      tmp_max1 = (v4si)por((v2di)tmp_v1, (v2di)tmp_v2);
      tmp_v1 = (v4si)punpckldq(max_v[i+2], max_v[i+3]);
      tmp_v2 = (v4si)punpckhdq(max_v[i+2], max_v[i+3]);
      tmp_max2 = (v4si)por((v2di)tmp_v1, (v2di)tmp_v2);

      tmp_v1 = (v4si)punpckldq(tmp_max1, tmp_max2);
      tmp_v2 = (v4si)punpckhdq(tmp_max1, tmp_max2);

      tmp1 = (v4si)por((v2di)tmp_v1, (v2di)tmp_v2);

      tmp2 = __builtin_ia32_psrldi128(tmp1, 16);
      tmp1 = (v4si)por((v2di)tmp1, (v2di)tmp2);
      tmp2 = __builtin_ia32_psrldi128(tmp1, 8);
      tmp1 = (v4si)por((v2di)tmp1, (v2di)tmp2);

      tmp1 = (v4si)pand((v2di)tmp1, (v2di)mask1);

      bits[i] = clz_lut[tmp1[0]];
      bits[i+1] = clz_lut[tmp1[2]];
      bits[i+2] = clz_lut[tmp1[1]];
      bits[i+3] = clz_lut[tmp1[3]];
    }
  }
  else if (block_size == 8) {
    int i;
    v2di mask = {0x00000000000000FF, 0x00000000000000FF};
    v2di val, shift;

    for(i=0;i<chunk_size/16;i++) {
      val= *(v2di*)(diff+16*i);
      shift = __builtin_ia32_psrldqi128((v2di)val, 32);
      val = por((v2di)val, (v2di)shift);
      shift = __builtin_ia32_psrldqi128((v2di)val, 16);
      val = por((v2di)val, (v2di)shift);
      shift = __builtin_ia32_psrldqi128((v2di)val, 8);
      val = por((v2di)val, (v2di)shift);
      val = pand((v2di)val, (v2di)mask);

      bits[i*2] = clz_lut[val[0]];
      bits[i*2+1] = clz_lut[val[1]];
    }
  }
  else if (block_size == 4) {
    int i;

    v4qi mask = {0x000000FF, 0x000000FF, 0x000000FF, 0x000000FF};
    v4qi val, shift;

    for(i=0;i<chunk_size/16;i++) {
      val = *(v4qi*)(diff+16*i);
      shift = (v4qi)__builtin_ia32_psrldi128((v4si)val, 16);
      val = (v4qi)por((v2di)val, (v2di)shift);
      shift = (v4qi)__builtin_ia32_psrldi128((v4si)val, 8);
      val = (v4qi)por((v2di)val, (v2di)shift);
      val = (v4qi)pand((v2di)val, (v2di)mask);

      bits[i*4] = clz_lut[val[0]];
      bits[i*4+1] = clz_lut[val[1]];
      bits[i*4+2] = clz_lut[val[2]];
      bits[i*4+3] = clz_lut[val[3]];
    }
  }
  else
    abort();
#else
  int i;
  for(i=0;i<chunk_size/block_size;i++)
    _code_max(diff+i*block_size, bits+i, block_size);
#endif
}
