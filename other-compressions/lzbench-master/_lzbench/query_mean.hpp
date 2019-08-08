
#ifndef QUERY_MEAN_HPP
#define QUERY_MEAN_HPP

#include "query_common.h"

namespace lzbench {

// template<class DataT, bool IsDense>
template<class DataT>
class OnlineMeanRowmajor {
public:
    using dist_t = typename DataTypeTraits<DataT>::AccumulatorT;
    // static const bool is_dense = IsDense;

    OnlineMeanRowmajor(uint32_t nrows, uint32_t ncols):
        _nrows(nrows), _ncols(ncols), _is_dense(true)
    {
        reset();
    }

    OnlineMeanRowmajor(uint32_t nrows, uint32_t ncols,
        const std::vector<uint16_t>& which_dims):
        _nrows(nrows), _ncols(ncols), _which_dims(which_dims),
        _is_dense(which_dims.size() == 0)
    {
        // if (IsDense) {
        //     printf("ERROR: can't specify subset of dims for Dense OnlineMean!");
        //     exit(1);
        // }
        reset();
    }

    void init(const DataT* window_start) {
        if (_is_dense) {
            for (uint32_t i = 0; i < _nrows; i++) {
                for (uint32_t j = 0; j < _ncols; j++) {
                    _sums[j] += window_start[i * _ncols + j];
                }
            }
        } else {
            for (uint32_t i = 0; i < _nrows; i++) {
                for (uint32_t j_idx = 0; j_idx < _which_dims.size(); j_idx++) {
                    auto j = _which_dims[j_idx];
                    _sums[j_idx] += window_start[i * _ncols + j];
                }
            }
        }
    }

    void update(const DataT* old_window_row, const DataT* new_window_row) {
        if (_is_dense) {
            for (uint32_t j = 0; j < _ncols; j++) {
                _sums[j] += (new_window_row[j] - old_window_row[j]);
            }
        } else {
            for (uint32_t j_idx = 0; j_idx < _which_dims.size(); j_idx++) {
                auto j = _which_dims[j_idx];
                _sums[j_idx] += (new_window_row[j] - old_window_row[j]);
            }
        }
    }

    void write_stats(DataT* out) const {
        for (uint32_t j = 0; j < _sums.size(); j++) {
            out[j] = _sums[j] / _nrows;
        }
    }

    void reset() {
        if (_sums.size() == 0) {
            auto sums_size = _is_dense ? _ncols : _which_dims.size();
            for (size_t i = 0; i < sums_size; i++) {
                _sums.push_back(0);
            }
        } else {
            for (size_t i = 0; i < _sums.size(); i++) {
                _sums[i] = 0;
            }
        }
    }

    uint32_t nrows() const { return _nrows(); }
    uint16_t ncols() const { return _ncols(); }

private:
    std::vector<uint16_t> _which_dims;
    std::vector<dist_t> _sums;
    uint32_t _nrows;
    uint16_t _ncols;
    bool _is_dense;
};

// XXX this func will return wrong results since buff is always u8 at call
// sites; this needs to take in elem_sz as well
template<class DataT>
QueryResult sliding_mean(const QueryParams& q,
    const DataInfo& di, const DataT* buff)
    // -> std::vector<typename DataTypeTraits<DataT>::AccumulatorT>
{
    // using StatT = typename DataTypeTraits<DataT>::AccumulatorT;

    using RealDataType = DataT; // XXX need to infer this from ElemSz

    auto window_nrows = q.window_nrows > 0 ? q.window_nrows : di.nrows;
    // printf("actually running sliding mean! window nrows, ncols, stride "
    //     " = %lld, %lld, %lld\n", window_nrows, q.window_ncols, q.window_stride);

    // figure out how long data is, and how many window positions we have
    auto nrows = di.nrows;
    int64_t last_window_start_row = nrows - window_nrows;
    int64_t nwindows = nrows - window_nrows + 1;

    // auto ret_size = nrows * di.ncols;
    size_t sparse_ncols = q.which_cols.size();
    bool sparse = sparse_ncols > 0;
    auto ret_ncols = sparse ? sparse_ncols : di.ncols;
    auto ret_size = nwindows * ret_ncols * sizeof(RealDataType);

    QueryResult ret;
    auto& ret_vals = ret.vals;
    // auto& ret_vals = QueryResultValsRef<DataT>{}(ret);
    ret_vals.resize(ret_size);

    if (nwindows < 1) { return ret; }

    if (di.storage_order == ROWMAJOR) {
        OnlineMeanRowmajor<RealDataType> stat(window_nrows, di.ncols, q.which_cols);
        stat.init(buff);
        auto ret_ptr = ret_vals.data();
        stat.write_stats(ret_ptr);
        for (size_t row = window_nrows; row < last_window_start_row; row++) {
            auto old_row = row - window_nrows;
            auto old_ptr = buff + di.ncols * old_row;
            auto new_ptr = buff + di.ncols * row;
            auto ret_row_ptr = ret_ptr + (old_row + 1) * ret_ncols;
            stat.update(old_ptr, new_ptr);
            stat.write_stats(ret_row_ptr);
        }
        return ret;
    }

    // column-major; treat each col as 1D rowmajor, and also write out results
    // in column-major order
    auto which_cols = q.which_cols;
    if (!sparse) {
        for (int i = 0; i < di.ncols; i++) {
            which_cols.push_back(i);
        }
    }
    for (int j_idx = 0; j_idx < which_cols.size(); j_idx++) {
        OnlineMeanRowmajor<RealDataType> stat(window_nrows, 1);
        auto buff_ptr = buff + di.nrows;
        auto ret_ptr = ret_vals.data() + di.nrows; // write to ret in colmajor order
        stat.init(buff_ptr);
        stat.write_stats(ret_ptr);
        for (size_t row = window_nrows; row < last_window_start_row; row++) {
            auto old_row = row - window_nrows;
            auto ret_row_ptr = ret_ptr + (old_row + 1);
            stat.update(buff_ptr + old_row, buff_ptr + row);
            stat.write_stats(ret_row_ptr);
        }
    }
    return ret;
}

} // namespace lzbench

#endif // QUERY_MEAN_HPP
