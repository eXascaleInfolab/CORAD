
#include "output.h"

#include <algorithm> // sort
#include <numeric>

namespace lzbench {

int istrcmp(const char *str1, const char *str2) {
    int c1, c2;
    while (1) {
        c1 = tolower((unsigned char)(*str1++));
        c2 = tolower((unsigned char)(*str2++));
        if (c1 == 0 || c1 != c2) return c1 == c2 ? 0 : c1 > c2 ? 1 : -1;
    }
}

void format(std::string& s, const char* formatstring, ...) {
   char buff[1024];
   va_list args;
   va_start(args, formatstring);

#ifdef WIN32
   _vsnprintf( buff, sizeof(buff), formatstring, args);
#else
   vsnprintf( buff, sizeof(buff), formatstring, args);
#endif

   va_end(args);

   s = buff;
}


std::vector<std::string> split(const std::string &text, char sep) {
  std::vector<std::string> tokens;
  std::size_t start = 0, end = 0;
  while (text[start] == sep) start++;
  while ((end = text.find(sep, start)) != std::string::npos) {
    tokens.push_back(text.substr(start, end - start));
    start = end + 1;
  }
  tokens.push_back(text.substr(start));
  return tokens;
}


void print_header(lzbench_params_t *params) {
    switch (params->textformat)
    {
        case CSV:
            if (params->show_speed)
                printf("Compressor name,Compression speed,Decompression speed,Original size,Compressed size,Ratio,Filename\n");
            else
                printf("Compressor name,Compression time in us,Decompression time in us,Original size,Compressed size,Ratio,Filename\n"); break;
            break;
        case TURBOBENCH:
            printf("  Compressed  Ratio   Cspeed   Dspeed         Compressor name Filename\n"); break;
        case TEXT:
            printf("Compressor name         Compress. Decompress. Compr. size  Ratio Filename\n"); break;
        case TEXT_FULL:
            printf("Compressor name         Compress. Decompress.  Orig. size  Compr. size  Ratio Filename\n"); break;
        case MARKDOWN:
            printf("| Compressor name         | Compression| Decompress.| Compr. size | Ratio | Filename |\n");
            printf("| ---------------         | -----------| -----------| ----------- | ----- | -------- |\n");
            break;
        case MARKDOWN2:
            printf("| Compressor name         | Ratio | Compression| Decompress.|\n");
            printf("| ---------------         | ------| -----------| ---------- |\n");
            break;
    }
}


void print_speed(lzbench_params_t *params, string_table_t& row) {
    float cspeed, dspeed, ratio;
    cspeed = row.col5_origsize * 1000.0 / row.col2_ctime;
    dspeed = (!row.col3_dtime) ? 0 : (row.col5_origsize * 1000.0 / row.col3_dtime);
    ratio = row.col4_comprsize * 100.0 / row.col5_origsize;

    switch (params->textformat)
    {
        case CSV:
            printf("%s,%.2f,%.2f,%llu,%llu,%.2f,%s\n", row.col1_algname.c_str(), cspeed, dspeed, (unsigned long long)row.col5_origsize, (unsigned long long)row.col4_comprsize, ratio, row.col6_filename.c_str()); break;
        case TURBOBENCH:
            printf("%12llu %6.1f%9.2f%9.2f  %22s %s\n", (unsigned long long)row.col4_comprsize, ratio, cspeed, dspeed, row.col1_algname.c_str(), row.col6_filename.c_str()); break;
        case TEXT:
        case TEXT_FULL:
            printf("%-23s", row.col1_algname.c_str());
            if (cspeed < 10) {
                printf("%6.2f MB/s", cspeed);
            } else {
                printf("%6d MB/s", (int)cspeed);
            }
            if (!dspeed) {
                printf("      ERROR");
            } else if (dspeed < 10) {
                printf("%6.2f MB/s", dspeed);
            } else {
                printf("%6d MB/s", (int)dspeed);
            }
            if (params->textformat == TEXT_FULL)
                printf("%12llu %12llu %6.2f %s\n", (unsigned long long) row.col5_origsize, (unsigned long long)row.col4_comprsize, ratio, row.col6_filename.c_str());
            else
                printf("%12llu %6.2f %s\n", (unsigned long long)row.col4_comprsize, ratio, row.col6_filename.c_str());
            break;
        case MARKDOWN:
            printf("| %-23s ", row.col1_algname.c_str());
            if (cspeed < 10) {
                printf("|%6.2f MB/s ", cspeed);
            } else {
                printf("|%6d MB/s ", (int)cspeed);
            }
            if (!dspeed) {
                printf("|      ERROR ");
            } else if (dspeed < 10) {
                printf("|%6.2f MB/s ", dspeed);
            } else {
                printf("|%6d MB/s ", (int)dspeed);
            }
            printf("|%12llu |%6.2f | %-s|\n", (unsigned long long)row.col4_comprsize, ratio, row.col6_filename.c_str());
            break;
        case MARKDOWN2:
            ratio = 1.0*row.col5_origsize / row.col4_comprsize;
            printf("| %-23s |%6.3f ", row.col1_algname.c_str(), ratio);
            if (cspeed < 10) {
                printf("|%6.2f MB/s ", cspeed);
            } else {
                printf("|%6d MB/s ", (int)cspeed);
            }
            if (!dspeed) {
                printf("|      ERROR ");
            } else if (dspeed < 10) {
                printf("|%6.2f MB/s ", dspeed);
            } else {
                printf("|%6d MB/s ", (int)dspeed);
            }
            printf("|\n");
            break;
    }
}


void print_time(lzbench_params_t *params, string_table_t& row) {
    float ratio = row.col4_comprsize * 100.0 / row.col5_origsize;
    uint64_t ctime = row.col2_ctime / 1000;
    uint64_t dtime = row.col3_dtime / 1000;

    switch (params->textformat)
    {
        case CSV:
            printf("%s,%llu,%llu,%llu,%llu,%.2f,%s\n", row.col1_algname.c_str(),
                (unsigned long long)ctime, (unsigned long long)dtime,
                (unsigned long long) row.col5_origsize,
                (unsigned long long)row.col4_comprsize, ratio,
                row.col6_filename.c_str());
            break;
        case TURBOBENCH:
            printf("%12llu %6.1f%9llu%9llu  %22s %s\n",
                (unsigned long long)row.col4_comprsize, ratio,
                (unsigned long long)ctime, (unsigned long long)dtime,
                row.col1_algname.c_str(), row.col6_filename.c_str());
            break;
        case TEXT:
        case TEXT_FULL:
            printf("%-23s", row.col1_algname.c_str());
            printf("%8llu us", (unsigned long long)ctime);
            if (!dtime)
                printf("      ERROR");
            else
                printf("%8llu us", (unsigned long long)dtime);
            if (params->textformat == TEXT_FULL)
                printf("%12llu %12llu %6.2f %s\n",
                    (unsigned long long) row.col5_origsize,
                    (unsigned long long)row.col4_comprsize, ratio,
                    row.col6_filename.c_str());
            else
                printf("%12llu %6.2f %s\n",
                    (unsigned long long)row.col4_comprsize, ratio,
                    row.col6_filename.c_str());
            break;
        case MARKDOWN:
            printf("| %-23s ", row.col1_algname.c_str());
            printf("|%8llu us ", (unsigned long long)ctime);
            if (!dtime)
                printf("|      ERROR ");
            else
                printf("|%8llu us ", (unsigned long long)dtime);
            printf("|%12llu |%6.2f | %-s|\n",
                (unsigned long long)row.col4_comprsize, ratio,
                row.col6_filename.c_str());
            break;
        case MARKDOWN2:
            printf("MARKDOWN2 not supported!\n");
            break;
    }
}


void print_stats(lzbench_params_t *params, const compressor_desc_t* desc,
    int level, std::vector<uint64_t> &ctime, std::vector<uint64_t> &dtime,
    size_t insize, size_t outsize, bool decomp_error)
{
    std::string col1_algname;
    std::sort(ctime.begin(), ctime.end());
    std::sort(dtime.begin(), dtime.end());
    uint64_t best_ctime, best_dtime;

    switch (params->timetype)
    {
        default:
        case FASTEST:
            best_ctime = ctime.empty()?0:ctime[0];
            best_dtime = dtime.empty()?0:dtime[0];
            break;
        case AVERAGE:
            best_ctime = ctime.empty()?0:std::accumulate(ctime.begin(),ctime.end(),(uint64_t)0) / ctime.size();
            best_dtime = dtime.empty()?0:std::accumulate(dtime.begin(),dtime.end(),(uint64_t)0) / dtime.size();
            break;
        case MEDIAN:
            best_ctime = ctime.empty()?0:(ctime[(ctime.size()-1)/2] + ctime[ctime.size()/2]) / 2;
            best_dtime = dtime.empty()?0:(dtime[(dtime.size()-1)/2] + dtime[dtime.size()/2]) / 2;
            break;
    }

    if (desc->first_level == 0 && desc->last_level==0)
        format(col1_algname, "%s %s", desc->name, desc->version);
    else
        format(col1_algname, "%s %s -%d", desc->name, desc->version, level);

    params->results.push_back(string_table_t(col1_algname, best_ctime, (decomp_error)?0:best_dtime, outsize, insize, params->in_filename));
    if (params->show_speed)
        print_speed(params, params->results[params->results.size()-1]);
    else
        print_time(params, params->results[params->results.size()-1]);

    ctime.clear();
    dtime.clear();
}

} // namespace lzbench
