/*
 *
 *  BBP - high speed image compressor using block-wise bitpacking
 *
 *  Copyright (C) 2014-2015 Hendrik Siedelmann <hendrik.siedelmann@googlemail.com>
 *
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 */

#include "bitstream.h"
#include "coding.h"

uint32_t signal_len(Block_Coder_Data *b)
{
  return b->cur_signal - b->signal_buf;
}

uint32_t block_len(Block_Coder_Data *b)
{
  return b->cur_block - b->block_buf+b->block_size;
}

CFINLINE void comp_coder_reset(Block_Coder_Data *b)
{
  //sets cur_block/signal
  b->cur_block = b->block_buf;
  b->cur_signal = b->signal_buf;
  b->cur_block_free_bits = 8;
  b->cur_data = b->data_buf;
  
  b->block_byte_count = 0;
  b->signal_byte_count = 0;
  
  memset(b->cur_block, 0, b->block_size);
  
  b->last = 0;
}


CFINLINE void comp_decoder_reset(Block_Coder_Data *b)
{
  //sets cur_block/signal
  b->cur_block = b->block_buf;
  b->cur_signal = b->signal_buf;
  b->cur_block_free_bits = 8;
  b->cur_data = b->data_buf;
  
  if (b->len >= b->block_size)
    memset(b->cur_data, 0, b->block_size);
  
  b->last = 0;
}