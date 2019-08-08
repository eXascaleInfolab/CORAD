import numpy as np
import pandas as pd
import matplotlib as plt
import time
import math
import sys
from DATA import *
from decimal import Decimal

class GAMPSCOM():
    """
    Discription: register data information of each single stream. In each file, 
    we make a two-dimensional dictionary to register streamming data information.
    Assumption made for the multi-stream data registration:
    1. Same time index
    2. Same size
    We have data stucture designed as:
    dataDict = {"advanced-6-5.csv": [[ValueList], Nomalized], ...} 
    """
    def __init__(self, dataDict, keyList, dataLength, c, espmax, decimal):   
        self.dataDict = dataDict 
        self.dataDictKey = keyList
        self.numElement = len(keyList)
        self.ts_N = dataLength
        self.espmax = (espmax)/100
        self.c = c 
        self.decimal = decimal
       
    """
    Base signal compression using normal APCA scheme
    Input: raw data list and normalized coefficient
    Output:
    1. The compressed signal list for further analysis.
    2. The file-input compressed list for file writing
    """
    def APCA_Base_compression(self, compressList):
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
                lowerBound = current * (1 - self.c * self.espmax)
                upperBound = current * (1 + self.c * self.espmax)
                
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
    Signal compression using normal APCA scheme based on normalized value
    The error tolerace in each data point holds constant
    Input: raw data list and normalized coefficient
    Output:
    1. The compressed signal list for further analysis.
    2. The file-input compressed list for file writing.
    """    
    def APCA_normal_Base_compression(self, compressList, normalize):
        maxTolerance = self.espmax * self.c * normalize
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
    
    """
    errorP = ratio signal maximum error guarantee to satitiate bound of compared signal.
    maxResult = maximum value of the ratio signal:maxResult
    BaseError = maximum error guarantee of the base signal:c*espmax
    maxBase = maximum value of the base signal:maxBase
    ComError = designed maximum error guarantee of the compared signal: normalize*espmax
    """
    def ratio_signal_error(self, baseError, ratio, signal, base):
        if((base + baseError) == 0):
            #This means base signal is 0 here, so ratio = signal, error should be +-esp
            upperBound = self.espmax * signal
            lowerBound = -self.espmax * signal
        else:
            #This means base signal is not 0 here, if ratio = 0, means signal = 0
            upperBound = (signal * self.espmax - baseError * ratio) / (base + baseError)
            lowerBound = (- signal * self.espmax - baseError * ratio) / (base + baseError)
        return [lowerBound, upperBound]   
    
    """
    errorP = ratio signal maximum error guarantee to satitiate bound of compared signal.
    maxResult = maximum value of the ratio signal:maxResult
    BaseError = maximum error guarantee of the base signal:c*espmax
    maxBase = maximum value of the base signal:maxBase
    ComError = designed maximum error guarantee of the compared signal: normalize*espmax
    """
    def ratio_normal_signal_error(self, baseError, ratio, signalN, base):
        if((base + baseError) == 0):
            #This means base signal is 0 here, so ratio = signal, error should be +-esp
            upperBound = self.espmax * signalN
            lowerBound = -self.espmax * signalN
        else:
            #This means base signal is not 0 here, if ratio = 0, means signal = 0
            upperBound = (signalN * self.espmax - baseError * ratio) / (base + baseError)
            lowerBound = (- signalN * self.espmax - baseError * ratio) / (base + baseError)
        return [lowerBound, upperBound]       
    
    
    """
    Ratio signal compression using normal APCA scheme
    Input: raw data list and normalized coefficient
    Output:
    1. The compressed signal list for further analysis.
    2. The file-input compressed list for file writing
    """
    def APCA_Ratio_compression(self, signalList, baseList, APCA):
        decimal = 2
        #[[a,b],c] a:grouping amount; b: values; c: the outlier's value with the untolerated variance
        baseErrorList = []
        ratioList = []
        upperList = []
        lowerList = []
        ratioErrorList = []
        compressedList = []
        APCAList = []
        rangelist = []
        
        tempCounter = 0;
        #numBuffer = [min, max]
        numBuffer = [0, 0] 
             
        for i in range(self.ts_N):
            #reload the value of the ratio signal, if base = 0, ratio = signal; if base != 0, ratio = ratio
            
            #1. we have raw ratio signal now:
            if (baseList[i] == 0):
                current = signalList[i]
            else:
                current = signalList[i]/baseList[i]
            ratioList.append(current)
            
            #2. we have base error now:
            baseError = APCA[i] - baseList[i]
            
            baseErrorList.append(baseError)
            
            #3. we have the range of ratio error now:
            errorRange = self.ratio_signal_error(float(baseError), current, signalList[i], baseList[i])
            upperBound = errorRange[1] + current
            upperList.append(upperBound)
            lowerBound = errorRange[0] + current
            lowerList.append(lowerBound)
            rangelist.append(errorRange)
            
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
        return [compressedList, APCAList, lowerList, upperList, ratioList, rangelist]
   
    
    """
    Ratio signal compression using normal APCA scheme
    Input: raw data list and normalized coefficient
    Output:
    1. The compressed signal list for further analysis.
    2. The file-input compressed list for file writing
    """
    def APCA_normal_Ratio_compression(self, signalList, baseList, APCA, normalize):
        #[[a,b],c] a:grouping amount; b: values; c: the outlier's value with the untolerated variance
        baseErrorList = []
        ratioList = []
        upperList = []
        lowerList = []
        ratioErrorList = []
        compressedList = []
        APCAList = []
        rangelist = []
        
        tempCounter = 0;
        #numBuffer = [min, max]
        numBuffer = [0, 0] 
             
        for i in range(self.ts_N):
            #reload the value of the ratio signal, if base = 0, ratio = signal; if base != 0, ratio = ratio
            
            #1. we have raw ratio signal now:
            if (baseList[i] == 0):
                current = signalList[i]
            else:
                current = signalList[i]/baseList[i]
            '''
            if(signalList[3] == 122) and (baseList[0] == 154):
                print(current)     
            '''
            ratioList.append(current)
            
            #2. we have base error now:
            baseError = APCA[i] - baseList[i]
            
            baseErrorList.append(baseError)
            
            #3. we have the range of ratio error now:
            errorRange = self.ratio_normal_signal_error(float(baseError), current, normalize, baseList[i])
            upperBound = errorRange[1] + current
            upperList.append(upperBound)
            lowerBound = errorRange[0] + current
            lowerList.append(lowerBound)
            rangelist.append(errorRange)
            
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
        return [compressedList, APCAList, lowerList, upperList, ratioList, rangelist]    
    
    """
    Check if the target signal exceed the boundary or not
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
    Round the number to reduce memory 
    """
    def round_decimal(self, number, decimal):
        if(round(Decimal(number),decimal - 1) == round(Decimal(number),decimal)):
            if((decimal - 1) == 0):
                approx = int(round(Decimal(number),decimal-1))
            else:
                approx = self.round_decimal(number, decimal - 1)
        else:
            approx = float(round(Decimal(number),decimal))
        return approx    
    
    def get_compress_size(self, compressedList, decimal):
        APCAsize = ''    
        for i in compressedList:
            for d in i:
                if (decimal == 0):
                    approx = int(d)
                else:
                    approx = self.round_decimal(d, decimal) 
                APCAsize += str(approx) +' '
            APCAsize += '\n'  
        capAPCA = sys.getsizeof(APCAsize)
        return capAPCA
    
    def get_base_size(self, baseList):
        basesize = ''
        for i in baseList:
            basesize += str(i) + '\n'         
        capbase = sys.getsizeof(basesize) 
        return capbase      
    
    """
    #Purpose	: find facility location solution to minimize memory cost problem
    #Return	: (int) allocated memory cost
    """
    def find_optima_solution(self,listBucket, listRatioSignalBucket):
        #init m_pTgood and Tgoodold and run array for caculating reduce cost
        totalCost = 0;
        numofStream = self.numElement
        m_arrBaseCost = listBucket
        m_pRatioCost = listRatioSignalBucket
        selectedSignal = []
        m_pTgood = []
        #Initialization of selected signal and m_pTgood
        for i in range(numofStream):
            m_pTgood.append(i)
            totalCost = m_arrBaseCost[i];
            selectedSignal.append(0);
    
        #Repeat until no changes between previous and current solution
        while True:

            maxReduceCostPos = -1;
            maxReduceCost = 0;
    
            #calculate reduce cost of signal ith
            for i in range(numofStream):
                if(selectedSignal[i] != 0):
                    continue
                reduceCost = 0;
                for j in range(numofStream):
                    if(selectedSignal[j] != 0):
                        continue
                    delta = m_arrBaseCost[i] - m_pRatioCost[i][j];
                    if(delta > 0):
                        #reduce cost is the deduction of apca orignial signal and apca ratio signal, measuring the efficiency of the ratio signal.
                        reduceCost = reduceCost + delta;
    
                if(reduceCost > 0 and reduceCost > maxReduceCost):
                    maxReduceCostPos = i;
                    maxReduceCost = reduceCost;


    
            # Choose the signal, which has maximum reduce cost, to be base signal
            # And the remaining signals, which have reduce cost > 0, become ratio signals
            if(maxReduceCostPos != -1):
                # update m_pTgood
                selectedSignal[maxReduceCostPos] = 1;
                m_pTgood[maxReduceCostPos] = maxReduceCostPos;

                for j in range(numofStream):
                    if(selectedSignal[j] != 0):
                        continue                
                    delta = m_arrBaseCost[maxReduceCostPos] - m_pRatioCost[maxReduceCostPos][j]
                    if(delta > 0):
                        m_pTgood[j] = maxReduceCostPos
                        selectedSignal[j] = 1;

            else: #Otherwise, all remaining signals become base signals
                for j in range(numofStream):
                    if(selectedSignal[j] != 0):
                        continue     
                    m_pTgood[j] = j
                break
    
        totalCost = 0
        for i in range(numofStream):
            totalCost += m_pRatioCost[i][m_pTgood[i]]
        package = [totalCost, m_pTgood]    
        return package; 
    
    """
    compute output based on base signals and ratio signals
    """
    def compute_output(self, baseBucketList, ratioBucketList, m_pTgood):
        numofStream = self.numElement
        baseBucketCount = 0
        baseCount = 0
        ratioCount = 0
        #[key[8]:[ratio1,...,ration], key[9]:[ratio1,...,ration]]
        ratioIndex = {}
        resultBaseSignal = {}
        resultRatioSignal = {}
        for i in range(numofStream):
            if(m_pTgood[i] == i):
                temp = baseBucketList[i]
                resultBaseSignal[i] = temp
                ratioIndex[i]= m_pTgood[i]
            else:
                temp = ratioBucketList[m_pTgood[i]][i]
                
                resultRatioSignal[i] = temp
                """
                print('!')
                print(baseBucketList[m_pTgood[i]])
                print(ratioBucketList[m_pTgood[i]][i])
                print('!')
                """
                ratioIndex[i]=m_pTgood[i]
                #ratioIndex = m_pTgood
        package = [ratioIndex, resultBaseSignal, resultRatioSignal]
        return package
    
    
    """
    Purpose	: static group given input data
    Parameter: gampsInputList: data need to be static grouped
    Return	: (int)allocated memory of stat grouped result
    """
    def stat_grouping(self, Type):
        numOfStream = self.numElement
        listBucket = []
        listRatioSignalBucket = []
    
        # Apply APCA to bas esignal
        for j in range(numOfStream):
            # choose one signal => base signal, compress it and push into base signal bucket list, this is a dictionary of signal and scale value
            baseSignal = self.dataDict[self.dataDictKey[j]]
            baseSignalValue = baseSignal[0]
            normalized = baseSignal[1]
            if(Type == 0):
                listBaseSignalBucket = self.APCA_Base_compression(baseSignalValue)
            elif(Type == 1):
                listBaseSignalBucket = self.APCA_normal_Base_compression(baseSignalValue, normalized)
            APCABase = listBaseSignalBucket[1]
            listBucket.append(listBaseSignalBucket[0])
            tempRatio = []
            for i in range(numOfStream):
                """
                foreach signal:
                + calculate ratio with base signal
                + apply APCA and push it into ratio bucket list
                """
                ratioSignal = self.dataDict[self.dataDictKey[i]]
                ratioSignalValue = ratioSignal[0]
                normalized = ratioSignal[1]
                if(Type == 0):
                    listRatioBucket = self.APCA_Ratio_compression(ratioSignalValue, baseSignalValue ,APCABase)  
                elif(Type == 1):
                    listRatioBucket = self.APCA_normal_Ratio_compression(ratioSignalValue, baseSignalValue ,APCABase, normalized)
                    """
                    if(ratioSignalValue[3] == 122) and (baseSignalValue[0] == 154):
                        print(listRatioBucket[0])      
                    """
                tempRatio.append(listRatioBucket[0])
            listRatioSignalBucket.append(tempRatio)

    
        #/*************** facility location *************/
        bSize = numOfStream;
        #for each scenario, what's the total cost? It should be 18 elements
        baseBucketCost = []
        ratioSignalCost= []

        #calculate each base signal bucket cost
        for i in range(bSize):
            oneBSize = self.get_base_size(listBucket[i])
            baseBucketCost.append(oneBSize)

        # put ratio signal cost into 2 dimension array array[baseSignal][ratioSignal]
        for i in range(bSize):
            #2 dimension array design as [[ratio],[ratio],...,[ratio] 
            tempArray = []
            for j in range(bSize):
                if (i != j):
                    oneSSize = self.get_compress_size(listRatioSignalBucket[i][j], self.decimal)
                else:
                    oneSSize = oneBSize
                tempArray.append(oneSSize)
            ratioSignalCost.append(tempArray)
            

        #find optimal solution for faciliting location
        package = self.find_optima_solution(baseBucketCost, ratioSignalCost)
        totalCost = package[0]
        m_Tgood = package[1]
        List = [totalCost] + self.compute_output(listBucket,listRatioSignalBucket,m_Tgood);
        #/************ end facility location ************/
       
        return List
  
  

        

class GAMPSDECOM(): 
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
        groupList = []
        subList = []
        #{1: '....csv'}
        nameDict = {}
        for i in range(len(self.compressedList)):
            if (self.compressedList[i][0] == '!'):
                sliceIndex.append(i)
                groupList.append(self.compressedList[i][1:])
                #[0],[0, 567]      
                
        for i in range(len(sliceIndex)):
            # the last one
            if (i == len(sliceIndex) - 1):
                temp = [groupList[i]] + self.compressedList[(sliceIndex[i] + 1):]
                subList.append(temp)
            else:
                temp = [groupList[i]] + self.compressedList[(sliceIndex[i] + 1) : sliceIndex[i + 1]]
                subList.append(temp)   
        return subList
                
    def get_group_index(self, index):
        groupDict = {}
        for i in range(len(index)):
            groupDict[str(i)] = index[i]
        return groupDict
                
    
    def gamps_decompression(self):
        timeString = self.get_time_index()
        subList = self.slice_group()
        #print(subList[0])
        nameDict = {}
        recoveredDict = {}
        finalRecoveredDict = {}
        for i in range(len(subList)):
            sliceList = subList[i]
            groupIndexList = sliceList[0]
            #print(groupIndexList)
            #print(sliceList)
            package = self.slice_list(sliceList)
            
            sortedDict = package[0]
            RawOrBase = self.get_group_index(groupIndexList)
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
                recoveredDict[key] = resumeList
                
            #print(sortedDict.keys())
            for key in RawOrBase:
                #ratio signal
                if (RawOrBase[key] != key):
                    resumeList = []
                    for i in range(len(recoveredDict[key])):
                        #(base * ratio)
                        temp = int(float(recoveredDict[RawOrBase[key]][i]) * float(recoveredDict[key][i]))
                        resumeList.append(temp)
                    if (key in finalRecoveredDict):
                        finalRecoveredDict[key]  += resumeList
                    else:
                        finalRecoveredDict[key]  = resumeList
                else:
                    resumeList = []
                    for i in range(len(recoveredDict[key])):
                        temp = int(float(recoveredDict[key][i]))
                        resumeList.append(temp)                     
                    if (key in finalRecoveredDict):
                        finalRecoveredDict[key]  += resumeList
                    else:
                        finalRecoveredDict[key]  = resumeList            
        #print(recoveredDict)
        return [finalRecoveredDict, timeString, nameDict]

                
                    
            
        