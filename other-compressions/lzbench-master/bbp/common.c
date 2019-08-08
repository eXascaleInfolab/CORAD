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

#include "common.h"

#define rot(x,k) (((x)<<(k))|((x)>>(32-(k))))

u4 ranval( ranctx *x ) {
    u4 e = x->a - rot(x->b, 27);
    x->a = x->b ^ rot(x->c, 17);
    x->b = x->c + x->d;
    x->c = x->d + e;
    x->d = e + x->a;
    return x->d;
}

void raninit( ranctx *x, u4 seed ) {
    u4 i;
    x->a = 0xf1ea5eed, x->b = x->c = x->d = seed;
    for (i=0; i<20; ++i) {
        (void)ranval(x);
    }
}

int inits_count = 0;

//lut for wrapped diffs:
/* lut[n] - n
 * 0 - 0
 * 1 - 255
 * 2 - 1
 * 3 - 254
 * 4 - 2
 * 5 - 253
 * ...
 * 254 - 127
 * 255 - 128
 *
 * actually:
 * 0 - 0 	0	00000000
 * 1 - 2	1	00000010
 * 2 - 4	2	00000100
 * 3 - 6	3	00000110
 * 4 - 8	4	00001000
 * ...
 * 127 - 254		11111110
 * 128 - 255		11111111
 * 129 - 253		11111101
 * 130 - 251
 * ...
 * 2*n:
 * 	127 - 254
 * 	128 - 0
 * 	129 - 2
 * 	130 - 4
 *
 * (2*n) * (n-128)/128) + (n/128)*(255+128-n)
 */
uint8_t *get_wrap_lut(void)
{
  int n;
  uint8_t tmp;
  uint8_t *lut = (uint8_t*)malloc(256);

  for(n=0;n<256;n++) {
    lut[(256 - (n+1)/2)*(n%2)+n/2*((n+1)%2)] = n;
  }

  for(n=0;n<256;n++) {
    tmp = (2*n) * (((n+128)%256)/128) + (n/128)*(511-2*n);
    /* w 8-bit wraparound
      = 2*n*((n+128)/128) + (n/128)*(255-2*n)
      */
    assert(lut[n] == tmp);
  }

  return lut;
}


uint8_t *get_wrap_lut_inv(void)
{
  int n;
  uint8_t *lut = (uint8_t*)malloc(256);

  for(n=0;n<256;n++)
    lut[n] = (256 - (n+1)/2)*(n%2)+n/2*((n+1)%2);

  return lut;
}

uint8_t *get_clz_lut(void)
{
  int n;
  uint8_t *clz_lut = (uint8_t*)malloc(256);

  clz_lut[0] = 0;
  for(n=1;n<256;n++)
    clz_lut[n] = 32-__builtin_clz((uint32_t)n);


  return clz_lut;
}

void print_byte_bits(uint8_t b)
{
    unsigned char byte;
    int j;

    for (j=7;j>=0;j--)
    {
	byte = b & (1<<j);
	byte >>= j;
	printf("%u", byte);
    }
    printf(" ");
}
