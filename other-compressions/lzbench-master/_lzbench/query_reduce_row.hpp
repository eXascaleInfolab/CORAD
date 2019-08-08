#ifndef QUERY_REDUCE_ROW_HPP
#define QUERY_REDUCE_ROW_HPP

#include <deque>
#include "query_common.h"

namespace lzbench {

// template<class DataT, int OpE>
// class OnlineWindowReductionRowmajor {
// public:
//     using dist_t = typename DataTypeTraits<DataT>::AccumulatorT;
//     using Op = BinaryOp<DataT, OpE>;

//     OnlineWindowReductionRowmajor(uint32_t nrows, uint32_t ncols,
//         const std::vector<DataT>& filter):
//         _filter(filter), _nrows(nrows), _ncols(ncols), _is_dense(true)
//     {
//         reset();
//     }

//     OnlineWindowReductionRowmajor(uint32_t nrows, uint32_t ncols,
//         const std::vector<DataT>& filter,
//         const std::vector<uint16_t>& which_dims):
//         _filter(filter), _nrows(nrows), _ncols(ncols), _which_dims(which_dims),
//         _is_dense(which_dims.size() == 0)
//     {
//         reset();
//     }

//     // void init(const DataT* window_start) {
//     //     reset();
//     //     // dist_t dist = dist;
//     //     if (_is_dense) {
//     //         for (uint32_t i = 0; i < _nrows; i++) {
//     //             dist_t row_sum = 0;
//     //             for (uint32_t j = 0; j < _ncols; j++) {
//     //                 auto idx = i * _ncols + j;
//     //                 row_sum += Op{}(_filter[idx], window_start[idx]);
//     //             }
//     //             // _rowsums.push_back(row_sum);
//     //             _current_dist += row_sum;
//     //         }
//     //     } else {
//     //         for (uint32_t i = 0; i < _nrows; i++) {
//     //             dist_t row_sum = 0;
//     //             for (uint32_t j_idx = 0; j_idx < _which_dims.size(); j_idx++) {
//     //                 auto j = _which_dims[j_idx];
//     //                 auto idx = i * _ncols + j;
//     //                 row_sum += Op{}(_filter[idx], window_start[idx]);
//     //             }
//     //             // _rowsums.push_back(row_sum);
//     //             _current_dist += row_sum;
//     //         }
//     //     }
//     //     // _stats.push_back(_current_dist);
//     // }

//     // void update(const DataT* old_window_row, const DataT* new_window_row) {
//     void update(const DataT* window_start) {
//         reset();
//         // dist_t dist = dist;
//         if (_is_dense) {
//             for (uint32_t i = 0; i < _nrows; i++) {
//                 dist_t row_sum = 0;
//                 for (uint32_t j = 0; j < _ncols; j++) {
//                     auto idx = i * _ncols + j;
//                     row_sum += Op{}(_filter[idx], window_start[idx]);
//                 }
//                 // _rowsums.push_back(row_sum);
//                 _current_dist += row_sum;
//             }
//         } else {
//             for (uint32_t i = 0; i < _nrows; i++) {
//                 dist_t row_sum = 0;
//                 for (uint32_t j_idx = 0; j_idx < _which_dims.size(); j_idx++) {
//                     auto j = _which_dims[j_idx];
//                     auto idx = i * _ncols + j;
//                     row_sum += Op{}(_filter[idx], window_start[idx]);
//                 }
//                 // _rowsums.push_back(row_sum);
//                 _current_dist += row_sum;
//             }
//         }
//     }

//     // time steps independent
//     void init(const DataT* window_start) { update(window_start); }

//         // _stats.push_back(_current_dist);
//         // // remove contribution of old row using cached result
//         // // auto old_dist = _rowsums.pop_front();
//         // // _current_dist -= old_dist;

//         // // add in contribution of this row
//         // dist_t dist = 0;
//         // if (_is_dense) {
//         //     for (uint32_t j = 0; j < _ncols; j++) {
//         //         auto idx = i * _ncols + j;
//         //         // dist += Op{}(_filter[idx], new_window_row[j]);
//         //     }
//         // } else {
//         //     for (uint32_t j_idx = 0; j_idx < _which_dims.size(); j_idx++) {
//         //         auto j = _which_dims[j_idx];
//         //         auto idx = i * _ncols + j;
//         //         dist += Op{}(_filter[idx], new_window_row[j]);
//         //     }
//         // }
//         // // _rowsums.push_back(dist);
//         // // _current_dist += dist;

//         // _current_dist = dist;
//     // }

//     void write_stats(dist_t* out) const {
//         *out = _current_dist;
//         // for (uint32_t j = 0; j < _stats.size(); j++) {
//         //     out[j] = _stats[j];
//         // }
//     }

//     void reset() {
//         // _stats.clear();
//         // _rowsums.clear();
//         // for (uint32_t i = 0; i < _nrows; i++) {
//         //     _rowsums.push_back(0);
//         // }
//         _current_dist = 0;
//         // if (_stats.size() == 0) {
//         //     _stats.push_back(0);
//         //     // auto sums_size = _is_dense ? _ncols : _which_dims.size();
//         //     // for (size_t i = 0; i < sums_size; i++) {
//         //     // }
//         // } else {
//         //     for (size_t i = 0; i < _stats.size(); i++) {
//         //         _stats[i] = 0;
//         //     }
//         // }
//     }

//     uint32_t nrows() const { return _nrows(); }
//     uint16_t ncols() const { return _ncols(); }

// private:
//     std::vector<DataT> _filter;
//     std::vector<uint16_t> _which_dims;
//     // std::vector<dist_t> _stats;
//     // std::deque<dist_t> _rowsums;
//     dist_t _current_dist;
//     uint32_t _nrows;
//     uint16_t _ncols;
//     bool _is_dense;
// };

// template<class DataT, int OpE>
// QueryResult sliding_window_reduction(const QueryParams& q,
//     const DataInfo& di, const DataT* buff)
// {
//     using dist_t = typename DataTypeTraits<DataT>::AccumulatorT;
//     auto window_nrows = q.window_nrows > 0 ? q.window_nrows : di.nrows;
//     // printf("actually running sliding max! window nrows, ncols, stride "
//     //     " = %lld, %lld, %lld\n", window_nrows, q.window_ncols, q.window_stride);

//     // figure out how long data is, and how many window positions we have
//     auto nrows = di.nrows;
//     int64_t last_window_start_row = nrows - window_nrows;
//     int64_t nwindows = nrows - window_nrows + 1;

//     size_t sparse_ncols = q.which_cols.size();
//     bool sparse = sparse_ncols > 0;
//     auto ret_ncols = 1; // scalar reduction
//     auto ret_size = nwindows * ret_ncols;

//     QueryResult ret;
//     auto& ret_vals = QueryResultValsRef<dist_t>{}(ret);
//     ret_vals.resize(ret_size);

//     if (nwindows < 1) { return ret; }

//     auto& query_data = QueryDataValsRef<DataT>{}(q);

//     if (di.storage_order == ROWMAJOR) {
//         OnlineWindowReductionRowmajor<DataT, OpE> stat(
//             window_nrows, di.ncols, query_data, q.which_cols);
//         stat.init(buff);
//         auto ret_ptr = ret_vals.data();
//         stat.write_stats(ret_ptr);
//         // for (size_t row = window_nrows; row < last_window_start_row; row++) {
//         for (size_t row = 1; row < last_window_start_row; row++) {
//             auto window_ptr = buff + di.ncols * row;
//             auto ret_row_ptr = ret_ptr + row * ret_ncols;
//             stat.update(window_ptr);
//             stat.write_stats(ret_row_ptr);
//         }
//         return ret;
//     }

//     // column-major; treat each col as 1D rowmajor, and also write out results
//     // in column-major order
//     auto which_cols = q.which_cols;
//     if (!sparse) {
//         for (int i = 0; i < di.ncols; i++) {
//             which_cols.push_back(i);
//         }
//     }
//     memset(ret_vals.data(), 0, ret_size * sizeof(ret_vals[0]));
//     std::vector<DataT> filter_col(q.window_nrows);
//     for (int j_idx = 0; j_idx < which_cols.size(); j_idx++) {
//         for (uint32_t i = 0; i < filter_col.size(); i++) {
//             filter_col[i] = query_data[i * which_cols.size() + j_idx];
//         }
//         OnlineWindowReductionRowmajor<DataT, OpE> stat(
//             window_nrows, 1, filter_col);
//         auto buff_ptr = buff + di.nrows;
//         auto ret_ptr = ret_vals.data() + di.nrows; // write to ret in colmajor order
//         stat.init(buff_ptr);
//         stat.write_stats(ret_ptr);
//         dist_t tmp; // exists so we can do +=, not just overwrite current sum
//         for (size_t row = 1; row < last_window_start_row; row++) {
//             auto window_ptr = buff + di.ncols * row;
//             auto ret_row_ptr = ret_ptr + row * ret_ncols;
//             stat.update(window_ptr);
//             stat.write_stats(&tmp);
//             ret_vals[row] += tmp;
//         }
//     }
//     return ret;
// }

// template<class DataT>
// QueryResult sliding_l2(const QueryParams& q,
//     const DataInfo& di, const DataT* buff)
// {
//     // printf("running sliding l2 query!\n");
//     return sliding_window_reduction<DataT, OpE::SQUARE_DIFF>(q, di, buff);
// }
// template<class DataT>
// QueryResult sliding_dot(const QueryParams& q,
//     const DataInfo& di, const DataT* buff)
// {
//     // printf("running sliding dot prod query!\n");
//     return sliding_window_reduction<DataT, OpE::PRODUCT>(q, di, buff);
// }

} // namespace lzbench

#endif // QUERY_REDUCE_ROW_HPP
