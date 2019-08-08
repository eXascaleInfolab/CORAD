/*********************************************************************
  Blosc - Blocked Shuffling and Compression Library

  Author: Francesc Alted <francesc@blosc.org>

  See LICENSES/BLOSC.txt for details about copyright and rights to use.
**********************************************************************/

/*********************************************************************
  The code in this file is heavily based on FastLZ, a lightning-fast
  lossless compression library.  See LICENSES/FASTLZ.txt for details
  about copyright and rights to use.
**********************************************************************/


#ifndef EXAMPLE_H
#define EXAMPLE_H

#if defined (__cplusplus)
extern "C" {
#endif

/**
  Compress a block of data in the input buffer and returns the size of
  compressed block. The size of input buffer is specified by
  length.

  The input buffer and the output buffer can not overlap.
*/

int example_compress(const void* input, int length, void* output, int maxout,
                     int opt_level, int custom_param);

int example_decompress(const void* input, int length, void* output, int maxout);

#if defined (__cplusplus)
}
#endif

#endif /* EXAMPLE_H */
