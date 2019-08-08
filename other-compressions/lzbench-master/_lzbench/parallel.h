//
// parallel.h
// Created by D Blalock 2018-2-28
//

#ifndef _lzbench_parallel_h
#define _lzbench_parallel_h

#include "lzbench.h"

#include <vector>

namespace lzbench {

// void do_parallel_stuff();
// void parallel_decomp(lzbench_params_t *paramsm const compressor_desc_t* desc,
//     int level, uint8_t *compbuf, uint8_t *decomp, uint8_t *tmp,  bench_rate_t rate,
//     size_t param1, std::vector<size_t> compr_sizes, char* workmem=NULL);

void parallel_decomp(lzbench_params_t *params,
    std::vector<size_t>& chunk_sizes, const compressor_desc_t* desc,
    std::vector<size_t> &compr_sizes, const uint8_t *inbuf, uint8_t *outbuf,
    uint8_t* tmpbuf, bench_rate_t rate, std::vector<uint64_t> comp_times,
    size_t param1, size_t param2, char* workmems[]);

} // namespace lzbench

#endif
