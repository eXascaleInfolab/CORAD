//
// parallel.cpp
// Created by D Blalock 2018-2-28
//

#include "parallel.h"

#include <chrono>  // TODO rm
#include <iostream>  // TODO rm
#include <future>
#include <thread>

#include "output.h"
#include "preprocessing.h"
#include "query.hpp"
#include "util.h"

namespace lzbench {

size_t _decomp_and_query(lzbench_params_t *params, const compressor_desc_t* desc,
    const uint8_t* comprbuff, size_t comprsize, uint8_t* outbuf, size_t outsize,
    bool already_materialized, bool push_down_query,
    size_t param1, size_t param2, void* workmem)
{
    // printf("decomp_and_query: running '%s' with insize %lu, outsize %u!\n", desc->name, comprsize, outsize);

    compress_func decompress = desc->decompress;

    size_t dlen = -1;
    if (!already_materialized || push_down_query) {
        // if (comprsize == outsize || true) { // TODO rm
        if (comprsize == outsize) { // uncompressed
            memcpy(outbuf, comprbuff, comprsize);
            dlen = comprsize;
        } else {
            // printf("about to decomp using compressor: %s\n", desc->name);
            // printf("can push down query: %d; workmem = %p\n", (int)push_down_query, workmem);
            dlen = decompress((char*)comprbuff, comprsize, (char*)outbuf,
                              outsize, param1, param2, workmem);
            // printf("finished decomp; dlen = %d\n", (int)dlen);
        }
        undo_preprocessors(params->preprocessors, outbuf, dlen,
            params->data_info.element_sz);

        // prevent compiler from not running above command (hopefully...)
        if (params->verbose >= 999 || dlen >= ((int64_t)1) << 31) {
            size_t cmn = common(comprbuff, outbuf, outsize);
            LZBENCH_PRINT(999, "ERROR in %s: only first %d / %d decompressed bytes were correct\n",
                desc->name, (int32_t)cmn, (int32_t)outsize);
        }
    } else {
        dlen = outsize;
    }

    // run query if one is specified
    auto qparams = params->query_params;
    if (qparams.type != QUERY_NONE && !push_down_query) {
        // printf("got query type: %d; about to run a query...\n", qparams.type);
        // auto& dinfo = params->data_info;
        DataInfo dinfo = params->data_info;
        if (dinfo.ncols < 1) {
            printf("ERROR: Must specify number of columns in data to run query!\n");
            exit(1);
        }
        dinfo.nrows = dlen / (dinfo.ncols * dinfo.element_sz);
        // printf("dlen: %lld\n", (int64_t)dlen);
        // printf("dinfo elem_sz, nrows, ncols, size: %lu, %lu, %lu, %lu\n",
        //     dinfo.element_sz, dinfo.nrows, dinfo.ncols, dinfo.nrows * dinfo.ncols);
        QueryResult result;
        if (push_down_query) {
            // result = ((QueryRefs*)workmem)->qres;
            result = *((QueryRefs*)workmem)->qres;
        } else {
            // printf("------------------------\nrunning query since can't push it down \n");
            // result = run_query(params->query_params, dinfo, outbuf);
            result = *run_query(params->query_params, dinfo, outbuf);
            // result = *poopinize(params->query_params, dinfo, outbuf);
            // auto resPtr = run_query(params->query_params, dinfo, outbuf);
            // printf("size of ptr result_vals: %lu\n", resPtr->vals.size());
            // result = *resPtr;
        }
        // QueryResult result = frobnicate(                         // TODO rm
        //     params->query_params, dinfo, outbuf);
        // printf("ran query type: %d\n", qparams.type);
        // // printf("number of idxs in result: %lu\n", result.idxs.size());
        // printf("size of result_vals: %lu\n", result.vals.size());

        // hack so it can't pull the below check out of the loop; dummy
        // can be any u8 but next line will always add 0, although compiler
        // doesn't know this (it's 0 because element_sz is in {1,2})
        // auto dummy = result.vals_u8.size() > 0 ? result.vals_u8[0] : 0;
        auto dummy = result.vals.size() > 0 ? result.vals[0] : 0;
        params->verbose += result.idxs.size() > ((int64_t)1e9) ? dummy : 0;

        // printf("query result: ");
        // for (auto val : result.vals) { printf("%d ", (int)val); }
        // printf("\n");

        // prevent compiler from optimizing away query
        // XXX does it actually have this effect? could pull this check
        // out of the loop and do nothing if condition is false
        if (params->verbose > 999) {
            printf("query result bytes: ");
            for (auto val : result.vals) { printf("%u ", (uint32_t)val); }
            printf("\n");
        }
    }
    return dlen;
}



void parallel_decomp(lzbench_params_t *params,
    std::vector<size_t>& chunk_sizes, const compressor_desc_t* desc,
    std::vector<size_t> &compr_sizes, const uint8_t *inbuf, uint8_t *outbuf,
    uint8_t* tmpbuf, bench_rate_t rate, std::vector<uint64_t> comp_times,
    size_t param1, size_t param2, char** workmems)
{
    // printf("calling parallel decomp for algorithm (T=%d): %s!\n", params->nthreads, desc->name);
    // printf("calling parallel decomp for algorithm %s!\n", desc->name);
    // if (params) {
    //     printf("using nthreads: %d\n", params->nthreads);
    // }

    std::vector<uint64_t> compressed_chunk_starts;
    compressed_chunk_starts.push_back(0);
    for (auto sz : compr_sizes) {
        compressed_chunk_starts.push_back(compressed_chunk_starts.back() + sz);
    }
    compressed_chunk_starts.pop_back(); // last one is just an end idx

    // printf("compr start idxs: ");
    // for (auto start_idx : compressed_chunk_starts) {
    //     printf("%lld, ", start_idx);
    // }
    // printf("\n");

    // printf("param1, param2 = %lu, %lu\n", param1, param2);
    // if (param1 != 80) {
    //     printf("param1 is %lu, not 80!\n", param1);
    // }

    uint64_t run_for_nanosecs = (uint64_t)params->dmintime*1000*1000;
    // printf("running for min nanosecs: %llu\n", run_for_nanosecs);

    // using result_t = std::tuple<int64_t, int64_t>;
    using result_t = std::tuple<int64_t, int64_t, int64_t>;

    int nthreads = params->nthreads;
    // std::vector<int64_t> total_scanned_sizes(nthreads);
    // std::vector<std::future<int64_t>> total_scanned_sizes(nthreads);
    std::vector<std::future<result_t>> thread_results_futures;
    std::vector<result_t> thread_results(nthreads);
    // std::vector<result_t> total_scanned_sizes(nthreads);
    // std::vector<std::thread> threads(nthreads);

    auto max_chunk_sz = chunk_sizes[0];
    int64_t total_raw_sz = 0;
    for (auto sz : chunk_sizes) {
        if (sz > max_chunk_sz) { max_chunk_sz = sz; }
        total_raw_sz += sz;
    }

    bool already_materialized = strings_equal(desc->name, "materialized");
    bool push_down_query = can_push_down_query(desc->name);

    // printf("number of chunks: %lu; raw size: %lld\n", compressed_chunk_starts.size(), total_raw_sz);

    // // hack to pass query info to algorithms that can push down queries
    // QueryResult res;
    // QueryRefs qrefs { .qparams = params->query_params,
    //     .dinfo = params->data_info, .qres = res};
    // if (!workmem) { workmem = (char*)&qrefs; }

    // nthreads = 1; // TODO uncomment

    uint8_t* buffs[nthreads];
    for (int i = 0; i < nthreads; i++) {
        buffs[i] = alloc_data_buffer(max_chunk_sz + 4096);
    }

    // for (int i = 0; i < nthreads; i++) {
        // auto& this_total = total_scanned_sizes[i];
        // size_t* this_total = total_scanned_sizes[i];
        // threads[i] = std::thread([&total_scanned_sizes[i]] {
        auto run_in_thread =
            [run_for_nanosecs, &buffs, total_raw_sz, inbuf, nthreads,
                params, desc, compr_sizes, chunk_sizes, rate,
                compressed_chunk_starts,
                already_materialized, push_down_query,
                // &total_scanned_sizes,
                param1, param2, workmems](int i) {

            // std::this_thread::sleep_for(std::chrono::duration<double, std::milli>(100));
            // // std::this_thread::sleep_for(std::chrono::duration<double>(1));
            // // std::this_thread::sleep_for(std::chrono::duration<double>(2));
            // // return (int64_t)total_raw_sz;
            // printf("Thread %d, done sleeping!\n", i);
            // return std::make_tuple(total_raw_sz, (int64_t)(100 * 1000 * 1000));

            //
            // TODO uncomment below here
            // EDIT: this scales linearly, so issue is something below here...
            //

            void* workmem_ptr = workmems[i];
            // printf("workmem_ptr: %p\n", workmem_ptr);

            //
            // TODO uncomment all this
            //
            // hack to pass query info to algorithms that can push down queries
            QueryResult res;
            // void* qrefsPtr = (void*)new QueryRefs{
            //     .qparams = &params->query_params,
            //     .dinfo = &params->data_info, .qres = &res};
            QueryRefs* qrefs = new QueryRefs();
            qrefs->qparams = &params->query_params;
            qrefs->dinfo = &params->data_info;
            qrefs->qres = &res;

            void* qrefsPtr = (void*)qrefs;

            // void* qrefsPtr = malloc(sizeof(QueryRefs));
            // memcpy(qrefsPtr, &qrefs, sizeof(qrefs));

            QueryRefs qrefs2 = *(lzbench::QueryRefs*)qrefsPtr;
            // printf("orig qrefs op: %d\n", (int)qrefs.qparams->type);
            // printf("copied qrefs op: %d\n", (int)((lzbench::QueryRefs*)qrefsPtr)->qparams->type);
            // *(QueryRefs*)qrefsPtr = qrefs;

            // printf("about to write workmem; pushdown query = %d, workmem = %p\n", (int)push_down_query, workmem_ptr);
            // printf("&qrefs = %p; workmem is null? %d\n", qrefsPtr, (int)(workmem_ptr == nullptr));
            if (push_down_query && workmem_ptr == nullptr) {
                workmem_ptr = qrefsPtr;
                // printf("assigning workmem_ptr to %p (%p as void*)\n", qrefsPtr, (void*)qrefsPtr);
                // printf("workmem_ptr")
            }

            // printf("about to run stuff; pushdown query = %d, workmem = %p\n", (int)push_down_query, workmem_ptr);

            int64_t comp_sz = 0;
            int64_t decomp_sz = 0;

            bench_timer_t t_end;
            int64_t max_iters = run_for_nanosecs > 0 ? 1000*1000*1000 : -1;
            int64_t niters = 0;
            auto num_chunks = compressed_chunk_starts.size();
            // XXX this is an ugly way to check this

            // printf("using num_chunks: %lld\n", (int64_t)num_chunks);
            // printf("using chunk sizes:"); for (auto sz : chunk_sizes) { printf("%lld, ", (int64_t)sz); } printf("\n");

            // printf("max chunk sz: %lu\n", max_chunk_sz);
            // uint8_t* decomp_buff = alloc_data_buffer(max_chunk_sz + 4096);
            uint8_t* decomp_buff = buffs[i];

            int64_t elapsed_nanos = 0;

            bench_timer_t t_start;
            GetTime(t_start);

            // printf("workmem_ptr now: %p\n", workmem_ptr);

            do {
                // run multiple iters betwen rtsc calls to avoid sync overhead
                // use nthreads iters as a heuristic so syncs/sec is constant
                for (int it = 0; it < num_chunks*nthreads; it++) {
                // for (int it = 0; it < nthreads; it++) {
                // for (int it = 0; it < 1; it++) { // TODO uncomment above
                    auto chunk_idx = rand() % num_chunks;
                    // auto chunk_idx = it % num_chunks;
                    auto inptr = inbuf + compressed_chunk_starts[chunk_idx];
                    // auto inptr = inbuf; // TODO uncomment above after debug
                    auto insize = compr_sizes[chunk_idx];
                    auto rawsize = chunk_sizes[chunk_idx];

                    _decomp_and_query(params, desc, inptr, insize,
                        decomp_buff, rawsize,
                        already_materialized, push_down_query,
                        param1, param2, workmem_ptr);

                    // std::this_thread::sleep_for(std::chrono::duration<double, std::milli>(100));
                    // std::this_thread::sleep_for(std::chrono::duration<double>(1));

                    // this_total += rawsize;
                    comp_sz += insize;
                    decomp_sz += rawsize;
                    // total_scanned_sizes[i] += rawsize;
                    // *(this_total) = *(this_total) + rawsize;
                    niters++;
                }

                // check whether we're done
                GetTime(t_end);
                elapsed_nanos = GetDiffTime(rate, t_start, t_end);

                bool done = elapsed_nanos >= run_for_nanosecs;
                done = done || ((max_iters >= 0) && (niters >= max_iters));
                if (done) {
                // if (true) {
                    LZBENCH_PRINT(8, "%d) elapsed iters, time: %lld, %lld/%lldns\n",
                        i, niters, elapsed_nanos, run_for_nanosecs);
                }
                if (done) { break; }
            } while (true);

            // auto total_comp_size = 0;
            // for (auto sz: compr_sizes) {
            //     total_comp_size += sz;
            // }
            // size_t cmn = common(inbuf, decomp_buff, total_raw_sz);
            // if (cmn < insize) {
            // printf("about to check whether decomp is correct...\n");
            // size_t cmn = common(inbuf, decomp_buff, max_chunk_sz);
            // if (cmn < max_chunk_sz) {
            //     LZBENCH_PRINT(999, "ERROR in %s: only first %d / %d decompressed bytes were correct\n",
            //     desc->name, (int32_t)cmn, (int32_t)max_chunk_sz);
            // }

            // free_data_buffer(decomp_buff);

            delete (QueryRefs*)qrefsPtr; // TODO uncomment
            // free(qrefsPtr);

            // return decomp_sz;
            return std::make_tuple(comp_sz, decomp_sz, elapsed_nanos);
        // });
        };
    // }

    // TODO uncomment below
    //
    // auto debug_lambda = [](int64_t i) { std::cout << i << "\n"; return i; };
    for (int i = 0; i < nthreads; i++) {
        thread_results_futures.push_back(std::async(run_in_thread, i));
        // thread_results_futures.push_back(std::async(debug_lambda, i));
    }
    // printf("about to try get()ing all the futures...\n");
    bench_timer_t t_start_main;
    GetTime(t_start_main);
    for (int i = 0; i < nthreads; i++) {
        thread_results[i] = thread_results_futures[i].get();
        // thread_results_futures[i].get();
    }
    bench_timer_t t_end_main;
    GetTime(t_end_main);
    auto elapsed_nanos_main = GetDiffTime(rate, t_start_main, t_end_main);
    // printf("Joined all the threads in %lld ns!\n", elapsed_nanos_main);

    for (int i = 0; i < nthreads; i++) {
        free_data_buffer(buffs[i]);
    }

    // // Single threaded version (for debugging)
    // for (int i = 0; i < nthreads; i++) {
    //     thread_results[i] = run_in_thread(i);
    // }

    // for (auto& t : threads) {
    //     t.join();
    // }

    // printf("total sizes: ");
    // for (auto res : thread_results) {
    //     printf("(%lldB, %lldns), ", std::get<0>(res), std::get<1>(res));
    // }
    // printf("\n");

    // compute total amount of data all the threads got through
    int64_t total_decomp_bytes = 0;
    int64_t total_comp_bytes = 0;
    // int64_t total_cpu_time = 0;
    for (auto res : thread_results) {
        total_comp_bytes += std::get<0>(res);
        total_decomp_bytes += std::get<1>(res);
        // total_cpu_time += std::get<2>(res);
    }
    double thruput_bytes_per_ns = total_decomp_bytes / elapsed_nanos_main;
    int64_t thruput_MB_per_sec = (int64_t)(thruput_bytes_per_ns * 1000);
    // printf("scanned %lld total bytes in %lld ns\n", total_decomp_bytes, elapsed_nanos_main);

    // if (!run_for_nanosecs) { // this case shouldn't be used for real results
    //     bench_timer_t t_end;
    //     GetTime(t_end);
    //     // printf("WARNING: minimum run time not specified\n");
    //     run_for_nanosecs = GetDiffTime(rate, t_start, t_end);
    // }
    // auto run_for_usecs = run_for_nanosecs / 1000;
    // auto thruput_MB_per_sec = total_decomp_bytes / run_for_usecs;
    // printf(">> \1%s avg thruput: %lld(MB/s)\n", desc->name, thruput_MB_per_sec);
    // printf(">> \1%s avg thruput: %lld(MB/s)\n", desc->name, thruput_MB_per_sec);

    size_t complen = 0;
    for (auto sz : compr_sizes) { complen += sz; }

    bool decomp_error = false;
    // std::vector<uint64_t> decomp_times {total_cpu_time};
    std::vector<uint64_t> decomp_times {elapsed_nanos_main};
    // size_t insize = total_decomp_bytes;

    // correct compressed size so compression thruputs are about right; note
    // that these are single-threaded thruputs, since we aren't actually
    // running compression in parallel
    size_t dset_comp_bytes = 0;
    for (int i = 0; i < compr_sizes.size(); i++) {
        dset_comp_bytes += compr_sizes[i];
    }
    for (int i = 0; i < comp_times.size(); i++) {
        comp_times[i] *= total_comp_bytes / (double)dset_comp_bytes;
    }
    print_stats(params, desc, param1, comp_times, decomp_times, total_decomp_bytes,
        total_comp_bytes, decomp_error);

    // printf("------------------------\n");
}


} // namespace lzbench
