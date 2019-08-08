import APCA
import SWING
from GAMPS import *
from SIRCS import *
from FILE_IO import *
from eva import *
import time
import numpy as np
import pandas as pd
import matplotlib
import os
import math
import sys

"""
Data compression
Output: 
1. key list containing all index for entering corresponding position in data dictionary
2. data dictionary with name of the building, mapped with data value and normalized coefficient
"""
def apca_compress(keyList, dataDict, fileNameDict, dataLength, timeIndex, espmax, savetopath, openFileName, timeRange, totalSize):
    decimal = 0
    file = FILE(openFileName, savetopath)
    aggregatedBase = [timeRange]
    tcf = 0
    tof = totalSize
    start = end = 0
    SE = dataSize = 0
    Time = 0
    scale = 0  
    MIN = 0
    MAX = 0
    for group in range(len(dataLength)):
        aggregatedBase.append(['!'])
        com = APCA.APCACOM(dataDict[group], keyList, dataLength[group], espmax)
        for name in dataDict[group]:
            
            Name = str(name)
            start = time.time()
            #compression
            
            basePackage = com.APCA_normal_compression(dataDict[group][Name][0], dataDict[group][Name][1])
            rawBase = dataDict[group][Name][0]
            compressedBase = basePackage[0]
            
            #start of evaluation
            ################################################################################################################            
            APCAbase = basePackage[1] 
            end = time.time()
            Time += computational_time(start, end)
            #evaluation
            baseExpand = APCAbase
            #boundary
            error = APCA_normal_target_diagnosis(baseExpand, dataDict[group][Name][0], dataDict[group][Name][1], espmax)
            if(len(error) != 0):
                print("APCA Error Violation Warning (base)\n")
            #Compute RMSE
            rmsePackage = RMSE(dataDict[group][Name][0], baseExpand)
            SE += rmsePackage[1]
            dataSize += rmsePackage[2]  
            minValue = rmsePackage[3] 
            maxValue = rmsePackage[4]
            if(minValue < MIN):
                MIN = minValue
            if(maxValue > MAX):
                MAX = maxValue
            #end of evaluation
            ################################################################################################################
            
            #insert the file name
            compressedBase.insert(0, [name, fileNameDict[name]])
            #The whole file containing everythin
            aggregatedBase += compressedBase
            
          
    #write the compressed file
    tcf = file.write_compressed_file(aggregatedBase, "apca_compressed.txt", decimal)
    
    #compression ratio
    #RMSE
    scale = (MAX - MIN) / 100
    totalRMSE = math.sqrt(SE / dataSize) / scale   
    totalRatio = tof / tcf 
    return [totalRatio, totalRMSE, Time]

def swing_compress(keyList, dataDict, fileNameDict, dataLength, timeIndex, espmax, savetopath, openFileName, timeRange, totalSize):
    decimal = 0
    tcf = 0
    tof = totalSize
    start = end = 0
    SE = dataSize = 0
    Time = 0
    scale = 0 
    MIN = 0
    MAX = 0    
    file = FILE(openFileName, savetopath)
    aggregatedBase = [timeRange]
    for group in range(len(dataLength)):
        aggregatedBase.append(['!'])
        com = SWING.SWINGCOM(dataDict[group], keyList, dataLength[group], espmax)
        for name in dataDict[group]:
            Name = str(name)
            #compression
            start = time.time()
            basePackage = com.SWING_normal_base_compression(dataDict[group][Name][0],dataDict[group][Name][1])
            rawBase = dataDict[group][Name][0]
            compressedBase = basePackage[0]
            
            ################################################################################################################
            #start of evaluation
            SWINGbase = basePackage[1] 
            end = time.time()
            Time += computational_time(start, end)
            #evaluation
            baseExpand = SWINGbase
            #boundary
            error = APCA_normal_target_diagnosis(baseExpand, dataDict[group][Name][0], dataDict[group][Name][1], espmax)
            if(len(error) != 0):
                print("Swing Error Violation Warning (base)\n")
            #Compute RMSE
            rmsePackage = RMSE(dataDict[group][Name][0], baseExpand)
            SE += rmsePackage[1]
            dataSize += rmsePackage[2]  
            minValue = rmsePackage[3] 
            maxValue = rmsePackage[4]
            if(minValue < MIN):
                MIN = minValue
            if(maxValue > MAX):
                MAX = maxValue            
            #end of evaluation
            ################################################################################################################
            
            #insert the file name
            compressedBase.insert(0, [name, fileNameDict[name]])
            #The whole file containing everythin
            
            aggregatedBase += compressedBase
            
    #write the compressed file
    tcf = file.write_compressed_file(aggregatedBase, "swing_compressed.txt", decimal)
    
    #compression ratio
    #RMSE
    scale = (MAX - MIN) / 100
    totalRMSE = math.sqrt(SE / dataSize) / scale   
    totalRatio = tof / tcf   
    return [totalRatio, totalRMSE, Time]

def gamps_compress(keyList, dataDict, fileNameDict, dataLength, timeIndex, espmax, savetopath, openFileName, timeRange, totalSize):
    decimal = 5
    c = 0.4
    tcf = 0
    tof = totalSize
    start = end = 0
    SE = dataSize = 0
    Time = 0
    scale = 0 
    MIN = 0
    MAX = 0    
    #1. time range 
    file = FILE(openFileName, savetopath)
    aggregatedBase = [timeRange]
    for group in range(len(dataLength)):
        start = time.time()
        com = GAMPSCOM(dataDict[group], keyList, dataLength[group], c, espmax, decimal)
        #load the time index
        List = com.stat_grouping(1)
        end = time.time()
        
        Time += computational_time(start, end)
        #ratio index show who is ratio and who is base
        RatioOrBase = List[1]
        BaseList = List[2]
        RatioList = List[3] 
        #load the cluster sequencing index
        index = []
        for key in RatioOrBase:
            index.append(RatioOrBase[key])
        #2. group and index 
        aggregatedBase.append(['!'] + index)
        
        
        #ratio signal list
        for name in RatioList:
            Name = str(name)
            compressedRatio = RatioList[name]           
            #start of evaluation
            ################################################################################################################
            ratioExpand = APCA_Ratio_recover(RatioList[name], BaseList[RatioOrBase[name]])
            #boundary
            error = APCA_normal_target_diagnosis(ratioExpand, dataDict[group][Name][0], dataDict[group][Name][1], espmax)
            if(len(error) != 0):
                print("GAMPS Error Violation Warning (ratio)\n")
            #Compute RMSE
            rmsePackage = RMSE(dataDict[group][Name][0], ratioExpand)
            SE += rmsePackage[1]
            dataSize += rmsePackage[2]
            minValue = rmsePackage[3] 
            maxValue = rmsePackage[4]
            if(minValue < MIN):
                MIN = minValue
            if(maxValue > MAX):
                MAX = maxValue            
            #end of evaluation
            ################################################################################################################
            
            #insert the file name
            compressedRatio.insert(0, [name, fileNameDict[str(name)]]) 
            #The whole file containing everythin
            aggregatedBase += compressedRatio
            
        #base signal list   
        for name in BaseList:
            Name = str(name)
            compressedBase = BaseList[name]
            
            #start of evaluation
            ################################################################################################################            
            baseExpand = APCA_Base_recover(BaseList[name])
            #print(baseExpand)
            #boundary
            error = APCA_normal_target_diagnosis(baseExpand, dataDict[group][Name][0], dataDict[group][Name][1], espmax)
            if(len(error) != 0):
                print("GAMPS Error Violation Warning (base)\n")
            #Compute RMSE
            rmsePackage = RMSE(dataDict[group][Name][0], baseExpand)
            SE += rmsePackage[1]
            dataSize += rmsePackage[2] 
            minValue = rmsePackage[3] 
            maxValue = rmsePackage[4]
            if(minValue < MIN):
                MIN = minValue
            if(maxValue > MAX):
                MAX = maxValue            
            #end of evaluation
            ################################################################################################################
            
            #3. compressed content
            #insert the file name
            compressedBase.insert(0, [name, fileNameDict[Name]])        
            #The whole file containing everythin
            aggregatedBase += compressedBase 
            
        
        
    #write the compressed file
    tcf = file.write_compressed_file(aggregatedBase, "gamps_compressed.txt", decimal)
    
    #compression ratio
    #RMSE
    scale = (MAX - MIN) / 100
    totalRMSE = math.sqrt(SE / dataSize) / scale  
    totalRatio = tof / tcf
    return [totalRatio, totalRMSE, Time]
    



def sircs_apca_compress(keyList, dataDict, rawBaseDict, fileNameDict, dataLength, timeIndex, espmax, savetopath, openFileName, timeRange, totalSize):
    tcf = 0
    tof = totalSize
    start = end = 0
    SE = dataSize = 0
    Time = 0
    scale = 0 
    MIN = 0
    MAX = 0    
    decimal = 0
    c = 1
    #1. time range 
    file = FILE(openFileName, savetopath)
    aggregatedBase = [timeRange]
    for group in range(len(dataLength)): 
        start = time.time()
        com = SIRCSCOM(dataDict[group], rawBaseDict[group], keyList, dataLength[group], espmax, decimal)
        #load the time index
        List = com.sircs_apca_compression(c)
        end = time.time()
        Time += computational_time(start, end)         
        #ratio index show who is ratio and who is base
        startBit = List[0]
        slopeRecorder = List[1]
        interceptRecorder = List[2] 
        compressedList = List[3] 
        APCAList = List[4]
        #2. tree
        aggregatedBase.append(startBit)
        slope = ['?']
        intercept = ['?']
        for key in keyList:
            slope.append(slopeRecorder[key])
            intercept.append(interceptRecorder[key])
        #3. slope and intercept
        aggregatedBase.append(slope)
        aggregatedBase.append(intercept)


        #4. signal dictionary  
        for name in compressedList:
            Name = str(name)
            compressed = compressedList[name]

            #start of evaluation
            ################################################################################################################
            baseExpand = APCAList[name]            
            #boundary
            error = APCA_normal_target_diagnosis(baseExpand, dataDict[group][Name][0], dataDict[group][Name][1], espmax)
            if(len(error) != 0):
                print("SIRCSAPCA Error Violation Warning (base)\n")
            #Compute RMSE
            rmsePackage = RMSE(dataDict[group][Name][0], baseExpand)
            SE += rmsePackage[1]
            dataSize += rmsePackage[2]   
            minValue = rmsePackage[3] 
            maxValue = rmsePackage[4]
            if(minValue < MIN):
                MIN = minValue
            if(maxValue > MAX):
                MAX = maxValue            
            #end of evaluation
            ################################################################################################################               
        
            #3. compressed content
            #insert the file name
            compressed.insert(0, [name, fileNameDict[name]])        
            #The whole file containing everythin
            aggregatedBase += compressed            

    #write the compressed file
    tcf = file.write_compressed_file(aggregatedBase, "sircsapca_compressed.txt", decimal)   
    #compression ratio
    #RMSE
    scale = (MAX - MIN) / 100
    totalRMSE = math.sqrt(SE / dataSize) / scale  
    totalRatio = tof / tcf   
    return [totalRatio, totalRMSE, Time]

def sircs_swing_compress(keyList, dataDict, rawBaseDict, fileNameDict, dataLength, timeIndex, espmax, savetopath, openFileName, timeRange, totalSize):
    tcf = 0
    tof = totalSize
    start = end = 0
    SE = dataSize = 0
    Time = 0
    scale = 0 
    decimal = 0
    c = 1
    MIN = 0
    MAX = 0    
    #1. time range 
    file = FILE(openFileName, savetopath)
    aggregatedBase = [timeRange]
    for group in range(len(dataLength)):  
        start = time.time()
        com = SIRCSCOM(dataDict[group], rawBaseDict[group], keyList, dataLength[group], espmax, decimal)
        #load the time index
        List = com.sircs_swing_compression(c)
        end = time.time()
        Time += computational_time(start, end)          
        #ratio index show who is ratio and who is base
        startBit = List[0]
        slopeRecorder = List[1]
        interceptRecorder = List[2] 
        compressedList = List[3] 
        APCAList = List[4]
        #2. tree
        aggregatedBase.append(startBit)
        slope = ['?']
        intercept = ['?']
        for key in keyList:
            slope.append(slopeRecorder[key])
            intercept.append(interceptRecorder[key])
        #3. slope and intercept
        aggregatedBase.append(slope)
        aggregatedBase.append(intercept)
        

        #4. signal dictionary  
        for name in compressedList:
            Name = str(name)
            compressed = compressedList[name]

            #start of evaluation
            ################################################################################################################
            baseExpand = APCAList[name]            
            #boundary
            error = APCA_normal_target_diagnosis(baseExpand, dataDict[group][Name][0], dataDict[group][Name][1], espmax)
            if(len(error) != 0):
                print("SIRCSAPCA Error Violation Warning (base)\n")
            #Compute RMSE
            rmsePackage = RMSE(dataDict[group][Name][0], baseExpand)
            SE += rmsePackage[1]
            dataSize += rmsePackage[2] 
            minValue = rmsePackage[3] 
            maxValue = rmsePackage[4]
            if(minValue < MIN):
                MIN = minValue
            if(maxValue > MAX):
                MAX = maxValue            
            #end of evaluation
            ################################################################################################################               
        
            #3. compressed content
            #insert the file name
            compressed.insert(0, [name, fileNameDict[name]])        
            #The whole file containing everythin
            aggregatedBase += compressed           
    #write the compressed file
    tcf = file.write_compressed_file(aggregatedBase, "sircsswing_compressed.txt", decimal)   
    #compression ratio
    #RMSE
    scale = (MAX - MIN) / 100
    totalRMSE = math.sqrt(SE / dataSize) / scale  
    totalRatio = tof / tcf  
    return [totalRatio, totalRMSE, Time]







"""
decompression
"""
def apca_decompress(savetopath, openFileName):  
    file = FILE(openFileName, savetopath) 
    fileName = openFileName.split('/')[-1]
    compressedList = file.read_decompress_file(fileName) 
    decom = APCA.APCADECOM(compressedList)
    package = decom.apca_decompression()
    file.write_decompress_in_csv(package[0], package[1], package[2])
    
def swing_decompress(savetopath, openFileName):  
    file = FILE(openFileName, savetopath) 
    fileName = openFileName.split('/')[-1]
    compressedList = file.read_decompress_file(fileName) 
    decom = SWING.SWINGDECOM(compressedList)
    package = decom.swing_decompression()
    file.write_decompress_in_csv(package[0], package[1], package[2])

def gamps_decompress(savetopath, openFileName):  
    file = FILE(openFileName, savetopath) 
    fileName = openFileName.split('/')[-1]
    compressedList = file.read_decompress_file(fileName) 
    decom = GAMPSDECOM(compressedList)
    package = decom.gamps_decompression()
    file.write_decompress_in_csv(package[0], package[1], package[2])

def sircs_apca_decompress(savetopath, openFileName):  
    file = FILE(openFileName, savetopath) 
    fileName = openFileName.split('/')[-1]
    compressedList = file.read_decompress_file(fileName) 
    decom = SIRCSDECOM(compressedList)
    package = decom.sircs_apca_decompression()
    file.write_decompress_in_csv(package[0], package[1], package[2])


def sircs_swing_decompress(savetopath, openFileName):  
    file = FILE(openFileName, savetopath) 
    fileName = openFileName.split('/')[-1]
    compressedList = file.read_decompress_file(fileName) 
    decom = SIRCSDECOM(compressedList)
    package = decom.sircs_swing_decompression()
    file.write_decompress_in_csv(package[0], package[1], package[2])






