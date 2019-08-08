#include "compressors.h"
#include "query_common.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h> // memcpy

#ifndef MAX
    #define MAX(a,b) ((a)>(b))?(a):(b)
#endif
#ifndef MIN
	#define MIN(a,b) ((a)<(b)?(a):(b))
#endif


int64_t lzbench_memcpy(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t , size_t, void* )
{
    memcpy(outbuf, inbuf, insize);
    return insize;
}

int64_t lzbench_return_0(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t , size_t, void* )
{
    return 0;
}


// #ifndef BENCH_REMOVE_BLOSCLZ
// #include "blosclz/blosclz.h"

// int64_t lzbench_blosclz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
// {
//     return blosclz_compress(level, inbuf, insize, outbuf, outsize, 1);
// }

// int64_t lzbench_blosclz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t , size_t, void*)
// {
//     return blosclz_decompress(inbuf, insize, outbuf, outsize);
// }

// #endif


#ifndef BENCH_REMOVE_BRIEFLZ
#include "brieflz/brieflz.h"

char* lzbench_brieflz_init(size_t insize, size_t level, size_t)
{
    return (char*) malloc(blz_workmem_size(insize));
}

void lzbench_brieflz_deinit(void* workmem)
{
    free((char*)workmem);
}

int64_t lzbench_brieflz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
    if (!workmem)
        return 0;

    int64_t res = blz_pack(inbuf, outbuf, insize, (void*)workmem);

    return res;
}

int64_t lzbench_brieflz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
    return blz_depack_safe(inbuf, insize, outbuf, outsize);
}

#endif



#ifndef BENCH_REMOVE_BROTLI
#include "brotli/encode.h"
#include "brotli/decode.h"

int64_t lzbench_brotli_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t windowLog, void*)
{
    if (!windowLog) windowLog = BROTLI_DEFAULT_WINDOW; // sliding window size. Range is 10 to 24.

    size_t actual_osize = outsize;
    return BrotliEncoderCompress(level, windowLog, BROTLI_DEFAULT_MODE, insize, (const uint8_t*)inbuf, &actual_osize, (uint8_t*)outbuf) == 0 ? 0 : actual_osize;
}
int64_t lzbench_brotli_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
    size_t actual_osize = outsize;
    return BrotliDecoderDecompress(insize, (const uint8_t*)inbuf, &actual_osize, (uint8_t*)outbuf) == BROTLI_DECODER_RESULT_ERROR ? 0 : actual_osize;
}

#endif




#ifndef BENCH_REMOVE_CRUSH
#include "crush/crush.hpp"

int64_t lzbench_crush_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	return crush::compress(level, (uint8_t*)inbuf, insize, (uint8_t*)outbuf);
}

int64_t lzbench_crush_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	return crush::decompress((uint8_t*)inbuf, (uint8_t*)outbuf, outsize);
}

#endif



#ifndef BENCH_REMOVE_CSC
#include "libcsc/csc_enc.h"
#include "libcsc/csc_dec.h"
#include <string.h> // memcpy

struct MemSeqStream
{
    union {
        ISeqInStream is;
        ISeqOutStream os;
    };
    char *buf;
	size_t len;
};


int stdio_read(void *p, void *buf, size_t *size)
{
    MemSeqStream *sss = (MemSeqStream *)p;
//    *size = fread(buf, 1, *size, sss->f);
	if (*size > sss->len)
		*size = sss->len;
	memcpy(buf, sss->buf, *size);
	sss->buf += *size;
	sss->len -= *size;
    return 0;
}

size_t stdio_write(void *p, const void *buf, size_t size)
{
    MemSeqStream *sss = (MemSeqStream *)p;

	memcpy(sss->buf, buf, size);
	sss->buf += size;
	sss->len += size;
    return size;
}

int64_t lzbench_csc_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t dict_size, void*)
{
	MemSeqStream isss, osss;
	CSCProps p;
	if (!dict_size) dict_size = 1<<26;

	if (insize < dict_size)
		dict_size = insize;

	CSCEncProps_Init(&p, dict_size, level);
	CSCEnc_WriteProperties(&p, (uint8_t*)outbuf, 0);

    isss.is.Read = stdio_read;
    isss.buf = inbuf;
	isss.len = insize;

    osss.os.Write = stdio_write;
    osss.buf = outbuf + CSC_PROP_SIZE;
	osss.len = CSC_PROP_SIZE;

	CSCEncHandle h = CSCEnc_Create(&p, (ISeqOutStream*)&osss, NULL);
	CSCEnc_Encode(h, (ISeqInStream*)&isss, NULL);
	CSCEnc_Encode_Flush(h);
	CSCEnc_Destroy(h);

//	printf("Estimated memory usage: %llu MB\n", CSCEnc_EstMemUsage(&p) / 1048576ull);
//	printf("insize=%lld osss.len=%lld\n", insize, osss.len);

	return osss.len;
}

int64_t lzbench_csc_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	MemSeqStream isss, osss;
	CSCProps p;

	CSCDec_ReadProperties(&p, (uint8_t*)inbuf);

    isss.is.Read = stdio_read;
    isss.buf = inbuf + CSC_PROP_SIZE;
	isss.len = insize - CSC_PROP_SIZE;

    osss.os.Write = stdio_write;
    osss.buf = outbuf;
	osss.len = 0;

	CSCDecHandle h = CSCDec_Create(&p, (ISeqInStream*)&isss, NULL);
	CSCDec_Decode(h, (ISeqOutStream*)&osss, NULL);
	CSCDec_Destroy(h);

	return osss.len;
}

#endif



#ifndef BENCH_REMOVE_DENSITY
extern "C"
{
	#include "density/density_api.h"
}

int64_t lzbench_density_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	density_buffer_processing_result result = density_buffer_compress((uint8_t *)inbuf, insize, (uint8_t *)outbuf, outsize, (DENSITY_COMPRESSION_MODE)level, DENSITY_BLOCK_TYPE_DEFAULT, NULL, NULL);
	if (result.state)
		return 0;

	return result.bytesWritten;
}

int64_t lzbench_density_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
    density_buffer_processing_result result = density_buffer_decompress((uint8_t *)inbuf, insize, (uint8_t *)outbuf, outsize, NULL, NULL);
	if (result.state)
		return 0;

	return result.bytesWritten;
}

#endif



#ifndef BENCH_REMOVE_FASTLZ
extern "C"
{
	#include "fastlz/fastlz.h"
}

int64_t lzbench_fastlz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	return fastlz_compress_level(level, inbuf, insize, outbuf);
}

int64_t lzbench_fastlz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	return fastlz_decompress(inbuf, insize, outbuf, outsize);
}

#endif


#ifndef BENCH_REMOVE_GIPFELI
#include "gipfeli/gipfeli.h"

int64_t lzbench_gipfeli_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
    int64_t res;
    util::compression::Compressor *gipfeli = util::compression::NewGipfeliCompressor();
    if (gipfeli)
    {
        util::compression::UncheckedByteArraySink sink((char*)outbuf);
        util::compression::ByteArraySource src((const char*)inbuf, insize);
        res = gipfeli->CompressStream(&src, &sink);
        delete gipfeli;
    }
    else res=0;
    return res;
}

int64_t lzbench_gipfeli_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
    int64_t res = 0;
    util::compression::Compressor *gipfeli = util::compression::NewGipfeliCompressor();
    if (gipfeli)
    {
        util::compression::UncheckedByteArraySink sink((char*)outbuf);
        util::compression::ByteArraySource src((const char*)inbuf, insize);
        if (gipfeli->UncompressStream(&src, &sink))
            res = outsize;
        delete gipfeli;
    }
    return res;
}

#endif



#ifndef BENCH_REMOVE_GLZA
#include "glza/GLZAcomp.h"
#include "glza/GLZAdecode.h"

int64_t lzbench_glza_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	if (GLZAcomp(insize, (uint8_t *)inbuf, &outsize, (uint8_t *)outbuf, (FILE *)0, NULL) == 0) return(0);
	return outsize;
}

int64_t lzbench_glza_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	if (GLZAdecode(insize, (uint8_t *)inbuf, &outsize, (uint8_t *)outbuf, (FILE *)0) == 0) return(0);
	return outsize;
}

#endif



#ifndef BENCH_REMOVE_LIBDEFLATE
#include "libdeflate/libdeflate.h"
int64_t lzbench_libdeflate_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
    struct libdeflate_compressor *compressor = libdeflate_alloc_compressor(level);
    if (!compressor)
        return 0;
    int64_t res = libdeflate_deflate_compress(compressor, inbuf, insize, outbuf, outsize);
    libdeflate_free_compressor(compressor);
    return res;
}
int64_t lzbench_libdeflate_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
    struct libdeflate_decompressor *decompressor = libdeflate_alloc_decompressor();
    if (!decompressor)
        return 0;
    size_t res = 0;
    if (libdeflate_deflate_decompress(decompressor, inbuf, insize, outbuf, outsize, &res) != LIBDEFLATE_SUCCESS) {
        return 0;
    }
    return res;
}
#endif



#ifndef BENCH_REMOVE_LIZARD
#include "lizard/lizard_compress.h"
#include "lizard/lizard_decompress.h"

int64_t lzbench_lizard_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	return Lizard_compress(inbuf, outbuf, insize, outsize, level);
}

int64_t lzbench_lizard_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	return Lizard_decompress_safe(inbuf, outbuf, insize, outsize);
}

#endif



#ifndef BENCH_REMOVE_LZ4
#include "lz4/lz4.h"
#include "lz4/lz4hc.h"

int64_t lzbench_lz4_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	return LZ4_compress_default(inbuf, outbuf, insize, outsize);
}

int64_t lzbench_lz4fast_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	return LZ4_compress_fast(inbuf, outbuf, insize, outsize, level);
}

int64_t lzbench_lz4hc_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	return LZ4_compress_HC(inbuf, outbuf, insize, outsize, level);
}

int64_t lzbench_lz4_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	return LZ4_decompress_safe(inbuf, outbuf, insize, outsize);
}

#endif



#ifndef BENCH_REMOVE_LZF
extern "C"
{
	#include "lzf/lzf.h"
}

int64_t lzbench_lzf_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	if (level == 0)
		return lzf_compress(inbuf, insize, outbuf, outsize);
	return lzf_compress_very(inbuf, insize, outbuf, outsize);
}

int64_t lzbench_lzf_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	return lzf_decompress(inbuf, insize, outbuf, outsize);
}

#endif



#ifndef BENCH_REMOVE_LZFSE
extern "C"
{
	#include "lzfse/lzfse.h"
}

char* lzbench_lzfse_init(size_t insize, size_t level, size_t)
{
    return (char*) malloc(MAX(lzfse_encode_scratch_size(), lzfse_decode_scratch_size()));
}

void lzbench_lzfse_deinit(void* workmem)
{
    free((char*)workmem);
}

int64_t lzbench_lzfse_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
	return lzfse_encode_buffer((uint8_t*)outbuf, outsize, (uint8_t*)inbuf, insize, (char*)workmem);
}

int64_t lzbench_lzfse_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void* workmem)
{
	return lzfse_decode_buffer((uint8_t*)outbuf, outsize, (uint8_t*)inbuf, insize, (char*)workmem);
}

#endif



#ifndef BENCH_REMOVE_LZVN
extern "C"
{
	#include "lzfse/lzvn.h"
}

char* lzbench_lzvn_init(size_t insize, size_t level, size_t)
{
    return (char*) malloc(MAX(lzvn_encode_scratch_size(), lzvn_decode_scratch_size()));
}

void lzbench_lzvn_deinit(void* workmem)
{
    free((char*)workmem);
}

int64_t lzbench_lzvn_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
	return lzvn_encode_buffer((uint8_t*)outbuf, outsize, (uint8_t*)inbuf, insize, (char*)workmem);
}

int64_t lzbench_lzvn_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void* workmem)
{
	return lzvn_decode_buffer_scratch((uint8_t*)outbuf, outsize, (uint8_t*)inbuf, insize, (char*)workmem);
}

#endif



#ifndef BENCH_REMOVE_LZG
#include "liblzg/lzg.h"

int64_t lzbench_lzg_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
    lzg_encoder_config_t cfg;
    cfg.level = level;
    cfg.fast = LZG_TRUE;
    cfg.progressfun = NULL;
    cfg.userdata = NULL;
    return LZG_Encode((const unsigned char*)inbuf, insize, (unsigned char*)outbuf, outsize, &cfg);
}

int64_t lzbench_lzg_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
    return LZG_Decode((const unsigned char*)inbuf, insize, (unsigned char*)outbuf, outsize);
}

#endif



#ifndef BENCH_REMOVE_LZHAM
#include "lzham/lzham.h"
#include <memory.h>

int64_t lzbench_lzham_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t dict_size_log, void*)
{
	lzham_compress_params comp_params;
	memset(&comp_params, 0, sizeof(comp_params));
	comp_params.m_struct_size = sizeof(lzham_compress_params);
	comp_params.m_dict_size_log2 = dict_size_log?dict_size_log:26;
	comp_params.m_max_helper_threads = 0;
	comp_params.m_level = (lzham_compress_level)level;

	lzham_compress_status_t comp_status;
	lzham_uint32 comp_adler32 = 0;

	if ((comp_status = lzham_compress_memory(&comp_params, (uint8_t*)outbuf, &outsize, (const lzham_uint8 *)inbuf, insize, &comp_adler32)) != LZHAM_COMP_STATUS_SUCCESS)
	{
		printf("Compression test failed with status %i!\n", comp_status);
		return 0;
	}

	return outsize;
}

int64_t lzbench_lzham_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t dict_size_log, void*)
{
	lzham_uint32 comp_adler32 = 0;
	lzham_decompress_params decomp_params;

	memset(&decomp_params, 0, sizeof(decomp_params));
	decomp_params.m_struct_size = sizeof(decomp_params);
	decomp_params.m_dict_size_log2 = dict_size_log?dict_size_log:26;

	lzham_decompress_memory(&decomp_params, (uint8_t*)outbuf, &outsize, (const lzham_uint8 *)inbuf, insize, &comp_adler32);
	return outsize;
}

#endif



#ifndef BENCH_REMOVE_LZJB
#include "lzjb/lzjb2010.h"

int64_t lzbench_lzjb_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	return lzjb_compress2010((uint8_t*)inbuf, (uint8_t*)outbuf, insize, outsize, 0);
}

int64_t lzbench_lzjb_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	return lzjb_decompress2010((uint8_t*)inbuf, (uint8_t*)outbuf, insize, outsize, 0);
}

#endif



#ifndef BENCH_REMOVE_LZLIB
#include "lzlib/lzlib.h"

int64_t lzbench_lzlib_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
  struct Lzma_options
  {
      int dictionary_size;		/* 4 KiB .. 512 MiB */
      int match_len_limit;		/* 5 .. 273 */
  };

  const struct Lzma_options option_mapping[10] = {
    {   65535,  16 },		/* -0 */
    { 1 << 20,   5 },		/* -1 */
    { 3 << 19,   6 },		/* -2 */
    { 1 << 21,   8 },		/* -3 */
    { 3 << 20,  12 },		/* -4 */
    { 1 << 22,  20 },		/* -5 */
    { 1 << 23,  36 },		/* -6 */
    { 1 << 24,  68 },		/* -7 */
    { 3 << 23, 132 },		/* -8 */
    { 1 << 25, 273 } };		/* -9 */

  struct LZ_Encoder * encoder;
  const int match_len_limit = option_mapping[level].match_len_limit;
  const unsigned long long member_size = 0x7FFFFFFFFFFFFFFFULL;	/* INT64_MAX */
  int new_pos = 0;
  int written = 0;
  bool error = false;
  int dict_size = option_mapping[level].dictionary_size;
  uint8_t *buf = (uint8_t*)inbuf;
  uint8_t *obuf = (uint8_t*)outbuf;


  if( dict_size > insize ) dict_size = insize;		/* saves memory */
  if( dict_size < LZ_min_dictionary_size() )
    dict_size = LZ_min_dictionary_size();
  encoder = LZ_compress_open( dict_size, match_len_limit, member_size );
  if( !encoder || LZ_compress_errno( encoder ) != LZ_ok )
    { LZ_compress_close( encoder ); return 0; }

  while( true )
    {
    int rd;
    if( LZ_compress_write_size( encoder ) > 0 )
      {
      if( written < insize )
        {
        const int wr = LZ_compress_write( encoder, buf + written, insize - written );
        if( wr < 0 ) { error = true; break; }
        written += wr;
        }
      if( written >= insize ) LZ_compress_finish( encoder );
      }
    rd = LZ_compress_read( encoder, obuf + new_pos, outsize - new_pos );
    if( rd < 0 ) { error = true; break; }
    new_pos += rd;
    if( LZ_compress_finished( encoder ) == 1 ) break;
    }

  if( LZ_compress_close( encoder ) < 0 ) error = true;
  if (error) return 0;

  return new_pos;
}


int64_t lzbench_lzlib_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
  struct LZ_Decoder * const decoder = LZ_decompress_open();
  uint8_t * new_data = (uint8_t*)outbuf;
  int new_data_size = outsize;		/* initial size */
  int new_pos = 0;
  int written = 0;
  bool error = false;
  uint8_t *data = (uint8_t*)inbuf;


  if( !decoder || LZ_decompress_errno( decoder ) != LZ_ok )
    { LZ_decompress_close( decoder ); return 0; }

  while( true )
    {
    int rd;
    if( LZ_decompress_write_size( decoder ) > 0 )
      {
      if( written < insize )
        {
        const int wr = LZ_decompress_write( decoder, data + written, insize - written );
     //   printf("write=%d written=%d left=%d\n", wr, written, insize - written);
        if( wr < 0 ) { error = true; break; }
        written += wr;
        }
      if( written >= insize ) LZ_decompress_finish( decoder );
      }
    rd = LZ_decompress_read( decoder, new_data + new_pos, new_data_size - new_pos );
  //  printf("read=%d new_pos=%d\n", rd, new_pos);
    if( rd < 0 ) { error = true; break; }
    new_pos += rd;
    if( LZ_decompress_finished( decoder ) == 1 ) break;
    }

  if( LZ_decompress_close( decoder ) < 0 ) error = true;

  return new_pos;
}

#endif



#ifndef BENCH_REMOVE_LZMA

#include <string.h>
#include "lzma/Alloc.h"
#include "lzma/LzmaDec.h"
#include "lzma/LzmaEnc.h"

static void *SzAlloc(void *p, size_t size) { p = p; return MyAlloc(size); }
static void SzFree(void *p, void *address) { p = p; MyFree(address); }
ISzAlloc g_Alloc = { SzAlloc, SzFree };

int64_t lzbench_lzma_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	CLzmaEncProps props;
	int res;
    size_t headerSize = LZMA_PROPS_SIZE;
	SizeT out_len = outsize - LZMA_PROPS_SIZE;

	LzmaEncProps_Init(&props);
	props.level = level;
	LzmaEncProps_Normalize(&props);
  /*
  p->level = 5;
  p->dictSize = p->mc = 0;
  p->reduceSize = (UInt64)(Int64)-1;
  p->lc = p->lp = p->pb = p->algo = p->fb = p->btMode = p->numHashBytes = p->numThreads = -1;
  p->writeEndMark = 0;
  */

  	res = LzmaEncode((uint8_t*)outbuf+LZMA_PROPS_SIZE, &out_len, (uint8_t*)inbuf, insize, &props, (uint8_t*)outbuf, &headerSize, 0/*int writeEndMark*/, NULL, &g_Alloc, &g_Alloc);
	if (res != SZ_OK) return 0;

//	printf("out_len=%u LZMA_PROPS_SIZE=%d headerSize=%d\n", (int)(out_len + LZMA_PROPS_SIZE), LZMA_PROPS_SIZE, (int)headerSize);
	return LZMA_PROPS_SIZE + out_len;
}

int64_t lzbench_lzma_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	int res;
	SizeT out_len = outsize;
	SizeT src_len = insize - LZMA_PROPS_SIZE;
	ELzmaStatus status;

//	SRes LzmaDecode(Byte *dest, SizeT *destLen, const Byte *src, SizeT *srcLen, const Byte *propData, unsigned propSize, ELzmaFinishMode finishMode, ELzmaStatus *status, ISzAlloc *alloc)
	res = LzmaDecode((uint8_t*)outbuf, &out_len, (uint8_t*)inbuf+LZMA_PROPS_SIZE, &src_len, (uint8_t*)inbuf, LZMA_PROPS_SIZE, LZMA_FINISH_END, &status, &g_Alloc);
	if (res != SZ_OK) return 0;

//	printf("out_len=%u\n", (int)(out_len + LZMA_PROPS_SIZE));
    return out_len;
}

#endif



#ifndef BENCH_REMOVE_LZMAT
#include "lzmat/lzmat.h"

int64_t lzbench_lzmat_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	uint32_t complen = outsize;
	if (lzmat_encode((uint8_t*)outbuf, &complen, (uint8_t*)inbuf, insize) != 0)
		return 0;
	return complen;
}

int64_t lzbench_lzmat_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	uint32_t decomplen = outsize;
	if (lzmat_decode((uint8_t*)outbuf, &decomplen, (uint8_t*)inbuf, insize) != 0)
		return 0;
	return decomplen;
}

#endif




#ifndef BENCH_REMOVE_LZO
#include "lzo/lzo1.h"
#include "lzo/lzo1a.h"
#include "lzo/lzo1b.h"
#include "lzo/lzo1c.h"
#include "lzo/lzo1f.h"
#include "lzo/lzo1x.h"
#include "lzo/lzo1y.h"
#include "lzo/lzo1z.h"
#include "lzo/lzo2a.h"

char* lzbench_lzo_init(size_t, size_t, size_t)
{
	lzo_init();

    return (char*) malloc(LZO1B_999_MEM_COMPRESS);
}

void lzbench_lzo_deinit(void* workmem)
{
    free((char*)workmem);
}

int64_t lzbench_lzo1_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
	lzo_uint lzo_complen = 0;
	int res;

    if (!workmem)
        return 0;

	if (level == 99)
		res = lzo1_99_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem);
    else
		res = lzo1_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem);

	if (res != LZO_E_OK) return 0;

	return lzo_complen;
}

int64_t lzbench_lzo1_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	lzo_uint decomplen = 0;

    if (lzo1_decompress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen, NULL) != LZO_E_OK) return 0;

	return decomplen;
}

int64_t lzbench_lzo1a_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
	lzo_uint lzo_complen = 0;
	int res;

    if (!workmem)
        return 0;

	if (level == 99)
		res = lzo1a_99_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem);
    else
		res = lzo1a_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem);

	if (res != LZO_E_OK) return 0;

	return lzo_complen;
}

int64_t lzbench_lzo1a_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	lzo_uint decomplen = 0;

    if (lzo1a_decompress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen, NULL) != LZO_E_OK) return 0;

	return decomplen;
}

int64_t lzbench_lzo1b_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
	lzo_uint lzo_complen = 0;
	int res;

    if (!workmem)
        return 0;

	switch (level)
	{
		default:
		case 1: res = lzo1b_1_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 2: res = lzo1b_2_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 3: res = lzo1b_3_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 4: res = lzo1b_4_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 5: res = lzo1b_5_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 6: res = lzo1b_6_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 7: res = lzo1b_7_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 8: res = lzo1b_8_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 9: res = lzo1b_9_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 99: res = lzo1b_99_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 999: res = lzo1b_999_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
	}

	if (res != LZO_E_OK) return 0;

	return lzo_complen;
}

int64_t lzbench_lzo1b_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	lzo_uint decomplen = 0;

    if (lzo1b_decompress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen, NULL) != LZO_E_OK) return 0;

	return decomplen;
}

int64_t lzbench_lzo1c_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
	lzo_uint lzo_complen = 0;
	int res;

    if (!workmem)
        return 0;

	switch (level)
	{
		default:
		case 1: res = lzo1c_1_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 2: res = lzo1c_2_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 3: res = lzo1c_3_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 4: res = lzo1c_4_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 5: res = lzo1c_5_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 6: res = lzo1c_6_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 7: res = lzo1c_7_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 8: res = lzo1c_8_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 9: res = lzo1c_9_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 99: res = lzo1c_99_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 999: res = lzo1c_999_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
	}

	if (res != LZO_E_OK) return 0;

	return lzo_complen;
}

int64_t lzbench_lzo1c_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	lzo_uint decomplen = 0;

    if (lzo1c_decompress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen, NULL) != LZO_E_OK) return 0;

	return decomplen;
}

int64_t lzbench_lzo1f_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
	lzo_uint lzo_complen = 0;
	int res;

    if (!workmem)
        return 0;

	if (level == 999)
		res = lzo1f_999_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem);
    else
		res = lzo1f_1_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem);

	if (res != LZO_E_OK) return 0;

	return lzo_complen;
}

int64_t lzbench_lzo1f_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	lzo_uint decomplen = 0;

    if (lzo1f_decompress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen, NULL) != LZO_E_OK) return 0;

	return decomplen;
}

int64_t lzbench_lzo1x_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
	lzo_uint lzo_complen = 0;
	int res;

    if (!workmem)
        return 0;

	switch (level)
	{
		default:
		case 1: res = lzo1x_1_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 11: res = lzo1x_1_11_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 12: res = lzo1x_1_12_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 15: res = lzo1x_1_15_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
		case 999: res = lzo1x_999_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem); break;
    }

	if (res != LZO_E_OK) return 0;

	return lzo_complen;
}

int64_t lzbench_lzo1x_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	lzo_uint decomplen = 0;

    if (lzo1x_decompress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen, NULL) != LZO_E_OK) return 0;

	return decomplen;
}

int64_t lzbench_lzo1y_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
	lzo_uint lzo_complen = 0;
	int res;

    if (!workmem)
        return 0;

	if (level == 999)
		res = lzo1y_999_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem);
    else
		res = lzo1y_1_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem);

	if (res != LZO_E_OK) return 0;

	return lzo_complen;
}

int64_t lzbench_lzo1y_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	lzo_uint decomplen = 0;

    if (lzo1y_decompress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen, NULL) != LZO_E_OK) return 0;

	return decomplen;
}

int64_t lzbench_lzo1z_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
	lzo_uint lzo_complen = 0;
	int res;

    if (!workmem)
        return 0;

    res = lzo1z_999_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem);

	if (res != LZO_E_OK) return 0;

	return lzo_complen;
}

int64_t lzbench_lzo1z_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	lzo_uint decomplen = 0;

    if (lzo1z_decompress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen, NULL) != LZO_E_OK) return 0;

	return decomplen;
}


int64_t lzbench_lzo2a_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
	lzo_uint lzo_complen = 0;
	int res;

    if (!workmem)
        return 0;

    res = lzo2a_999_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &lzo_complen, (void*)workmem);

	if (res != LZO_E_OK) return 0;

	return lzo_complen;
}

int64_t lzbench_lzo2a_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	lzo_uint decomplen = 0;

    if (lzo2a_decompress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen, NULL) != LZO_E_OK) return 0;

	return decomplen;
}

#endif





#ifndef BENCH_REMOVE_LZRW
extern "C"
{
	#include "lzrw/lzrw.h"
}

char* lzbench_lzrw_init(size_t, size_t, size_t)
{
    return (char*) malloc(lzrw2_req_mem());
}

void lzbench_lzrw_deinit(void* workmem)
{
    free((char*)workmem);
}

int64_t lzbench_lzrw_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
    if (!workmem)
        return 0;

	uint32_t complen = 0;
	switch (level)
	{
		default:
		case 1: lzrw1_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &complen); break;
		case 2: lzrw1a_compress(COMPRESS_ACTION_COMPRESS, (uint8_t*)workmem, (uint8_t*)inbuf, insize, (uint8_t*)outbuf, &complen); break;
		case 3: lzrw2_compress(COMPRESS_ACTION_COMPRESS, (uint8_t*)workmem, (uint8_t*)inbuf, insize, (uint8_t*)outbuf, &complen); break;
		case 4: lzrw3_compress(COMPRESS_ACTION_COMPRESS, (uint8_t*)workmem, (uint8_t*)inbuf, insize, (uint8_t*)outbuf, &complen); break;
		case 5: lzrw3a_compress(COMPRESS_ACTION_COMPRESS, (uint8_t*)workmem, (uint8_t*)inbuf, insize, (uint8_t*)outbuf, &complen); break;
	}

	return complen;
}

int64_t lzbench_lzrw_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
    if (!workmem)
        return 0;

	uint32_t decomplen = 0;
	switch (level)
	{
		default:
		case 1: lzrw1_decompress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen); break;
		case 2: lzrw1a_compress(COMPRESS_ACTION_DECOMPRESS, (uint8_t*)workmem, (uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen); break;
		case 3: lzrw2_compress(COMPRESS_ACTION_DECOMPRESS, (uint8_t*)workmem, (uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen); break;
		case 4: lzrw3_compress(COMPRESS_ACTION_DECOMPRESS, (uint8_t*)workmem, (uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen); break;
		case 5: lzrw3a_compress(COMPRESS_ACTION_DECOMPRESS, (uint8_t*)workmem, (uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen); break;
	}

	return decomplen;
}

#endif



#ifndef BENCH_REMOVE_LZSSE
#include "lzsse/lzsse2/lzsse2.h"

char* lzbench_lzsse2_init(size_t insize, size_t, size_t)
{
    return (char*) LZSSE2_MakeOptimalParseState(insize);
}

void lzbench_lzsse2_deinit(void* workmem)
{
    if (!workmem) return;
    LZSSE2_FreeOptimalParseState((LZSSE2_OptimalParseState*) workmem);
}

int64_t lzbench_lzsse2_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
    if (!workmem) return 0;

    return LZSSE2_CompressOptimalParse((LZSSE2_OptimalParseState*) workmem, inbuf, insize, outbuf, outsize, level);
}

int64_t lzbench_lzsse2_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	return LZSSE2_Decompress(inbuf, insize, outbuf, outsize);
}


#include "lzsse/lzsse4/lzsse4.h"

char* lzbench_lzsse4_init(size_t insize, size_t, size_t)
{
    return (char*) LZSSE4_MakeOptimalParseState(insize);
}

void lzbench_lzsse4_deinit(void* workmem)
{
    if (!workmem) return;
    LZSSE4_FreeOptimalParseState((LZSSE4_OptimalParseState*) workmem);
}

int64_t lzbench_lzsse4_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
    if (!workmem) return 0;

    return LZSSE4_CompressOptimalParse((LZSSE4_OptimalParseState*) workmem, inbuf, insize, outbuf, outsize, level);
}

int64_t lzbench_lzsse4_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
    return LZSSE4_Decompress(inbuf, insize, outbuf, outsize);
}

char* lzbench_lzsse4fast_init(size_t, size_t, size_t)
{
    return (char*) LZSSE4_MakeFastParseState();
}

void lzbench_lzsse4fast_deinit(void* workmem)
{
    if (!workmem) return;
    LZSSE4_FreeFastParseState((LZSSE4_FastParseState*) workmem);
}

int64_t lzbench_lzsse4fast_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t , size_t, void* workmem)
{
    if (!workmem) return 0;

    return LZSSE4_CompressFast((LZSSE4_FastParseState*) workmem, inbuf, insize, outbuf, outsize);
}


#include "lzsse/lzsse8/lzsse8.h"

char* lzbench_lzsse8_init(size_t insize, size_t, size_t)
{
    return (char*) LZSSE8_MakeOptimalParseState(insize);
}

void lzbench_lzsse8_deinit(void* workmem)
{
    if (!workmem) return;
    LZSSE8_FreeOptimalParseState((LZSSE8_OptimalParseState*) workmem);
}

int64_t lzbench_lzsse8_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
    if (!workmem) return 0;

    return LZSSE8_CompressOptimalParse((LZSSE8_OptimalParseState*) workmem, inbuf, insize, outbuf, outsize, level);
}

int64_t lzbench_lzsse8_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
    return LZSSE8_Decompress(inbuf, insize, outbuf, outsize);
}

char* lzbench_lzsse8fast_init(size_t, size_t, size_t)
{
    return (char*) LZSSE8_MakeFastParseState();
}

void lzbench_lzsse8fast_deinit(void* workmem)
{
    if (!workmem) return;
    LZSSE8_FreeFastParseState((LZSSE8_FastParseState*) workmem);
}

int64_t lzbench_lzsse8fast_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t , size_t, void* workmem)
{
    if (!workmem) return 0;

    return LZSSE8_CompressFast((LZSSE8_FastParseState*) workmem, inbuf, insize, outbuf, outsize);
}

#endif



#ifndef BENCH_REMOVE_PITHY
#include "pithy/pithy.h"

int64_t lzbench_pithy_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	return pithy_Compress(inbuf, insize, outbuf, outsize, level);
}

int64_t lzbench_pithy_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	size_t res = pithy_Decompress(inbuf, insize, outbuf, outsize);
//	printf("insize=%lld outsize=%lld res=%lld\n", insize, outsize, res);
	if (res)
		return outsize;
	return 0;
}

#endif


#ifndef BENCH_REMOVE_QUICKLZ
#include "quicklz/quicklz151b7.h"
#include "quicklz/quicklz.h"
#define MAX(a,b) ((a)>(b))?(a):(b)

int64_t lzbench_quicklz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t , void*)
{
    int64_t res;
    qlz150_state_compress* state = (qlz150_state_compress*) calloc(1, MAX(qlz_get_setting_3(1),MAX(qlz_get_setting_1(1), qlz_get_setting_2(1))));
    if (!state)
        return 0;


	switch (level)
	{
		default:
		case 1:	res = qlz_compress_1(inbuf, outbuf, insize, (qlz150_state_compress*)state); break;
		case 2:	res = qlz_compress_2(inbuf, outbuf, insize, (qlz150_state_compress*)state); break;
		case 3:	res = qlz_compress_3(inbuf, outbuf, insize, (qlz150_state_compress*)state); break;
		case 4:	res = qlz_compress(inbuf, outbuf, insize, (qlz_state_compress*)state); break;
	}

    free(state);
    return res;
}

int64_t lzbench_quicklz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t , void*)
{
    int64_t res;
    qlz150_state_compress* dstate = (qlz150_state_compress*) calloc(1, MAX(qlz_get_setting_3(2),MAX(qlz_get_setting_1(2), qlz_get_setting_2(2))));
    if (!dstate)
        return 0;

	switch (level)
	{
		default:
		case 1: res = qlz_decompress_1(inbuf, outbuf, (qlz150_state_decompress*)dstate); break;
		case 2: res = qlz_decompress_2(inbuf, outbuf, (qlz150_state_decompress*)dstate); break;
		case 3: res = qlz_decompress_3(inbuf, outbuf, (qlz150_state_decompress*)dstate); break;
		case 4: res = qlz_decompress(inbuf, outbuf, (qlz_state_decompress*)dstate); break;
	}

    free(dstate);
    return res;
}

#endif



#ifndef BENCH_REMOVE_SHRINKER
#include "shrinker/shrinker.h"

int64_t lzbench_shrinker_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	return shrinker_compress(inbuf, outbuf, insize);
}

int64_t lzbench_shrinker_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	return shrinker_decompress(inbuf, outbuf, outsize);
}

#endif


#ifndef BENCH_REMOVE_SNAPPY
#include "snappy/snappy.h"

int64_t lzbench_snappy_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	snappy::RawCompress(inbuf, insize, outbuf, &outsize);
	return outsize;
}

int64_t lzbench_snappy_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	snappy::RawUncompress(inbuf, insize, outbuf);
	return outsize;
}

#endif




#ifndef BENCH_REMOVE_TORNADO
#include "tornado/tor_test.h"

int64_t lzbench_tornado_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	return tor_compress(level, (uint8_t*)inbuf, insize, (uint8_t*)outbuf, outsize);
}

int64_t lzbench_tornado_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	return tor_decompress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, outsize);
}

#endif



#ifndef BENCH_REMOVE_UCL
#include "ucl/ucl.h"

int64_t lzbench_ucl_nrv2b_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	ucl_uint complen;
	int res = ucl_nrv2b_99_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &complen, NULL, level, NULL, NULL);

	if (res != UCL_E_OK) return 0;
	return complen;
}

int64_t lzbench_ucl_nrv2b_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	ucl_uint decomplen;
	int res = ucl_nrv2b_decompress_8((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen, NULL);

	if (res != UCL_E_OK) return 0;
	return decomplen;
}

int64_t lzbench_ucl_nrv2d_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	ucl_uint complen;
	int res = ucl_nrv2d_99_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &complen, NULL, level, NULL, NULL);

	if (res != UCL_E_OK) return 0;
	return complen;
}

int64_t lzbench_ucl_nrv2d_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	ucl_uint decomplen;
	int res = ucl_nrv2d_decompress_8((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen, NULL);

	if (res != UCL_E_OK) return 0;
	return decomplen;
}

int64_t lzbench_ucl_nrv2e_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	ucl_uint complen;
	int res = ucl_nrv2e_99_compress((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &complen, NULL, level, NULL, NULL);

	if (res != UCL_E_OK) return 0;
	return complen;
}

int64_t lzbench_ucl_nrv2e_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	ucl_uint decomplen;
	int res = ucl_nrv2e_decompress_8((uint8_t*)inbuf, insize, (uint8_t*)outbuf, &decomplen, NULL);

	if (res != UCL_E_OK) return 0;
	return decomplen;
}

#endif



#ifndef BENCH_REMOVE_WFLZ
#include "wflz/wfLZ.h"

char* lzbench_wflz_init(size_t, size_t, size_t)
{
    return (char*) malloc(wfLZ_GetWorkMemSize());
}

void lzbench_wflz_deinit(void* workmem)
{
    free((char*)workmem);
}

int64_t lzbench_wflz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
    int64_t res;
    if (!workmem)
        return 0;

    if (level == 0)
		res = wfLZ_CompressFast((const uint8_t*)inbuf, insize, (uint8_t*)outbuf, (uint8_t*)workmem, 0);
    else
        res = wfLZ_Compress((const uint8_t*)inbuf, insize, (uint8_t*)outbuf, (uint8_t*)workmem, 0);

    return res;
}

int64_t lzbench_wflz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
    wfLZ_Decompress((const uint8_t*)inbuf, (uint8_t*)outbuf);
    return outsize;
}

#endif



#ifndef BENCH_REMOVE_XZ
#include "xpack/lib/libxpack.h"

typedef struct {
    struct xpack_compressor *xpackc;
    struct xpack_decompressor *xpackd;
} xpack_params_s;

char* lzbench_xpack_init(size_t insize, size_t level, size_t)
{
    xpack_params_s* xpack_params = (xpack_params_s*) malloc(sizeof(xpack_params_s));
    if (!xpack_params) return NULL;
    xpack_params->xpackc = xpack_alloc_compressor(insize, level);
    xpack_params->xpackd = xpack_alloc_decompressor();

    return (char*) xpack_params;
}

void lzbench_xpack_deinit(void* workmem)
{
    xpack_params_s* xpack_params = (xpack_params_s*) workmem;
    if (!xpack_params) return;
    if (xpack_params->xpackc) xpack_free_compressor(xpack_params->xpackc);
    if (xpack_params->xpackd) xpack_free_decompressor(xpack_params->xpackd);
    free((char*)workmem);
}

int64_t lzbench_xpack_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem)
{
    xpack_params_s* xpack_params = (xpack_params_s*) workmem;
    if (!xpack_params || !xpack_params->xpackc) return 0;

    return xpack_compress(xpack_params->xpackc, inbuf, insize, outbuf, outsize);
}

int64_t lzbench_xpack_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void* workmem)
{
    xpack_params_s* xpack_params = (xpack_params_s*) workmem;
    if (!xpack_params || !xpack_params->xpackd) return 0;

    size_t res = xpack_decompress(xpack_params->xpackd, inbuf, insize, outbuf, outsize, NULL);
    if (res != 0) return 0;

    return outsize;
}

#endif



#ifndef BENCH_REMOVE_XZ
#include "xz/alone.h"

int64_t lzbench_xz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
    return xz_alone_compress(inbuf, insize, outbuf, outsize, level, 0, 0);
}

int64_t lzbench_xz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
    return xz_alone_decompress(inbuf, insize, outbuf, outsize, 0, 0, 0);
}

#endif



#ifndef BENCH_REMOVE_YALZ77
#include "yalz77/lz77.h"

int64_t lzbench_yalz77_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
  lz77::compress_t compress(level, lz77::DEFAULT_BLOCKSIZE);
  std::string compressed = compress.feed((unsigned char*)inbuf, (unsigned char*)inbuf+insize);
  if (compressed.size() > outsize) return 0;
  memcpy(outbuf, compressed.c_str(), compressed.size());
  return compressed.size();
}

int64_t lzbench_yalz77_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
  lz77::decompress_t decompress;
  std::string temp;
  decompress.feed((unsigned char*)inbuf, (unsigned char*)inbuf+insize, temp);
  const std::string& decompressed = decompress.result();
  if (decompressed.size() > outsize) return 0;
  memcpy(outbuf, decompressed.c_str(), decompressed.size());
  return decompressed.size();
}

#endif



#ifndef BENCH_REMOVE_YAPPY
#include "yappy/yappy.hpp"

char* lzbench_yappy_init(size_t insize, size_t level, size_t)
{
	YappyFillTables();
    return NULL;
}

int64_t lzbench_yappy_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	return YappyCompress((uint8_t*)inbuf, (uint8_t*)outbuf, insize, level) - (uint8_t*)outbuf;
}

int64_t lzbench_yappy_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	return YappyUnCompress((uint8_t*)inbuf, (uint8_t*)inbuf+insize, (uint8_t*)outbuf) - (uint8_t*)outbuf;
}

#endif



#ifndef BENCH_REMOVE_ZLIB
#include "zlib/zlib.h"

int64_t lzbench_zlib_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	uLongf zcomplen = insize;
	int err = compress2((uint8_t*)outbuf, &zcomplen, (uint8_t*)inbuf, insize, level);
	if (err != Z_OK)
		return 0;
	return zcomplen;
}

int64_t lzbench_zlib_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	uLongf zdecomplen = outsize;
	int err = uncompress((uint8_t*)outbuf, &zdecomplen, (uint8_t*)inbuf, insize);
	if (err != Z_OK)
		return 0;
	return outsize;
}

#endif



#if !defined(BENCH_REMOVE_SLZ) && !defined(BENCH_REMOVE_ZLIB)
extern "C"
{
	#include "slz/slz.h"
}

int64_t lzbench_slz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t param2, void*)
{
	struct slz_stream strm;
	size_t outlen = 0;
	size_t window = 8192 << ((level & 3) * 2);
	size_t len;
	size_t blk;

	if (param2 == 0)
		slz_init(&strm, !!level, SLZ_FMT_GZIP);
	else if (param2 == 1)
		slz_init(&strm, !!level, SLZ_FMT_ZLIB);
	else
		slz_init(&strm, !!level, SLZ_FMT_DEFLATE);

	do {
		blk = MIN(insize, window);

		len = slz_encode(&strm, outbuf, inbuf, blk, insize > blk);
		outlen += len;
		outbuf += len;
		inbuf += blk;
		insize -= blk;
	} while (insize > 0);

	outlen += slz_finish(&strm, outbuf);
	return outlen;
}

/* uses zlib to perform the decompression */
int64_t lzbench_slz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t param2, void*)
{
	z_stream stream;
	int err;

	stream.zalloc    = NULL;
	stream.zfree     = NULL;

	stream.next_in   = (unsigned char *)inbuf;
	stream.avail_in  = insize;
	stream.next_out  = (unsigned char *)outbuf;
	stream.avail_out = outsize;

	outsize = 0;

	if (param2 == 0)      // gzip
		err = inflateInit2(&stream, 15 + 16);
	else if (param2 == 1) // zlip
		err = inflateInit2(&stream, 15);
	else                  // deflate
		err = inflateInit2(&stream, -15);

	if (err == Z_OK) {
		if (inflate(&stream, Z_FINISH) == Z_STREAM_END)
			outsize = stream.total_out;
		inflateEnd(&stream);
	}
	return outsize;
}
#endif



#ifndef BENCH_REMOVE_ZLING
#include "libzling/libzling.h"

namespace baidu {
namespace zling {

struct MemInputter: public baidu::zling::Inputter {
	MemInputter(uint8_t* buffer, size_t buflen) :
		m_buffer(buffer),
		m_buflen(buflen),
        m_total_read(0) {}

    size_t GetData(unsigned char* buf, size_t len) {
		if (len > m_buflen - m_total_read)
			len = m_buflen - m_total_read;

		memcpy(buf, m_buffer + m_total_read, len);
		m_total_read += len;
		return len;
	}
    bool   IsEnd() { return m_total_read >= m_buflen; }
    bool   IsErr() { return false; }
    size_t GetInputSize() { return m_total_read; }

private:
	uint8_t* m_buffer;
	size_t m_buflen, m_total_read;
};

struct MemOutputter : public baidu::zling::Outputter {
	MemOutputter(uint8_t* buffer, size_t buflen) :
		m_buffer(buffer),
		m_buflen(buflen),
        m_total_write(0) {}

    size_t PutData(unsigned char* buf, size_t len) {
		if (len > m_buflen - m_total_write)
			len = m_buflen - m_total_write;

		memcpy(m_buffer + m_total_write, buf, len);
		m_total_write += len;
		return len;
	}
    bool   IsErr() { return m_total_write > m_buflen; }
    size_t GetOutputSize() { return m_total_write; }

private:
    FILE*  m_fp;
	uint8_t* m_buffer;
	size_t m_buflen, m_total_write;
};

}  // namespace zling
}  // namespace baidu

int64_t lzbench_zling_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	baidu::zling::MemInputter  inputter((uint8_t*)inbuf, insize);
	baidu::zling::MemOutputter outputter((uint8_t*)outbuf, outsize);
	baidu::zling::Encode(&inputter, &outputter, NULL, level);

	return outputter.GetOutputSize();
}

int64_t lzbench_zling_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	baidu::zling::MemInputter  inputter((uint8_t*)inbuf, insize);
	baidu::zling::MemOutputter outputter((uint8_t*)outbuf, outsize);
	baidu::zling::Decode(&inputter, &outputter);

	return outputter.GetOutputSize();
}

#endif



#ifndef BENCH_REMOVE_ZSTD
#define ZSTD_STATIC_LINKING_ONLY
#include "zstd/lib/zstd.h"
#include "zstd/lib/common/fse.h"
#include "zstd/lib/common/huf.h"
#include "zstd/lib/common/zstd_errors.h"

typedef struct {
    ZSTD_CCtx* cctx;
    ZSTD_DCtx* dctx;
    ZSTD_CDict* cdict;
    ZSTD_parameters zparams;
    ZSTD_customMem cmem;
} zstd_params_s;

char* lzbench_zstd_init(size_t insize, size_t level, size_t windowLog)
{
    zstd_params_s* zstd_params = (zstd_params_s*) malloc(sizeof(zstd_params_s));
    if (!zstd_params) return NULL;
    zstd_params->cctx = ZSTD_createCCtx();
    zstd_params->dctx = ZSTD_createDCtx();
#if 1
    zstd_params->cdict = NULL;
#else
    zstd_params->zparams = ZSTD_getParams(level, insize, 0);
    zstd_params->cmem = { NULL, NULL, NULL };
    if (windowLog && zstd_params->zparams.cParams.windowLog > windowLog) {
        zstd_params->zparams.cParams.windowLog = windowLog;
        zstd_params->zparams.cParams.chainLog = windowLog + ((zstd_params->zparams.cParams.strategy == ZSTD_btlazy2) | (zstd_params->zparams.cParams.strategy == ZSTD_btopt) | (zstd_params->zparams.cParams.strategy == ZSTD_btopt2));
    }
    zstd_params->cdict = ZSTD_createCDict_advanced(NULL, 0, zstd_params->zparams, zstd_params->cmem);
#endif

    // printf("zstd returning workmem ptr: %p\n", (char*) zstd_params);
    return (char*) zstd_params;
}

void lzbench_zstd_deinit(void* workmem)
{
    // printf("calling zstd deinit on workmem %p...\n", workmem);
    zstd_params_s* zstd_params = (zstd_params_s*) workmem;
    if (!zstd_params) return;
    if (zstd_params->cctx) ZSTD_freeCCtx(zstd_params->cctx);
    if (zstd_params->dctx) ZSTD_freeDCtx(zstd_params->dctx);
    if (zstd_params->cdict) ZSTD_freeCDict(zstd_params->cdict);
    free((zstd_params_s*)workmem);
}

int64_t lzbench_zstd_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t windowLog, void* workmem)
{
    size_t res;

    zstd_params_s* zstd_params = (zstd_params_s*) workmem;
    if (!zstd_params || !zstd_params->cctx) {
        printf("ERROR: zstd compress had null params or compress context!\n");
        return 0;
    }

#if 1
    zstd_params->zparams = ZSTD_getParams(level, insize, 0);
    zstd_params->zparams.fParams.contentSizeFlag = 1;
    if (windowLog && zstd_params->zparams.cParams.windowLog > windowLog) {
        zstd_params->zparams.cParams.windowLog = windowLog;
        zstd_params->zparams.cParams.chainLog = windowLog + ((zstd_params->zparams.cParams.strategy == ZSTD_btlazy2) || (zstd_params->zparams.cParams.strategy == ZSTD_btopt) || (zstd_params->zparams.cParams.strategy == ZSTD_btopt2));
    }
    res = ZSTD_compress_advanced(zstd_params->cctx, outbuf, outsize, inbuf, insize, NULL, 0, zstd_params->zparams);
//    res = ZSTD_compressCCtx(zstd_params->cctx, outbuf, outsize, inbuf, insize, level);
#else
    if (!zstd_params->cdict) return 0;
    res = ZSTD_compress_usingCDict(zstd_params->cctx, outbuf, outsize, inbuf, insize, zstd_params->cdict);
#endif
    if (ZSTD_isError(res)) printf("zstd compress got error: %d!\n", (int)res);
    // if (ZSTD_isError(res)) return res;

    return res;
}

int64_t lzbench_zstd_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void* workmem)
{
    // printf("called zstd decompress\n");
    const zstd_params_s* zstd_params = (const zstd_params_s*) workmem;
    if (!zstd_params || !zstd_params->dctx) return 0;

    // printf("zstd params and dctx not null!\n");
    auto res = ZSTD_decompressDCtx(zstd_params->dctx, outbuf, outsize, inbuf, insize);
    // printf("zstd ran decompression! dlen = %d\n", (int)res);
    if (ZSTD_isError(res)) printf("ERROR: zstd decomp got error: '%s'\n",
        ZSTD_getErrorString(ZSTD_getErrorCode(res)));
    return res;

    // return ZSTD_decompressDCtx(zstd_params->dctx, outbuf, outsize, inbuf, insize);
}

int64_t lzbench_fse_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void*)
{
    auto ret = FSE_compress(outbuf, outsize, inbuf, insize);
    if (FSE_isError(ret)) {
        printf("FSE compression had error: %s\n", FSE_getErrorName(ret));
    }

    // printf("FSE writing compressed size %lu (from insize %lu)\n", ret, insize);

    if (ret == 0 || ret == 9) { // fse does nothing if it deems input incompressible
        // *(uint64_t*)outbuf = insize;
        memcpy(outbuf, inbuf, insize);
        return insize;
    } else if (ret == 1) { // whole input is a constant
        *(uint64_t*)outbuf = insize;
        *(outbuf + 8) = *inbuf;
        return 9;
    }
    return ret;
}

int64_t lzbench_fse_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void*)
{
    // printf("FSE decompress: received compressed size: %lu\n", insize);
    if (insize == 9) {
        uint64_t size = *(uint64_t*)inbuf;
        uint8_t val = *(inbuf + 8);
        memset(outbuf, val, size);
        return size;
    }

    auto ret = FSE_decompress(outbuf, outsize, inbuf, insize);
    if (FSE_isError(ret)) {
        printf("FSE decompression had error: %s\n", FSE_getErrorName(ret));
    }
    return ret;
}

int64_t lzbench_huff0_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void*)
{
    // if (insize < 10) {
    //     printf("------ HUFF0 requires larger data; received input of size %lu\n", insize);
    //     return 0;
    // }

    *(uint32_t*)outbuf = insize;  // Huff0 decomp needs original input size

    // fprintf(stderr, "HUF compress final 2 bytes: %d %d\n", (int)inbuf[insize - 2], (int)inbuf[insize - 1]);

    // auto ret = HUF_compress(outbuf, outsize, inbuf, insize);
    // fprintf(stderr, "HUF compress: received raw data size, outsize: %lub, %lub\n", insize, outsize);
    auto ret = HUF_compress(outbuf + 4, outsize - 4, inbuf, insize);
    if (HUF_isError(ret)) {
        printf("HUFF0 compression had error: %s\n", HUF_getErrorName(ret));
        if (ret == ZSTD_error_srcSize_wrong) {
            printf("Maximum block size is 128KiB; try lzbench arg: '-b127'\n");
        }
    }

    // huff0 does nothing if it deems input incompressible; we also have to
    // catch ret == 9 case because we would be incorrect when that happened
    if (ret == 0 || ret == 9) {
        // printf("input incompressible; just memcpy-ing\n");
        *(uint32_t*)outbuf = 0;
        *(uint32_t*)(outbuf + 4) = insize;
        memcpy(outbuf + 8, inbuf, insize);
        return insize + 8;
    } else if (ret == 1) { // whole input is a constant
        *(uint64_t*)outbuf = insize;
        *(outbuf + 8) = *inbuf;
        return 9;
    }
    // fprintf(stderr, "HUF compress: compressed %lu bytes -> %lu bytes\n", insize, ret + 4);
    return ret + 4;
}
int64_t lzbench_huff0_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void*)
{
    // LZBENCH_PRINT(1, "HUF decompress: received compressed size: %lu\n", insize);
    if (insize == 9) {
        uint64_t size = *(uint64_t*)inbuf;
        uint8_t val = *(inbuf + 8);
        memset(outbuf, val, size);
        return size;
    }

    uint32_t orig_size = *(uint32_t*)inbuf;
    // printf("read back insize: %u\n", orig_size);

    // fprintf(stderr, "HUF decompress: received compressed "
    //     "size, orig_size, outsize: %lub, %ub, %lub\n",
    //     insize, orig_size, outsize);

    // printf("HUF decompress: first few bytes of compressed data = ");
    // for (int i = 0; i < 10; i++) {
    //     printf("%d ", (int)inbuf[i]);
    // }
    // printf("\n");

    if (orig_size == 0) {
        // printf("WARNING: Huffman decompress just memcpying "
        //     " (%lld bytes)\n", (long long)orig_size);
        orig_size = *(uint32_t*)(inbuf + 4);
        memcpy(outbuf, inbuf + 8, orig_size);
        return orig_size;
    }

    // auto ret = HUF_decompress(outbuf, outsize, inbuf + 8, insize);
    // auto ret = HUF_decompress(outbuf, orig_size, inbuf + 8, insize - 8);
    auto ret = HUF_decompress(outbuf, orig_size, inbuf + 4, insize - 4);
    if (HUF_isError(ret)) {
        printf("HUFF0 decompression had error: %s\n", HUF_getErrorName(ret));
        exit(1);
    }
    if (ret > outsize) {
        fprintf(stderr, "ERROR: Huffman decompression wrote past end of output"
            " buffer! (Wrote %lu bytes to buffer of length %lu)\n",
            ret, outsize);
        exit(1);
    }
    if (ret != orig_size) {
        printf("ERROR: Huffman decompression returned output of the wrong size"
            " (%ld instead of %lu)!", (long)ret, (unsigned long)orig_size);
        exit(1);
    }
    // fprintf(stderr, "ran HUF decompress; returning size %lub\n", ret);

    // fprintf(stderr, "HUF decompress wrote to : %d %d\n", (int)outbuf[orig_size - 2], (int)outbuf[orig_size - 1]);
    // fprintf(stderr, "HUF decompress final 2 bytes: %d %d\n", (int)outbuf[orig_size - 2], (int)outbuf[orig_size - 1]);
    // fprintf(stderr, "HUF decompress final 2 bytes: %d %d\n", (int)outbuf[orig_size - 2], (int)outbuf[orig_size - 1]);

    return ret;
}

#endif



#ifdef BENCH_HAS_NAKAMICHI
#include "nakamichi/nakamichi.h"

int64_t lzbench_nakamichi_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
	return NakaCompress(outbuf, inbuf, insize);
}

int64_t lzbench_nakamichi_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
	return NakaDecompress(outbuf, inbuf, insize);
}

#endif


#ifndef BENCH_REMOVE_FASTPFOR
#include "fastpfor/codecfactory.h"

// avoid polluting namespace
#define FASTPFOR_BLOCK_SZ 128

int64_t fastpfor_compress_with_codec(const char* codecname, char *inbuf,
    size_t insize, char *outbuf, size_t outsize)
{
    using namespace FastPForLib;
    IntegerCODEC& codec = *CODECFactory::getFromName(codecname);
    size_t compressed_size = outsize / 4; // written to, but also read...

    // to include the whole input, we need to round up the number of integers
    // since the number of bytes might not be a multiple of 4
    // XXX: reading past end of input only okay because of padding
    insize += (insize % 4) ? 4 - (insize % 4) : 0;

    codec.encodeArray((const uint32_t*)inbuf, insize / 4,
                      (uint32_t*)outbuf, compressed_size);
    return compressed_size * 4;
}

int64_t fastpfor_decompress_with_codec(const char* codecname, char *inbuf,
    size_t insize, char *outbuf, size_t outsize)
{
    using namespace FastPForLib;
    IntegerCODEC& codec = *CODECFactory::getFromName(codecname);
    size_t decompressed_size = outsize / 4; // written to, but also read...

    codec.decodeArray((const uint32_t*)inbuf, insize / 4,
                      (uint32_t*)outbuf, decompressed_size);
    return decompressed_size * 4;
}


#define FASTPFOR_FUNC(NAME, CODEC_NAME)                                     \
int64_t lzbench_ ## NAME ## _compress(char *inbuf, size_t insize,           \
    char *outbuf, size_t outsize, size_t level, size_t, void*) {            \
    return fastpfor_compress_with_codec(CODEC_NAME, inbuf, insize,          \
                                        outbuf, outsize);                   \
}                                                                           \
int64_t lzbench_ ## NAME ## _decompress(char *inbuf, size_t insize,         \
    char *outbuf, size_t outsize, size_t, size_t, void*) {                  \
    return fastpfor_decompress_with_codec(CODEC_NAME, inbuf, insize,        \
                                          outbuf, outsize);                 \
}

FASTPFOR_FUNC(fastpfor, "simdfastpfor256");
FASTPFOR_FUNC(binarypacking, "simdbinarypacking");
FASTPFOR_FUNC(optpfor, "simdoptpfor");
FASTPFOR_FUNC(varintg8iu, "varintg8iu");
FASTPFOR_FUNC(simple8b, "simple8b");
FASTPFOR_FUNC(simdgroupsimple, "simdgroupsimple");

int64_t lzbench_simdbp128_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*) {
    return 0; // TODO
}

int64_t lzbench_simdbp128_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*) {
    return fastpfor_decompress_with_codec("simdfastpfor256", inbuf, insize,
                                      outbuf, outsize);
}

#endif

#ifndef BENCH_REMOVE_EXAMPLE
#include "example_compressor/example.h"

int64_t lzbench_example_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*)
{
    return example_compress(inbuf, insize, outbuf, outsize, level, -1);
}

int64_t lzbench_example_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*)
{
    return example_decompress(inbuf, insize, outbuf, outsize);
}
#endif


#ifndef BENCH_REMOVE_BLOSC
#include "blosc/blosc.h"
#include "blosc/blosclz.h"

// ------------------------ blosclz
int64_t lzbench_blosclz_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t, void*)
{
    return blosclz_compress(level, inbuf, insize, outbuf, outsize, 1);
}
int64_t lzbench_blosclz_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t , size_t, void*)
{
    return blosclz_decompress(inbuf, insize, outbuf, outsize);
}

// ------------------------ shuffling
int64_t lzbench_blosc_bitshuf_compress(char *inbuf, size_t insize,
    char *outbuf, size_t outsize, size_t level, size_t elem_sz, void*)
{
    // printf("blosc received elem_sz: %lu\n", elem_sz);
    return blosc_compress_ctx(level, BLOSC_BITSHUFFLE, elem_sz, insize, inbuf,
                              outbuf, outsize, "blosclz", 0, 1);
}
int64_t lzbench_blosc_bitshuf_decompress(char *inbuf, size_t insize,
    char *outbuf, size_t outsize, size_t, size_t, void*)
{
    return blosc_decompress_ctx(inbuf, outbuf, outsize, 1);
}

int64_t lzbench_blosc_byteshuf_compress(char *inbuf, size_t insize,
    char *outbuf, size_t outsize, size_t level, size_t elem_sz, void*)
{
    // what these arguments mean (see blosc.h for details):
// int blosc_compress_ctx(int clevel, int doshuffle, size_t typesize,
//                        size_t nbytes, const void* src, void* dest,
//                        size_t destsize, const char* compressor,
//                        size_t blocksize, int numinternalthreads);
    return blosc_compress_ctx(level, BLOSC_SHUFFLE, elem_sz, insize, inbuf,
                              outbuf, outsize, "blosclz", 0, 1);
}
int64_t lzbench_blosc_byteshuf_decompress(char *inbuf, size_t insize,
    char *outbuf, size_t outsize, size_t, size_t, void*)
{
    return blosc_decompress_ctx(inbuf, outbuf, outsize, 1);
}
#endif

#ifndef BENCH_REMOVE_BBP
extern "C" {
    #include "bbp/bbp.h"
}
int64_t lzbench_bbp_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t level, size_t, void*)
{
    // TODO get BBP decompression to stop yielding bus errors; below
    // compression code appears to work
    std::cout << "WARNING: BBP not implemented; defaulting to memcpy\n";

    // int blocksize = 0; // use library default
    // int blocksize2 = 0; // use library default
    // int offset = 16; // minimum possible value; 1 would be delta coding
    // return bbp_code_offset((uint8_t*)inbuf, (uint8_t*)outbuf, blocksize,
    //                        blocksize2, (int)insize, (int)offset);
    memcpy(outbuf, inbuf, insize);
    return insize;
}
int64_t lzbench_bbp_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void*)
{
    // code in this function *should* work based on BBP CLI code, but
    // throws bus a error instead.

    // uint64_t remainder_in = ((uint64_t)inbuf) % 16;
    // uint64_t remainder_out = ((uint64_t)outbuf) % 16;
    // printf("inbuf, outbuf alignments: %llu, %llu\n", remainder_in, remainder_out);

    // // std::cout << "no really, print stuff in decomp func...\n";

    // uint32_t uncompressed_sz, compressed_sz;
    // bbp_header_sizes((uint8_t*)inbuf, &uncompressed_sz, &compressed_sz);
    // printf("compressed, decompressed sizes: %u, %u\n", compressed_sz, uncompressed_sz);

    // bbp_decode((uint8_t*)inbuf, (uint8_t*)outbuf);
    // return uncompressed_sz;
    memcpy(outbuf, inbuf, insize);
    return insize;
}

char* lzbench_bbp_init(size_t insize, size_t level, size_t) {
    bbp_init();
    return NULL;
}
void lzbench_bbp_deinit(void* workmem) {
    bbp_shutdown();
}
#endif

#ifndef BENCH_REMOVE_SPRINTZ
#include "sprintz/sprintz.h"
#include "sprintz/univariate_8b.h"
#include "sprintz/sprintz_delta.h"
#include "sprintz/sprintz_xff.h"
#include "sprintz/bitpack.h"
#include "sprintz/delta.h"
#include "sprintz/predict.h"
#include "sprintz/query.hpp"
#include "sprintz/sprintz_delta.h"


static const double HUF_PAD_FRAC = 1 + .375; // .375 is the worst-case overhead
static const double HUF_PAD_CONST = 1000;

// #define PAD_SIZE(SIZE) (size_t)(SIZE)

size_t pad_size(size_t size) {
    return static_cast<size_t>(size * HUF_PAD_FRAC + HUF_PAD_CONST);
}

// #include "util.h" // TODO rm; just for aligned alloc to debug rle + huff0

int64_t lzbench_sprintz_delta_1d_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t, void*)
{
    // return compress8b_delta((uint8_t*)inbuf, insize, (int8_t*)outbuf);
    return compress8b_delta_online((uint8_t*)inbuf, insize, (int8_t*)outbuf);
    // return compress8b_delta_simple((uint8_t*)inbuf, insize, (int8_t*)outbuf);
    // memcpy(outbuf, inbuf, insize);
    // return insize;
}
int64_t lzbench_sprintz_delta_1d_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void*)
{
    // printf("about to call delta decompress func...\n");
    // return decompress8b_delta((int8_t*)inbuf, (uint8_t*)outbuf);
    return decompress8b_delta_online((int8_t*)inbuf, (uint8_t*)outbuf);
    // return decompress8b_delta_simple((int8_t*)inbuf, (uint8_t*)outbuf);
    // memcpy(outbuf, inbuf, insize);
    // return insize;
}

int64_t lzbench_sprintz_dbldelta_1d_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t, void*)
{
    // printf("about to call double delta compress func...\n");
    return compress8b_doubledelta((uint8_t*)inbuf, insize, (int8_t*)outbuf);
    // memcpy(outbuf, inbuf, insize);
    // return insize;
}
int64_t lzbench_sprintz_dbldelta_1d_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void*)
{
    return decompress8b_doubledelta((int8_t*)inbuf, (uint8_t*)outbuf);
    // memcpy(outbuf, inbuf, insize);
    // return insize;
}

int64_t lzbench_sprintz_dyndelta_1d_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t, void*)
{
    return compress8b_dyndelta((uint8_t*)inbuf, insize, (int8_t*)outbuf);
    // memcpy(outbuf, inbuf, insize);
    // return insize;
}
int64_t lzbench_sprintz_dyndelta_1d_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void*)
{
    return decompress8b_dyndelta((int8_t*)inbuf, (uint8_t*)outbuf);
    // memcpy(outbuf, inbuf, insize);
    // return insize;
}

int64_t lzbench_sprintz_delta2_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t, void*)
{
    return compress8b_delta2_online((uint8_t*)inbuf, insize, (int8_t*)outbuf);
}
int64_t lzbench_sprintz_delta2_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void*)
{
    return decompress8b_delta2_online((int8_t*)inbuf, (uint8_t*)outbuf);
}


int64_t lzbench_sprintz_delta_rle_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t, void*)
{
    return compress8b_delta_rle((uint8_t*)inbuf, insize, (int8_t*)outbuf);
}
int64_t lzbench_sprintz_delta_rle_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void*)
{
    return decompress8b_delta_rle((int8_t*)inbuf, (uint8_t*)outbuf);
}

int64_t lzbench_sprintz_delta_rle2_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t, void*)
{
    return compress8b_delta_rle2((uint8_t*)inbuf, insize, (int8_t*)outbuf);
}
int64_t lzbench_sprintz_delta_rle2_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void*)
{
    return decompress8b_delta_rle2((int8_t*)inbuf, (uint8_t*)outbuf);
}

int64_t lzbench_sprintz_delta_rle_fse_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t, void*)
{
    char* tmp = (char*)malloc(pad_size(insize));
    auto len = compress8b_delta_rle((uint8_t*)inbuf, insize, (int8_t*)tmp);
    return lzbench_fse_compress(tmp, len, outbuf, outsize, level, 0, NULL);

}
int64_t lzbench_sprintz_delta_rle_fse_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t, void*)
{
    char* tmp = (char*)malloc(pad_size(outsize));
    auto len = lzbench_fse_decompress(inbuf, insize, tmp, outsize, level, 0, NULL);
    return decompress8b_delta_rle((int8_t*)tmp, (uint8_t*)outbuf);
}

int64_t lzbench_sprintz_delta_rle_huf_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t, void*)
{
    char* tmp = (char*)malloc(pad_size(outsize));
    auto len = compress8b_delta_rle((uint8_t*)inbuf, insize, (int8_t*)tmp);
    auto ret = lzbench_huff0_compress((char*)tmp, len, outbuf, outsize, level, 0, NULL);

    // if (ret == 4) {
    //     printf("orig insize, outsize, insize after deltaRLE, final size: %lu, %lu, %lld, %lld\n", insize, outsize, len, ret);
    // }
    // if (ret < 100) {
    // }
    // if (ret == len) {
    //     printf("orig insize, outsize, insize after deltaRLE, final size: %lu, %lu, %lld, %lld\n", insize, outsize, len, ret);
    // }

    free(tmp);
    return ret;
}
int64_t lzbench_sprintz_delta_rle_huf_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t, void*)
{
    char* tmp = (char*)malloc(pad_size(outsize));
    auto len = lzbench_huff0_decompress((char*)inbuf, insize, (char*)tmp, outsize, level, 0, NULL);
    // memcpy(outbuf, tmp, len); // TODO might need to uncomment this?

    auto ret = decompress8b_delta_rle((int8_t*)tmp, (uint8_t*)outbuf);
    free(tmp);
    return ret;
}

int64_t lzbench_sprintz_delta_rle_zstd_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t windowLog, void* workmem)
{
    char* tmp = (char*)malloc(pad_size(insize));
    auto len = compress8b_delta_rle((uint8_t*)inbuf, insize, (int8_t*)tmp);
    return lzbench_zstd_compress(tmp, len, outbuf, outsize, level, windowLog, (char*)workmem);
}
int64_t lzbench_sprintz_delta_rle_zstd_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void* workmem)
{
    char* tmp = (char*)malloc(pad_size(outsize));
    auto len = lzbench_zstd_decompress(inbuf, insize, tmp, outsize, 0, 0, (char*)workmem);
    return decompress8b_delta_rle((int8_t*)tmp, (uint8_t*)outbuf);
}

int64_t lzbench_fixed_bitpack_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t nbits, size_t, void*)
{
    return compress8b_bitpack((const uint8_t*)inbuf, insize, (uint8_t*)outbuf, nbits);
}
int64_t lzbench_fixed_bitpack_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t nbits, size_t, void*)
{
    return decompress8b_bitpack((const uint8_t*)inbuf, insize, (uint8_t*)outbuf, nbits);
}

int64_t lzbench_just_bitpack_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t nbits, size_t, void*)
{
    return compress8b_online((uint8_t*)inbuf, insize, (int8_t*)outbuf);
}
int64_t lzbench_just_bitpack_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t nbits, size_t, void*)
{
    return decompress8b_online((int8_t*)inbuf, (uint8_t*)outbuf);
}

int64_t lzbench_sprintz_row_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return compress_rowmajor_8b((uint8_t*)inbuf, insize, (int8_t*)outbuf, ndims);
}
int64_t lzbench_sprintz_row_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return decompress_rowmajor_8b((int8_t*)inbuf, (uint8_t*)outbuf);
}

int64_t lzbench_sprintz_row_delta_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return compress_rowmajor_delta_8b((uint8_t*)inbuf, insize, (int8_t*)outbuf, ndims);
}
int64_t lzbench_sprintz_row_delta_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return decompress_rowmajor_delta_8b((int8_t*)inbuf, (uint8_t*)outbuf);
}

int64_t lzbench_sprintz_row_delta_huf_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    char* tmp = (char*)calloc(pad_size(outsize), 1);
    // auto len = compress8b_delta_rle((uint8_t*)inbuf, insize, (int8_t*)tmp);
    auto len = compress_rowmajor_delta_8b((uint8_t*)inbuf, insize, (int8_t*)tmp, ndims);

    // printf("rowmajor compressed len: %lld\n", len);

    auto ret = lzbench_huff0_compress((char*)tmp, len, outbuf, outsize, 0, 0, NULL);

    // printf("huff compressed len: %lld\n", ret);

    free(tmp);
    return ret;
}
int64_t lzbench_sprintz_row_delta_huf_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{

    char* tmp = (char*)calloc(pad_size(outsize), 1);
    auto len = lzbench_huff0_decompress((char*)inbuf, insize, (char*)tmp, outsize, 0, 0, NULL);
    // auto ret = decompress8b_delta_rle((int8_t*)tmp, (uint8_t*)outbuf);
    auto ret = decompress_rowmajor_delta_8b((int8_t*)tmp, (uint8_t*)outbuf);
    free(tmp);
    return ret;
}

int64_t lzbench_sprintz_row_delta_rle_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return compress_rowmajor_delta_rle_8b((uint8_t*)inbuf, insize, (int8_t*)outbuf, ndims);
}
int64_t lzbench_sprintz_row_delta_rle_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return decompress_rowmajor_delta_rle_8b((int8_t*)inbuf, (uint8_t*)outbuf);
}

int64_t lzbench_sprintz_row_delta_rle_lowdim_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return compress_rowmajor_delta_rle_lowdim_8b((uint8_t*)inbuf, insize, (int8_t*)outbuf, ndims);
}
int64_t lzbench_sprintz_row_delta_rle_lowdim_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return decompress_rowmajor_delta_rle_lowdim_8b((int8_t*)inbuf, (uint8_t*)outbuf);
}

int64_t lzbench_sprintz_row_delta_rle_huf_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    char* tmp = (char*)calloc(pad_size(outsize), 1);
    auto len = compress_rowmajor_delta_rle_8b((uint8_t*)inbuf, insize, (int8_t*)tmp, ndims);
    auto ret = lzbench_huff0_compress((char*)tmp, len, outbuf, outsize, 0, 0, NULL);
    free(tmp);
    return ret;
}
int64_t lzbench_sprintz_row_delta_rle_huf_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{

    char* tmp = (char*)calloc(pad_size(outsize), 1);
    auto len = lzbench_huff0_decompress((char*)inbuf, insize, (char*)tmp, outsize, 0, 0, NULL);
    // auto ret = decompress8b_delta_rle((int8_t*)tmp, (uint8_t*)outbuf);
    auto ret = decompress_rowmajor_delta_rle_8b((int8_t*)tmp, (uint8_t*)outbuf);
    free(tmp);
    return ret;
}

int64_t lzbench_sprintz_row_delta_fse_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    char* tmp = (char*)malloc(pad_size(insize));
    // auto len = compress8b_delta_rle((uint8_t*)inbuf, insize, (int8_t*)tmp);
    auto len = compress_rowmajor_delta_8b((uint8_t*)inbuf, insize, (int8_t*)tmp, ndims);
    return lzbench_fse_compress(tmp, len, outbuf, outsize, 0, 0, NULL);
}
int64_t lzbench_sprintz_row_delta_fse_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    char* tmp = (char*)malloc(pad_size(outsize));
    auto len = lzbench_fse_decompress(inbuf, insize, tmp, outsize, 0, 0, NULL);
    // return decompress8b_delta_rle((int8_t*)tmp, (uint8_t*)outbuf);
    return decompress_rowmajor_delta_8b((int8_t*)tmp, (uint8_t*)outbuf);
}

// ================================ transforms

// ------------------------ delta
int64_t lzbench_sprintz_delta_encode(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return encode_delta_rowmajor_8b((uint8_t*)inbuf, insize, (int8_t*)outbuf, ndims);
}
int64_t lzbench_sprintz_delta_decode(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return decode_delta_rowmajor_8b((int8_t*)inbuf, (uint8_t*)outbuf);
}
// 16b
int64_t lzbench_sprintz_delta_encode_16b(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return encode_delta_rowmajor_16b((uint16_t*)inbuf, insize / 2, (int16_t*)outbuf, ndims) * 2;
}
int64_t lzbench_sprintz_delta_decode_16b(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return decode_delta_rowmajor_16b((int16_t*)inbuf, (uint16_t*)outbuf) * 2;
}

// ------------------------ double delta
int64_t lzbench_sprintz_doubledelta_encode(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return encode_doubledelta_rowmajor_8b((uint8_t*)inbuf, insize, (int8_t*)outbuf, ndims);
}
int64_t lzbench_sprintz_doubledelta_decode(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return decode_doubledelta_rowmajor_8b((int8_t*)inbuf, (uint8_t*)outbuf);
}
// 16b
int64_t lzbench_sprintz_doubledelta_encode_16b(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return encode_doubledelta_rowmajor_16b((uint16_t*)inbuf, insize / 2, (int16_t*)outbuf, ndims) * 2;
}
int64_t lzbench_sprintz_doubledelta_decode_16b(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return decode_doubledelta_rowmajor_16b((int16_t*)inbuf, (uint16_t*)outbuf) * 2;
}

// ------------------------ xff
int64_t lzbench_sprintz_xff_encode(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return encode_xff_rowmajor_8b((uint8_t*)inbuf, insize, (int8_t*)outbuf, ndims);
}
int64_t lzbench_sprintz_xff_decode(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return decode_xff_rowmajor_8b((int8_t*)inbuf, (uint8_t*)outbuf);
}
// 16b
int64_t lzbench_sprintz_xff_encode_16b(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return encode_xff_rowmajor_16b((uint16_t*)inbuf, insize / 2, (int16_t*)outbuf, ndims) * 2;
}
int64_t lzbench_sprintz_xff_decode_16b(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return decode_xff_rowmajor_16b((int16_t*)inbuf, (uint16_t*)outbuf) * 2;
}

// ================================ sprintz xff funcs

int64_t lzbench_sprintz_row_xff_rle_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*)
{
    return compress_rowmajor_xff_rle_8b((uint8_t*)inbuf, insize, (int8_t*)outbuf, ndims);
}
int64_t lzbench_sprintz_row_xff_rle_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return decompress_rowmajor_xff_rle_8b((int8_t*)inbuf, (uint8_t*)outbuf);
}

int64_t lzbench_sprintz_row_xff_rle_lowdim_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*)
{
    return compress_rowmajor_xff_rle_lowdim_8b((uint8_t*)inbuf, insize, (int8_t*)outbuf, ndims);
}
int64_t lzbench_sprintz_row_xff_rle_lowdim_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    return decompress_rowmajor_xff_rle_lowdim_8b((int8_t*)inbuf, (uint8_t*)outbuf);
}

// ================================ top-level sprintz functions

QueryParams create_sprintz_query_params(void* queryPtr) {
    lzbench::QueryRefs qrefs = *(lzbench::QueryRefs*)queryPtr;
    QueryTypes::Operation op;
    switch (qrefs.qparams->type) {
    case (lzbench::QUERY_NONE): op = QueryTypes::NOOP; break;
    case (lzbench::QUERY_MAX): op = QueryTypes::REDUCE_MAX; break;
    case (lzbench::QUERY_SUM): op = QueryTypes::REDUCE_SUM; break;
    default: op = QueryTypes::NOOP; break;
    }
    QueryParams sprintz_qparams{ .op = op, .materialize = false };
    return sprintz_qparams;
}

// ------------------------ 8b

// delta
int64_t lzbench_sprintz_delta_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*)
{
    return sprintz_compress_delta_8b((uint8_t*)inbuf, insize, (int8_t*)outbuf, ndims);
}
int64_t lzbench_sprintz_delta_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void* queryPtr)
{
    // printf("called sprintzDelta8b; queryPtr = %p\n", queryPtr);
    if (queryPtr) {
        // printf("created qparams = %p\n", queryPtr);
        auto sprintz_qparams = create_sprintz_query_params(queryPtr);
        // auto op = sprintz_qparams.op;
        // printf("created qparams; op = %d, materialize = %d\n",
        //     (int)sprintz_qparams.op, (int)sprintz_qparams.materialize);
        // printf("using inbuf, outpuf = %p, %p\n", inbuf, outbuf);
        // printf("about to query; using insize, outsize = %lu, %lu\n", insize, outsize);
        query_rowmajor_delta_rle_8b((int8_t*)inbuf, (uint8_t*)outbuf, sprintz_qparams);
        // printf("ran query, didn't crash!\n");
        return -1;
    }
    // printf("sprintzDelta8b: about to decomp from buff %p to buff %p\n", inbuf, outbuf);
    return sprintz_decompress_delta_8b((int8_t*)inbuf, (uint8_t*)outbuf);
}

// xff
int64_t lzbench_sprintz_xff_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*)
{
    return sprintz_compress_xff_8b((uint8_t*)inbuf, insize, (int8_t*)outbuf, ndims);
}
int64_t lzbench_sprintz_xff_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void* queryPtr)
{
    if (queryPtr) {
        auto sprintz_qparams = create_sprintz_query_params(queryPtr);
        query_rowmajor_xff_rle_8b((int8_t*)inbuf, (uint8_t*)outbuf, sprintz_qparams);
        return -1;
    }
    return sprintz_decompress_xff_8b((int8_t*)inbuf, (uint8_t*)outbuf);
}

// delta + huffman
int64_t lzbench_sprintz_delta_huf_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*)
{
    char* tmp = (char*)calloc(pad_size(outsize), 1);
    auto len = sprintz_compress_delta_8b((uint8_t*)inbuf, insize, (int8_t*)tmp, ndims);
    auto ret = lzbench_huff0_compress((char*)tmp, len, outbuf, outsize, 0, 0, NULL);
    free(tmp);
    return ret;
}
int64_t lzbench_sprintz_delta_huf_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    auto padded_outsize = pad_size(outsize);
    char* tmp = (char*)calloc(padded_outsize, 1);
    auto len = lzbench_huff0_decompress((char*)inbuf, insize, (char*)tmp, padded_outsize, 0, 0, NULL);
    auto ret = sprintz_decompress_delta_8b((int8_t*)tmp, (uint8_t*)outbuf);
    free(tmp);
    return ret;
}

// xff + huffman
int64_t lzbench_sprintz_xff_huf_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*)
{
    char* tmp = (char*)calloc(pad_size(outsize), 1);
    auto len = sprintz_compress_xff_8b((uint8_t*)inbuf, insize, (int8_t*)tmp, ndims);
    auto ret = lzbench_huff0_compress((char*)tmp, len, outbuf, outsize, 0, 0, NULL);
    free(tmp);
    return ret;
}
int64_t lzbench_sprintz_xff_huf_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    auto padded_outsize = pad_size(outsize);
    char* tmp = (char*)calloc(padded_outsize, 1);
    auto len = lzbench_huff0_decompress((char*)inbuf, insize, (char*)tmp, padded_outsize, 0, 0, NULL);
    auto ret = sprintz_decompress_xff_8b((int8_t*)tmp, (uint8_t*)outbuf);
    free(tmp);
    return ret;
}

// ------------------------ 16b

// #define CREATE_SPRINTZ_QUERY_PARAMS(queryPtr)                           \
//     lzbench::QueryRefs qrefs = *(lzbench::QueryRefs*)queryPtr;          \
//     QueryTypes::Operation op;                                           \
//     switch (qrefs.qparams->type) {                                      \
//     case (lzbench::QUERY_NONE): op = QueryTypes::NOOP; break;           \
//     case (lzbench::QUERY_MAX): op = QueryTypes::REDUCE_MAX; break;
//     case (lzbench::QUERY_SUM): op = QueryTypes::REDUCE_SUM; break;
//     default: op = QueryTypes::NOOP; break;
//     }
//     QueryParams sprintz_qparams{ .op = op, .materialize = false };



// delta
int64_t lzbench_sprintz_delta_compress_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*)
{
    return sprintz_compress_delta_16b((uint16_t*)inbuf, insize/2, (int16_t*)outbuf, ndims) * 2;
}
int64_t lzbench_sprintz_delta_decompress_16b(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void* queryPtr)
{
    // if (false) {
    if (queryPtr) {
        // // printf("about to deref workmem; addr = %p\n", queryPtr);
        // lzbench::QueryRefs qrefs = *(lzbench::QueryRefs*)queryPtr;
        // // printf("qrefs op: %d\n", (int)qrefs.qparams.type);
        // QueryTypes::Operation op;
        // switch (qrefs.qparams->type) {
        // case (lzbench::QUERY_NONE): op = QueryTypes::NOOP; break;
        // case (lzbench::QUERY_MAX): op = QueryTypes::REDUCE_MAX; break;
        // case (lzbench::QUERY_SUM): op = QueryTypes::REDUCE_SUM; break;
        // default: op = QueryTypes::NOOP; break;
        // }
        // QueryParams sprintz_qparams{ .op = op, .materialize = false };
        // printf("running query #%d!\n", (int)op);
        auto sprintz_qparams = create_sprintz_query_params(queryPtr);
        query_rowmajor_delta_rle_16b((int16_t*)inbuf, (uint16_t*)outbuf, sprintz_qparams);
        return -1;
    }
    return sprintz_decompress_delta_16b((int16_t*)inbuf, (uint16_t*)outbuf) * 2;
}

// xff
int64_t lzbench_sprintz_xff_compress_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*)
{
    return sprintz_compress_xff_16b((uint16_t*)inbuf, insize/2, (int16_t*)outbuf, ndims) * 2;
}
int64_t lzbench_sprintz_xff_decompress_16b(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void* queryPtr)
{
    if (queryPtr) {
        auto sprintz_qparams = create_sprintz_query_params(queryPtr);
        query_rowmajor_xff_rle_16b((int16_t*)inbuf, (uint16_t*)outbuf, sprintz_qparams);
        return -1;
    }
    return sprintz_decompress_xff_16b((int16_t*)inbuf, (uint16_t*)outbuf) * 2;
}

// delta + huffman
int64_t lzbench_sprintz_delta_huf_compress_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*)
{
    auto padded_sz = pad_size(outsize);
    // auto padded_sz = outsize;
    char* tmp = (char*)calloc(padded_sz, 1);
    // printf("delta huf compress: first two bytes = %d, %d\n", (int)inbuf[0], (int)inbuf[1]);

    // printf("delta huf compress: first few bytes = ");
    // for (int i = 0; i < 10; i++) {
    //     printf("%d ", (int)inbuf[i]);
    // }
    // printf("\n");
    // printf("delta huf compress: last few bytes (using len = %d) = ", (int)insize);
    // for (int i = 0; i < 10; i++) {
    //     printf("%d ", (int)inbuf[insize - 10 + i]);
    // }
    // printf("\n");

    // TODO rm + 1 in next line after off-by-one fix
    auto len = sprintz_compress_delta_16b((uint16_t*)inbuf, insize/2, (int16_t*)tmp, ndims) * 2 + 1;
    auto ret = lzbench_huff0_compress((char*)tmp, len, outbuf, padded_sz, 0, 0, NULL);
    free(tmp);

    // printf("delta huf compress: first few bytes of compressed data = ");
    // for (int i = 0; i < 10; i++) {
    //     printf("%d ", (int)outbuf[i]);
    // }
    // printf("\n");
    // printf("\tCOMP:   compressed data ptr: %p; compressed sz: %d\n", outbuf, (int)ret);

    return ret;
}
int64_t lzbench_sprintz_delta_huf_decompress_16b(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    auto padded_outsize = pad_size(outsize);
    // auto padded_outsize = outsize; // TODO rm after debug
    char* tmp = (char*)calloc(padded_outsize, 1);
    // printf("\tDECOMP: compressed data ptr: %p; compressed sz: %d\n", inbuf, (int)insize);
    auto len = lzbench_huff0_decompress((char*)inbuf, insize, (char*)tmp, padded_outsize, 0, 0, NULL);
    auto ret = sprintz_decompress_delta_16b((int16_t*)tmp, (uint16_t*)outbuf) * 2;
    // printf("delta huf decompress: first two bytes = %d, %d\n", (int)outbuf[0], (int)outbuf[1]);

    // printf("delta huf decompress: first few bytes = ");
    // for (int i = 0; i < 10; i++) {
    //     printf("%d ", (int)outbuf[i]);
    // }
    // printf("\n");
    // printf("delta huf decompress: last few bytes (using len = %d) = ", (int)ret);
    // for (int i = 0; i < 10; i++) {
    //     printf("%d ", (int)outbuf[ret - 10 + i]);
    // }
    // printf("\n");

    free(tmp);
    return ret;
}

// xff + huffman
int64_t lzbench_sprintz_xff_huf_compress_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*)
{
    char* tmp = (char*)calloc(pad_size(outsize), 1);
    // TODO rm + 1 in next line after off-by-one fix
    auto len = sprintz_compress_xff_16b((uint16_t*)inbuf, insize/2, (int16_t*)tmp, ndims) * 2 + 1;
    auto ret = lzbench_huff0_compress((char*)tmp, len, outbuf, outsize, 0, 0, NULL);
    free(tmp);
    return ret;
}
int64_t lzbench_sprintz_xff_huf_decompress_16b(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t ndims, size_t, void*)
{
    auto padded_outsize = pad_size(outsize);
    char* tmp = (char*)calloc(padded_outsize, 1);
    auto len = lzbench_huff0_decompress((char*)inbuf, insize, (char*)tmp, padded_outsize, 0, 0, NULL);
    auto ret = sprintz_decompress_xff_16b((int16_t*)tmp, (uint16_t*)outbuf) * 2;
    free(tmp);
    return ret;
}


// ================================ queries

int64_t lzbench_sprintz_delta_query0_8b(char *inbuf, size_t insize,
        char *outbuf, size_t outsize, size_t ndims, size_t, void*)
{
    // // works (but doesn't run the query)
    // return lzbench_sprintz_delta_decompress(inbuf, insize, outbuf, outsize, ndims, 0, NULL);

    // // memcpy(outbuf, inbuf, insize);
    // // return insize;
    // // qp.op = REDUCE_MAX;
    QueryParams qp;
    qp.op = QueryTypes::REDUCE_MAX;
    return query_rowmajor_delta_rle_8b((int8_t*)inbuf, (uint8_t*)outbuf, qp);
}

int64_t lzbench_sprintz_xff_query1_16b(char *inbuf, size_t insize,
        char *outbuf, size_t outsize, size_t ndims, size_t, void*)
{
    // memcpy(outbuf, inbuf, insize);
    // return insize;
    // return -1;

    QueryParams qp;
    qp.op = QueryTypes::REDUCE_SUM;
    return query_rowmajor_xff_rle_16b((int16_t*)inbuf, (uint16_t*)outbuf, qp);
}

#endif


