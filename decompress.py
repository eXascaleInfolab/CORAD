import pickle
import argparse


parser = argparse.ArgumentParser(description = 'Script for running the decompression')
parser.add_argument('-d', '--dataset', nargs = '?', type = str, help = 'Dataset path', default = 'datasets/20160930_203718-2.csv')
args = parser.parse_args()

with open(args.dataset, 'rb') as pickle_file:
	print(pickle_file)
	data = pickle.load(pickle_file)
	print(data)