import numpy as np
import pandas as pd
import matplotlib as plt
import time
import math
import sys
from DATA import *
from decimal import Decimal

class APCACOM():
    """
    Discription: register data information of each single stream. In each file, 
    we make a two-dimensional dictionary to register streamming data information.
    Assumption made for the multi-stream data registration:
    1. Same time index
    2. Same size
    We have data stucture designed as:
    dataDict = {"advanced-6-5.csv": [[ValueList], Nomalized], ...} 
    """
    def __init__(self, dataDict, keyList, dataLength, espmax):   
        self.dataDict = dataDict 
        self.dataDictKey = keyList
        self.ts_N = dataLength
        self.espmax = espmax/100
    
    """
    Signal compression using normal APCA scheme
    Input: raw data list and normalized coefficient
    Output:
    1. The compressed signal list for further analysis.
    2. The file-input compressed list for file writing
    3. The upperbound error list
    4. The lowerbound error list
    """
    def APCA_compression(self, compressList):
        decimal = 2
        #[[a,b],c] a:grouping amount; b: values; c: the outlier's value with the untolerated variance
        upperList = []
        lowerList = []
        compressedList = []
        APCAList = []
        
        tempCounter = 0;
        #numBuffer = [min, max]
        numBuffer = [0, 0] 
             
        for i in range(self.ts_N):
            #reload the value of the base signal
            #1. we have raw base signal now:
            current = compressList[i]
            
            #2. we have the range of base error tolerance now:
            #a. check if it is zero case
            if (current == 0):
                #if it is, no tolerance exists
                lowerBound = 0
                upperBound = 0
            else:
                #if not, tolerance exists
                lowerBound = current * (1 - self.espmax)
                upperBound = current * (1 + self.espmax)
                
            upperList.append(upperBound)
            lowerList.append(lowerBound)
            
            #4. reload the numBuffer, use lower bound as the reference:
            #a. one possibility for upper bound, they all exceed
            if (lowerBound > numBuffer[1]):
                #summaries previous data
                if(tempCounter == 1):
                    approx = (numBuffer[0] + numBuffer[1]) / 2
                    compressedList.append([approx])
                    APCAList.append(approx)
                elif(tempCounter > 1):
                    average = (numBuffer[0] + numBuffer[1]) / 2
                    compressedList.append([tempCounter, average])
                    APCAList += [average] * tempCounter 
                
                #refresh the two boundaries
                numBuffer[0] = lowerBound
                numBuffer[1] = upperBound
                #clear tempcounter to 1
                tempCounter = 1

                
            #b. two possibilities: upper bound in between or exceeds
            elif ((lowerBound <= numBuffer[1]) and (lowerBound >= numBuffer[0])):
                #renew lower bound for sure
                numBuffer[0] = lowerBound
                #in between
                if(upperBound <= numBuffer[1]):
                    #renew upperbound for sure
                    numBuffer[1] = upperBound 

                    tempCounter += 1
                #upper, nothing happens
                else:
                    tempCounter += 1
                    
            #c. three possibilities: upper bound below, in between, or exceeds   
            elif (lowerBound < numBuffer[0]):
                #all below
                if(upperBound < numBuffer[0]):
                    #summaries previous data
                    if(tempCounter == 1):
                        approx = (numBuffer[0] + numBuffer[1]) / 2
                        compressedList.append([approx])
                        APCAList.append(approx)
                    elif(tempCounter > 1):
                        average = (numBuffer[0] + numBuffer[1]) / 2
                        compressedList.append([tempCounter, average])
                        APCAList += [average] * tempCounter 
                    #refresh the two boundaries
                    numBuffer[0] = lowerBound
                    numBuffer[1] = upperBound 
                    #clear tempcounter to 1
                    tempCounter = 1 

                #upper in between
                elif((upperBound >= numBuffer[0]) and (upperBound <= numBuffer[1])):
                    numBuffer[1] = upperBound

                    tempCounter += 1
                #upper above   
                else:
                    tempCounter += 1
                    
            #5. check if it is the last one
            if (i == self.ts_N - 1):  
                #summaries previous data
                if(tempCounter == 1):
                    approx = (numBuffer[0] + numBuffer[1]) / 2
                    compressedList.append([approx])
                    APCAList.append(approx)
                elif(tempCounter > 1):
                    average = (numBuffer[0] + numBuffer[1]) / 2
                    compressedList.append([tempCounter, average])
                    APCAList += [average] * tempCounter                   
        return [compressedList, APCAList, lowerList, upperList]   
        
        
    """
    Check if the target signal exceed the boundary or not
    This suits the standard APCA compression
    """    
    def APCA_target_diagnosis(self, APCAsignal, rawSignal):
        errorList = []
        for i in range(self.ts_N):
            if(rawSignal[i] == 0):
                percentage = 0
            else:
                percentage = (APCAsignal[i] - rawSignal[i]) / rawSignal[i]
            if (percentage <= (self.espmax)):
                pass
            else:
                errorList.append(str(i) +":" + str(APCAsignal[i]) + "-" + str(rawSignal[i]) + "/" + str(rawSignal[i]) + "=" + str(percentage))
        return errorList     
    
    """
    Check if the target signal exceed the boundary or not
    This suits the normalized APCA compression
    """    
    def APCA_normal_target_diagnosis(self, APCAsignal, rawSignal, normalize):
        errorList = []
        maxTolerance = self.espmax * normalize
        for i in range(self.ts_N):
            if(rawSignal[i] == 0):
                percentage = 0
            else:
                percentage = APCAsignal[i] - rawSignal[i]
            if (percentage <= (maxTolerance)):
                pass
            else:
                errorList.append(str(i) +":" + str(APCAsignal[i]) + "-" + str(rawSignal[i]) + "=" + str(percentage))
        return errorList      
        

                                       
    """
    Signal compression using normal APCA scheme based on normalized value
    The error tolerace in each data point holds constant
    Input: raw data list and normalized coefficient
    Output:
    1. The compressed signal list for further analysis.
    2. The file-input compressed list for file writing.
    """    
    def APCA_normal_compression(self, compressList, normalize):
        maxTolerance = self.espmax * normalize
        #[[a,b],c] a:grouping amount; b: values; c: the outlier's value with the untolerated variance
        compressedList = []
        tempCounter = 0;
        numBuffer = []
        minValue = 0;
        maxValue = 0;
        zeroFlag = 0; 
        APCAList = []
        for i in range(self.ts_N):
            current = compressList[i]  
            #Tackle the zero case [4 10] [3] [4 0]
            if (current == 0): 
                maxValue = minValue = current 
                # Check if previous one is not the zero case
                if (zeroFlag == 0):     
                    if(tempCounter == 1):
                        if (numBuffer != []): 
                            compressedList.append([numBuffer[0]])
                            APCAList += [numBuffer[0]]
                    else:
                        if (numBuffer != []):  
                            average = float(np.mean(np.array(numBuffer)))
                            compressedList.append([tempCounter, average])
                            APCAList += [average] * tempCounter 
                    tempCounter = 0
                    numBuffer = []
                    zeroFlag = 1
                tempCounter += 1
                if (i == self.ts_N - 1):  
                    compressedList.append([tempCounter, 0]) 
                    APCAList += [0] * tempCounter 
                    
            #Tackle the non-zero case
            else:       
                # Check if previous one is the zero case
                if (zeroFlag == 1):
                    maxValue = minValue = current 
                    compressedList.append([tempCounter, 0]) 
                    APCAList += [0] * tempCounter 
                    tempCounter = 0
                    numBuffer = []
                    zeroFlag = 0
                #Refresh the min and max, setting the new boundary
                if(current < minValue):
                    minValue = current
                elif(current > maxValue):
                    maxValue = current                 
                #Check if the value exceed the boundary
                if((maxValue-minValue) <= maxTolerance):
                    numBuffer.append(current)
                    tempCounter += 1
                    if (i == self.ts_N - 1):    
                        average = float(np.mean(np.array(numBuffer)))
                        compressedList.append([tempCounter, average])
                        APCAList += [average] * tempCounter 
                else:
                    maxValue = minValue = current 
                    #Check if it is an outlier
                    if(tempCounter == 1):
                        compressedList.append([numBuffer[0]])
                        APCAList += [numBuffer[0]]
                    elif(tempCounter != 0):
                        average = float(np.mean(np.array(numBuffer)))
                        compressedList.append([tempCounter, average])
                        APCAList += [average] * tempCounter 
                    numBuffer = [current]
                    tempCounter = 1;
                    if (i == self.ts_N - 1):  
                        compressedList.append([numBuffer[0]])
                        APCAList += [numBuffer[0]]
        return [compressedList, APCAList] 
    
    
        

class APCADECOM(): 
    def __init__(self, compressedList):   
        self.compressedList = compressedList 
        self.timeRange = self.compressedList[0]

    def get_time_index(self):
        timeString = []
        #print(self.timeRange)
        time = TIME(int(self.timeRange[0]), int(self.timeRange[1]), int(self.timeRange[2]), int(self.timeRange[3]), int(self.timeRange[4]), int(self.timeRange[5]))
        timeStamps = time.correct_time_index()[1]
        for i in timeStamps:
            for j in i:
                timeString.append(str(j))
        return timeString



    def slice_list(self, subList):
        sortedDict = {}
        sliceIndex = []
        keyList = []
        #{1: '....csv'}
        nameDict = {}
        for i in range(len(subList)):
            if (len(subList[i]) == 2) and (subList[i][1].split('.')[-1] == 'csv'):
                sliceIndex.append(i)
                keyList.append(subList[i][0])
                nameDict[subList[i][0]] = subList[i][1]
        #[0],[0, 567] 
        for i in range(len(sliceIndex)):
            # the last one
            if (i == len(sliceIndex) - 1):
                sortedDict[keyList[i]] = subList[(sliceIndex[i] + 1):]
            else:
                sortedDict[keyList[i]] = subList[(sliceIndex[i] + 1) : sliceIndex[i + 1]]
        return [sortedDict, nameDict]

    def slice_group(self):
        sortedDict = {}
        sliceIndex = []

        subList = []
        #{1: '....csv'}
        nameDict = {}
        for i in range(len(self.compressedList)):
            if (self.compressedList[i][0] == '!'):
                sliceIndex.append(i)
                #[0],[0, 567] 

        for i in range(len(sliceIndex)):
            # the last one
            if (i == len(sliceIndex) - 1):
                temp = self.compressedList[(sliceIndex[i] + 1):]
                subList.append(temp)
            else:
                temp = self.compressedList[(sliceIndex[i] + 1) : sliceIndex[i + 1]]
                subList.append(temp)   
        return subList


    def apca_decompression(self):
        timeString = self.get_time_index()
        subList = self.slice_group()
        nameDict = {}
        recoveredDict = {}
        for i in range(len(subList)):
            sliceList = subList[i]
            package = self.slice_list(sliceList)
            sortedDict = package[0]
            nameDict = package[1]
                     
            for key in sortedDict:
                resumeList = []
                compressedList = sortedDict[key]
                for i in compressedList:
                    #print(i)
                    if (len(i) > 1):
                        for a in range(int(i[0])):
                            resumeList.append(float(i[1]))
                    else:
                        resumeList.append(float(i[0]))
                if(key in recoveredDict):
                    recoveredDict[key] += resumeList
                else:
                    recoveredDict[key] = resumeList
            
        return [recoveredDict, timeString, nameDict]               

    
    
                
                    
            
        