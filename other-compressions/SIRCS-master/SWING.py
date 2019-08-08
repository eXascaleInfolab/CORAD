import numpy as np
import pandas as pd
import matplotlib as plt
import time
import math
import sys
from DATA import *
from decimal import Decimal

class SWINGCOM():
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
    Check if the target signal exceed the boundary or not
    This suits the normalized APCA compression
    """    
    def SWING_normal_base_target_diagnosis(self, SFsignal, rawSignal, normalize):
        errorList = []
        maxTolerance = self.espmax * normalize
        for i in range(self.ts_N):
            if(rawSignal[i] == 0):
                percentage = 0
            else:
                percentage = SFsignal[i] - rawSignal[i]
            if (percentage <= (maxTolerance * 1.00001)):
                pass
            else:
                errorList.append(str(i) +":" + str(SFsignal[i]) + "-" + str(rawSignal[i]) + "=" + str(percentage ) + '>' + str(maxTolerance))
        return errorList      
        

    """
    calculate the upper line and lower line between two points
    Input: 
    1. Point1
    2. Point2
    3. tolerance
    Output:
    1.lower and upperline information
    """
    def get_l_and_u(self, basePoint, point2, espmax):
        LU = []
        # one line contains: slope, cross pointx, crous point y [slope, x, y]
        U = []
        L = []
        #lower bound
        point2y_L = point2[1] - espmax
        
        #upper bound
        point2y_U = point2[1] + espmax
        
        #x coordinate
        basePointy = basePoint[1]
        basePointx = basePoint[0]
        point2x = point2[0]
        
        #lower bound slope
        slope_L = (point2y_L - basePointy) / (point2x - basePointx)
        L = [slope_L, basePointx, basePointy]
        
        #upper bound slope
        slope_U = (point2y_U - basePointy) / (point2x - basePointx)
        U = [slope_U, basePointx, basePointy]
        #print("upper:" + str(slope_U) + "lower:" + str(slope_L))
        LU = [L, U]
        
        return LU
        
        
        
    """
    Update the lower and upper line, and, if two lines overturn, return []
    Input:
    1. point list
    2. current optimized lower and upper line
    Output:
    1.New slide filter set
    """
    def update_l_and_u(self, tempPointBuffer, Filter, maxTolerance):
        currentFilter = Filter       
        if((currentFilter == []) and (len(tempPointBuffer) == 2)):
            #get the first two lines from the first two points
            currentFilter = self.get_l_and_u(tempPointBuffer[0], tempPointBuffer[1], maxTolerance)
        else:  
            #print(tempPointBuffer)
            #print(currentFilter)
            basePoint = tempPointBuffer[0]
            currentPoint = tempPointBuffer[len(tempPointBuffer) - 1]
            #get the current slope
            slope_L = currentFilter[0][0]
            slope_U = currentFilter[1][0]
            #check new point's line set
            newLines = self.get_l_and_u(basePoint, currentPoint, maxTolerance)
            #test if L is larger than the old
            newSlope_L = newLines[0][0]
            if(newSlope_L >= slope_L):
                #update currentFilter
                if(newSlope_L < slope_U):
                    currentFilter[0] = newLines[0]
                else:
                    #if 0 is received, slide filter need to be updated
                    return 0
                
            #test if U is lower than the old
            newSlope_U = newLines[1][0]
            if(newSlope_U < slope_U):
                #update currentFilter
                if(newSlope_U >= slope_L):
                    currentFilter[1] = newLines[1]
                else:
                    #if 0 is received, slide filter need to be updated
                    return 0                  
           
        return currentFilter
    """
    sf coefficient to slope and intercept
    """
    def sf_to_sc(self, sf):
        slope = sf[0]
        #cross through (a, b)
        a = sf[1]
        b = sf[2]
        #written as : y = slope * (x - a) + b
        #intercept: b - a * slope
        intercept = b - a * slope
        return [slope, intercept]
    """
    Get the intersection of two lines
    The intersection of the two lines are the xbar and ybar of the regression line
    """
    def line_intersection(self, line1, line2):
        slope1 = line1[0]
        slope2 = line2[0]
        intercept1 = line1[1]
        intercept2 = line2[1]
        
        x = (intercept2 - intercept1) / (slope1 - slope2)
        y = slope1 * x + intercept1
        return (x, y)
    
    """
    Get the least square slope from the filter
    """
    def least_sqaure_slope(self, xbar, ybar, slope_L, slope_U, tempPointBuffer):
        numerator = 0
        denominator = 0
        for points in tempPointBuffer:
            #beta_1 = SXY / SXX
            numerator += (points[1] - ybar) * (points[0] - xbar);
            denominator += (points[0] - xbar) * (points[0] - xbar);
        beta_1 = numerator / denominator  
        if(beta_1 > slope_L and beta_1 < slope_U):   
            pass
        #else:
            #beta_1 = (slope_L + slope_U) / 2
        elif(beta_1 < slope_L):
            beta_1 = slope_L
        elif(beta_1 > slope_U):
            beta_1 = slope_U
            #print("upper:" + str(slope_U) + "lower:" + str(slope_L) + 'beta:' + str(beta_1))
        #print(tempPointBuffer) 
        #print(str(numerator) + "/" + str(denominator) + "=" + str(beta_1))
        return beta_1
    
    
    
    """
    record format:
    [[slope, x, y],[slope, x, y],num] --> [starty, slope, num]
    """
    def record_sf(self, slideFilter, tempPointBuffer):
        #convert to two line format
        startPoint = tempPointBuffer[0]
        endPoint = tempPointBuffer[len(tempPointBuffer) - 1]

        #get the intersection. it's an array:
        intersection = startPoint
            
        #get the slope:
        slope = self.least_sqaure_slope(intersection[0], intersection[1], slideFilter[0][0], slideFilter[1][0], tempPointBuffer)
        #get starty:
        starty = startPoint[1]
        return [starty, slope]
            
    """
    Signal compression using normal APCA scheme based on normalized value
    The error tolerace in each data point holds constant
    [sf:[3], 2 points:a, zero:[2]]
    Input: raw data list and normalized coefficient
    Output:
    1. The compressed signal list for further analysis.
    2. The file-input compressed list for file writing.
    """    
    def SWING_normal_base_compression(self, compressList, normalize):
        maxTolerance = self.espmax * normalize
        #[[a,b],c] a:grouping amount; b: values; c: the outlier's value with the untolerated variance
        compressedList = []
        #register every piecewise slidefilter, form[[sf], num]
        SFList = []
        uandl = []
        #slide filter that register the optimized upper and lower line, form: [L,U] L = U = [slope, x, y]
        slideFilter = []
        #register the points of current interval, it helps counting the number
        tempPointBuffer = []
        #zero if it is the first registered point, one otherwise
        inProgress = 0 
        #zero Counter
        zeroCounter = 0
        #zero flag
        zeroFlag = 0
        for i in range(self.ts_N):
            current = compressList[i]  
            #Tackle the zero case [4 10] [3] [4 0]
            if (current == 0): 
                # Check if previous one is not the zero case, this means not
                if (zeroFlag == 0):    
                    #throw the linear piecewise away
                    #case 1: already registered
                    if((slideFilter == []) and (tempPointBuffer == [])):
                        pass
                    #case 2: only one point is pending
                    elif((slideFilter == []) and (tempPointBuffer != [])):
                        SFList += [tempPointBuffer[0][1]]
                        compressedList.append([tempPointBuffer[0][1]])
                    #case 3: more than one point is pending
                    elif((slideFilter != []) and (tempPointBuffer != [])):  
                        #throw them into SF list
                        pointNumber = len(tempPointBuffer)
                        if(pointNumber == 2):
                            SFList += [tempPointBuffer[0][1], tempPointBuffer[1][1]]
                            compressedList.append([tempPointBuffer[0][1]])
                            compressedList.append([tempPointBuffer[1][1]])                        
                        else:
                            uandl.append(slideFilter)
                            compressed = self.record_sf(slideFilter, tempPointBuffer) + [pointNumber]
                            compressedList.append(compressed) 
                            for index in range(pointNumber):
                                y = compressed[0] + index * compressed[1]
                                SFList.append(y)
                    
                    #set flay to 1
                    zeroFlag = 1
                    #count this zero to the counter
                    zeroCounter = 1
                elif(zeroFlag == 1):
                    #count one zero to the counter
                    zeroCounter += 1
                #reset the linear piecewise parameters 
                tempPointBuffer = []
                slideFilter = []
                inProgress = 0                
            #Tackle the non-zero case
            else:       
                # Check if previous one is the zero case
                #throw the zero buffer away
                if (zeroFlag == 1):  
                    #expend the zero list
                    if(zeroCounter == 1):
                        compressedList.append([0]) 
                        SFList += [0]                       
                    else:
                        compressedList.append([zeroCounter, 0]) 
                        SFList += [0] * zeroCounter 
                    #reset the zero flag to non, clear everything
                    zeroFlag = 0                     
                    zeroCounter = 0
                    tempPointBuffer = []
                    slideFilter == []
                    inProgress = 0
                    #print(inProgress)
                #This means new interval is ready to create, register two points into the list
                if (inProgress == 0):
                    #get the point
                    point = [i, compressList[i]]
                    #append to point list
                    tempPointBuffer.append(point)
                    inProgress = 1          
                else:
                    #get the point
                    point = [i, compressList[i]]
                    #append to point list
                    tempPointBuffer.append(point)
                                 
                    #update the slidefilter
                    currentFilter = self.update_l_and_u(tempPointBuffer, slideFilter, maxTolerance)
                    """
                    if(slideFilter != [] and slideFilter[0][0] > slideFilter[1][0]):
                        print("upper:" + str(slideFilter[1][0]) + "lower:" + str(slideFilter[0][0]))  
                    elif(slideFilter == []):
                        print(True)
                    """
                    #it's time to summarize the piece and reset the parameter
                    if(currentFilter == 0):
                        #the last point doesn't suit, minus one
                        pointNumber = len(tempPointBuffer) - 1                   
                        if(pointNumber == 2):
                            SFList += [tempPointBuffer[0][1], tempPointBuffer[1][1]]
                            compressedList.append([tempPointBuffer[0][1]])
                            compressedList.append([tempPointBuffer[1][1]])
                        else:
                            uandl.append(slideFilter)
                            compressed = self.record_sf(slideFilter, tempPointBuffer) + [pointNumber]
                            compressedList.append(compressed)
                            for index in range(pointNumber):
                                y = compressed[0] + index * compressed[1]
                                SFList.append(y)                            
                        #reset everything
                        tempPointBuffer = [point]
                        slideFilter = []              
                    #update accomplished
                    else:    
                        slideFilter = currentFilter
                        #print("upper:" + str(slideFilter[1][0]) + "lower:" + str(slideFilter[0][0]))
                    
                    
            #check if it's the last one    
            if(i == self.ts_N - 1):  
                #the current case is not zero
                if(zeroFlag == 0):
                    #case 1: already registered
                    if((slideFilter == []) and (tempPointBuffer == [])):
                        pass
                    #case 2: only one point is pending
                    elif((slideFilter == []) and (tempPointBuffer != [])):
                        SFList += [tempPointBuffer[0][1]]
                        compressedList.append([tempPointBuffer[0][1]])
                    #case 3: more than one point is pending
                    elif((slideFilter != []) and (tempPointBuffer != [])):    
                        #throw them into SF list
                        pointNumber = len(tempPointBuffer)
                        if(pointNumber == 2):
                            SFList += [tempPointBuffer[0][1], tempPointBuffer[1][1]]
                            compressedList.append([tempPointBuffer[0][1]])
                            compressedList.append([tempPointBuffer[1][1]])                        
                        else:
                            uandl.append(slideFilter)
                            compressed = self.record_sf(slideFilter, tempPointBuffer) + [pointNumber]
                            compressedList.append(compressed) 
                            for index in range(pointNumber):
                                y = compressed[0] + index * compressed[1]
                                SFList.append(y)                            
                else:
                    #expend the zero list
                    if(zeroCounter == 1):
                        compressedList.append([0]) 
                        SFList += [0]                       
                    else:
                        compressedList.append([zeroCounter, 0]) 
                        SFList += [0] * zeroCounter                  
        return [compressedList, SFList]
                
    """
    Remainder signal compression using normal SWING scheme based on the 
    normalized value
    Input: raw data list and normalized coefficient
    Output:
    1. The compressed signal list for further analysis.
    2. The file-input compressed list for file writing
    """   
    def SWING_normal_res_compression(self, compressList, rawListNormalize, slope, intercept, coeff):
        maxTolerance = (coeff * self.espmax) * rawListNormalize
        #[[a,b],c] a:grouping amount; b: values; c: the outlier's value with the untolerated variance
        compressedList = [[slope, intercept]]
        #register every piecewise slidefilter, form[[sf], num]
        SFList = []
        uandl = []
        #slide filter that register the optimized upper and lower line, form: [L,U] L = U = [slope, x, y]
        slideFilter = []
        #register the points of current interval, it helps counting the number
        tempPointBuffer = []
        #zero if it is the first registered point, one otherwise
        inProgress = 0 
        #zero Counter
        zeroCounter = 0
        #zero flag
        zeroFlag = 0
        for i in range(self.ts_N):
            current = compressList[i]  
            #Tackle the zero case [4 10] [3] [4 0]
            if (current == Zero): 
                # Check if previous one is not the zero case, this means not
                if (zeroFlag == 0):    
                    #throw the linear piecewise away
                    #case 1: already registered
                    if((slideFilter == []) and (tempPointBuffer == [])):
                        pass
                    #case 2: only one point is pending
                    elif((slideFilter == []) and (tempPointBuffer != [])):
                        SFList += [tempPointBuffer[0][1]]
                        compressedList.append([tempPointBuffer[0][1]])
                    #case 3: more than one point is pending
                    elif((slideFilter != []) and (tempPointBuffer != [])):  
                        #throw them into SF list
                        pointNumber = len(tempPointBuffer)
                        if(pointNumber == 2):
                            SFList += [tempPointBuffer[0][1], tempPointBuffer[1][1]]
                            compressedList.append([tempPointBuffer[0][1]])
                            compressedList.append([tempPointBuffer[1][1]])                        
                        else:
                            uandl.append(slideFilter)
                            compressed = self.record_sf(slideFilter, tempPointBuffer) + [pointNumber]
                            compressedList.append(compressed) 
                            for index in range(pointNumber):
                                y = compressed[0] + index * compressed[1]
                                SFList.append(y)
    
                    #set flay to 1
                    zeroFlag = 1
                    #count this zero to the counter
                    zeroCounter = 1
                elif(zeroFlag == 1):
                    #count one zero to the counter
                    zeroCounter += 1
                #reset the linear piecewise parameters 
                tempPointBuffer = []
                slideFilter = []
                inProgress = 0                
            #Tackle the non-zero case
            else:       
                # Check if previous one is the zero case
                #throw the zero buffer away
                if (zeroFlag == 1):  
                    #expend the zero list
                    if(zeroCounter == 1):
                        compressedList.append([Zero]) 
                        SFList += [Zero]                       
                    else:
                        compressedList.append([zeroCounter, Zero]) 
                        SFList += [Zero] * zeroCounter 
                    #reset the zero flag to non, clear everything
                    zeroFlag = 0                     
                    zeroCounter = 0
                    tempPointBuffer = []
                    slideFilter == []
                    inProgress = 0
                    #print(inProgress)
                #This means new interval is ready to create, register two points into the list
                if (inProgress == 0):
                    #get the point
                    point = [i, compressList[i]]
                    #append to point list
                    tempPointBuffer.append(point)
                    inProgress = 1          
                else:
                    #get the point
                    point = [i, compressList[i]]
                    #append to point list
                    tempPointBuffer.append(point)
    
                    #update the slidefilter
                    currentFilter = self.update_l_and_u(tempPointBuffer, slideFilter, maxTolerance)
                    """
                    if(slideFilter != [] and slideFilter[0][0] > slideFilter[1][0]):
                        print("upper:" + str(slideFilter[1][0]) + "lower:" + str(slideFilter[0][0]))  
                    elif(slideFilter == []):
                        print(True)
                    """
                    #it's time to summarize the piece and reset the parameter
                    if(currentFilter == 0):
                        #the last point doesn't suit, minus one
                        pointNumber = len(tempPointBuffer) - 1                   
                        if(pointNumber == 2):
                            SFList += [tempPointBuffer[0][1], tempPointBuffer[1][1]]
                            compressedList.append([tempPointBuffer[0][1]])
                            compressedList.append([tempPointBuffer[1][1]])
                        else:
                            uandl.append(slideFilter)
                            compressed = self.record_sf(slideFilter, tempPointBuffer) + [pointNumber]
                            compressedList.append(compressed)
                            for index in range(pointNumber):
                                y = compressed[0] + index * compressed[1]
                                SFList.append(y)                            
                        #reset everything
                        tempPointBuffer = [point]
                        slideFilter = []              
                    #update accomplished
                    else:    
                        slideFilter = currentFilter
                        #print("upper:" + str(slideFilter[1][0]) + "lower:" + str(slideFilter[0][0]))
    
    
            #check if it's the last one    
            if(i == self.ts_N - 1):  
                #the current case is not zero
                if(zeroFlag == 0):
                    #case 1: already registered
                    if((slideFilter == []) and (tempPointBuffer == [])):
                        pass
                    #case 2: only one point is pending
                    elif((slideFilter == []) and (tempPointBuffer != [])):
                        SFList += [tempPointBuffer[0][1]]
                        compressedList.append([tempPointBuffer[0][1]])
                    #case 3: more than one point is pending
                    elif((slideFilter != []) and (tempPointBuffer != [])):    
                        #throw them into SF list
                        pointNumber = len(tempPointBuffer)
                        if(pointNumber == 2):
                            SFList += [tempPointBuffer[0][1], tempPointBuffer[1][1]]
                            compressedList.append([tempPointBuffer[0][1]])
                            compressedList.append([tempPointBuffer[1][1]])                        
                        else:
                            uandl.append(slideFilter)
                            compressed = self.record_sf(slideFilter, tempPointBuffer) + [pointNumber]
                            compressedList.append(compressed) 
                            for index in range(pointNumber):
                                y = compressed[0] + index * compressed[1]
                                SFList.append(y)                            
                else:
                    #expend the zero list
                    if(zeroCounter == 1):
                        compressedList.append([Zero]) 
                        SFList += [Zero]                       
                    else:
                        compressedList.append([zeroCounter, Zero]) 
                        SFList += [Zero] * zeroCounter                  
        return [compressedList, SFList]        
    
    """
    grouping compression is to help analyzing the holistic compression performace of apca
    """
    def group_compression(self, pathDataIO):
        culmulativeTime = 0
        comStartTime = 0
        comEndTime = 0
        tof = tcf = 0
        SE = 0
        dataSize = 0
        scale = 0
        maxCheck = {}
        ratioList = []
        num = NUM(pathDataIO, self.dataDict)
        for name in self.dataDict:
            #compression
            comStartTime = time.time()
            basePackage = self.SWING_normal_base_compression(self.dataDict[name][0],self.dataDict[name][1])
            comEndTime = time.time()
            rawBase = self.dataDict[name][0]
            compressedBase = basePackage[0]
            swingbase = basePackage[1]     
            #evaluation
            
            #Check if max exceed
            error = self.SWING_normal_base_target_diagnosis(swingbase, rawBase,self.dataDict[name][1])
            if(len(error) != 0):
                print("SWING Error Violation Warning.\n")            
            #Compute RMSE
            rmsePackage = num.RMSE(rawBase, swingbase)
            SE += rmsePackage[1]
            dataSize += rmsePackage[2]
            if(rmsePackage[3] > scale):
                scale = rmsePackage[3] / 10            
            #Compute Compression Ratio
            package = num.get_compress_ratio(rawBase, compressedBase, 0)
            tof += package[2]
            tcf += package[1]
            
            #Compute Compression Time
            tempTime = num.computational_time(comStartTime, comEndTime)
            culmulativeTime += tempTime
        totalRMSE = math.sqrt(SE / dataSize) / scale
        totalRatio = tcf / tof        
        return [float(round(Decimal(totalRMSE),2)), float(round(Decimal(totalRatio),2)), float(round(Decimal(culmulativeTime),2))]
    """
    Recover the SWING signal from a residual SWING signal. This is used in chain compression
    """
    def get_recovered_SWING(self, SWINGx, residualy, slope, intercept):
        resumeList = []     
        for i in range(len(residualy)):
            if (residualy[i] == Zero):
                temp = 0
                resumeList.append(temp) 
            else:
                temp = int(SWINGx[i] * slope + intercept + residualy[i])
                resumeList.append(temp)
        return resumeList

    
    
        




class SWINGDECOM():
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
                
                
    def swing_decompression(self):
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
                    if (len(i) == 1):
                        resumeList.append(float(i[0]))
                    elif (len(i) == 2):
                        resumeList += [0] * int(i[0])
                    else:
                        for index in range(int(i[2])):
                            y = float(i[0]) + index * float(i[1])
                            resumeList.append(y) 
                if(key in recoveredDict):
                    recoveredDict[key] += resumeList
                else:
                    recoveredDict[key] = resumeList
                
          
        return [recoveredDict, timeString, nameDict]

                
                    
             
    
    """
    The residual decompression take the APCA base list and the signal residual list.
    The recover equation is y = yhat + res. 
    Input: 
    1. Compressed APCA base list
    2. Compressed APCA signal residual list
    Output:
    1. The recover series
    """
    def lm_Residual_decompression(self, readfileRes, readfileBase):
        resumeListBase = []
        resumeListRes = []
        resumeList = []
        #timeIndex = self.decompress_index(compressedList[0])
        for i in compressedList:
            if (len(i) == 1):
                resumeListBase.append(float(i[0]))
                
            elif (len(i) == 2):
                resumeListBase += [0] * int(i[0])
            else:
                for index in range(int(i[2])):
                    y = float(i[0]) + index * float(i[1])
                    resumeListBase.append(y) 
                    
        #get the lm coefficient
        slope = readfileRes[0][0]
        intercept = readfileRes[0][1]
        for i in readfileRes[1:]:
            if (len(i) == 1):
                if(i[0] == Zero):
                    resumeListRes.append(Zero)
                else:
                    resumeListRes.append(float(i[0]))
            elif (len(i) == 2):
                if(i[1] == Zero):
                    for a in range(int(i[0])):
                        resumeListRes.append(Zero)
                else:
                    for a in range(int(i[0])):
                        resumeListRes.append(float(i[1]))                
            else:
                for index in range(int(i[2])):
                    y = float(i[0]) + index * float(i[1])
                    resumeListRes.append(y) 
    
        for i in range(len(resumeListRes)):
            if(resumeListRes[i] == Zero):
                temp = 0
                resumeList.append(temp) 
            else:
                temp = int(resumeListBase[i] * slope + intercept + resumeListRes[i])
                resumeList.append(temp)           
        return resumeList    
    
            
        