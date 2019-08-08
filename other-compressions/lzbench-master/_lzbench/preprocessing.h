//
// preprocessing.h
// Created by D Blalock 2017-10-18
//

#ifndef _preprocessing_h
#define _preprocessing_h

#include <stdint.h>
#include <vector>


namespace lzbench {

void apply_preprocessors(const std::vector<int64_t>& preprocessors,
    const uint8_t* inbuf, size_t size, int element_sz, uint8_t* outbuf);
void undo_preprocessors(const std::vector<int64_t>& preprocessors,
    uint8_t* inbuf, size_t size, int element_sz, uint8_t* outbuf=nullptr);

} // namespace lzbench

#endif
