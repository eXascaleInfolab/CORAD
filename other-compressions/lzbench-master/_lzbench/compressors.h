#ifndef LZBENCH_COMPRESSORS_H
#define LZBENCH_COMPRESSORS_H

#include <stdlib.h>
#include <stdint.h> // int64_t

#define BENCH_REMOVE_LZHAM  // not compiling on ubuntu for some reason

int64_t lzbench_memcpy(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t , size_t, void* );
int64_t lzbench_return_0(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t , size_t, void* );



// #ifndef BENCH_REMOVE_BLOSCLZ
// 	int64_t lzbench_blosclz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
// 	int64_t lzbench_blosclz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
// #else
// 	#define lzbench_blosclz_compress NULL
// 	#define lzbench_blosclz_decompress NULL
// #endif


#ifndef BENCH_REMOVE_BRIEFLZ
    char* lzbench_brieflz_init(size_t insize, size_t level, size_t);
    void lzbench_brieflz_deinit(void* workmem);
	int64_t lzbench_brieflz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_brieflz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_brieflz_init NULL
	#define lzbench_brieflz_deinit NULL
	#define lzbench_brieflz_compress NULL
	#define lzbench_brieflz_decompress NULL
#endif


#ifndef BENCH_REMOVE_BROTLI
	int64_t lzbench_brotli_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_brotli_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_brotli_compress NULL
	#define lzbench_brotli_decompress NULL
#endif


#ifndef BENCH_REMOVE_CRUSH
	int64_t lzbench_crush_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_crush_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_crush_compress NULL
	#define lzbench_crush_decompress NULL
#endif


#ifndef BENCH_REMOVE_CSC
	int64_t lzbench_csc_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_csc_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_csc_compress NULL
	#define lzbench_csc_decompress NULL
#endif


#ifndef BENCH_REMOVE_DENSITY
	int64_t lzbench_density_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_density_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_density_compress NULL
	#define lzbench_density_decompress NULL
#endif


#ifndef BENCH_REMOVE_FASTLZ
	int64_t lzbench_fastlz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_fastlz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_fastlz_compress NULL
	#define lzbench_fastlz_decompress NULL
#endif


#ifndef BENCH_REMOVE_GIPFELI
	int64_t lzbench_gipfeli_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_gipfeli_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_gipfeli_compress NULL
	#define lzbench_gipfeli_decompress NULL
#endif


#ifndef BENCH_REMOVE_GLZA
	int64_t lzbench_glza_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
	int64_t lzbench_glza_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_glza_compress NULL
	#define lzbench_glza_decompress NULL
#endif


#ifndef BENCH_REMOVE_LIBDEFLATE
	int64_t lzbench_libdeflate_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_libdeflate_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_libdeflate_compress NULL
	#define lzbench_libdeflate_decompress NULL
#endif


#ifndef BENCH_REMOVE_LIZARD
	int64_t lzbench_lizard_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_lizard_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_lizard_compress NULL
	#define lzbench_lizard_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZ4
	int64_t lzbench_lz4_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_lz4fast_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize,  size_t level, size_t, void*);
	int64_t lzbench_lz4hc_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize,  size_t level, size_t, void*);
	int64_t lzbench_lz4_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_lz4_compress NULL
	#define lzbench_lz4fast_compress NULL
	#define lzbench_lz4hc_compress NULL
	#define lzbench_lz4_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZF
	int64_t lzbench_lzf_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_lzf_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_lzf_compress NULL
	#define lzbench_lzf_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZFSE
    char* lzbench_lzfse_init(size_t insize, size_t level, size_t);
    void lzbench_lzfse_deinit(void* workmem);
	int64_t lzbench_lzfse_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_lzfse_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_lzfse_init NULL
	#define lzbench_lzfse_deinit NULL
	#define lzbench_lzfse_compress NULL
	#define lzbench_lzfse_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZVN
    char* lzbench_lzvn_init(size_t insize, size_t level, size_t);
    void lzbench_lzvn_deinit(void* workmem);
	int64_t lzbench_lzvn_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_lzvn_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_lzvn_init NULL
	#define lzbench_lzvn_deinit NULL
	#define lzbench_lzvn_compress NULL
	#define lzbench_lzvn_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZG
	int64_t lzbench_lzg_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_lzg_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_lzg_compress NULL
	#define lzbench_lzg_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZHAM
	int64_t lzbench_lzham_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_lzham_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_lzham_compress NULL
	#define lzbench_lzham_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZJB
	int64_t lzbench_lzjb_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_lzjb_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_lzjb_compress NULL
	#define lzbench_lzjb_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZLIB
	int64_t lzbench_lzlib_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_lzlib_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_lzlib_compress NULL
	#define lzbench_lzlib_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZMA
	int64_t lzbench_lzma_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_lzma_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_lzma_compress NULL
	#define lzbench_lzma_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZMAT
	int64_t lzbench_lzmat_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_lzmat_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_lzmat_compress NULL
	#define lzbench_lzmat_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZO
    char* lzbench_lzo_init(size_t insize, size_t level, size_t);
    void lzbench_lzo_deinit(void* workmem);
    int64_t lzbench_lzo1_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem);
    int64_t lzbench_lzo1_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_lzo1a_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem);
    int64_t lzbench_lzo1a_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_lzo1b_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem);
    int64_t lzbench_lzo1b_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_lzo1c_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem);
    int64_t lzbench_lzo1c_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_lzo1f_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem);
    int64_t lzbench_lzo1f_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_lzo1x_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem);
    int64_t lzbench_lzo1x_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_lzo1y_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem);
    int64_t lzbench_lzo1y_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_lzo1z_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem);
    int64_t lzbench_lzo1z_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_lzo2a_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void* workmem);
    int64_t lzbench_lzo2a_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
#else
	#define lzbench_lzo_init NULL
	#define lzbench_lzo_deinit NULL
	#define lzbench_lzo1_compress NULL
	#define lzbench_lzo1_decompress NULL
	#define lzbench_lzo1a_compress NULL
	#define lzbench_lzo1a_decompress NULL
	#define lzbench_lzo1b_compress NULL
	#define lzbench_lzo1b_decompress NULL
	#define lzbench_lzo1c_compress NULL
	#define lzbench_lzo1c_decompress NULL
	#define lzbench_lzo1f_compress NULL
	#define lzbench_lzo1f_decompress NULL
	#define lzbench_lzo1x_compress NULL
	#define lzbench_lzo1x_decompress NULL
	#define lzbench_lzo1y_compress NULL
	#define lzbench_lzo1y_decompress NULL
	#define lzbench_lzo1z_compress NULL
	#define lzbench_lzo1z_decompress NULL
	#define lzbench_lzo2a_compress NULL
	#define lzbench_lzo2a_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZRW
    char* lzbench_lzrw_init(size_t insize, size_t level, size_t);
    void lzbench_lzrw_deinit(void* workmem);
	int64_t lzbench_lzrw_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_lzrw_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_lzrw_init NULL
	#define lzbench_lzrw_deinit NULL
	#define lzbench_lzrw_compress NULL
	#define lzbench_lzrw_decompress NULL
#endif


#ifndef BENCH_REMOVE_LZSSE
    char* lzbench_lzsse2_init(size_t insize, size_t level, size_t);
    void lzbench_lzsse2_deinit(void* workmem);
    int64_t lzbench_lzsse2_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_lzsse2_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
    char* lzbench_lzsse4_init(size_t insize, size_t level, size_t);
    void lzbench_lzsse4_deinit(void* workmem);
    int64_t lzbench_lzsse4_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_lzsse4_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
    char* lzbench_lzsse4fast_init(size_t insize, size_t level, size_t);
    void lzbench_lzsse4fast_deinit(void* workmem);
    int64_t lzbench_lzsse4fast_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    char* lzbench_lzsse8_init(size_t insize, size_t level, size_t);
    void lzbench_lzsse8_deinit(void* workmem);
    int64_t lzbench_lzsse8_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_lzsse8_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
    char* lzbench_lzsse8fast_init(size_t insize, size_t level, size_t);
    void lzbench_lzsse8fast_deinit(void* workmem);
    int64_t lzbench_lzsse8fast_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
#else
    #define lzbench_lzsse2_init NULL
    #define lzbench_lzsse2_deinit NULL
    #define lzbench_lzsse2_compress NULL
    #define lzbench_lzsse2_decompress NULL
    #define lzbench_lzsse4_init NULL
    #define lzbench_lzsse4_deinit NULL
    #define lzbench_lzsse4_compress NULL
    #define lzbench_lzsse4_decompress NULL
    #define lzbench_lzsse4fast_init NULL
    #define lzbench_lzsse4fast_deinit NULL
    #define lzbench_lzsse4fast_compress NULL
    #define lzbench_lzsse8_init NULL
    #define lzbench_lzsse8_deinit NULL
    #define lzbench_lzsse8_compress NULL
    #define lzbench_lzsse8_decompress NULL
    #define lzbench_lzsse8fast_init NULL
    #define lzbench_lzsse8fast_deinit NULL
    #define lzbench_lzsse8fast_compress NULL
#endif


#ifndef BENCH_REMOVE_PITHY
	int64_t lzbench_pithy_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_pithy_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_pithy_compress NULL
	#define lzbench_pithy_decompress NULL
#endif


#ifndef BENCH_REMOVE_QUICKLZ
	int64_t lzbench_quicklz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_quicklz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_quicklz_compress NULL
	#define lzbench_quicklz_decompress NULL
#endif


#ifndef BENCH_REMOVE_SHRINKER
	int64_t lzbench_shrinker_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_shrinker_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_shrinker_compress NULL
	#define lzbench_shrinker_decompress NULL
#endif


#ifndef BENCH_REMOVE_SLZ
	int64_t lzbench_slz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
	int64_t lzbench_slz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_slz_compress NULL
	#define lzbench_slz_decompress NULL
#endif


#ifndef BENCH_REMOVE_SNAPPY
	int64_t lzbench_snappy_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_snappy_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_snappy_compress NULL
	#define lzbench_snappy_decompress NULL
#endif


#ifndef BENCH_REMOVE_TORNADO
	int64_t lzbench_tornado_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_tornado_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_tornado_compress NULL
	#define lzbench_tornado_decompress NULL
#endif


#ifndef BENCH_REMOVE_UCL
    int64_t lzbench_ucl_nrv2b_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_ucl_nrv2b_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_ucl_nrv2d_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_ucl_nrv2d_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_ucl_nrv2e_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_ucl_nrv2e_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
#else
	#define lzbench_ucl_nrv2b_compress NULL
	#define lzbench_ucl_nrv2b_decompress NULL
	#define lzbench_ucl_nrv2d_compress NULL
	#define lzbench_ucl_nrv2d_decompress NULL
	#define lzbench_ucl_nrv2e_compress NULL
	#define lzbench_ucl_nrv2e_decompress NULL
#endif


#ifndef BENCH_REMOVE_WFLZ
    char* lzbench_wflz_init(size_t insize, size_t level, size_t);
    void lzbench_wflz_deinit(void* workmem);
	int64_t lzbench_wflz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_wflz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_wflz_init NULL
	#define lzbench_wflz_deinit NULL
	#define lzbench_wflz_compress NULL
	#define lzbench_wflz_decompress NULL
#endif


#ifndef BENCH_REMOVE_XPACK
    char* lzbench_xpack_init(size_t insize, size_t level, size_t);
    void lzbench_xpack_deinit(void* workmem);
	int64_t lzbench_xpack_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_xpack_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_xpack_init NULL
	#define lzbench_xpack_deinit NULL
	#define lzbench_xpack_compress NULL
	#define lzbench_xpack_decompress NULL
#endif


#ifndef BENCH_REMOVE_XZ
	int64_t lzbench_xz_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_xz_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_xz_compress NULL
	#define lzbench_xz_decompress NULL
#endif


#ifndef BENCH_REMOVE_YALZ77
	int64_t lzbench_yalz77_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_yalz77_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_yalz77_compress NULL
	#define lzbench_yalz77_decompress NULL
#endif


#ifndef BENCH_REMOVE_YAPPY
    char* lzbench_yappy_init(size_t insize, size_t level, size_t);
	int64_t lzbench_yappy_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_yappy_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_yappy_init NULL
	#define lzbench_yappy_compress NULL
	#define lzbench_yappy_decompress NULL
#endif


#ifndef BENCH_REMOVE_ZLIB
	int64_t lzbench_zlib_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
	int64_t lzbench_zlib_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_zlib_compress NULL
	#define lzbench_zlib_decompress NULL
#endif


#ifndef BENCH_REMOVE_ZLING
	int64_t lzbench_zling_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
	int64_t lzbench_zling_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_zling_compress NULL
	#define lzbench_zling_decompress NULL
#endif


#ifndef BENCH_REMOVE_ZSTD
    char* lzbench_zstd_init(size_t insize, size_t level, size_t);
    void lzbench_zstd_deinit(void* workmem);
	int64_t lzbench_zstd_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
	int64_t lzbench_zstd_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);

    int64_t lzbench_fse_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
    int64_t lzbench_fse_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);

    int64_t lzbench_huff0_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
    int64_t lzbench_huff0_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);


#else
	#define lzbench_zstd_init NULL
	#define lzbench_zstd_deinit NULL
	#define lzbench_zstd_compress NULL
	#define lzbench_zstd_decompress NULL
#endif


#ifdef BENCH_HAS_NAKAMICHI
	int64_t lzbench_nakamichi_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
	int64_t lzbench_nakamichi_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
	#define lzbench_nakamichi_compress NULL
	#define lzbench_nakamichi_decompress NULL
#endif

#ifndef BENCH_REMOVE_EXAMPLE
    int64_t lzbench_example_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_example_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
    #define lzbench_example_compress NULL
    #define lzbench_example_decompress NULL
#endif

#ifndef BENCH_REMOVE_FASTPFOR

    #define DECLARE_FASTPFOR_FUNC(NAME)                                     \
        int64_t lzbench_ ## NAME ## _compress(char *inbuf, size_t insize,       \
            char *outbuf, size_t outsize, size_t level, size_t, void*);     \
        int64_t lzbench_ ## NAME ## _decompress(char *inbuf, size_t insize,     \
            char *outbuf, size_t outsize, size_t, size_t, void*);           \

    DECLARE_FASTPFOR_FUNC(fastpfor)
    DECLARE_FASTPFOR_FUNC(binarypacking)
    DECLARE_FASTPFOR_FUNC(optpfor)
    DECLARE_FASTPFOR_FUNC(varintg8iu)
    DECLARE_FASTPFOR_FUNC(simple8b)
    DECLARE_FASTPFOR_FUNC(simdgroupsimple)
    // int64_t lzbench_fastpfor_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    // int64_t lzbench_fastpfor_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);

    // int64_t lzbench_simdbp128_compress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t level, size_t, void*);
    // int64_t lzbench_simdbp128_decompress(char *inbuf, size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#else
    #define lzbench_fastpfor_compress NULL
    #define lzbench_fastpfor_decompress NULL

    #define lzbench_simdbp128_compress NULL
    #define lzbench_simdbp128_decompress NULL
#endif

#ifndef BENCH_REMOVE_BLOSC
 int64_t lzbench_blosclz_compress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t level, size_t, void*);
 int64_t lzbench_blosclz_decompress(char *inbuf, size_t insize, char *outbuf,
    size_t outsize, size_t, size_t, void*);

 int64_t lzbench_blosc_bitshuf_compress(char *inbuf, size_t insize,
    char *outbuf, size_t outsize, size_t level, size_t, void*);
 int64_t lzbench_blosc_bitshuf_decompress(char *inbuf, size_t insize,
    char *outbuf, size_t outsize, size_t, size_t, void*);

 int64_t lzbench_blosc_byteshuf_compress(char *inbuf, size_t insize,
    char *outbuf, size_t outsize, size_t level, size_t, void*);
 int64_t lzbench_blosc_byteshuf_decompress(char *inbuf, size_t insize,
    char *outbuf, size_t outsize, size_t, size_t, void*);

#else
 #define lzbench_blosclz_compress NULL
 #define lzbench_blosclz_decompress NULL
#endif


#ifndef BENCH_REMOVE_BBP
    int64_t lzbench_bbp_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_bbp_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t, size_t, void*);
    char* lzbench_bbp_init(size_t insize, size_t level, size_t);
    void lzbench_bbp_deinit(void* workmem);
#else
    #define lzbench_bbp_compress NULL
    #define lzbench_bbp_decompress NULL
    #define lzbench_bbp_init NULL
    #define lzbench_bbp_deinit NULL
#endif

#ifndef BENCH_REMOVE_SPRINTZ
    int64_t lzbench_sprintz_delta_1d_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_sprintz_delta_1d_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t, size_t, void*);

    int64_t lzbench_sprintz_dbldelta_1d_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_sprintz_dbldelta_1d_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t, size_t, void*);

    int64_t lzbench_sprintz_dyndelta_1d_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_sprintz_dyndelta_1d_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t, size_t, void*);

    int64_t lzbench_sprintz_delta2_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_sprintz_delta2_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t, size_t, void*);

    int64_t lzbench_sprintz_delta_rle_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_sprintz_delta_rle_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t, size_t, void*);

    int64_t lzbench_sprintz_delta_rle2_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_sprintz_delta_rle2_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t, size_t, void*);

    int64_t lzbench_sprintz_delta_rle_fse_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_sprintz_delta_rle_fse_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t, size_t, void*);

    int64_t lzbench_sprintz_delta_rle_huf_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t level, size_t, void* workmem);
    int64_t lzbench_sprintz_delta_rle_huf_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t level, size_t, void* workmem);

#ifndef BENCH_REMOVE_ZSTD
    int64_t lzbench_sprintz_delta_rle_zstd_compress(char *inbuf, size_t insize,
        char *outbuf, size_t outsize, size_t level, size_t, void*);
    int64_t lzbench_sprintz_delta_rle_zstd_decompress(char *inbuf,
        size_t insize, char *outbuf, size_t outsize, size_t, size_t, void*);
#endif

    int64_t lzbench_fixed_bitpack_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t nbits, size_t, void*);
    int64_t lzbench_fixed_bitpack_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t nbits, size_t, void*);

    int64_t lzbench_just_bitpack_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_just_bitpack_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    int64_t lzbench_sprintz_row_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_row_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    int64_t lzbench_sprintz_row_delta_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_row_delta_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    int64_t lzbench_sprintz_row_delta_huf_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_row_delta_huf_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    int64_t lzbench_sprintz_row_delta_fse_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_row_delta_fse_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    int64_t lzbench_sprintz_row_delta_rle_compress(char *inbuf, size_t insize,
        char *outbuf, size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_row_delta_rle_decompress(char *inbuf, size_t insize,
        char *outbuf, size_t outsize, size_t ndims, size_t, void*);

    int64_t lzbench_sprintz_row_delta_rle_lowdim_compress(char *inbuf,
        size_t insize, char *outbuf, size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_row_delta_rle_lowdim_decompress(char *inbuf,
        size_t insize, char *outbuf, size_t outsize, size_t ndims, size_t, void*);

    int64_t lzbench_sprintz_row_delta_rle_huf_compress(char *inbuf,
        size_t insize, char *outbuf, size_t outsize, size_t ndims, size_t,
        void*);
    int64_t lzbench_sprintz_row_delta_rle_huf_decompress(char *inbuf,
        size_t insize, char *outbuf, size_t outsize, size_t ndims, size_t,
        void*);

    // ================================ transforms

    // ------------------------ delta
    int64_t lzbench_sprintz_delta_encode(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_delta_decode(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_delta_encode_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_delta_decode_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    // ------------------------ double delta
    int64_t lzbench_sprintz_doubledelta_encode(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_doubledelta_decode(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_doubledelta_encode_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_doubledelta_decode_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    // ------------------------ xff
    int64_t lzbench_sprintz_xff_encode(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_xff_decode(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_xff_encode_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_xff_decode_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    // ================================ xff funcs

    // raw xff
    int64_t lzbench_sprintz_xff_encode(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_xff_decode(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    // xff + rle
    int64_t lzbench_sprintz_row_xff_rle_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_row_xff_rle_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    // xff lowdim
    int64_t lzbench_sprintz_row_xff_rle_lowdim_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_row_xff_rle_lowdim_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    // ================================ top-level sprintz functions

    // ------------------------ 8b

    // delta
    int64_t lzbench_sprintz_delta_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_delta_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    // xff
    int64_t lzbench_sprintz_xff_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_xff_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    // delta + huffman
    int64_t lzbench_sprintz_delta_huf_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_delta_huf_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    // xff + huffman
    int64_t lzbench_sprintz_xff_huf_compress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_xff_huf_decompress(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    // ------------------------ 16b

    // delta
    int64_t lzbench_sprintz_delta_compress_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_delta_decompress_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    // xff
    int64_t lzbench_sprintz_xff_compress_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_xff_decompress_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    // delta + huffman
    int64_t lzbench_sprintz_delta_huf_compress_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_delta_huf_decompress_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    // xff + huffman
    int64_t lzbench_sprintz_xff_huf_compress_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);
    int64_t lzbench_sprintz_xff_huf_decompress_16b(char *inbuf, size_t insize, char *outbuf,
        size_t outsize, size_t ndims, size_t, void*);

    // ================================ sprintz query functions

    // ------------------------ 8b
    int64_t lzbench_sprintz_delta_query0_8b(char *inbuf, size_t insize,
        char *outbuf, size_t outsize, size_t ndims, size_t, void*);

    // ------------------------ 16b
    int64_t lzbench_sprintz_xff_query1_16b(char *inbuf, size_t insize,
        char *outbuf, size_t outsize, size_t ndims, size_t, void*);


#else
    #define lzbench_sprintz_delta_1d_compress
    #define lzbench_sprintz_delta_1d_decompress
    #define lzbench_sprintz_delta2_compress
    #define lzbench_sprintz_delta2_decompress
    #define lzbench_sprintz_dbldelta_1d_compress
    #define lzbench_sprintz_dbldelta_1d_decompress
    #define lzbench_sprintz_dyndelta_1d_compress
    #define lzbench_sprintz_dyndelta_1d_decompress

    #define lzbench_sprintz_delta_rle_compress
    #define lzbench_sprintz_delta_rle_decompress
    #define lzbench_sprintz_delta_rle2_compress
    #define lzbench_sprintz_delta_rle2_decompress

    #define lzbench_sprintz_delta_rle_fse_compress
    #define lzbench_sprintz_delta_rle_fse_decompress
    #define lzbench_sprintz_delta_rle_huf_compress
    #define lzbench_sprintz_delta_rle_huf_decompress
    #define lzbench_sprintz_delta_rle_zstd_compress
    #define lzbench_sprintz_delta_rle_zstd_decompress
#endif

#endif // LZBENCH_COMPRESSORS_H
