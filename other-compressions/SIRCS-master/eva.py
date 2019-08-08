import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import random
import itertools
from collections import OrderedDict
import math
import os
from prettytable import PrettyTable
from decimal import Decimal
import sys



    
"""
Round the number to reduce memory 
"""
def round_decimal(number, decimal):
    if(decimal == 0):
        approx = number
    else:
        if(round(Decimal(number),decimal - 1) == round(Decimal(number),decimal)):
            if((decimal - 1) == 0):
                approx = int(round(Decimal(number),decimal-1))
            else:
                approx = round_decimal(number, decimal - 1)
        else:
            approx = float(round(Decimal(number),decimal))
    return approx     
        
def write_in_csv(dataFrame, filename):
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
    df.to_csv(filename)     
    
def RMSE(original, compressed):
    npo = original
    npc = compressed
    se = 0
    rmse = 0
    dataSize = len(original)

    for i in range(dataSize):
        inputValue = float(npo[i])
        approxValue = float(npc[i])
        error = approxValue - inputValue
        error = pow(error,2)
        se = se + error
    rmse = math.sqrt(se / dataSize)
    #Normalize RMSE with respect to data range
    maxValue = max(npo)
    minValue = min(npo)
    result = 0
    return [result, se, dataSize, minValue, maxValue]


def get_compress_ratio(baseList, compressedList, decimal):
    APCAsize = ''
    basesize = ''
    for i in compressedList:
        for d in i: 
            if (type(d) == str):
                approx = d
            else:
                approx = round_decimal(d, decimal) 
            APCAsize += str(approx) +' '
        APCAsize += '\n'  
    capAPCA = sys.getsizeof(APCAsize)
    
    for i in baseList:
        basesize += str(i) + '\n'         
    capbase = sys.getsizeof(basesize) 
    ratio = capAPCA / capbase
    return [ratio, capAPCA, capbase]

"""
Calculate the compressed and raw data size in the form of strings, and return the ratio
of the two data size.
Input:
1. the original data list
2. the compressed data list
3. decimal that needs to preserve in the string
Output:
1. compression ratio
2. size of the compressed file
3. size of the raw file
"""
def get_lm_group_compress_ratio(baseList, compressedList, decimal, Type):
    basesize = ''
    #Type 0 for lm
    if (Type == 0):
        APCAsize = str(compressedList[0][0]) + ' ' + str(compressedList[0][1])
        for i in compressedList[1:]:
            for d in i: 
                if (decimal == 0):
                    if(type(d) == str):   
                        approx = d
                    else:
                        approx = int(d)
                else:
                    if(type(d) == str):   
                        approx = d
                    else:
                        approx = round_decimal(float(d), decimal) 
                APCAsize += str(approx) +' '
            APCAsize += '\n' 
    #Type 1 for base
    elif(Type == 1):
        APCAsize = ''
        for i in compressedList:
            for d in i: 
                if (decimal == 0):
                    if(type(d) == str):   
                        approx = d
                    else:
                        approx = int(d)
                else:
                    if(type(d) == str):   
                        approx = d
                    else:
                        approx = round_decimal(float(d), decimal) 
                APCAsize += str(approx) +' '
            APCAsize += '\n'                 
    capAPCA = sys.getsizeof(APCAsize)
    for i in baseList:
        basesize += str(i) + '\n'         
    capbase = sys.getsizeof(basesize) 
    ratio = capAPCA / capbase
    return [ratio, capAPCA, capbase] 

def computational_time(startTime, endTime):
    time = endTime - startTime
    return time

"""
Check if the target signal exceed the boundary or not
This suits the normalized APCA compression
"""    
def APCA_normal_target_diagnosis(APCAsignal, rawSignal, normalize, espmax):
    errorList = []
    maxTolerance = espmax * normalize
    for i in range(len(APCAsignal)):
        if(rawSignal[i] == 0):
            percentage = 0
        else:
            percentage = APCAsignal[i] - rawSignal[i]
        if (percentage <= (maxTolerance)):
            pass
        else:
            errorList.append(str(i) +":" + str(APCAsignal[i]) + "-" + str(rawSignal[i]) + "=" + str(percentage))
    return errorList  


def APCA_Base_recover(compressedList):
    resumeList = []
    #timeIndex = self.decompress_index(compressedList[0])
    for i in compressedList:
        #print(i)
        if (len(i) > 1):
            for a in range(int(i[0])):
                resumeList.append(int(float(i[1])))
        else:
            resumeList.append(int(float(i[0])))    
    return resumeList

def APCA_Ratio_recover(readfileRatio, readfileBase):
    resumeListBase = []
    resumeListRatio = []
    resumeList = []

    #timeIndex = self.decompress_index(compressedList[0])  
    for i in readfileBase:
        #print(i)
        if (len(i) > 1):
            for a in range(int(i[0])):
                resumeListBase.append(float(i[1]))
        else:
            resumeListBase.append(float(i[0]))

    for i in readfileRatio:
        #print(i)
        if (len(i) > 1):
            for a in range(int(i[0])):
                resumeListRatio.append(float(i[1]))
        else:
            resumeListRatio.append(float(i[0])) 
    #print(len(resumeListBase) == len(resumeListRatio))

    for i in range(len(resumeListRatio)):
        temp = int(resumeListBase[i] * resumeListRatio[i])
        resumeList.append(temp)             
    return resumeList