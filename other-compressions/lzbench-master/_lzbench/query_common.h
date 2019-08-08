// TODO should rename this file to avoid ambiguity with query.hpp

#ifndef QUERY_H
#define QUERY_H

#include <vector>

namespace lzbench {

enum query_type_e { QUERY_NONE = 0, QUERY_MAX = 1, QUERY_SUM = 2,
    QUERY_MEAN = 3, QUERY_MIN = 4,
    QUERY_L2 = 5, QUERY_DOT = 6, QUERY_NORM = 7};
enum query_reduction_e { REDUCE_NONE = 0, REDUCE_THRESH = 1, REDUCE_TOP_K = 2};
enum storage_order_e { ROWMAJOR = 0, COLMAJOR = 1};

template<class A, class B>
static inline auto min(A x, B y) -> decltype(x - y) { return x <= y ? x : y; }
template<class A, class B>
static inline auto max(A x, B y) -> decltype(x - y) { return x >= y ? x : y; }

// #ifndef MIN
//     #define MIN(X, Y) (X) <= (Y) ? (X) : (Y);
// #endif
// #ifndef MAX
//     #define MAX(X, Y) (X) >= (Y) ? (X) : (Y);
// #endif

namespace OpE { enum { MIN = 0, MAX = 1, SQUARE_DIFF = 2, PRODUCT = 3}; }

template<class DataT, int OpE, class OutT=DataT> struct BinaryOp {};
template<class DataT> struct BinaryOp<DataT, OpE::MIN, DataT> {
    DataT operator()(const DataT& x, const DataT& y) { return min(x, y); }
};
template<class DataT> struct BinaryOp<DataT, OpE::MAX, DataT> {
    DataT operator()(const DataT& x, const DataT& y) { return max(x, y); }
};
template<class DataT, class OutT> struct BinaryOp<DataT, OpE::SQUARE_DIFF, OutT>
{
    DataT operator()(const DataT& x, const DataT& y) { return (x-y)*(x-y); }
};
template<class DataT, class OutT> struct BinaryOp<DataT, OpE::PRODUCT, OutT>
{
    DataT operator()(const DataT& x, const DataT& y) { return x * y; }
};

// // traits for different types of queries
// template<int query_type>
// class query_type_traits { enum { needs_data_window = 0 }; }
// template<>
// class query_type_traits<QUERY_L2> { enum { needs_data_window = 1 }; }
// template<>
// class query_type_traits<QUERY_DOT> { enum { needs_data_window = 1 }; }

typedef struct QueryParams {
    // double version is populated when argv parsed for simplicity; exactly
    // one of the others should be populated
    std::vector<double> window_data_dbl;
    std::vector<int8_t> window_data_i8;
    std::vector<uint8_t> window_data_u8;
    std::vector<int16_t> window_data_i16;
    std::vector<uint16_t> window_data_u16;
    std::vector<uint16_t> which_cols; // TODO populate to enable sparse queries
    int64_t window_nrows;
    int64_t window_ncols;
    int64_t window_stride;
    uint16_t k; // used for topk queries
    query_type_e type;
    query_reduction_e reduction;
} QueryParams;

typedef struct QueryResult {
    std::vector<int64_t> idxs;
    std::vector<uint8_t> vals;
    // std::vector<int8_t> vals_i8;
    // std::vector<uint8_t> vals_u8;
    // std::vector<int16_t> vals_i16;
    // std::vector<uint16_t> vals_u16;
    // std::vector<int32_t> vals_i32;

    QueryResult() = default;
    QueryResult(const QueryResult& other) = default;
    QueryResult(QueryResult&& other) = default;
    QueryResult& operator=(const QueryResult& other) = default;
} QueryResult;

typedef struct DataInfo {
    size_t element_sz;
    size_t nrows; // TODO populate this in decomp func
    size_t ncols;
    bool is_signed;
    storage_order_e storage_order;
} DataInfo;

typedef struct QueryRefs { // used in hack for pushing down queries
    const QueryParams* qparams;
    QueryResult* qres;
    const DataInfo* dinfo;
} QueryRefs;

template <class data_t> struct DataTypeTraits {};
template <> struct DataTypeTraits<uint8_t> { using AccumulatorT = uint16_t; };
template <> struct DataTypeTraits<uint16_t> { using AccumulatorT = uint32_t; };

template <int ElemSz> struct ElemSizeTraits {};
template <> struct ElemSizeTraits<1> { using DataT = uint8_t; };
template <> struct ElemSizeTraits<2> { using DataT = uint16_t; };

// // pull out reference to appropriate vector of values
// template<class DataT> struct QueryResultValsRef {};
// template <> struct QueryResultValsRef<int8_t> {
//     std::vector<int8_t>& operator()(QueryResult& qr) { return qr.vals_i8; }
// };
// template <> struct QueryResultValsRef<uint8_t> {
//     std::vector<uint8_t>& operator()(QueryResult& qr) { return qr.vals_u8; }
// };
// template <> struct QueryResultValsRef<int16_t> {
//     std::vector<int16_t>& operator()(QueryResult& qr) { return qr.vals_i16; }
// };
// template <> struct QueryResultValsRef<uint16_t> {
//     std::vector<uint16_t>& operator()(QueryResult& qr) { return qr.vals_u16; }
// };

template<class DataT> struct QueryDataValsRef {};
template <> struct QueryDataValsRef<int8_t> {
    const std::vector<int8_t>& operator()(const QueryParams& q) {
        return q.window_data_i8;
    }
};
template <> struct QueryDataValsRef<uint8_t> {
    const std::vector<uint8_t>& operator()(const QueryParams& q) {
        return q.window_data_u8;
    }
};
template <> struct QueryDataValsRef<int16_t> {
    const std::vector<int16_t>& operator()(const QueryParams& q) {
        return q.window_data_i16;
    }
};
template <> struct QueryDataValsRef<uint16_t> {
    const std::vector<uint16_t>& operator()(const QueryParams& q) {
        return q.window_data_u16;
    }
};

}

#endif // QUERY_HPP
