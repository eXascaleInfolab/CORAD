import numpy as np
import pandas as pd
from datetime import date
import os

class TIME():
    def __init__(self, startyear, startmonth, startday, endyear, endmonth, endday):
        #Date time manipulation
        self.startyear = startyear
        self.startmonth = startmonth
        self.startday = startday
        self.endyear = endyear
        self.endmonth = endmonth
        self.endday = endday 
        
        
    def show_days(self):
        d0 = date(self.startyear, self.startmonth, self.startday)
        d1 = date(self.endyear, self.endmonth, self.endday)
        delta = d1 - d0   
        return delta.days 
    
    """
    Self-made time index with 100% correctness and customized time range.
    Input: start time and end time with the minimum varying frequency
    Output: list of pandas time index, say, after input Jan-1~Jan-3, it get 3 lists of day 1,2,3
            [[day1 index], [day2 index], [day3 index]]
    """
    def correct_time_index(self):
        startString = str(self.startyear) + '-' + str(self.startmonth) + '-' + str(self.startday) + ' 5:00:00'
        endString = str(self.startyear) + '-' + str(self.startmonth) + '-' + str(self.startday) + ' 19:00:00'
        startTimestamp = pd.Timestamp(startString)
        endTimestamp = pd.Timestamp(endString)
        timeIndex = []
        length = 0
        days = self.show_days()
        for i in (range(days + 1)):    
            temp = pd.date_range(start = startTimestamp + pd.DateOffset(i), end = endTimestamp + pd.DateOffset(i), freq='min')
            timeIndex.append(temp)   
            length = length + len(temp)
        return [length, timeIndex]    


"""
Data cleansing applied to the sloar time index, where hour variation occurs between 5am to 7pm.
This class includes functions of value correction, data converting to list, normalized value extraction.
But no sensitivity test is conducted in grouping signals analysis.
Input: filename, startdate and enddate
Output: file information, including:
1. Cleansing data, type: list 
2. Normalized coefficient: type: int
"""
class SOLAR():
    #time_series = pd.read_csv("../../Data/st-lucia-11-41/UQCentre-11-41.csv", parse_dates=True, index_col = 'time', dayfirst=True)
    #ts = pd.DataFrame(time_series) 
    #ts_T = ts.index
    #ts_V = ts["power (W)"]
    #t = SOLAR(2018,1,1,2018,4,1, ts_T, ts_V)
    def __init__(self, ts_T, ts_V):
        self.ts_T = ts_T
        self.ts_v = ts_V
             
    """
    Shows the real row number in the csv file where clock jitter error occurs.
    If it shows 579, then between 578 and 579, there's a missing data.
    """
    def data_diagnosis(self, correctionIndex):
        fullLength = correctionIndex[0]
        correctIndex = correctionIndex[1]
        counter = 0
        #[index of error, correct stamp, false stamp]
        falseList = []
        #result shows length, errorlist
        result = []
        for group in correctIndex:
            for stamp in group:
                if (self.ts_T[counter] != stamp):
                    falseList.append(counter + 2)
                    falseList.append(stamp)
                    falseList.append(self.ts_T[counter])
                else:
                    counter += 1
        return [fullLength, falseList]
    
    """
    [0,1,2,3,4,5,6,7,8]
    [1,2,3,4,5,6,7,8,9]
    [1,2,3,4,5,7,8,9,10]
    Clean the above data with inserting a 6 between 5 and 7.
    Also calculate the normalized coefficient of the cleansed data.
    Input: the correct time index from correct_time_index(self)
    Output: an output package with normalization and cleansed data
    """
    def data_cleansing(self, correctionIndex):
        correctIndex = correctionIndex[1]
        counter = 0
        correctValue = []
        correctTimeFlag = 1
        maximumValue = 0
        minimumValue = 0
        for group in correctIndex:
            for stamp in group:
                if (self.ts_T[counter] != stamp):
                    correctTimeFlag = 0
                    compensation = (self.ts_v[counter] + self.ts_v[counter - 1]) / 2
                    correctValue.append(compensation)
                    if(compensation > maximumValue):
                        maximumValue = compensation
                    elif (compensation < minimumValue):
                        minimumValue = compensation
                else:
                    correctValue.append(self.ts_v[counter])
                    if(self.ts_v[counter] > maximumValue):
                        maximumValue = self.ts_v[counter]
                    elif (self.ts_v[counter] < minimumValue):
                        minimumValue = self.ts_v[counter]                  
                    counter += 1
        normalized = maximumValue - minimumValue
        package = [correctValue, normalized]
        if(correctTimeFlag == 1):
            package.append(self.ts_T)
        else:
            package.append([])
        return package    

"""
Propose the data from the fileList, this will include data cleansing process and generate a clean dict of data
"""
class DATA():
    def __init__(self, startyear, startmonth, startday, endyear, endmonth, endday, filelist, index, valueIndex):
        correct = TIME(startyear, startmonth, startday, endyear, endmonth, endday)
        self.timeIndex = [startyear, startmonth, startday, endyear, endmonth, endday]
        self.realTime = correct.correct_time_index()
        self.filelist = filelist
        self.index = index
        self.valueIndex = valueIndex
                      
    def extraction(self, filename, index, valueIndex):
        time_series = pd.read_csv(filename, parse_dates=True, index_col = index, dayfirst=True)  
        ts = pd.DataFrame(time_series)
        ts_T = ts.index
        ts_V = ts[valueIndex]    
        return [ts_T, ts_V]
    
    def cleanse_list(self, dataPackage, correctionIndex):
        clean = SOLAR(dataPackage[0], dataPackage[1])
        package = clean.data_cleansing(correctionIndex)

        return package
    """
    Generate the dynamic index
    """
    def get_index(self, dataLength, dycoeff):
        indexList = []
        subLength = dataLength / dycoeff
        for i in range(dycoeff):
            if(int((i + 1) * subLength) > dataLength):
                indexList.append([int(i * subLength), int(dataLength)])
            else:   
                indexList.append([int(i * subLength), int((i + 1) * subLength)])
        return indexList  
    
    def get_sub_dict(self, cleanedDict, rawdict, startIndex, endIndex):
        subDataDict = {}
        subRawDict = {}
        subLength = endIndex - startIndex 
        for key in cleanedDict:
            subDataDict[key] = [cleanedDict[key][0][startIndex: endIndex], cleanedDict[key][1]]
            subRawDict[key] = rawdict[key][startIndex:endIndex]
        return [subDataDict, subRawDict, subLength] 
    
    def group_clean(self, dycoeff):
        cleanedDict = {}
        rawDict = {}
        keyList = []
        fullLength = self.realTime[0]
        realTime = []
        groupList = []
        grouprawList = []
        fullLengthList = []
        for key in self.filelist:
            dataInfo = self.extraction(self.filelist[key], self.index, self.valueIndex)
            cleaned = self.cleanse_list(dataInfo, self.realTime)
            cleanedDict[key] = cleaned
            #print(cleanedDict[key][1])
            rawDict[key] = cleaned[0]
            keyList.append(key)
            if (len(cleaned[2]) != 0):
                realTime = cleaned[2]     
        
        indexList = self.get_index(fullLength, dycoeff)
        for ran in indexList:
            package = self.get_sub_dict(cleanedDict, rawDict, ran[0], ran[1])
            
            groupList.append(package[0])
            grouprawList.append(package[1])
            fullLengthList.append(package[2])
        tof = self.get_original_size(self.timeIndex, grouprawList)
        return [keyList, groupList, fullLengthList, realTime, grouprawList, tof]
    
    def get_original_size(self, timeIndex, grouprawList):
        tof = 0
        f= open("ori", "w+")
        for i in timeIndex:
            f.write("%s" % i + ' ')
        f.write('\n')    
        for sub in grouprawList:
            for key in sub:
                for i in sub[key]:
                    f.write("%s" % i + '\n')
        f.close() 
        tof = os.path.getsize("ori")
        return tof
                
        
        
        
    
        
        