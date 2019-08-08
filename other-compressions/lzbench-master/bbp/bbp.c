#include <arpa/inet.h>

#include "coding.h"
#include "bitstream.h"
#include "bitpacking.h"

#define DEFAULT_BLOCK_SIZE 16
#define DEFAULT_BLOCK_SIZE_S 32

#define HEADER_SIZE 64

#define MAGIC 325498741

#define HP_MAGIC       0 //magic
#define HP_SIZE        1 //uncompressed size == b.len
#define HP_SIZE_C      2 //full compressed size (including header signals etc.)
#define HP_MODES       3 //compression modes ->also determines positions for coder/decoder NOTE: high 16bit are unused atm.
#define HP_OFFSET      4 //offset for b
#define HP_BLOCK_SIZES 5 //offset for b
#define HP_B_SIZE_C    6 //compressed size for first stage block data

static inline void header_write(uint8_t *buf, Block_Coder_Data *b, Block_Coder_Data *s, uint32_t input_size, uint32_t compressed_size)
{
  int mode_b = 0, mode_s = 0;
  int bs = 0, bs_s = 0;
  uint32_t *header = (uint32_t*)buf;

  memset(buf, 0, HEADER_SIZE);

  if (b) {
    mode_b = b->coder;
    assert(b->block_size);
    bs = __builtin_ctz(b->block_size);
  }
  if (s) {
    mode_s = s->coder;
    assert(s->block_size);
    bs_s = __builtin_ctz(s->block_size);
  }

  //MAGIC
  header[HP_MAGIC] = htonl((uint32_t)MAGIC);
  header[HP_SIZE] = htonl((uint32_t)input_size);
  header[HP_SIZE_C] = htonl((uint32_t)compressed_size);
  header[HP_MODES] = htonl((uint32_t)(mode_b+256*mode_s));
  header[HP_OFFSET] = htonl((uint32_t)b->offset);
  header[HP_BLOCK_SIZES] = htonl((uint32_t)(bs+bs_s*65536));
  header[HP_B_SIZE_C] = htonl((uint32_t)b->len_c);
}

void header_read(uint8_t *buf, Block_Coder_Data *b, Block_Coder_Data *s, uint32_t *size, uint32_t *size_c)
{
  uint32_t *header = (uint32_t*)buf;

  //MAGIC
  assert(header[HP_MAGIC] == htonl((uint32_t)MAGIC));
  *size = ntohl(header[HP_SIZE]);
  b->len = *size;
  *size_c = ntohl(header[HP_SIZE_C]);
  b->coder = ntohl(header[HP_MODES]) & 0xFF;
  s->coder = (ntohl(header[HP_MODES])/256) & 0xFF;
  b->offset = ntohl(header[HP_OFFSET]);
  s->offset = BBP_ALIGNMENT;
  b->block_size = 1 << (ntohl(header[HP_BLOCK_SIZES]) & 0xFFFF);
  s->block_size = 1 << (ntohl(header[HP_BLOCK_SIZES])/65536);
  b->len_c = ntohl(header[HP_B_SIZE_C]);
}

void bbp_init(void)
{
  if (inits_count) {
    inits_count++;
    return;
  }

  init_masks();
  lut = get_wrap_lut();
  lut_inv = get_wrap_lut_inv();
  clz_lut = get_clz_lut();

  inits_count++;
}

void bbp_shutdown(void)
{
  inits_count--;

  if (inits_count)
    return;

  free(lut);
  free(lut_inv);
  free(clz_lut);
}

int bbp_code_offset(uint8_t *in, uint8_t *out, int bs, int bs_r, int len, int offset)
{
  int recursive;
  Block_Coder_Data b;
  Block_Coder_Data s;
  int len_c;
  int b_s_len;

  memset(&b, 0, sizeof(b));
  memset(&s, 0, sizeof(b));

  assert(len);
  assert(inits_count);
#ifdef BBP_USE_SIMD
  assert(!((uintptr_t)in % BBP_ALIGNMENT));
  assert(!((uintptr_t)out % BBP_ALIGNMENT));
#endif

  if (!bs) bs = DEFAULT_BLOCK_SIZE;
  if (!bs_r) {
    if (bs >= 128)
      bs_r = -1;
    else
      bs_r = DEFAULT_BLOCK_SIZE_S;
  }

  if (bs_r < 0)
    recursive = 0;
  else
    recursive = 1;

  b.block_size = bs;
  b.len = len;
  b.coder = CODER_OFFSET;
  b.offset = offset;

  b_s_len = offset_calc_signal_len(&b);

  if (recursive && b_s_len) {
    b.signal_buf = (uint8_t*)malloc(len/bs);
    b.block_buf = out + HEADER_SIZE;
  }
  else {
    b.signal_buf = out+HEADER_SIZE;
    b.block_buf = b.signal_buf+RU_N(b_s_len, BBP_ALIGNMENT);
  }

  code(&b, in, len);

  //remove or commen out?
  assert(b.cur_block_free_bits == 8);
  assert((b.cur_block-out)%BBP_ALIGNMENT == 0);
  assert(signal_len(&b) <= len/bs);
  assert(signal_len(&b) == offset_calc_signal_len(&b));

  if (b_s_len && recursive) {
    s.block_size = bs_r;
    s.len = signal_len(&b);
    s.coder = CODER_OFFSET;
    s.offset = BBP_ALIGNMENT;
    s.signal_buf = out+HEADER_SIZE+b.len_c;
    s.block_buf = s.signal_buf + RU_N(offset_calc_signal_len(&s), BBP_ALIGNMENT);

    code(&s, b.signal_buf, signal_len(&b));
    free(b.signal_buf);

    len_c = s.cur_block-out;
    header_write(out, &b, &s, len, len_c);
  }
  else {
    len_c = HEADER_SIZE+RU_N(b_s_len, BBP_ALIGNMENT)+b.len_c;
    header_write(out, &b, NULL, len, len_c);
  }


  assert(len_c % 16 == 0);

  //printf("comp size: %d-%d\n", len_c, b.len_c);
  //printf("enc positions: %d %d %d\n", b.block_buf-out, s.block_buf-out, s.signal_buf-out);

  return len_c;
}

void bbp_header_sizes(uint8_t *buf, uint32_t *size, uint32_t *size_c)
{
  Block_Coder_Data b, s;
  header_read(buf, &b, &s, size, size_c);
}

int bbp_decode(uint8_t *in, uint8_t *out)
{
  int b_s_len;
  uint32_t size, size_c;
  Block_Coder_Data b;
  Block_Coder_Data s;

  assert(in);
  assert(out);
#ifdef BBP_USE_SIMD
  assert(!((uintptr_t)in % 16));
  assert(!((uintptr_t)out % 16));
#endif

  printf("about to call header_read\n");

  //determines block_size(s), coder(s), offset(s), b->len_c and b->len
  header_read(in, &b, &s, &size, &size_c);

  b_s_len = offset_calc_signal_len(&b);
  //printf("decode s len: %d\n", b_s_len);
  if (b_s_len) {
    s.len = offset_calc_signal_len(&b);
    s.signal_buf = in+HEADER_SIZE+b.len_c;
    s.data_buf = (uint8_t*)malloc(b_s_len); //for decoded signal of b
    assert(s.data_buf);
    //offset_calc_signal_len needs offset, block_size and len which are now known
    s.block_buf = s.signal_buf + RU_N(offset_calc_signal_len(&s), BBP_ALIGNMENT);
  }

  b.signal_buf = s.data_buf;
  b.block_buf = in + HEADER_SIZE;
  b.data_buf = out;

  //printf("dec positions: %d %d %d\n", b.block_buf-in, s.block_buf-in, s.signal_buf-in);

  printf("about to call decode\n");

  if (b_s_len) {
    //printf("decode signal len: %d\n", b_s_len);
    decode(&s);
    /*int i;
    for(i=0;i<b_s_len;i++)
      printf("%d ", b.signal_buf[i]);
    printf("\n");*/
  }
  //printf("decode block len: %d\n", b.len);
  decode(&b);

  assert(b.cur_data-b.data_buf == size);

  if (b_s_len)
    free(s.data_buf);

  return size;
}


uint32_t bbp_max_compressed_size(uint32_t uncompressed)
{
  return uncompressed+uncompressed/4+64+64;
}
