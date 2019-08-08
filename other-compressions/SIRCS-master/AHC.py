# 
# Compression application using adaptive Huffman coding
# 
# Usage: python adaptive-huffman-compress.py InputFile OutputFile
# Then use the corresponding adaptive-huffman-decompress.py application to recreate the original input file.
# Note that the application starts with a flat frequency table of 257 symbols (all set to a frequency of 1),
# collects statistics while bytes are being encoded, and regenerates the Huffman code periodically. The
# corresponding decompressor program also starts with a flat frequency table, updates it while bytes are being
# decoded, and regenerates the Huffman code periodically at the exact same points in time. It is by design that
# the compressor and decompressor have synchronized states, so that the data can be decompressed properly.
# 
# Copyright (c) Project Nayuki
# 
# https://www.nayuki.io/page/reference-huffman-coding
# https://github.com/nayuki/Reference-Huffman-coding
# 

import sys
import huffmancoding
python3 = sys.version_info.major >= 3

class AHCOM():
	def __init__(self, inputfile, outputfile):
		self.ipf = open(inputfile, "rb")
		self.opf = huffmancoding.BitOutputStream(open(outputfile, "wb"))
	
	# Command line main application function.
	def exe_huffman_compression(self):
		# Perform file compression
		try:
			self.compress(self.ipf, self.opf)
		finally:
			self.opf.close()
			self.ipf.close()
	
	def is_power_of_2(self,x):
		return x > 0 and x & (x - 1) == 0	
	def compress(self,inp, bitout):
		initfreqs = [1] * 257
		freqs = huffmancoding.FrequencyTable(initfreqs)
		enc = huffmancoding.HuffmanEncoder(bitout)
		enc.codetree = freqs.build_code_tree()  # Don't need to make canonical code because we don't transmit the code tree
		count = 0  # Number of bytes read from the input file
		while True:
			# Read and encode one byte
			symbol = inp.read(1)
			if len(symbol) == 0:
				break
			symbol = symbol[0] if python3 else ord(symbol)
			enc.write(symbol)
			count += 1
			
			# Update the frequency table and possibly the code tree
			freqs.increment(symbol)
			if (count < 262144 and self.is_power_of_2(count)) or count % 262144 == 0:  # Update code tree
				enc.codetree = freqs.build_code_tree()
			if count % 262144 == 0:  # Reset frequency table
				freqs = huffmancoding.FrequencyTable(initfreqs)
		enc.write(256)  # EOF
	
	
	


class AHDECOM():
	def __init__(self, inputfile, outputfile):
		self.ipf =huffmancoding.BitInputStream(open(inputfile, "rb"))
		self.opf = open(outputfile, "wb")	
		
	# Command line main application function.
	def exe_huffman_decompression(self):
		try:
			self.decompress(self.ipf, self.opf)
		finally:
			self.opf.close()
			self.ipf.close()
	
	def is_power_of_2(self, x):
		return x > 0 and x & (x - 1) == 0	
	def decompress(self, bitin, out):
		initfreqs = [1] * 257
		freqs = huffmancoding.FrequencyTable(initfreqs)
		dec = huffmancoding.HuffmanDecoder(bitin)
		dec.codetree = freqs.build_code_tree()  # Use same algorithm as the compressor
		count = 0  # Number of bytes written to the output file
		while True:
			# Decode and write one byte
			symbol = dec.read()
			if symbol == 256:  # EOF symbol
				break
			out.write(bytes((symbol,)) if python3 else chr(symbol))
			count += 1
			
			# Update the frequency table and possibly the code tree
			freqs.increment(symbol)
			if (count < 262144 and self.is_power_of_2(count)) or count % 262144 == 0:  # Update code tree
				dec.codetree = freqs.build_code_tree()
			if count % 262144 == 0:  # Reset frequency table
				freqs = huffmancoding.FrequencyTable(initfreqs)
	
	
		