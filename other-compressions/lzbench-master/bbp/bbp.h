#ifndef _BBP_H
#define _BBP_H

#include <stdint.h>

#define BBP_MAX_BLOCK_SIZE 4096

#define BBP_ALIGNMENT 32

/** initialize bbp library (not threadsafe) */
void bbp_init();

/** shutdown bbp library (not threadsafe) */
void bbp_shutdown();


/** compress a block of size \p len from \p in to \p out using block size \p
 * bs and \p bs_r, using deltas from \p offset
 *
 * This function should be used to compress relatively small chunks in the
 * range of several hundred kilobytes up to few megabytes so processing fits
 * the cache. The compressed output includes a 64 byte header which allows
 * decompression using bbp_decode().
 *
 * \param in input buffer, must be 16 byte aligned
 * \param out output buffer, must be 16 byte aligned, and fit at least
 *  bbp_max_compressed_size() bytes
 * \param bs primary block size, must be a power of 2 between 4 and 512. Use
 *  0 for the default of 16. In
 *  general a smaller block size results in better compression at slower speed
 * \param bs_r block size for the second compression step, must be a power of
 *  2 between 4 and 512, or 0 for the default of 32. Impact is relativeley low
 *  as long as content is not very compressible.
 * \param offset the coder calculates deltas from this offset, this should be
 *  the image width in bytes, or two times the image width for Bayer pattern
 *  data. Must be larger than 16, which is also a good default for unknown or
 *  not very compressible sources.
 * \return size of the compressed data
 */
int bbp_code_offset(uint8_t *in, uint8_t *out, int bs, int bs_r, int len, int offset);


/** decompress a block previously compressed using
 *
 * decompress a block from \p in to \p out, parameters are derived from the
 * header in \p
 * \param in input buffer, must be 16 byte aligned
 * \param out output buffer, must be 16 byte aligned, and fit the uncompressed
 *  size which can be read using bbp_header_sizes()
 * \return the size of the decompressed data is returned
 */
int bbp_decode(uint8_t *in, uint8_t *out);

/** read compressed and uncompressed sizes from header
 * \param buf the buffer which contains the 64 byte header
 * \param *size pointer to an integer where the uncompressed size will be written
 * \param *size_c the compressed size
 */
void bbp_header_sizes(uint8_t *buf, uint32_t *size, uint32_t *size_c);

/** returns the maximum output size of bbp_code_offset() for a given input size
 */
uint32_t bbp_max_compressed_size(uint32_t uncompressed);

#endif
