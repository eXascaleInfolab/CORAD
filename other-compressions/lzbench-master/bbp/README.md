Main Page
=========

# Introduction
This is the implementation for the paper "High Speed Lossless Image Compression" [[1]](#f1), see the paper for an overview and evaluation of the compression method.

BBP provides very fast compression for image like data and sequences with very high correlation. Compression is based on delta coding for a specified offset, data rates reach over 6GiB/s, using a single core of an Intel(R) Core(TM) i7-2600 @ 3.40GHz.

\b WARNING: The file format is still subject to change! Experimental use only!

# Installation
> cmake .

> make

and possibly (as root)

> make install

> ldconfig

this will also install the bbp executable which can be used to compress and decompress files using BBP.

# Usage
See bbp.h for the details, library must be intialized with bbp_init() before usage, and shut down with bbp_shutdown() afterwards.
Compression is executed from buffer to buffer with bbp_code_offset() and decoding with bbp_decode().

# Performance


A few examples, using the sintel trailer from https://media.xiph.org/video/derf/y4m/sintel_trailer_2k_480p24.y4m (735MB). All examples on an core i7-860 @ 2.8Ghz

## Fast

    time ./bbp e sintel_trailer_2k_480p24.y4m test.bbp 512 512 854
    compressed at 3760.288MB/s / 1561.830MB/s ratio 2.74
    real    0m0.500s
    user    0m0.193s
    sys     0m0.307s

    time ./bbp d test.bbp test.cmp
    decompressed at 5066.676MB/s / 1555.852MB/s ratio 2.74
    real    0m0.534s
    user    0m0.150s
    sys     0m0.380s

## Medium

    time ./bbp e sintel_trailer_2k_480p24.y4m test.bbp 16 32 854
    compressed at 1338.091MB/s / 943.820MB/s ratio 5.22
    real    0m0.794s
    user    0m0.540s
    sys     0m0.253s

    time ./bbp d test.bbp test.cmp
    decompressed at 1476.182MB/s / 921.617MB/s ratio 5.22
    real    0m0.863s
    user    0m0.500s
    sys     0m0.360s

## Slow

    time ./bbp e sintel_trailer_2k_480p24.y4m test.bbp 8 32 854
    compressed at 955.210MB/s / 736.977MB/s ratio 5.52
    real    0m1.014s
    user    0m0.763s
    sys     0m0.250s

    time ./bbp d test.bbp test.cmp
    decompressed at 1143.277MB/s / 780.014MB/s ratio 5.52
    real    0m1.007s
    user    0m0.647s
    sys     0m0.360s

## LZ4

    time lz4 -f sintel_trailer_2k_480p24.y4m /est.bbp 
    Compressed 770452201 bytes into 223385955 bytes ==> 28.99%                     
    real    0m2.043s
    user    0m1.793s
    sys     0m0.247s

    time lz4 -d -f test.bbp test.cmp 
    Successfully decoded 770452201 bytes                                           
    real    0m0.967s
    user    0m0.643s
    sys     0m0.323s

## LZO

    time lzop -f -o test.bbp sintel_trailer_2k_480p24.y4m
    real    0m1.642s
    user    0m1.467s
    sys     0m0.173s

    time lzop -f -d test.bbp -o test.cmp 
    real    0m1.984s
    user    0m1.703s
    sys     0m0.280s

# A Note on Compilers
The library was tested and developed with gcc on Linux, clang on Mac should also work (but might be broken at any given time). Others are not supported at the moment.

# Coding Style
Code is supposed to be C99, but with some quirks. In many places LTO is used to split implementation from declaration while still keeping inline capability. In such cases we do specify the inline keyword in the header, which provokes warnings by gcc, but not only compiles, but seems to actually be used by gcc for inline decisions when using LTO. Change the CFINLINE define in globals.h header to compare different declarations (example performance: 2468MiB/s vs 2670MiB/s).

<b id="f1">[1]</b> Hendrik Siedelmann, Alexander Wender, Martin Fuchs, High Speed Lossless Image Compression, 37th German Conference on Pattern Recognition, Aachen, Germany, 7-9 September 2015, [http://go.visus.uni-stuttgart.de/hslic](http://go.visus.uni-stuttgart.de/hslic)