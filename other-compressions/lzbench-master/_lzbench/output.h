//
// output.h
// Created by D Blalock 2017-10-18
//

#ifndef output_h
#define output_h

#include <string>
#include "lzbench.h"

namespace lzbench {

int istrcmp(const char *str1, const char *str2);
void format(std::string& s, const char* formatstring, ...);
std::vector<std::string> split(const std::string &text, char sep);
void print_header(lzbench_params_t *params);
void print_speed(lzbench_params_t *params, string_table_t& row);
void print_time(lzbench_params_t *params, string_table_t& row);
void print_stats(lzbench_params_t *params, const compressor_desc_t* desc,
    int level, std::vector<uint64_t> &ctime, std::vector<uint64_t> &dtime,
    size_t insize, size_t outsize, bool decomp_error);

} // namespace lzbench

#endif
