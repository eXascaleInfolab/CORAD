
#include <algorithm> // std::sort

#include "lzbench.h"
#include "output.h"
#include "util.h"

using namespace lzbench; // TODO separate out individual types/funcs we need

void usage(lzbench_params_t* params) {
    // fprintf(stderr, "usage: " PROGNAME " [options] input [input2] [input3]\n\nwhere [input] is a file or a directory and [options] are:\n");
    fprintf(stderr, "usage: " PROGNAME " [options] input [input2] [input3]\n\nwhere [input] is a file or a directory.\n");
    fprintf(stderr, "See README for more information.\n");
//     fprintf(stderr, " -b#   set block/chunk size to # KB (default = MIN(filesize,%d KB))\n", (int)(params->chunk_size>>10));
//     fprintf(stderr, " -c#   sort results by column # (1=algname, 2=ctime, 3=dtime, 4=comprsize)\n");
//     fprintf(stderr, " -e#   #=compressors separated by '/' with parameters specified after ',' (deflt=fast)\n");
//     fprintf(stderr, " -iX,Y set min. number of compression and decompression iterations (default = %d, %d)\n", params->c_iters, params->d_iters);
//     fprintf(stderr, " -j    join files in memory but compress them independently (for many small files)\n");
//     fprintf(stderr, " -l    list of available compressors and aliases\n");
//     fprintf(stderr, " -R    read block/chunk size from random blocks (to estimate for large files)\n");
//     fprintf(stderr, " -m#   set memory limit to # MB (default = no limit)\n");
//     fprintf(stderr, " -o#   output text format 1=Markdown, 2=text, 3=text+origSize, 4=CSV (default = %d)\n", params->textformat);
//     fprintf(stderr, " -p#   print time for all iterations: 1=fastest 2=average 3=median (default = %d)\n", params->timetype);
// #ifdef UTIL_HAS_CREATEFILELIST
//     fprintf(stderr, " -r    operate recursively on directories\n");
// #endif
//     fprintf(stderr, " -s#   use only compressors with compression speed over # MB (default = %d MB)\n", params->cspeed);
//     fprintf(stderr, " -tX,Y set min. time in seconds for compression and decompression (default = %.0f, %.0f)\n", params->cmintime/1000.0, params->dmintime/1000.0);
//     fprintf(stderr, " -v    disable progress information\n");
//     fprintf(stderr, " -x    disable real-time process priority\n");
//     fprintf(stderr, " -z    show (de)compression times instead of speed\n");
//     fprintf(stderr,"\nExample usage:\n");
//     fprintf(stderr,"  " PROGNAME " -ezstd filename = selects all levels of zstd\n");
//     fprintf(stderr,"  " PROGNAME " -ebrotli,2,5/zstd filename = selects levels 2 & 5 of brotli and zstd\n");
//     fprintf(stderr,"  " PROGNAME " -t3 -u5 fname = 3 sec compression and 5 sec decompression loops\n");
//     fprintf(stderr,"  " PROGNAME " -t0 -u0 -i3 -j5 -ezstd fname = 3 compression and 5 decompression iter.\n");
//     fprintf(stderr,"  " PROGNAME " -t0u0i3j5 -ezstd fname = the same as above with aggregated parameters\n");
}

bool query_needs_data_window(QueryParams q) {
    switch (q.type) {
        case QUERY_L2: return true;
        case QUERY_DOT: return true;
        default: return false;
    }
}

int main(int argc, char** argv) {
    FILE *in;
    char* encoder_list = NULL;
    int result = 0, sort_col = 0, real_time = 1;
    lzbench_params_t lzparams;
    lzbench_params_t* params = &lzparams;
    const char** inFileNames = (const char**) calloc(argc, sizeof(char*));
    unsigned ifnIdx=0;
    bool join = false;
#ifdef UTIL_HAS_CREATEFILELIST
    const char** extendedFileList = NULL;
    char* fileNamesBuf = NULL;
    unsigned fileNamesNb, recursive=0;
#endif

    if (inFileNames==NULL) {
        LZBENCH_PRINT(2, "Allocation error : not enough memory%c\n", ' ');
        return 1;
    }

    memset(params, 0, sizeof(lzbench_params_t));
    params->timetype = FASTEST;
    params->textformat = TEXT;
    params->show_speed = 1;
    params->verbose = 2;
    params->chunk_size = (1ULL << 31) - (1ULL << 31)/6;
    params->cspeed = 0;
    params->c_iters = params->d_iters = 1;
    // params->cmintime = 10*DEFAULT_LOOP_TIME/1000000; // 1 sec
    // params->dmintime = 20*DEFAULT_LOOP_TIME/1000000; // 2 sec
    params->cmintime = 0;
    params->dmintime = 0;
    params->cloop_time = params->dloop_time = DEFAULT_LOOP_TIME;

    // convenient abbreviations
    auto& qparams = params->query_params;
    auto& dinfo = params->data_info;

    while ((argc>1) && (argv[1][0]=='-')) {
    char* argument = argv[1]+1;
    if (!strcmp(argument, "-compress-only")) params->compress_only = 1;
    else while (argument[0] != 0) {
        char* numPtr = argument + 1;
        int64_t number = 0;
        while ((*numPtr >='0') && (*numPtr <='9')) { number *= 10;  number += *numPtr - '0'; numPtr++; }

        // // parse number passed
        // int decimal_pos = -1;
        // int length = 0;
        // while (((*numPtr >='0') && (*numPtr <='9')) || *numPtr == '.') {
        //     if (*numPtr == '.') {
        //         decimal = true;
        //         decimal_pos = length;
        //         continue;
        //     }
        //     number *= 10;
        //     number += *numPtr - '0';
        //     numPtr++;
        //     length++;
        // }
        // if (length < 1) {
        //     LZBENCH_PRINT(1, 'Received malformed numeric argument: %s\n', argument);
        //     return 1;
        // }
        // bool decimal = decimal_pos >= 0;
        // bool ignored_decimal = decimal;
        // int64_t divide_decimal_by = std::pow(10, length - decimal_pos);

        switch (argument[0])
        {
        case 'a':
            encoder_list = strdup(argument + 1);
            numPtr += strlen(numPtr);
            break;
        case 'b':
            params->chunk_size = number << 10;
            break;
        case 'c':
            dinfo.ncols = number;
            break;
        case 'C':
            qparams.which_cols.push_back(number);
            while (*numPtr == ',') { // parse whole list of numbers
                numPtr++;
                number = 0;
                while ((*numPtr >='0') && (*numPtr <='9')) { number *= 10;  number += *numPtr - '0'; numPtr++; }
                qparams.which_cols.push_back(number);
            }
            break;
        case 'd':
            params->preprocessors.push_back(number);
            // printf("params preprocessors current size: %lu\n", params->preprocessors.size());
            // params->preprocessors.push_back(1);
            // printf("params preprocessors new size: %lu\n", params->preprocessors.size());
            // params->preprocessors.clear();
            // printf("params preprocessors cleared size: %lu\n", params->preprocessors.size());
            break;
        case 'D':
            params->preprocessors.push_back(number + (1 << 16)); // XXX total hack
            break;
        case 'e':
            dinfo.element_sz = number;
            break;
        // case 'g':
        //     params->time_preproc = true;
        //     break;
        // case 'e':
        //     encoder_list = strdup(argument + 1);
        //     numPtr += strlen(numPtr);
        //     break;
        case 'f':
            // XXX: for sprintz forecasting, pass in negative of the
            // dimensionality; this is a total hack
            params->preprocessors.push_back(-number);
            break;
        case 'i':
            params->c_iters = number;
            if (*numPtr == ',')
            {
                numPtr++;
                number = 0;
                while ((*numPtr >='0') && (*numPtr <='9')) { number *= 10;  number += *numPtr - '0'; numPtr++; }
                params->d_iters = number;
            }
            break;
        case 'j':
            join = true;
            break;
        case 'm':
            params->mem_limit = number << 18; /*  total memory usage = mem_limit * 4  */
            if (params->textformat == TEXT) params->textformat = TEXT_FULL;
            break;
        case 'o':
            params->textformat = (textformat_e)number;
            if (params->textformat == CSV) params->verbose = 0;
            break;
        case 'p':
            params->timetype = (timetype_e)number;
            break;
        case 'q':
            qparams.type = (query_type_e)number;
            // printf("set query type to %d\n", (int)qparams.type);
            break;
        case 'Q':
            qparams.window_data_dbl.push_back(number);
            while (*numPtr == ',') { // parse whole list of numbers
                numPtr++;
                number = 0;
                while ((*numPtr >='0') && (*numPtr <='9')) { number *= 10;  number += *numPtr - '0'; numPtr++; }
                qparams.window_data_dbl.push_back(number);
            }
            break;
        case 'r':
            recursive = 1;
            break;
        case 'R':
            params->random_read = 1;
            srand(time(NULL));
            break;
        case 's':
            params->cspeed = number;
            break;
        case 'S':
            dinfo.storage_order = (storage_order_e)number;
        case 't':
            params->cmintime = 1000*number;
            params->cloop_time = (params->cmintime)?DEFAULT_LOOP_TIME:0;
            if (*numPtr == ',')
            {
                numPtr++;
                number = 0;
                while ((*numPtr >='0') && (*numPtr <='9')) { number *= 10;  number += *numPtr - '0'; numPtr++; }
                params->dmintime = 1000*number;
                params->dloop_time = (params->dmintime)?DEFAULT_LOOP_TIME:0;
            }
            break;
        case 'T':
            params->nthreads = number;
            break;
        case 'u':
            params->dmintime = 1000*number;
            params->dloop_time = (params->dmintime)?DEFAULT_LOOP_TIME:0;
            break;
        case 'U':
            params->unverified = true;
        case 'v':
            params->verbose = number;
            break;
        case 'w':
            // TODO: duplicate code to advance ptr and parse number is hideous
            qparams.window_nrows = number;
            // parse next number after the comma (ncols) or default it
            if (*numPtr != ',') {
                qparams.window_ncols = -1;
                break;
            }
            numPtr++;
            number = 0;
            while ((*numPtr >='0') && (*numPtr <='9')) { number *= 10;  number += *numPtr - '0'; numPtr++; }
            // parse next number after the comma (stride) or default it
            if (*numPtr != ',') {
                qparams.window_stride = -1;
                break;
            }
            numPtr++;
            number = 0;
            while ((*numPtr >='0') && (*numPtr <='9')) { number *= 10;  number += *numPtr - '0'; numPtr++; }
            break;
        case 'x':
            real_time = 0;
            break;
        case 'z':
            params->show_speed = 0;
            break;
        case '-': // --help
        case 'h':
            usage(params);
            goto _clean;
        case 'l':
            printf("\nAvailable compressors for -e option:\n");
            printf("all - alias for all available compressors\n");
            printf("fast - alias for compressors with compression speed over 100 MB/s (default)\n");
            printf("opt - compressors with optimal parsing (slow compression, fast decompression)\n");
            printf("lzo / ucl - aliases for all levels of given compressors\n");
            for (int i=1; i<LZBENCH_COMPRESSOR_COUNT; i++)
            {
                if (comp_desc[i].compress)
                {
                    if (comp_desc[i].first_level < comp_desc[i].last_level)
                        printf("%s %s [%d-%d]\n", comp_desc[i].name, comp_desc[i].version, comp_desc[i].first_level, comp_desc[i].last_level);
                    else
                        printf("%s %s\n", comp_desc[i].name, comp_desc[i].version);
                }
            }
            return 0;
        default:
            fprintf(stderr, "unknown option: %s\n", argv[1]);
            result = 1; goto _clean;
        }

        // if (decimal and ignored_decimal) {
        //     LZBENCH_PRINT(2, "Argument does not except decimal input!");
        //     return 1;
        // }

        argument = numPtr;
    }
    argv++;
    argc--;
    }

    while (argc > 1) {
        inFileNames[ifnIdx++] = argv[1];
        argv++;
        argc--;
    }

    // if we got a query with data, make sure we actually got data and a window
    // shape (possibly specified to use default values)
    if (query_needs_data_window(qparams)) {
        qparams.window_ncols =
            qparams.window_ncols < 1 ? dinfo.ncols : qparams.window_ncols;
        qparams.window_stride =
            qparams.window_stride < 1 ? 1 : qparams.window_stride;

        auto needed_window_sz = qparams.window_nrows * qparams.window_ncols;
        auto data_sz = qparams.window_data_dbl.size();
        if (needed_window_sz != data_sz) {
            LZBENCH_PRINT(1, "Got data window of size %lu, but expected size "
                "%lld (%lld, x %lld)", data_sz, needed_window_sz,
                qparams.window_nrows, qparams.window_ncols);
            return -1;
        }
    }
    if (qparams.window_data_dbl.size() > 0) {
        auto dinfo = params->data_info;
        if (dinfo.element_sz == 1) {
            if (dinfo.is_signed) {
                for (auto num : qparams.window_data_dbl) {
                    qparams.window_data_i8.push_back((int8_t)num);
                }
            } else {
                for (auto num : qparams.window_data_dbl) {
                    qparams.window_data_u8.push_back((uint8_t)num);
                }
            }
        } else if (dinfo.element_sz == 2) {
            if (dinfo.is_signed) {
                for (auto num : qparams.window_data_dbl) {
                    qparams.window_data_i16.push_back((int16_t)num);
                }
            } else {
                for (auto num : qparams.window_data_dbl) {
                    qparams.window_data_u16.push_back((uint16_t)num);
                }
            }
        } else {
            LZBENCH_PRINT(0, "Must specify valid element size (-e) to execute "
                "queries! Got element size %lld", (int64_t)dinfo.element_sz);
            return -1;
        }
    }

    LZBENCH_PRINT(2, PROGNAME " " PROGVERSION " (%d-bit " PROGOS ")   Assembled by P.Skibinski\n", (uint32_t)(8 * sizeof(uint8_t*)));
    LZBENCH_PRINT(5, "params: chunk_size=%d c_iters=%d d_iters=%d cspeed=%d cmintime=%d dmintime=%d encoder_list=%s\n", (int)params->chunk_size, params->c_iters, params->d_iters, params->cspeed, params->cmintime, params->dmintime, encoder_list);

    if (ifnIdx < 1)  { usage(params); goto _clean; }

    if (real_time)
    {
        SET_HIGH_PRIORITY;
    } else {
        LZBENCH_PRINT(2, "The real-time process priority disabled%c\n", ' ');
    }


#ifdef UTIL_HAS_CREATEFILELIST
    if (recursive) {  /* at this stage, filenameTable is a list of paths, which can contain both files and directories */
        extendedFileList = UTIL_createFileList(inFileNames, ifnIdx, &fileNamesBuf, &fileNamesNb);
        if (extendedFileList) {
            unsigned u;
            for (u=0; u<fileNamesNb; u++) LZBENCH_PRINT(4, "%u %s\n", u, extendedFileList[u]);
            free((void*)inFileNames);
            inFileNames = extendedFileList;
            ifnIdx = fileNamesNb;
        }
    }
#endif

    /* Main function */
    if (join)
        result = lzbench_join(params, inFileNames, ifnIdx, encoder_list);
    else
        result = lzbench_main(params, inFileNames, ifnIdx, encoder_list);

    if (params->chunk_size > 10 * (1<<20)) {
        LZBENCH_PRINT(2, "done... (cIters=%d dIters=%d cTime=%.1f dTime=%.1f chunkSize=%dMB cSpeed=%dMB)\n", params->c_iters, params->d_iters, params->cmintime/1000.0, params->dmintime/1000.0, (int)(params->chunk_size >> 20), params->cspeed);
    } else {
        LZBENCH_PRINT(2, "done... (cIters=%d dIters=%d cTime=%.1f dTime=%.1f chunkSize=%dKB cSpeed=%dMB)\n", params->c_iters, params->d_iters, params->cmintime/1000.0, params->dmintime/1000.0, (int)(params->chunk_size >> 10), params->cspeed);
    }

    if (sort_col <= 0) goto _clean;

    printf("\nThe results sorted by column number %d:\n", sort_col);
    print_header(params);

    switch (sort_col)
    {
        default:
        case 1: std::sort(params->results.begin(), params->results.end(), less_using_1st_column()); break;
        case 2: std::sort(params->results.begin(), params->results.end(), less_using_2nd_column()); break;
        case 3: std::sort(params->results.begin(), params->results.end(), less_using_3rd_column()); break;
        case 4: std::sort(params->results.begin(), params->results.end(), less_using_4th_column()); break;
        case 5: std::sort(params->results.begin(), params->results.end(), less_using_5th_column()); break;
    }

    for (std::vector<string_table_t>::iterator it = params->results.begin(); it!=params->results.end(); it++)
    {
        if (params->show_speed)
            print_speed(params, *it);
        else
            print_time(params, *it);
    }

_clean:
    if (encoder_list) free(encoder_list);
#ifdef UTIL_HAS_CREATEFILELIST
    if (extendedFileList)
        UTIL_freeFileList(extendedFileList, fileNamesBuf);
    else
#endif
        free((void*)inFileNames);
    return result;
}
