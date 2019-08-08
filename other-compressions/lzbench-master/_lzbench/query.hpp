
#ifndef QUERY_HPP
#define QUERY_HPP

#include "query_common.h"
#include "query_mean.hpp"
#include "query_minmax.hpp"
#include "query_reduce_row.hpp"

namespace lzbench {

// if we weren't just benchmarking, would need to return something in all
// of these

// template<class DataT>
// void sliding_mean(const QueryParams& q, const DataInfo& di, const DataT* buff) {

// }

// template<class DataT>
// QueryResult sliding_min(const QueryParams& q, const DataInfo& di,
//     const DataT* buff)
// {
//     return QueryResult{}; // TODO
// }

// template<class DataT>
// QueryResult sliding_max(const QueryParams& q, const DataInfo& di,
//     const DataT* buff)
// {
//     return QueryResult{}; // TODO
// }

// template<class DataT>
// QueryResult sliding_l2(const QueryParams& q, const DataInfo& di,
//     const DataT* buff)
// {
//     if (q.reduction == REDUCE_NONE) {

//     } else if (q.reduction == REDUCE_THRESH) {

//     } else if (q.reduction == REDUCE_TOP_K) {

//     } else {
//         printf("Invalid reduction %d for L2 query!\n", (int)q.reduction);
//         exit(1);
//     }
//     return QueryResult{}; // TODO
// }

// template<class DataT>
// QueryResult sliding_dot(const QueryParams& q, const DataInfo& di,
//     const DataT* buff)
// {
//     if (q.reduction == REDUCE_NONE) {

//     } else if (q.reduction == REDUCE_THRESH) {

//     } else if (q.reduction == REDUCE_TOP_K) {

//     } else {
//         printf("Invalid reduction %d for dot product query!\n",
//             (int)q.reduction);
//         exit(1);
//     }
//     return QueryResult{}; // TODO
// }



static inline bool can_push_down_query(std::string algo_name) {
    auto is_sprintz_algo = algo_name.find("sprintz") == 0; //  "sprintz"
    auto uses_huf = algo_name.find("HUF") != std::string::npos;
    return is_sprintz_algo && !uses_huf;
}

template<class DataT>
QueryResult corr(const QueryParams& q, const DataInfo& di,
    const DataT* buff)
{

}


template<class DataT>
QueryResult _frobnicate(const QueryParams& q, const DataInfo& di, const DataT* buff) {
    printf("actually running frobnicate; query_type=%d!\n", (int)q.type);
    return QueryResult{};
}

template<int ElemSz, class DataT>
// static inline QueryResult reduce_contiguous(const QueryParams& q,
static inline std::unique_ptr<QueryResult> reduce_contiguous(const QueryParams& q,
    const DataInfo& di, const DataT* buff)
{
    // // fprintf(stderr, "running reduce_contiguous\n");
    // printf("******* running reduce_contiguous using query type %d\n", q.type);
    // exit(1);

    // compute actual data type based on elemsz; buff is likely to be a byte*
    // regardless of what those bytes represent
    using RealDataType = typename ElemSizeTraits<ElemSz>::DataT;
    using RowmajorMat = Eigen::Map<const Eigen::Matrix<
        RealDataType, Eigen::Dynamic, Eigen::Dynamic, Eigen::RowMajor> >;
    using ColmajorMat = Eigen::Map<const Eigen::Matrix<
        RealDataType, Eigen::Dynamic, Eigen::Dynamic, Eigen::ColMajor> >;
    using RowVector = Eigen::Array<RealDataType, 1, Eigen::Dynamic, Eigen::RowMajor>;
    using RowVectorMap = Eigen::Map<RowVector>;
    using RowVector_I32 = Eigen::Array<int32_t, 1, Eigen::Dynamic, Eigen::RowMajor>;

    // using MutVector = Eigen::Map<Eigen::Vector<DataT, Eigen::Dynamic> >;
    // printf("running sliding min query!\n");
    // return sliding_binary_op<DataT, OpE::MIN>(q, di, buff);

    // printf("******* running reduce_contiguous\n");
    // std::cout << "RUN THIS CODE YOU RETARDED COMPILER" << std::endl;
    // exit(1);

    // QueryResult ret;
    // auto& ret_vals = ret.vals;
    auto ret = std::unique_ptr<QueryResult>(new QueryResult());
    auto& ret_vals = ret->vals;
    // auto& ret_vals = QueryResultValsRef<RealDataType>{}(ret);
    // auto& ret_vals_i32 = ret.vals_i32;

    // only rowmajor impl actually upconverts to prevent overhead without
    // overflow; colmajor impls just use eigen, which doesn't, AFAICT,
    // support summing using more bits than original dtype
    bool use_i32_output = (q.type != QUERY_MIN) && (q.type != QUERY_MAX);
    use_i32_output = use_i32_output && di.storage_order == ROWMAJOR;

    // ret_vals.resize(di.ncols);
    int output_elem_sz = use_i32_output ? sizeof(int32_t) : ElemSz;
    // ret_vals.reserve(output_elem_sz * di.ncols);
    auto outbuff_size = output_elem_sz * di.ncols;
    // if (di.storage_order == ROWMAJOR) {
    //     // only pad if rowmajor since this makes colmajor (eigen) segfault
    //     auto nstripes_in = div_round_up(di.ncols * ElemSz, 32); // XXX don't hardcode avx2
    //     outbuff_size = nstripes_in * output_elem_sz / ElemSz;
    // }
    ret_vals.resize(outbuff_size);
    // ret_vals.resize(output_elem_sz * di.ncols);

    // return ret;

    const RealDataType* data_ptr = (const RealDataType*)buff;

    // // printf("retvals elem_sz: %lu\n", sizeof(ret_vals[0]));
    // printf("------> retvals size: %lu\n", ret_vals.size());
    // printf("------> retvals capacity: %lu\n", ret_vals.capacity());

    // MutRowmajorMat ret_vec(ret_vals.data(), 1, di.ncols);
    // RowVectorMap ret_vec(ret_vals.data(), 1, di.ncols * output_elem_sz / ElemSz);
    RowVectorMap ret_vec((RealDataType*)ret_vals.data(),
        di.ncols * output_elem_sz / ElemSz);
    // auto ret_buff_i32 = ret_vals_i32.data();

    // printf("nrows, ncols: %d, %d\n", (int)di.nrows, (int)di.ncols);
    // exit(1);

    // TODO uncomment below
    //
    if (di.storage_order == ROWMAJOR) {
        RowmajorMat mat(data_ptr, di.nrows, di.ncols);
        // RowVector tmp(di.ncols);

        // printf("*** using rowmajor storage order\n");
        // printf("rowmajor size of reduce_sum: %d\n", (int)mat.colwise().sum().size());

        // NOTE: using same eigen cols as below is insanely slow, so we
        // have to implement these reductions ourselves
        switch (q.type) {
        case QUERY_MEAN:
            // printf("running rowmajor query_mean!\n");
            reduce_sum_avx2_rowmajor_ax0<ElemSz>(
                mat.data(), di.nrows, di.ncols, (int32_t*)ret_vals.data());
            // for (size_t j = 0; j < di.ncols; j++) {
            //     ret_buff_i32[j] /= di.nrows;
            // }
        case QUERY_SUM:
            // printf("about to compute the sum...\n");
            reduce_sum_avx2_rowmajor_ax0<ElemSz>(
                mat.data(), di.nrows, di.ncols, (int32_t*)ret_vals.data());
            // printf("computed the sum!\n");
        case QUERY_MIN:
            ret_vec = mat.row(0);
            for (size_t i = 1; i < di.nrows; i++) {
                ret_vec = ret_vec.min(mat.row(i).array());
            }
            break;
        case QUERY_MAX:
            ret_vec = mat.row(0);
            for (size_t i = 1; i < di.nrows; i++) {
                ret_vec = ret_vec.max(mat.row(i).array());
            }
            break;
        case QUERY_NORM:
            ret_vec = mat.colwise().squaredNorm(); break;
        default:
            printf("Unsupported query type for contiguous data: %d!\n",
                (int)q.type); exit(1);
        }
    } else { // XXX pretty sure all of these (except min/max) ignore overflows
        ColmajorMat mat(data_ptr, di.nrows, di.ncols);

        // printf("colmajor size of reduce_sum: %d\n", (int)mat.colwise().sum().size());
        // printf("colmajor number of rows, cols: %d, %d\n", (int)mat.rows(), (int)mat.cols());
        // printf("colmajor size of ret_vec: %d\n", (int)ret_vec.size());
        // // printf("colmajor last val in sum: %d\n", (int)mat.colwise().sum()(0, 17));

        switch (q.type) {
        case QUERY_MEAN:
            ret_vec = mat.colwise().mean(); break;
        case QUERY_SUM:
            /// XXX sums will integer overflow for small int types
            ret_vec = mat.colwise().sum(); break;
            // printf("about to compute the sum...\n");
            // ret_vec = mat.colwise().sum();
            // printf("computed the sum!\n");
            // break;
        case QUERY_MIN:
            ret_vec = mat.colwise().minCoeff(); break;
        case QUERY_MAX:
            ret_vec = mat.colwise().maxCoeff(); break;
        case QUERY_NORM:
            ret_vec = mat.colwise().squaredNorm(); break;
        default:
            printf("Unsupported query type for contiguous data: %d!\n",
                (int)q.type); exit(1);
        }
    }
    // printf("ran the query; about to return result\n");
    return ret;
}

template<class DataT>
// QueryResult run_query(const QueryParams& q, const DataInfo& di, const DataT* buff) {
// std::unique_ptr<QueryResult> poopinize(const QueryParams& q, const DataInfo& di, const DataT* buff) {
std::unique_ptr<QueryResult> run_query(const QueryParams& q, const DataInfo& di, const DataT* buff) {

    // printf("actually running run_query; query_type=%d!\n", (int)q.type);

    // QueryResult ret;
    switch (di.element_sz) {
    case 1: return reduce_contiguous<1>(q, di, buff);
    case 2: return reduce_contiguous<2>(q, di, buff);
    // case 1: return frobnicate(q, di, buff);
    // case 2: return frobnicate(q, di, buff);
    default:
        printf("Invalid element size %d!\n", (int)di.element_sz); exit(1);
        exit(1);
    }
    // switch (q.type) {
    //     // case QUERY_MEAN: ret = sliding_mean(q, di, buff); break;
    //     case QUERY_MEAN: ret = reduce_contiguous(q, di, buff); break;
    //     // XXX "sliding" min and max actually just write out min/max seen
    //     // so far, which is a weird thing to do
    //     case QUERY_MIN: ret = reduce_contiguous(q, di, buff); break;
    //     case QUERY_MAX: ret = reduce_contiguous(q, di, buff); break;
    //     // case QUERY_L2: ret = sliding_l2(q, di, buff); break;
    //     // case QUERY_DOT: ret = sliding_dot(q, di, buff); break;
    //     case QUERY_SUM: ret = reduce_contiguous(q, di, buff); break;
    //     default:
    //         printf("Invalid query type %d!\n", (int)q.type); exit(1);
    // }

    // TODO check if query has a reduction here and do it in this one place
    // if so

    // if (q.reduction == REDUCE_NONE) {

    // } else if (q.reduction == REDUCE_THRESH) {

    // } else if (q.reduction == REDUCE_TOP_K) {

    // } else {
    //     printf("Unsupported reduction %d!\n", (int)q.reduction);
    //     exit(1);
    // }
    // return QueryResult{}; // can't happen, in theory
    printf("XXX returning empty QueryResult!\n");
    return std::unique_ptr<QueryResult>(new QueryResult()); // can't happen, in theory
}

} // namespace lzbench

#endif // QUERY_HPP
