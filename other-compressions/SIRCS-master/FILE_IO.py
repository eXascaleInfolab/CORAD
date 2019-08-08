from AHC import AHCOM
from AHC import AHDECOM
import numpy as np
import pandas as pd
import matplotlib as plt
import random
import itertools
from collections import OrderedDict
import math
import os
from prettytable import PrettyTable
from decimal import Decimal
import sys

class FILE():  
    def __init__(self, openPathName, savePath):
        self.openPathName = openPathName
        self.savePath = savePath
        
    """
    Round the number to reduce memory 
    """
    def round_decimal(self, number, decimal):
        if(decimal == 0):
            approx = int(number)
        else:
            if(round(Decimal(number),decimal - 1) == round(Decimal(number),decimal)):
                if((decimal - 1) == 0):
                    approx = int(round(Decimal(number),decimal-1))
                else:
                    approx = self.round_decimal(number, decimal - 1)
            else:
                approx = float(round(Decimal(number),decimal))
        return approx     

          
    def write_compressed_file(self, compressedList, savefile, decimal):
        tcf = 0
        f= open(self.savePath + "text_" + savefile,"w+")
        counter = 0;
        for i in compressedList:
            if (i[0] == '?'):
                for d in i:                  
                    approx = d  
                    f.write("%s" % approx + ' ')
                f.write("\n")                    
            else:
                for d in i:                  
                    if (type(d) == str):
                        approx = d
                    else:
                        d = float(d)
                        approx = self.round_decimal(d, decimal) 
                    f.write("%s" % approx + ' ')
                f.write("\n")
        f.close()
        #get the text file size
        tcf = os.path.getsize(self.savePath + "text_" + savefile)
        #text+savefile is the readable file, whil savefile is the final compressed file using huffman coding.
        huffc = AHCOM(self.savePath + "text_" + savefile, self.savePath + savefile)
        huffc.exe_huffman_compression()  
        #os.remove(self.savePath + "text_" + savefile)
        return tcf
        
    def read_decompress_file(self, filename):
        huffd = AHDECOM(self.openPathName, self.savePath + "text_" + filename)
        huffd.exe_huffman_decompression()          
        f=open(self.savePath + "text_" + filename, "r")
        counter = 0
        collection = []
        value = []
        for line in f:
            line = line.replace('\n',' ')
            collect = []
            temp = list(line.split(' '))
            temp=list(filter(('').__ne__, temp))
            for c in temp:
                collect.append((c))
            if (collect != []):
                value.append(collect) 
            counter += 1
        collection += value
        #os.remove(self.savePath + "text_" + filename)
        return collection
    
    def write_in_csv(self, dataFrame, filename):
        df = dataFrame
        for column in df.columns:
            for idx in df[column].index:
                x = df.at[idx,column]
                try:
                    x = x if type(x) == str else str(x).encode('utf-8','ignore').decode('utf-8','ignore')
                    df.at[idx,column] = x
                except Exception:
                    print('encoding error: {0} {1}'.format(idx,column))
                    df.at[idx,column] = ''
                    continue
        df.to_csv(self.savePath + filename, index=False)
        
    def write_decompress_in_csv(self, recoveredDict, timeString, nameDict):
        header = ['time', 'power (W)']
        for key in recoveredDict:
            csvList = []
            for i in range(len(timeString)):
                csvList.append((timeString[i], recoveredDict[key][i]))
                df = pd.DataFrame.from_records(csvList, columns=header)
            self.write_in_csv(df, nameDict[key])


