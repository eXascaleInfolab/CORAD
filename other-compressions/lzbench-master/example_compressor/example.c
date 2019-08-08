/*********************************************************************
  Blosc - Blocked Shuffling and Compression Library

  Author: Francesc Alted <francesc@blosc.org>
  Creation date: 2009-05-20

  See LICENSES/BLOSC.txt for details about copyright and rights to use.
**********************************************************************/

/*********************************************************************
  The code in this file is heavily based on FastLZ, a lightning-fast
  lossless compression library.  See LICENSES/FASTLZ.txt for details.
**********************************************************************/


#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include "example.h"

int example_compress(const void* input, int length, void* output, int maxout,
                     int opt_level, int custom_param)
{
  memcpy(output, input, length);
  return length;
}

int example_decompress(const void* input, int length, void* output, int maxout)
{
  memcpy(output, input, length);
  return length;
}
