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

#ifndef _BBP_INTRINSICS_C_H
#define _BBP_INTRINSICS_C_H

#include "common.h"

#define LOAD_UA(T, S) memcpy(&(T), (S), 16);

CFINLINE v2di pand(v2di a, v2di b);
CFINLINE v2di pxor(v2di a, v2di b);
CFINLINE v2di por(v2di a, v2di b);
CFINLINE v16qi psubb(v16qi d, v16qi s);
CFINLINE v16qi paddusb(v16qi d, v16qi s);
CFINLINE v16qi psubusb(v16qi d, v16qi s);
CFINLINE v16qi pminub(v16qi d, v16qi s);
CFINLINE v16qi pmaxub(v16qi d, v16qi s);
CFINLINE v4si psrldi(v4si d, int n);
CFINLINE v16qi pcmpgtb(v16qi d, v16qi s);

CFINLINE v2di pand(v2di a, v2di b)
{
  return a & b;
}

CFINLINE v2di pxor(v2di a, v2di b)
{
  return a ^ b;
}

CFINLINE v2di por(v2di a, v2di b)
{
  return a | b;
}

CFINLINE v16qi psubb(v16qi d, v16qi s)
{
  int i;
  for(i=0;i<16;i++)
    d[i] = d[i]-s[i];
  
  return d;
}

CFINLINE v16qi paddusb(v16qi d, v16qi s)
{
  int i, tmp;
  for(i=0;i<16;i++) {
    tmp = (uint8_t)d[i]+(uint8_t)s[i];
    if (tmp >= 256)
      d[i] = 255;
    else
      d[i] = tmp;
  }
  
  return d;
}

CFINLINE v16qi psubusb(v16qi d, v16qi s)
{
  int i;
  for(i=0;i<16;i++) {
    if ((uint8_t)s[i] >= (uint8_t)d[i])
      d[i] = 0;
    else
      d[i] = (uint8_t)d[i]-(uint8_t)s[i];
  }
  
  return d;
}

CFINLINE v4si psrldi(v4si d, int n)
{
  int i;
  for(i=0;i<4;i++)
    d[i] = ((v4qi)d)[i] >> n;
  
  return d;
}


CFINLINE v16qi pcmpgtb(v16qi d, v16qi s)
{
  int i;
  for(i=0;i<16;i++)
    if (d[i] > s[i])
      d[i] = 0xFF;
      
  return d;
}


CFINLINE v16qi pminub(v16qi d, v16qi s)
{
  int i;
  for(i=0;i<16;i++)
    if ((uint8_t)d[i] > (uint8_t)s[i])
      d[i] = s[i];
      
  return d;
}


CFINLINE v16qi pmaxub(v16qi d, v16qi s)
{
  int i;
  for(i=0;i<16;i++)
    if ((uint8_t)d[i] < (uint8_t)s[i])
      d[i] = s[i];
      
  return d;
}

#endif