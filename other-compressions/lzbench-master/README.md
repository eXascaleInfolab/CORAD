Introduction
-------------------------

lzbench is an in-memory benchmark of open-source LZ77/LZSS/LZMA compressors. It joins all compressors into a single executable.
At the beginning an input file is read to memory.
Then all compressors are used to compress and decompress the file and decompressed file is verified.
This approach has a big advantage of using the same compiler with the same optimizations for all compressors.
The disadvantage is that it requires source code of each compressor (therefore Slug or lzturbo are not included).

This is a fork of the [original lzbench](https://github.com/inikep/lzbench) with added functionality. In particular, it allows integrated [double-]delta coding and execution of simple queries after decompression.

<!-- |Status   |
|---------|
| [![Build Status][travisMasterBadge]][travisLink] [![Build status][AppveyorMasterBadge]][AppveyorLink]  |

[travisMasterBadge]: https://travis-ci.org/inikep/lzbench.svg?branch=master "Continuous Integration test suite"
[travisLink]: https://travis-ci.org/inikep/lzbench
[AppveyorMasterBadge]: https://ci.appveyor.com/api/projects/status/u7kjj8ino4gww40v/branch/master?svg=true "Visual test suite"
[AppveyorLink]: https://ci.appveyor.com/project/inikep/lzbench
 -->

Usage
-------------------------

```
usage: lzbench [options] input [input2] [input3]

```

| Flag | Example | Effect |
| ---- | ---- | ---- |
| `-a` | `-azstd,1,3/lz4` | Compression algorithms to use. Compression levels to use are separated by commas, and algorithms are separated by slashes. If an algorithm allows multiple compression levels and not are specified, all levels will be used in succession. |
| `-b` | `-b512` | Input is split into blocks of at most 512KB. Default = min(filesize,1747626 KB) |
| `-c` | `-c6` | Treat data as having 6 columns (so every 6th value represents the same attribute/variable). Only needed when running queries |
| `-d` | `-d3` | Add delta coding as a preprocessor with a lag of 3 values. I.e., replace each value $x_i$ with $x_i - x_{i-3}$ before compressing. Preprocessing time is included in speed calculations. |
| `-D` | `-D3` | Like previous but with double delta coding. I.e., replace $x_i$ with $x_i - 2x_{i-3} + x_{i-6}$ |
| `-e` | `-e2` | Set the size of each element to two bytes. This would cause, e.g., delta coding to operate on 16 bit values. Default is 1 (8 bits). |
| `-f` | `-f3` | Like delta and double delta coding, but uses the Sprintz's FIRE forecaster instead. |
| `-i` | `-i0,10` | Run at least 0 compression iterations and 10 decompression iterations. Each iteration runs through all the data. |
| `-j` | `-j` | Joins all data to be compressed in memory before compressing it. I.e., copies it all to one contiguous buffer. Blocks always align on the boundaries between files, however, so each file is compressed independently. Default is not copying. |
| `-m` | `-m512` | Set memory limit to 512MB. Default is no limit. |
| `-o` | `-o4` | Set output format. 1=Markdown, 2=text, 3=text+origSize, 4=CSV (default = 2) |
| `-p` | -p2 | print time for all iterations: 1=fastest 2=average 3=median (default = 1) |
| `-q` | -q2 | Set query to run on the data in each decompression iteration after decompressing it. 0 = no query, 1 = mean of each column, 2 = min of each column, 3 = max of each column (default = 0). Use the "materialized" codec (-amaterialized) to time queries with no decompression. |
| `-r` | `-r` | Whether to traverse directories recursively when finding files to compress. |
| `-s` | `-s100` | Use only compressors with compression speed over 100 MB (default = 0 MB) |
| `-S` | `-s` | Storage order. Only relevant for queries. 0 = row-major, 1 = column-major |
| `-t` | `-t3,5` | Run compression iterations for at least 3 seconds and decompression iterations for at least 5 seconds. |
| `-U` | `-U` | Unverified. By default, the benchmark checks that the decompressor's output matches the compressor's input. Use this to disable this behavior. |
| `-v` | `-v5` | Verbosity level. Default is 0. |
| `-z` | `-z` | Show times instead of throughputs. |


Example usage:
```
  lzbench -azstd filename  # selects all levels of zstd
  lzbench -abrotli,2,5/zstd filename  # selects levels 2 & 5 of brotli and zstd
  lzbench -t3,5 filename  # 3 sec compression and 5 sec decompression loops
  lzbench -t0,0 -i3,5 -azstd filename  # 3 compression and 5 decompression iters
```

Compilation
-------------------------

The preferred method of building and running this code is using Docker:

```
$ docker build --tag=lzb . && docker run -it lzb
```

Because debugging errors in other people's compression libraries on other people's machines is not something I have time for, I will only support errors / build issues encountered while using Docker.


If you want to do something more customized on your own, however, see below.


For Linux/MacOS/MinGW (Windows):
```
make
```

For 32-bit compilation:
```
make BUILD_ARCH=32-bit

```

To remove one of compressors you can add `-DBENCH_REMOVE_XXX` to `DEFINES` in Makefile (e.g. `DEFINES += -DBENCH_REMOVE_LZ4` to remove LZ4).
You also have to remove corresponding `*.o` files (e.g. `lz4/lz4.o` and `lz4/lz4hc.o`).

lzbench was tested with:
- Ubuntu: gcc 4.6.3, 4.8.4 (both 32-bit and 64-bit), 4.9.3, 5.3.0, 6.1.1 and clang 3.4, 3.5, 3.6, 3.8
- MacOS: Apple LLVM version 6.0
- MinGW (Windows): gcc 5.3.0, 4.9.3 (32-bit), 4.8.3 (32-bit)


Supported compressors
-------------------------
**Warning**: some of the compressors listed here have security issues and/or are
no longer maintained.  For information about the security of the various compressors,
see the [CompFuzz Results](https://github.com/nemequ/compfuzz/wiki/Results) page.
```
blosclz 2015-11-10
brieflz 1.1.0
brotli 2017-03-10
crush 1.0
csc 2016-10-13 (WARNING: it can throw SEGFAULT compiled with Apple LLVM version 7.3.0 (clang-703.0.31))
density 0.12.5 beta (WARNING: it contains bugs (shortened decompressed output))
fastlz 0.1
gipfeli 2016-07-13
glza 0.8
libdeflate v0.7
lizard v1.0 (formerly lz5)
lz4/lz4hc v1.7.5
lzf 3.6
lzfse/lzvn 2017-03-08
lzg 1.0.8
lzham 1.0
lzjb 2010
lzlib 1.8
lzma v16.04
lzmat 1.01 (WARNING: it contains bugs (decompression error; returns 0); it can throw SEGFAULT compiled with gcc 4.9+ -O3)
lzo 2.09
lzrw 15-Jul-1991
lzsse 2016-05-14
pithy 2011-12-24 (WARNING: it contains bugs (decompression error; returns 0))
quicklz 1.5.0
shrinker 0.1 (WARNING: it can throw SEGFAULT compiled with gcc 4.9+ -O3)
slz 1.0.0 (only a compressor, uses zlib for decompression)
sprintz 0.0
snappy 1.1.4
tornado 0.6a
ucl 1.03
wflz 2015-09-16 (WARNING: it can throw SEGFAULT compiled with gcc 4.9+ -O3)
xpack 2016-06-02
xz 5.2.3
yalz77 2015-09-19
yappy 2014-03-22 (WARNING: fails to decompress properly on ARM)
zlib 1.2.11
zling 2016-04-10 (according to the author using libzling in a production environment is not a good idea)
zstd 1.1.4
```


Adding a new compressor
-------------------------

If you have another compressor that you would like to add to lzbench, this can be done as follows:

 1. Add all the relevant code in some subdirectory.
 1. Go to `_lzbench/lzbench.h`
    1. Increment `LZBENCH_COMPRESSOR_COUNT` (around line 140)
    1. Add the relevant info in the array `comp_desc`. The fields are described in the struct immediately above it (`compressor_desc_t`).
        1. name and version are self explanatory
        1. First and last level refer to levels of compression. By convention, higher levels mean more compression.
        1. `additional_param` is another (optional) argument that gets passed to the compression and decompression functions you will provide below.
        1. `max_block_size`; lzbench splits the data into chunks, each of which it passes to the compressor/decompressor independently. This parameter limits how large the chunks can be.
        1. `compress` and `decompress` need to be pointers to functions matching the signatures immediately above the struct definition. Note that these should be wrapper functions (which we'll define in a moment), not your actual compression and decompression functions.
        1. The same is true for `init` and `deinit`, though these can be `NULL`.
    1. Optionally, add an alias to the `alias_desc` array below and increment `LZBENCH_ALIASES_COUNT`.
 1. Go to `_lzbench/compressors.h` and add in an `ifdef` block declaring the functions you specified in the `comp_desc` array.
 1. Go to `_lzbench/compressors.cpp` and add in an `ifdef` block defining these functions, presumably by calling your own compressor's top-level compress and decompress functions. Note that you should only `#include` your header within this `ifdef`.

 1. Go to the Makefile. Add in a variable containing all the .o files your compressor needs. Then add this variable to the list under the `lzbench` target.
    1. If you need special flags, add a custom rule above this build rule, copying the (simple) structure used by other such rules.


See the `example_compressor` directory, and the associated `example_compress`, `example_decompress`, and other functions, for a minimal working example.
