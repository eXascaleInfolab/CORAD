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

#ifndef _BBP_INTR_H
#define _BBP_INTR_H

// #ifdef __AVX2__
//     #define BBP_USE_AVX2 1
// #endif
    // #define BBP_USE_SIMD 1
    // #define BBP_USE_SSE 1
    // #define BBP_USE_SSSE 1
// #else
    // #error "Requires a machine with avx2 for now..."
// #endif

#ifdef BBP_USE_AVX2
#include <immintrin.h>

typedef int32_t v8si __attribute__ ((vector_size (16)));

//bitvector
#define or_32(A,B) _mm256_or_si256((__m256i)A,(__m256i)B)
#define and_32(A,B) _mm256_and_si256((__m256i)A,(__m256i)B)
#define LOAD_UA_32(T, S) memcpy(&(T), (S), 32);

//vector with n-byte divion
#define sll_4_32(A,B) _mm256_sll_epi32((__m256i)A, (__m128i)B)
#define srl_4_32(A,B) _mm256_srl_epi32((__m256i)A, (__m128i)B)
#define srl_4_32(A,B) _mm256_srl_epi32((__m256i)A, (__m128i)B)
#define sub_u1_32(A,B) _mm256_sub_epi8((__m256i)A, (__m256i)B)
#define sub_sat_u1_32(A,B) _mm256_subs_epi8((__m256i)A, (__m256i)B)
#define add_u1_32(A,B) _mm256_add_epi8((__m256i)A, (__m256i)B)
#define add_sat_u1_32(A,B) _mm256_adds_epi8((__m256i)A, (__m256i)B)
#define min_u1_32(A,B) _mm256_min_epu8((__m256i)A, (__m256i)B)
#define max_u1_32(A,B) _mm256_max_epu8((__m256i)A, (__m256i)B)

#define set1_1_32(A) _mm256_set1_epi8((char)A)



//typed vecto


#endif

#ifdef BBP_USE_SSE
#ifdef COMPILER_GCC

#define pand      __builtin_ia32_pand128
#define psubb     __builtin_ia32_psubb128
#define pxor      __builtin_ia32_pxor128
#define pcmpgtb   __builtin_ia32_pcmpgtb128
#define por       __builtin_ia32_por128
#define punpckldq __builtin_ia32_punpckldq128
#define punpckhdq __builtin_ia32_punpckhdq128
#define punpcklwd __builtin_ia32_punpcklwd128
#define punpckhwd __builtin_ia32_punpckhwd128
#define punpcklbw __builtin_ia32_punpcklbw128
#define punpckhbw __builtin_ia32_punpckhbw128
#define pmullw    __builtin_ia32_pmullw128
#define pshufd    __builtin_ia32_pshufd
#define addps     __builtin_ia32_addps
#define subps     __builtin_ia32_subps
#define mulps     __builtin_ia32_mulps
#define paddd     __builtin_ia32_paddd128
#define paddusb   __builtin_ia32_paddusb128
#define psubusb   __builtin_ia32_psubusb128
#define psrldi    __builtin_ia32_psrldi128
#define pminub    __builtin_ia32_pminub128
#define pmaxub    __builtin_ia32_pmaxub128

#define LOAD_UA(T, S) memcpy(&(T), (S), 16);

#elif COMPILER_CLANG

#include <mmintrin.h>

#define pand      _mm_and_si128
#define psubb     _mm_sub_epi8
#define pxor      _mm_xor_si128
#define pcmpgtb   _mm_cmpgt_epi8
#define por       _mm_or_si128
#define punpckldq _mm_unpacklo_epi32
#define punpckhdq _mm_unpackhi_epi32
#define punpcklwd _mm_unpacklo_epi16
#define punpckhwd _mm_unpackhi_epi16
#define punpcklbw _mm_unpacklo_epi8
#define punpckhbw _mm_unpackhi_epi8
#define pmullw    _mm_mullo_epi16
#define pshufd    _mm_shuffle_epi32
#define addps     _mm_add_ps
#define subps     _mm_sub_ps
#define mulps     _mm_mul_ps
#define paddd     _mm_add_epi64
#define paddusb   _mm_adds_epu8
#define psubusb   _mm_subs_epu8
#define psrldi    _mm_srli_epi32
#define pminub    _mm_min_epu8
#define pmaxub    _mm_max_epu8

#define LOAD_UA(T, S) memcpy(&(T), (S), 16);

#endif

#elif BBP_USE_NEON
#include "arm_neon.h"

#define pminub    vminq_u8
#define pmaxub    vmaxq_u8

#define paddb     vaddq_u8
#define paddusb   vqaddq_u8
#define psubb     vsubq_u8
#define psubusb   vqsubq_u8

#define pand      vandq_u8
#define por       vorrq_u8
#define pxor      veorq_u8

//FIXME check gcc version?
#define pcmpgtb   vcgtq_u8

#define psrldi    vshrq_n_u8

#define shl_u8x16 vshlq_u8
#define shl_u64x2 vshlq_u64

#define LOAD_UA(T, S) (T) = vld1q_u8(S);

#else
#include "intrinsics_c.h"
#endif

#endif
