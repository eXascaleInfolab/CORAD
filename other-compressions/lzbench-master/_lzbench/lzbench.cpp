/*
(C) 2011-2016 by Przemyslaw Skibinski (inikep@gmail.com)

    LICENSE

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation; either version 3 of
    the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful, but
    WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    General Public License for more details at
    Visit <http://www.gnu.org/copyleft/gpl.html>.

*/

#include "lzbench.h"
#include "util.h"
#include "output.h"
#include "parallel.h"
#include "preprocessing.h"
#include "query.hpp"

#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>

namespace lzbench {

inline int64_t lzbench_compress(lzbench_params_t *params,
    std::vector<size_t>& chunk_sizes, compress_func compress,
    std::vector<size_t> &compr_sizes, const uint8_t *inbuf, uint8_t *outbuf,
    uint8_t* tmpbuf, size_t outsize, size_t param1, size_t param2,
    char* workmem)
{
    int64_t clen;
    size_t outpart, part, sum = 0;
    const uint8_t *start = inbuf;
    int cscount = chunk_sizes.size();

    compr_sizes.resize(cscount);

    for (int i = 0; i < cscount; i++) {
        part = chunk_sizes[i];
        outpart = GET_COMPRESS_BOUND(part);
        if (outpart > outsize) outpart = outsize;

        const uint8_t* inptr = inbuf;
        if (params->preprocessors.size() > 0) {
            apply_preprocessors(params->preprocessors, inbuf, part, params->data_info.element_sz, tmpbuf);
            inptr = (const uint8_t*)tmpbuf;
        }

        clen = compress((char*)inptr, part, (char*)outbuf, outpart, param1, param2, workmem);
        LZBENCH_PRINT(9, "ENC part=%d clen=%d in=%d\n", (int)part, (int)clen, (int)(inbuf-start));

        // if (clen <= 0 || clen == part)
        if (clen <= 0) {
            LZBENCH_PRINT(3, "WARNING: got compressed data length of %lld!\n", (long long)clen);
            if (part > outsize) return 0;
            memcpy(outbuf, inbuf, part);
            clen = part;
        }

        inbuf += part;
        outbuf += clen;
        outsize -= clen;
        compr_sizes[i] = clen;
        sum += clen;
    }
    return sum;
}


inline int64_t lzbench_decompress(lzbench_params_t *params,
    std::vector<size_t>& chunk_sizes, const compressor_desc_t* desc,
    std::vector<size_t> &compr_sizes, const uint8_t *inbuf, uint8_t *outbuf,
    uint8_t* tmpbuf, size_t param1, size_t param2, char* workmem)
{
    int64_t dlen = 0;
    size_t part, sum = 0;
    uint8_t *outstart = outbuf;
    int cscount = compr_sizes.size();
    compress_func decompress = desc->decompress;

    // bool has_preproc = params->preprocessors.size() > 0;

    auto qparams = params->query_params;
    // bool already_materialized = strings_equal(desc->name, "materialized") &&
    //     qparams.type != QUERY_NONE;
    bool already_materialized = strings_equal(desc->name, "materialized");

    LZBENCH_PRINT(9, "---- Decompressing %d chunks\n", (int)chunk_sizes.size());
    for (int i = 0; i < chunk_sizes.size(); i++) {
        LZBENCH_PRINT(9, "Chunk %d: orig size, compressed size = %d, %d\n",
            (int)i, (int)chunk_sizes[i], (int)compr_sizes[i]);
    }

    // printf("already_materialized? %d\n", (int)already_materialized);

    for (int i = 0; i < cscount; i++) {
        part = compr_sizes[i];

        if (!already_materialized) {
            if (part == chunk_sizes[i]) { // uncompressed
                memcpy(outbuf, inbuf, part);
                dlen = part;
            } else {
                LZBENCH_PRINT(9, "chunk %d: about to decompress\n", i);
                dlen = decompress((char*)inbuf, part, (char*)outbuf,
                    chunk_sizes[i], param1, param2, workmem);
            }
            undo_preprocessors(params->preprocessors, outbuf, dlen,
                params->data_info.element_sz);
        } else {
            // printf("already_materialized; skipping decomp, etc\n");
            dlen = part;
        }
        // printf("lzbench_decompress: undid preprocs!\n");

        // run query if one is specified
        if (qparams.type != QUERY_NONE) {
            // printf("got query type: %d; about to run a query...\n", qparams.type);
            // auto& dinfo = params->data_info;
            DataInfo dinfo = params->data_info;
            if (dinfo.ncols < 1) {
                printf("ERROR: Must specify number of columns in data to run query!\n");
                exit(1);
            }
            dinfo.nrows = dlen / (dinfo.ncols * dinfo.element_sz);
            // printf("dinfo nrows, ncols, size: %lu, %lu, %lu\n",
            //     dinfo.nrows, dinfo.ncols, dinfo.nrows * dinfo.ncols);

            // printf("------------------------ running query %d\n", (int)qparams.type);
            // QueryResult result = *poopinize(
            QueryResult result = *run_query(
                params->query_params, dinfo, outbuf);
            // printf("ran query type: %d\n", qparams.type);
            // printf("number of idxs in result: %lu\n", result.idxs.size());

            // printf("got query type: %d, flattened window data: \n", qparams.type);
            // for (auto val : qparams.window_data_dbl) {
            //     printf("%g", (double)val);
            // }
            // printf("\nData in window shape:\n");
            // for (int i = 0; i < qparams.window_nrows; i++) {
            //     for (int j = 0; i < qparams.window_ncols; j++) {
            //         auto idx = i * qparams.window_ncols + j;
            //         printf("%g", qparams.window_data_dbl[idx]);
            //     }
            // }
            // printf("\n");
            // volatile QueryResult res;
            // volatile vector<uint8_t> vals_u8;
            // volatile vector<uint16_t> vals_u16;
            // for (auto val : result.vals_u8) { vals_u8.push_back(val); }
            // for (auto val : result.vals_u16) { vals_u16.push_back(val); }

            // for (auto val : result.vals_u8) {
            //     // volatile uint8_t x = val;
            //     LZBENCH_PRINT(0, "%d ", (int)val);
            // }


            // prevent compiler from optimizing away query
            if (params->verbose > 999) {
                printf("query result bytes: ");
                for (auto val : result.vals) { printf("%u ", (uint32_t)val); }
                printf("\n");
            }
            // if (params->verbose > 999) {
            //     printf("query u8 result: ");
            //     for (auto val : result.vals_u8) { printf("%d ", (int)val); }
            //     printf("\n");
            //     printf("query u16 result: ");
            //     for (auto val : result.vals_u16) { printf("%d ", (int)val); }
            //     printf("\n");
            // }
            // for (auto val : result.vals_u8) { LZBENCH_PRINT(99, "%d ", (int)val); }
            // for (auto val : result.vals_u16) { LZBENCH_PRINT(99, "%d ", (int)val); }

            // res.vals_u8 = result.vals_u8;
            // res.vals_u16 = result.vals_u16;
            // LZBENCH_PRINT(4, "number of result values: %lu (u8) %lu (u16)\n",
            //     result.vals_u8.size(), result.vals_u16.size());
            LZBENCH_PRINT(4, "number of result values: %lu \n", result.vals.size());
        }

        LZBENCH_PRINT(9, "chunk %d: DEC part=%d dlen=%d out=%d\n",
            i, (int)part, (int)dlen, (int)(outbuf - outstart));
        if (dlen <= 0) { return dlen; }

        inbuf += part;
        outbuf += dlen;
        sum += dlen;
    }

    return sum;
}


void lzbench_test(lzbench_params_t *params, std::vector<size_t> &file_sizes,
    const compressor_desc_t* desc, int level, const uint8_t *inbuf,
    size_t insize, uint8_t *compbuf, size_t comprsize, uint8_t *decomp,
    bench_rate_t rate, size_t param1)
{
    float speed;
    int i, total_c_iters, total_d_iters;
    bench_timer_t loop_ticks, start_ticks, end_ticks, timer_ticks;
    int64_t complen=0, decomplen;
    uint64_t nanosec, total_nanosec;
    std::vector<uint64_t> ctime, dtime;
    std::vector<size_t> compr_sizes, chunk_sizes;
    bool decomp_error = false;
    char* workmem = nullptr;
    size_t param2 = desc->additional_param;
    size_t chunk_size = (params->chunk_size > insize) ? insize : params->chunk_size;

    uint8_t* tmpbuf = alloc_data_buffer(GET_COMPRESS_BOUND(insize));
    // printf("allocated tmpbuf of size: %d\n", (int)GET_COMPRESS_BOUND(insize));

    LZBENCH_PRINT(5, "*** trying %s insize=%d comprsize=%d chunk_size=%d\n", desc->name, (int)insize, (int)comprsize, (int)chunk_size);

    int nthreads = params->nthreads > 0 ? params->nthreads : 1;
    char* workmems[nthreads];
    for (int i = 0; i < nthreads; i++) { workmems[i] = nullptr; }
    if (desc->init) {
        for (int i = 0; i < nthreads; i++) {
            workmems[i] = desc->init(chunk_size, param1, param2);
        }
        workmem = workmems[0];

        // printf("workmem ptrs: ");
        // for (int i = 0; i < nthreads; i++) { printf("%p, ", workmems[i]); }
        // printf("\n");
    }
    // } else {
    //     printf("not initializing workmems cuz no desc->init\n");
    // }

    // printf("workmem ptrs: ");
    // for (int i = 0; i < nthreads; i++) { printf("%p, ", workmems[i]); }
    // printf("\n");

    if (desc->max_block_size != 0 && chunk_size > desc->max_block_size) chunk_size = desc->max_block_size;
    if (!desc->compress || !desc->decompress) goto done;
    // if (desc->init) workmem = desc->init(chunk_size, param1, param2);

    // if there's a minimum speed, check whether this codec is fast enough
    if (params->cspeed > 0) {
        size_t part = MIN(100*1024, chunk_size);
        GetTime(start_ticks);
        int64_t clen = desc->compress((char*)inbuf, part, (char*)compbuf, comprsize, param1, param2, workmem);
        GetTime(end_ticks);
        nanosec = GetDiffTime(rate, start_ticks, end_ticks) / 1000;
        if (clen > 0 && nanosec >= 1000) {
            part = (part / nanosec); // speed in MB/s
            if (part < params->cspeed) {
                LZBENCH_PRINT(7, "%s (100K) slower than %d MB/s nanosec=%d\n",
                    desc->name, (uint32_t)part, (uint32_t)nanosec);
                goto done;
            }
        }
    }

    // compute sizes of each chunk, given size limit and actual sizes
    for (int i=0; i<file_sizes.size(); i++) {
        size_t tmpsize = file_sizes[i];
        while (tmpsize > 0) {
            chunk_sizes.push_back(MIN(tmpsize, chunk_size));
            tmpsize -= MIN(tmpsize, chunk_size);
        }
    }

    LZBENCH_PRINT(5, "%s using %lu chunks; sizes = ",
        desc->name, chunk_sizes.size());
    for (auto sz : chunk_sizes) {
        LZBENCH_PRINT(5, "%lu ", (unsigned long)sz);
    }
    LZBENCH_PRINT(5, "%s", "\n"); // can't just print \n since needs VA_ARGS
    // printf("%s using %d chunks\n", desc->name, (int)chunk_sizes.size());
    // printf("chunk sizes: "); for (auto sz : chunk_sizes) { printf("%d ", int(sz)); } printf("\n");

    // compress the data until we hit either the minimum time or the minimum
    // number of iterations
    total_c_iters = 0;
    GetTime(timer_ticks);
    do {
        i = 0;
        uni_sleep(1); // give processor to other processes
        GetTime(loop_ticks);
        do {
            GetTime(start_ticks);
            complen = lzbench_compress(params, chunk_sizes, desc->compress,
                compr_sizes, inbuf, compbuf, tmpbuf, comprsize, param1, param2, workmem);
            GetTime(end_ticks);
            nanosec = GetDiffTime(rate, start_ticks, end_ticks);
            if (nanosec >= 10000) { ctime.push_back(nanosec); }
            i++;
        } while (GetDiffTime(rate, loop_ticks, end_ticks) < params->cloop_time);

        nanosec = GetDiffTime(rate, loop_ticks, end_ticks);
        ctime.push_back(nanosec/i);
        speed = nanosec > 0 ? (float)insize*i*1000/nanosec : -1;
        LZBENCH_PRINT(8, "%s nanosec=%d\n", desc->name, (int)nanosec);

        if ((uint32_t)speed < params->cspeed) {
            LZBENCH_PRINT(7, "%s slower than %d MB/s\n",
                desc->name, (uint32_t)speed);
            return;
        }

        total_nanosec = GetDiffTime(rate, timer_ticks, end_ticks);
        total_c_iters += i;
        if ((total_c_iters >= params->c_iters) && (total_nanosec > ((uint64_t)params->cmintime*1000000))) break;
        LZBENCH_PRINT(2, "%s compr iter=%d time=%.2fs speed=%.2f MB/s     \r", desc->name, total_c_iters, total_nanosec/1000000000.0, speed);
    } while (true);

    // decompress the data until we hit either the minimum time or the minimum
    // number of iterations; we reuse the data in compbuf written by the final
    // iteration of the compression
    total_d_iters = 0;
    GetTime(timer_ticks);

    if (!params->compress_only && params->nthreads > 0) {
        parallel_decomp(params, chunk_sizes,
                desc, compr_sizes, compbuf, decomp, tmpbuf, rate, ctime,
                param1, param2, &workmems[0]);
        // return;
        goto done;
    }

    if (!params->compress_only)
    do {
        i = 0;
        uni_sleep(1); // give processor to other processes

        // if running queries on (supposedly) materialized views of the data,
        // no decompression should be done when timing the query; we therefore
        // populate the decompressed buffer here so that lzbench_decompress,
        // which is what gets timed, can skip that part
        //
        // TODO string comparison is an ugly way of checking this
        // bool do_materialize = strings_equal(desc->name, "materialized") &&
        //     params->query_params.type != QUERY_NONE;
        bool do_materialize = strings_equal(desc->name, "materialized");
        // printf("do_materialize? %d\n", (int)do_materialize);
        // printf("query type: %d\n", (int)params->query_params.type);
        // printf("query type != query_none? %d\n", (int)(params->query_params.type != QUERY_NONE));
        if (do_materialize) {
            auto inptr = compbuf;
            auto outptr = decomp;
            for (int i = 0; i < compr_sizes.size(); i++) {
                auto comp_sz = compr_sizes[i];
                auto orig_sz = chunk_sizes[i];
                if (comp_sz != orig_sz) {
                    LZBENCH_PRINT(0, "Compressed size %lu != original size %lu"
                        " when we supposedly memcopied!", comp_sz, orig_sz);
                }
                // if (params->preprocessors.size() > 0) {
                //     undo_preprocessors(params->preprocessors, outptr, orig_sz,
                //         params->data_info.element_sz, outptr);
                // } else {
                    memcpy(outptr, inptr, orig_sz);
                    undo_preprocessors(params->preprocessors, outptr, orig_sz,
                        params->data_info.element_sz);
                // }
                inptr += orig_sz;
                outptr += orig_sz;
            }
        }

        GetTime(loop_ticks);
        do {
            GetTime(start_ticks);
            decomplen = lzbench_decompress(params, chunk_sizes,
                desc, compr_sizes, compbuf, decomp, tmpbuf, param1,
                param2, workmem);
            GetTime(end_ticks);
            nanosec = GetDiffTime(rate, start_ticks, end_ticks);
            if (nanosec >= 10000) dtime.push_back(nanosec);
            i++;
        }
        while (GetDiffTime(rate, loop_ticks, end_ticks) < params->dloop_time);

        // LZBENCH_PRINT(2, "=====A had decomp error? %d\n", (int)decomp_error);

        nanosec = GetDiffTime(rate, loop_ticks, end_ticks);
        dtime.push_back(nanosec/i);
        LZBENCH_PRINT(9, "%s dnanosec=%d\n", desc->name, (int)nanosec);

        if (insize != decomplen && !params->unverified) {
            decomp_error = true;
            LZBENCH_PRINT(1, "ERROR: input length (%d) != decompressed length (%d)\n",
                (int32_t)insize, (int32_t)decomplen);
        }

        if (!params->unverified && memcmp(inbuf, decomp, insize) != 0) {
            decomp_error = true;

            // printf("comparing buffs up to index %d\n", (int)insize);
            // printf("input data: first few bytes =\t\t");
            // for (int i = 0; i < 10; i++) {
            //     printf("%d ", (int)inbuf[i]);
            // }
            // printf("\ndecomp data: first few bytes =\t\t");
            // for (int i = 0; i < 10; i++) {
            //     printf("%d ", (int)decomp[i]);
            // }
            // printf("\n");
            // printf("input data: last few bytes =\t\t");
            // for (int i = 0; i < 10; i++) {
            //     printf("%d ", (int)inbuf[insize - 10 + i]);
            // }
            // printf("\ndecomp data: last few bytes =\t\t");
            // for (int i = 0; i < 10; i++) {
            //     printf("%d ", (int)decomp[insize - 10 + i]);
            // }
            // printf("\n");

            size_t cmn = common(inbuf, decomp, insize);
            LZBENCH_PRINT(1, "ERROR in %s: only first %d / %d decompressed bytes were correct\n",
                desc->name, (int32_t)cmn, (int32_t)insize);

            if (params->verbose >= 10) {
                char text[256];
                snprintf(text, sizeof(text), "%s_failed", desc->name);
                cmn /= chunk_size;
                size_t err_size = MIN(insize, (cmn+1)*chunk_size);
                err_size -= cmn*chunk_size;
                printf("ERROR: fwrite %d-%d to %s\n", (int32_t)(cmn*chunk_size),
                    (int32_t)(cmn*chunk_size+err_size), text);
                FILE *f = fopen(text, "wb");
                if (f) {
                    fwrite(inbuf + (cmn * chunk_size), 1, err_size, f);
                    fclose(f);
                }
                exit(1);
            }
        }

        memset(decomp, 0, insize); // clear output buffer

        // LZBENCH_PRINT(2, "===== had decomp error? %d\n", (int)decomp_error);
        if (decomp_error) { break; }
        // LZBENCH_PRINT(2, "===== did we get here? %d\n", 1);

        total_nanosec = GetDiffTime(rate, timer_ticks, end_ticks);
        total_d_iters += i;

        double time_secs = total_nanosec/1e9;
        double thruput = nanosec ? (float)insize * i * 1000 / nanosec : -1;
        // LZBENCH_PRINT(5, "%s decompr iter=%d time=%.2fs speed=%.2f MB/s     \r",
        LZBENCH_PRINT(5, "%s decompr rawsize=%lu iter=%d time=%.5fs speed=%.2f MB/s     \n",
            desc->name, insize, total_d_iters, time_secs, thruput);

        bool done = total_d_iters >= params->d_iters;
        done = done && (total_nanosec > ((uint64_t)params->dmintime*1000*1000));
        if (done) { break; }

    } while (true);

    print_stats(params, desc, level, ctime, dtime, insize,
        complen, decomp_error);

done:
    if (desc->deinit) {
        for (int i = 0; i < nthreads; i++) {
            if (workmems[i]) { desc->deinit(workmems[i]); }
        }
    }
}


void lzbench_test_with_params(lzbench_params_t *params,
    std::vector<size_t> &file_sizes, const char *namesWithParams,
    uint8_t *inbuf, size_t insize, uint8_t *compbuf, size_t comprsize,
    uint8_t *decomp, bench_rate_t rate)
{
    std::vector<std::string> cnames, cparams;

	if (!namesWithParams) { return; }

    cnames = split(namesWithParams, '/');

    for (int k=0; k<cnames.size(); k++) {
        LZBENCH_PRINT(5, "cnames[%d] = %s\n", k, cnames[k].c_str());
    }

    for (int k=0; k<cnames.size(); k++) {
        for (int i=0; i<LZBENCH_ALIASES_COUNT; i++) {
            if (istrcmp(cnames[k].c_str(), alias_desc[i].name)==0) {
                lzbench_test_with_params(params, file_sizes,
                    alias_desc[i].params, inbuf, insize, compbuf, comprsize,
                    decomp, rate);
                goto next_k;
            }
        }

        LZBENCH_PRINT(5, "params = %s\n", cnames[k].c_str());
        cparams = split(cnames[k].c_str(), ',');
        if (cparams.size() >= 1) {
            int j = 1;
            do {
                bool found = false;
                for (int i=1; i<LZBENCH_COMPRESSOR_COUNT; i++) {
                    if (istrcmp(comp_desc[i].name, cparams[0].c_str()) == 0) {
                        found = true;
                        if (j >= cparams.size()) {
                            for (int level=comp_desc[i].first_level;
                                    level<=comp_desc[i].last_level; level++)
                            {
                                lzbench_test(params, file_sizes, &comp_desc[i],
                                    level, inbuf, insize, compbuf, comprsize,
                                    decomp, rate, level);
                            }
                        } else {
                            lzbench_test(params, file_sizes, &comp_desc[i],
                                atoi(cparams[j].c_str()), inbuf, insize,
                                compbuf, comprsize, decomp, rate,
                                atoi(cparams[j].c_str()));
                        }
                        break;
                    }
                }
                if (!found) {
                    printf("NOT FOUND: %s %s\n", cparams[0].c_str(),
                        (j<cparams.size()) ? cparams[j].c_str() : NULL);
                }
                j++;
            } while (j < cparams.size());
        }
next_k:
        continue;
    }
}


int lzbench_join(lzbench_params_t* params, const char** inFileNames,
    unsigned ifnIdx, char* encoder_list)
{
    bench_rate_t rate;
    size_t comprsize, insize, inpos, totalsize;//, aligned_totalsize;
    uint8_t *inbuf, *compbuf, *decomp;
    std::vector<size_t> file_sizes;
    std::string text;
    FILE* in;
    const char* pch;

    totalsize = UTIL_getTotalFileSize(inFileNames, ifnIdx);
    if (totalsize == 0) {
        printf("Could not find input files\n");
        return 1;
    }

    size_t data_buf_size = totalsize + PAD_SIZE + (ALIGN_BYTES * ifnIdx);
    comprsize = GET_COMPRESS_BOUND(totalsize) + (ALIGN_BYTES * ifnIdx);
    inbuf = alloc_data_buffer(data_buf_size);
    compbuf = alloc_data_buffer(comprsize);
    // tmpbuf = alloc_data_buffer(data_buf_size);  // for preprocessing
    decomp = alloc_data_buffer(data_buf_size);

    if (!inbuf || !compbuf || !decomp) {
        printf("Not enough memory, please use -m option!\n");
        return 1;
    }

    InitTimer(rate);
    inpos = 0;

    for (int i=0; i<ifnIdx; i++) {
        if (UTIL_isDirectory(inFileNames[i])) {
            fprintf(stderr, "warning: use -r to process directories (%s)\n",
                inFileNames[i]);
            continue;
        }

        if (!(in=fopen(inFileNames[i], "rb"))) {
            perror(inFileNames[i]);
            continue;
        }

        fseeko(in, 0L, SEEK_END);
        insize = ftello(in);
        rewind(in);
        insize = fread(inbuf+inpos, 1, insize, in);

        // force even multiple of ALIGN_BYTES so start of next file
        // will be aligned properly
        size_t remainder = insize % ALIGN_BYTES;
        insize += remainder ? ALIGN_BYTES - remainder : 0;

        file_sizes.push_back(insize);
        inpos += insize;
        fclose(in);
    }

    if (file_sizes.size() == 0) {
        goto _clean;
    }

    format(text, "%d files", file_sizes.size());
    params->in_filename = text.c_str();

    LZBENCH_PRINT(5, "totalsize=%d inpos=%d\n", (int)totalsize, (int)inpos);
    totalsize = inpos;

    {
        std::vector<size_t> single_file;
        lzbench_params_t params_memcpy(*params);

        print_header(params);
        // params_memcpy.cmintime = params_memcpy.dmintime = 0;
        // params_memcpy.c_iters = params_memcpy.d_iters = 0;
        // params_memcpy.cmintime = params.cmintime;
        // params_memcpy.dmintime = params.dmintime;
        params_memcpy.cloop_time = params_memcpy.dloop_time = DEFAULT_LOOP_TIME;
        single_file.push_back(totalsize);
        lzbench_test(&params_memcpy, file_sizes, &comp_desc[0], 0, inbuf, totalsize, compbuf, totalsize, decomp, rate, 0);
    }

    lzbench_test_with_params(params, file_sizes, encoder_list?encoder_list:alias_desc[0].params, inbuf, totalsize, compbuf, comprsize, decomp, rate);

_clean:
    free_data_buffer(inbuf);
    free_data_buffer(compbuf);
    free_data_buffer(decomp);

    return 0;
}


int lzbench_main(lzbench_params_t* params, const char** inFileNames,
    unsigned ifnIdx, char* encoder_list)
{
    bench_rate_t rate;
    size_t comprsize, insize, real_insize;
    uint8_t *inbuf, *compbuf, *decomp;
    std::vector<size_t> file_sizes;
    FILE* in;
    const char* pch;

    for (int i=0; i<ifnIdx; i++) {
        if (UTIL_isDirectory(inFileNames[i])) {
            fprintf(stderr, "warning: use -r to process directories (%s)\n",
                inFileNames[i]);
            continue;
        }
        if (!(in=fopen(inFileNames[i], "rb"))) {
            perror(inFileNames[i]);
            continue;
        }

        pch = strrchr(inFileNames[i], '\\');
        params->in_filename = pch ? pch+1 : inFileNames[i];

        InitTimer(rate);

        fseeko(in, 0L, SEEK_END);
        real_insize = ftello(in);
        rewind(in);

        bool limit_mem = params->mem_limit > 0 && \
            real_insize > params->mem_limit;
        insize = limit_mem ? params->mem_limit : real_insize;

        comprsize = GET_COMPRESS_BOUND(insize) + ALIGN_BYTES;
        size_t data_buf_size = insize + PAD_SIZE + ALIGN_BYTES;
        inbuf = alloc_data_buffer(data_buf_size);
        compbuf = alloc_data_buffer(comprsize);
        decomp = alloc_data_buffer(data_buf_size);

        if (!inbuf || !compbuf || !decomp) {
            printf("Not enough memory; please use -m option!");
            return 1;
        }

        if(params->random_read) {
          long long unsigned pos = 0;
          if (params->chunk_size < real_insize){
            pos = (rand() % (real_insize / params->chunk_size)) * params->chunk_size;
            insize = params->chunk_size;
            fseeko(in, pos, SEEK_SET);
          } else {
            insize = real_insize;
          }
          printf("Seeking to: %llu %ld %ld\n", pos, (long)params->chunk_size, (long)insize);
        }

        insize = fread(inbuf, 1, insize, in);

        // always run a memcpy first as a baseline
        if (i == 0) {
            print_header(params);
            lzbench_params_t params_memcpy(*params);
            params_memcpy.cmintime = params_memcpy.dmintime = 0;
            params_memcpy.c_iters = params_memcpy.d_iters = 0;
            params_memcpy.cloop_time = params_memcpy.dloop_time = DEFAULT_LOOP_TIME;
            file_sizes.push_back(insize);
            lzbench_test(&params_memcpy, file_sizes, &comp_desc[0], 0,
                inbuf, insize, compbuf, insize, decomp, rate, 0);
            file_sizes.clear();
        }

        // if memory limit is set, split input into chunks
        if (params->mem_limit && real_insize > params->mem_limit) {
            int i;
            std::string partname;
            const char* filename = params->in_filename;
            for (i=1; insize > 0; i++) {
                format(partname, "%s part %d", filename, i);
                params->in_filename = partname.c_str();
                file_sizes.push_back(insize);
                lzbench_test_with_params(params, file_sizes,
                    encoder_list ? encoder_list : alias_desc[0].params,
                    inbuf, insize, compbuf, comprsize, decomp, rate);
                file_sizes.clear();
                insize = fread(inbuf, 1, insize, in);
            }
        } else {
            file_sizes.push_back(insize);
            lzbench_test_with_params(params, file_sizes,
                encoder_list ? encoder_list : alias_desc[0].params,
                inbuf, insize, compbuf, comprsize, decomp, rate);
            file_sizes.clear();
        }

        fclose(in);
        free_data_buffer(inbuf);
        free_data_buffer(compbuf);
        free_data_buffer(decomp);
    }

    return 0;
}

} // namespace lzbench
