from DATA import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import math
import sys
from decimal import Decimal
import os
import random
import itertools
from collections import OrderedDict
from scipy import stats

Zero = 0        
class TREE():
    def __init__(self, sortList, keyList):
        self.sortList = sortList
        self.locationList = keyList 
        self.size = len(keyList)
        
    """
    Get the dictionary to convert string name to int during encoding
    Input: None
    Ouput: number dicitonary
    """
    def get_encode_dict(self):
        numberDict = {}
        counter = 0
        for name in self.locationList:
            numberDict[name] = counter
            counter += 1 
        return numberDict
    
    """
    Get the dictionary to convert int to string name during encoding
    Input: None
    Ouput: number dicitonary
    """
    def get_decode_dict(self):
        stringDict = {}
        for num in range(len(self.locationList)):
            stringDict[num] = self.locationList[num]
        return stringDict    
            
        
    """
    Pair the name according to the row-to-column sequence with its corresponding value
    Input: Ascending or descending sequence
    Output: value dictionary
    {'a&b':0.98, ...}
    """
    def name_match_value(self, Type):
        valueDict = {}
        for i in range(self.size):
            for j in range(self.size):
                if(i == j):
                    pass
                else:
                    valueDict[self.locationList[i] + '&' + self.locationList[j]] = self.sortList[i][j]
        #ascending sequence
        if(Type == 0):
            sortedDict = dict(OrderedDict(sorted(valueDict.items(), key=lambda x: x[1], reverse=True)))
        #descending sequence
        elif(Type == 1):
            sortedDict = dict(OrderedDict(sorted(valueDict.items(), key=lambda x: x[1])))
        return sortedDict
 
    
    """
    Get the minimum group from the sorted dictionary that contains every element from the key list.
    Input: sorted dictionary
    Output: 
    1. the minimum dictionary pairs containing parent and shild
    2. the parent's roster
    3. the child's roster
    [parent1, child1] [parent1] [child1]
    [parent2, child2] [parent2] [child2]
    [parent3, child3] [parent3] [child3]
    ...
    """
    def chain_connection(self, sortedDict):
        roster = set()
        sortedDict = sortedDict
        treeDict = {}
        branchList = []
        parent = []
        son = []        
        for key in sortedDict:
            [loc1,loc2] = key.split("&")
            if (len(roster) < self.size):
                if((loc1 in roster) and (loc2 in roster)):
                    pass
                elif((loc1 in roster) and (loc2 not in roster)):
                    #show exsistence
                    roster.add(loc2) 
                    addFlag = 0
                    #search if loc1 is the parent of the exsisted tree
                    for key in treeDict:
                        #if it is append it's child list and break
                        if(key == loc1):
                            treeDict[key].append(loc2)
                            addFlag = 1
                            break
                    #if not, flag will remain 0, so creat a new parent dictionary index
                    if(addFlag == 0):
                        treeDict[loc1] = []
                        treeDict[loc1].append(loc2)                            
                elif((loc1 not in roster) and (loc2 in roster)):
                    #show exsistence
                    roster.add(loc1) 
                    addFlag = 0
                    #search if loc1 is the parent of the exsisted tree
                    for key in treeDict:
                        #if it is append it's child list and break
                        if(key == loc2):
                            treeDict[key].append(loc1)
                            addFlag = 1
                            break
                    #if not, flag will remain 0, so creat a new parent dictionary index
                    if(addFlag == 0):
                        treeDict[loc2] = []
                        treeDict[loc2].append(loc1)    
                elif((loc1 not in roster) and (loc2 not in roster)):
                    #show exsistence
                    roster.add(loc1)
                    roster.add(loc2)
                    #creat branch
                    treeDict[loc1] = []
                    treeDict[loc1].append(loc2)   
            else:
                break
        for key in treeDict:
            tempBranch = []
            for child in treeDict[key]:
                tempBranch.append([key, child])
                parent.append(key)
                son.append(child)
            branchList += tempBranch
        return [branchList, parent, son]        
   
    
    """
    Take the raw tree list and synthesize the list into different branches with multiple nodes
    Input: 
    1. tree dictionary
    Output: 
    1. branch list
    2. parent list
    """
    def find_family_branch(self, branchList):
        noMoreRepetition = 0
        branch = branchList
        branchDict = {}
        while True:
            #plantation variables
            #for parent twig
            extraction = []
            #for base twing
            truncation = []
            #for combination
            completion = [] 
            #find the entry index
            headList = []
            for twig in branch:
                headList.append(twig[0])
            #iterate every head index
            for entry in headList:
                index = headList.index(entry)
                #get ready for extraction of current branch
                extraction = branch[index]
                #iterate the current branches
                for twig in branch:
                    # time to connect head to the other body in current twig
                    if (entry in twig) and (twig[0] != entry):
                        noMoreRepetition = 1
                        truncation = twig[: twig.index(entry) + 1]
                        if(truncation in branch):
                            del branch[branch.index(truncation)] 
                        del branch[branch.index(extraction)]                     
                        completion = truncation + extraction[1:]
                        branch.append(completion)                    
                        break
                #break the iteration
                if(noMoreRepetition == 1):
                    break
        
            if(noMoreRepetition == 0):
                break
            else:
                noMoreRepetition = 0
        
        
        for index in range(len(branch)):
            header = branch[index][0]
            if(header in branchDict):
                branchDict[header].append(branch[index])
            else:
                branchDict[header] = [branch[index]]
        return branchDict

    """
    Get the coefficient of correlation for the aggregated data point, and find the final branch of the tree
    Input:
    1. The original branch list
    2. The parent of the branch list
    3. The son of the branch list
    4. The sorted correlation dictionary
    5. Ascending for descending type
    6. Counter for recursion
    Output:
    1. The parent coefficient for final mapping
    2. The raw branches of the tree
    3. The parent list
    """
    def find_family_coeff(self, branchDict, sortedDict, Type):        
        dadCoeff = {}
        parentList = list(branchDict.keys())
        #fix one parent ID and go through all the other branches
        for parent in parentList:
            tempCoeff = []
            maxCor = -1000000000000 
            minCor = 1000000000000            
            #except the branches where the parent ID grow, go through all the branches
            for key in branchDict:              
                if (key == parent):
                    continue
                #the branch to be examined
                checkingBranch = branchDict[key]
                #each branch has some twigs, but they share the same parent node
                for twig in checkingBranch: 
                    #the element in the twig has the correlation with the parent node
                    for element in twig:
                        loc1 = element
                        loc2 = parent
                        cor = sortedDict[loc1 +'&'+ loc2]
                        if(Type == 0):
                            if (cor > maxCor):
                                maxCor = cor
                                tempCoeff = [loc1, loc2, maxCor]  
                        elif(Type == 1):
                            if (cor < minCor):
                                minCor = cor
                                tempCoeff = [loc1, loc2, minCor]  
            dadCoeff[tempCoeff[0]+'&'+tempCoeff[1]] = tempCoeff[2]
        if(Type == 0):
            Key = max(dadCoeff, key=dadCoeff.get)
        elif(Type == 1):
            Key = max(dadCoeff, key=dadCoeff.get)
        ID = Key.split('&')
        outcome = ID + [dadCoeff[Key]]
        return outcome
    
    """
    Get the final tree of the chain compression
    Input: 
    1. type of the matrix sequence
    2. counter for recursion
    Ouput:
    1. The final tree list
    """
    def find_family_stem(self, Type):       
        final = []
        corSeq = self.name_match_value(Type)
        corPackage = self.chain_connection(corSeq)
               
        #find family branch
        branchDict = self.find_family_branch(corPackage[0]) 
          
        iteration = len(branchDict.keys()) - 1
        for num in range(iteration):
            #find coefficient
            
            coeff = self.find_family_coeff(branchDict, corSeq, Type)
            baseID = coeff[0]
            parentID = coeff[1]
            #plantation variables
            #for parent twig
            extraction = []
            #for base twing
            trunID = ''
            truncation = []
            #for combination
            completion = []
            
            #search the truncation and base branch info
            for branchName in branchDict:
                for twig in branchDict[branchName]:
                    if (baseID in twig):
                        truncation = twig[: twig.index(baseID) + 1]
                        #delete the twig if truncation is the twig
                        if(truncation in branchDict[branchName]):
                            del branchDict[branchName][branchDict[branchName].index(truncation)]                        
                        trunID = branchName
            
            #extract the replaced parent twigs
            for twig in branchDict[parentID]:
                extraction = twig
                completion = truncation + extraction
                branchDict[trunID].append(completion)
            del branchDict[parentID]
        for branchName in branchDict:
            for twig in branchDict[branchName]:
                final.append(twig)
        return final
    """
    Encode the optimized tree chain from the strings to number, according to the number dict
    Input: Tree list
    Output: Tree list encoded
    """
    def encode_tree(self, tree):
        encodetree = []
        numberDict = self.get_encode_dict()
        for branch in tree:
            temptree = []
            for name in branch:
                temptree.append(numberDict[name])
            encodetree.append(temptree)
        return encodetree




class GPS():
    def __init__(self, coordDict, keyList):
        self.coordDict = coordDict
        self.locationList = keyList 
        self.size = len(keyList)
    
    def dms_to_dd(self):
        degreeDict = {}
        for item in self.coordDict:
            coordinate = []
            for location in self.coordDict[item]:
                (d,m,s) = location
                dd = d + float(m)/60 + float(s)/3600
                coordinate.append(dd)
            degreeDict[item] = coordinate
        return degreeDict   
    
    def get_distance(self,coord1,coord2):
        R = 6371; # Radius of the earth in km
        lon1 = coord1[0]
        lon2 = coord2[0]
        lat1 = coord1[1]
        lat2 = coord2[1]
        dLat = np.deg2rad(lat2-lat1);  # deg2rad below
        dLon = np.deg2rad(lon2-lon1); 
        a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(np.deg2rad(lat1)) * math.cos(np.deg2rad(lat2)) * math.sin(dLon/2) * math.sin(dLon/2); 
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)); 
        d = 1000 * R * c; # Distance in m
        return d;
    
    def distance_matrix(self):
        matrix = []
        #Get coordination in degree 
        degreeDict = self.dms_to_dd() 
        for row in self.locationList:
            temp = []
            for col in self.locationList:
                temp.append(self.get_distance(degreeDict[row], degreeDict[col]))
            matrix.append(temp)
        return matrix
        
    def get_random_pairs(self):
        #Get coordination in degree 
        degreeDict = self.dms_to_dd()
        #Sort every location name into a list
        
        # Generate all possible non-repeating pairs
        pairs = list(itertools.combinations(self.locationList, 2))     
        # Randomly shuffle these pairs
        random.shuffle(pairs)
        return pairs    
    
    def get_pairs_name(self):
        #Get random pair
        pairList = self.get_random_pairs()
        pairName = []
        for item in pairList:
            pairName.append(item[0]+'&'+item[1])  
        return pairName
    
    def distance_pair(self):
        #distanceList = []
        distanceDict = {}
        #Get random pair
        pairList = self.get_random_pairs()
        #Get coordination in degree 
        degreeDict = self.dms_to_dd()        
        for item in pairList:
            distanceDict[item[0]+'&'+item[1]] = self.get_distance(degreeDict[item[0]],degreeDict[item[1]])
        sortedDict = dict(OrderedDict(sorted(distanceDict.items(), key=lambda x: x[1])))
        return sortedDict
    
    def chain_connection(self):
        roster = set()
        sortedDict = self.distance_pair()
        shortDict = {}
        for key in sortedDict:
            [loc1,loc2] = key.split("&")
            if (len(roster) != self.size):
                shortDict[key] = sortedDict[key]
                roster.add(loc1)
                roster.add(loc2)
        return shortDict    
    
    
class LINEAR():
    """
    Operate linear regression to random pair of signals.
    It uses the location name list to iterate and form the n * n matrix of lm parameters.
    The lm is operated based on one raw data stream and one APCA compressed base stream.
    """
    def __init__(self, comparedDict, dataDict, locationList):
        self.dataDict = dataDict 
        self.locationList = locationList
        self.comparedDict = comparedDict   
        
    """
    Use the linear model in scipy and register the coefficients to a list.
    Input: 
    1. base signal stream
    2. raw signal stream
    Output:
    1. Coefficient bundle
    """
    def get_coeff(self, x, y):
        coeff = []
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        rSquared = r_value**2
        coeff = [slope, intercept, rSquared, p_value, std_err]
        return coeff
    
    """
    Generate the lm matrix for each pair of the signals. 
    This includes the matrices of each parameters.
    Input: None
    Output:The matrix dictionary using parameter's name as indexes, 
    and access the corresponding matrices of that parameter.
    """
    def APCA_lm_matrix(self):
        matrix = {}
        matrix['slope'] = []
        matrix['intercept'] = []
        matrix['rSquared'] = []
        matrix['p_value'] = []
        matrix['std_err'] = []     
        #Get coordination in degree 
        for row in self.locationList:
            tempSlope = []
            tempIntercept = []
            temprSquared = []  
            tempp = [] 
            tempstderr = [] 
            for col in self.locationList:
                coeff = self.get_coeff(self.comparedDict[row], self.dataDict[col][0])
                tempSlope.append(coeff[0])
                tempIntercept.append(coeff[1])
                temprSquared.append(coeff[2])
                tempp.append(coeff[3])
                tempstderr.append(coeff[4])
            matrix['slope'].append(tempSlope)
            matrix['intercept'].append(tempIntercept)
            matrix['rSquared'].append(temprSquared)
            matrix['p_value'].append(tempp)
            matrix['std_err'].append(tempstderr) 
        return matrix 
    
    """
    Write the lm matrix to the csv file
    Input: The matrix dictionary from the above function.
    Output: The csv file.
    """
    def lm_matrix_to_frame(self, matrix):
        slope = []
        intercept = []
        rSquared = []
        p_value = []
        std_err = []        
        for key in matrix:
            header = [key] + self.locationList
            csvList = []
            #iterate the two demensional matrix
            for num in range(len(self.locationList)):
                rowInfo = tuple([self.locationList[num]] + matrix[key][num])
                csvList.append(rowInfo)
            df = pd.DataFrame.from_records(csvList, columns = header) 
            self.write_in_csv(df, key + "_matrix.csv") 
    
    
    """
    The residuals lists obtained from the y value and y hat. 
    The zero is recovered from the symbol registration so that 
    the reconstructed signal and preserve the zero values.
    Input:
    1. APCA base signal list:x
    2. Real target signal list: y
    3. slope: a
    4. intercept: b
    """
    def get_residuals(self, xList, yList, a, b):
        minimum = 0
        maximum = 0
        res = []
        real = []
        if (len(xList) != len(yList)):
            print('list not equal.\n')
        else:
            for num in range(len(yList)):
                yhat = a * xList[num] + b
                if(yList[num] == 0):
                    e = Zero
                else:
                    e = yList[num] - yhat
                res.append(e)  
                real.append(yList[num] - yhat)
        return [res, real]
    
    """
    Register the residual of each pair of the signal into the matrix.
    Input: The parameter matrix of the linear model to retrieve the slope and intercept values
    Output: The residual matrix with the corresponding base signal and target signal.
    """
    def APCA_residual_matrix(self, matrix):
        #Get coordination in degree 
        res = []
        realRes = []
        for i in range(len(self.locationList)):
            row = self.locationList[i]
            tempRes = []
            tempReal = []
            xList = self.comparedDict[row]
            for j in range(len(self.locationList)):                    
                col = self.locationList[j]
                yList = self.dataDict[col][0]
                a = matrix['slope'][i][j]
                b = matrix['intercept'][i][j]
                package = self.get_residuals(xList, yList, a, b)
                tempRes.append(package[0])
                tempReal.append(package[1])
            res.append(tempRes)
            realRes.append(tempReal)
        return [res, realRes]
    """
    Get the normalized standard deviation
    Input: The list of numbers
    Output: Normalized standard deviation
    """
    def coeff_of_variation(self, List):
        normailized = max(List) - min(List)
        test = np.array(List)
        return np.std(test) / normailized
    
    """
    Get the normalized standard deviation matrix
    Input: Residual matrix
    Output: Variation matrix
    """
    def get_variation(self, realRes):
        Var = []
        for i in range(len(realRes)):
            tempVar = []
            for j in range(len(realRes)):            
                if(i == j):
                    tempVar.append(0)
                else:
                    tempVar.append(self.coeff_of_variation(realRes[i][j]))
            Var.append(tempVar) 
        return Var
        
                

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
    Signal compression using normal APCA scheme based on normalized value
    The error tolerace in each data point holds constant
    Input: raw data list and normalized coefficient
    Output:
    1. The compressed signal list for further analysis.
    2. The file-input compressed list for file writing.
    """    
    def APCA_normal_Base_compression(self, compressList, normalize):
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
    
    """
    After the base compression, register into a dictionary.
    This will be used in the linear matrix configuration
    Input: None
    Output: Expanded compressed List and normal compressed List
    """
    """
    Remainder signal compression using normal APCA scheme based on the 
    normalized value
    Input: raw data list and normalized coefficient
    Output:
    1. The compressed signal list for further analysis.
    2. The file-input compressed list for file writing
    """   
    def APCA_normal_res_compression(self, compressList, rawListNormalize, slope, intercept, coeff):
        maxTolerance = (self.espmax * coeff) * rawListNormalize
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
            if (current == Zero): 
                maxValue = minValue = 0
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
                    compressedList.append([tempCounter, Zero]) 
                    APCAList += [Zero] * tempCounter 
                    
            #Tackle the non-zero case
            else:       
                # Check if previous one is the zero case
                if (zeroFlag == 1):
                    maxValue = minValue = current
                    compressedList.append([tempCounter, Zero]) 
                    APCAList += [Zero] * tempCounter 
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
    Recover the APCA signal from a residual APCA signal. This is used in chain compression
    """
    def get_recovered_APCA(self, APCAx, residualy, slope, intercept):
        resumeList = []     
        for i in range(len(residualy)):
            if (residualy[i] == Zero):
                temp = 0
                resumeList.append(temp) 
            else:
                temp = int(APCAx[i] * slope + intercept + residualy[i])
                resumeList.append(temp)
        return resumeList

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
    def SWING_normal_Base_compression(self, compressList, normalize):
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

    
    
        



class SIRCSCOM():
    """
    Discription: register data information of each single stream. In each file, 
    we make a two-dimensional dictionary to register streamming data information.
    Assumption made for the multi-stream data registration:
    1. Same time index
    2. Same size
    We have data stucture designed as:
    dataDict = {"advanced-6-5.csv": [[ValueList], Nomalized], ...} 
    """
    def __init__(self, dataDict, rawBaseDict, keyList, dataLength, espmax, decimal):#, dyCoeff   
        #Initialize data cleansing
        #list of all locations' name
        self.keyList = keyList
        #dictionary with [[values], nomalization]
        self.dataDict = dataDict
        #Correct size of one single data
        self.dataLength = dataLength
        #get real time index
        self.rawBaseDict = rawBaseDict
        #self.dyCoeff = dyCoeff
        
               
        
        #Compression
        self.decimal = decimal
        self.espmax = espmax
        self.com = APCACOM(self.dataDict, self.keyList, self.dataLength, self.espmax)   
        self.swcom = SWINGCOM(self.dataDict, self.keyList, self.dataLength, self.espmax) 
     
       
    """
    Most likely as the grouping method above, but support dynamic grouping
    """
    def dy_group(self, subRawBaseDict, subDataDict):
        #get linear regression information and put parameters into csv       
        lin = LINEAR(subRawBaseDict, subDataDict, self.keyList)
        lmMatrix = lin.APCA_lm_matrix()
        #correlation sequencing, from high to low
        rSquared = lmMatrix['rSquared']
        tree = TREE(rSquared, self.keyList)
        treechain = tree.find_family_stem(0)
        encodeTree = tree.encode_tree(treechain) 
        #encode and decode dictionary
        decodeDict = tree.get_decode_dict()         
        #Compression
        return [encodeTree, lin, decodeDict]
    
    """
    apca group compression
    """
    def sircs_apca_compression(self, coeff):
        baseIndexList = []
        totalGroupTime = 0
        APCAList = {}
        compressedList = {}  
        dataDict = self.dataDict
        rawBaseDict = self.rawBaseDict
        
        dyPackage = self.dy_group(rawBaseDict, dataDict)
        encodeTree = dyPackage[0]
        lin = dyPackage[1]
        decodeDict = dyPackage[2]
        
        com = APCACOM(dataDict, self.keyList, self.dataLength, self.espmax) 

        #encode the tree to the compressedList
        startBit = []
        for branch in encodeTree:
            pair = ['!'] + branch
            startBit += pair
            
        #base compression
        baseIndex = encodeTree[0][0]            
        baseIndexList.append(baseIndex)            
        baseParcel = com.APCA_normal_Base_compression(dataDict[decodeDict[baseIndex]][0], dataDict[decodeDict[baseIndex]][1]) 
        compressedList[decodeDict[baseIndex]] = baseParcel[0]  
        APCAList[decodeDict[baseIndex]] = baseParcel[1]
        #record slope information
        slopeRecorder = {}
        #record intercept information
        interceptRecorder = {}
        #base index are zero in both case
        slopeRecorder[decodeDict[baseIndex]] = 0
        interceptRecorder[decodeDict[baseIndex]] = 0   
        #residual compression
        for branch in encodeTree:
            for index in range(len(branch)):       
                #skip if encounter base signal or shared node signal
                if str(branch[index]) in compressedList:
                    continue
                #start compression
                else:
                    #get lm slope and intercept from the previous APCA                     
                    lmCoeff = lin.get_coeff(APCAList[decodeDict[branch[index - 1]]], dataDict[decodeDict[branch[index]]][0])
                    slope = lmCoeff[0]
                    intercept = lmCoeff[1]
                    slopeRecorder[decodeDict[branch[index]]] = slope
                    interceptRecorder[decodeDict[branch[index]]] = intercept
                    
                    #get the residual list based on lm coefficient
                    resPackage = lin.get_residuals(APCAList[decodeDict[branch[index - 1]]], dataDict[decodeDict[branch[index]]][0], slope, intercept)
                    rawResidual = resPackage[0]
                    
                    resParcel = com.APCA_normal_res_compression(rawResidual, dataDict[decodeDict[branch[index]]][1], slope, intercept, coeff)
                    
                    #update compressedList here
                    compressedList[decodeDict[branch[index]]] = resParcel[0]
                    #estimate the current APCA signal
                    APCARes = resParcel[1] 
                    
                    APCAResidual = com.get_recovered_APCA(APCAList[decodeDict[branch[index - 1]]], APCARes, slope, intercept)
                    #register APCA signal to the APCAList
                    
                    APCAList[decodeDict[branch[index]]] = APCAResidual                    
        #print(len(slopeRecorder))
        return [startBit, slopeRecorder, interceptRecorder, compressedList, APCAList]   
    
    """
     group compression
    """
    def sircs_swing_compression(self, coeff):
        baseIndexList = []
        totalGroupTime = 0
        SWINGList = {}
        compressedList = {}  
        dataDict = self.dataDict
        rawBaseDict = self.rawBaseDict
        
        dyPackage = self.dy_group(rawBaseDict, dataDict)
        encodeTree = dyPackage[0]
        lin = dyPackage[1]
        decodeDict = dyPackage[2]
        
        com = SWINGCOM(dataDict, self.keyList, self.dataLength, self.espmax) 

        #encode the tree to the compressedList
        startBit = []
        for branch in encodeTree:
            pair = ['!'] + branch
            startBit += pair
            
        #base compression
        baseIndex = encodeTree[0][0]            
        baseIndexList.append(baseIndex)            
        baseParcel = com.SWING_normal_Base_compression(dataDict[decodeDict[baseIndex]][0], dataDict[decodeDict[baseIndex]][1]) 
        compressedList[decodeDict[baseIndex]] = baseParcel[0]  
        SWINGList[decodeDict[baseIndex]] = baseParcel[1]
        #record slope information
        slopeRecorder = {}
        #record intercept information
        interceptRecorder = {}
        #base index are zero in both case
        slopeRecorder[decodeDict[baseIndex]] = 0
        interceptRecorder[decodeDict[baseIndex]] = 0   
        #residual compression
        for branch in encodeTree:
            for index in range(len(branch)):       
                #skip if encounter base signal or shared node signal
                if str(branch[index]) in compressedList:
                    continue
                #start compression
                else:
                    #get lm slope and intercept from the previous APCA                     
                    lmCoeff = lin.get_coeff(SWINGList[decodeDict[branch[index - 1]]], dataDict[decodeDict[branch[index]]][0])
                    slope = lmCoeff[0]
                    intercept = lmCoeff[1]
                    slopeRecorder[decodeDict[branch[index]]] = slope
                    interceptRecorder[decodeDict[branch[index]]] = intercept
                    
                    #get the residual list based on lm coefficient
                    resPackage = lin.get_residuals(SWINGList[decodeDict[branch[index - 1]]], dataDict[decodeDict[branch[index]]][0], slope, intercept)
                    rawResidual = resPackage[0]
                    
                    resParcel = com.SWING_normal_res_compression(rawResidual, dataDict[decodeDict[branch[index]]][1], slope, intercept, coeff)
                    
                    #update compressedList here
                    compressedList[decodeDict[branch[index]]] = resParcel[0]
                    #estimate the current APCA signal
                    SWINGRes = resParcel[1] 
                    
                    SWINGResidual = com.get_recovered_SWING(SWINGList[decodeDict[branch[index - 1]]], SWINGRes, slope, intercept)
                    #register APCA signal to the SWINGList
                    
                    SWINGList[decodeDict[branch[index]]] = SWINGResidual                    
        #print(len(slopeRecorder))
        return [startBit, slopeRecorder, interceptRecorder, compressedList, SWINGList]      
    
class SIRCSDECOM(): 
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
        slopeList = []
        interceptList = []
        subList = []
        #{1: '....csv'}
        nameDict = {}
        for i in range(len(self.compressedList)):
            if (self.compressedList[i][0] == '!'):
                sliceIndex.append(i)
                groupList.append(self.compressedList[i][1:])
                #[0],[0, 567] 
            if (self.compressedList[i][0] == '?'):
                if(self.compressedList[i - 1][0] == '!'):
                    slopeList.append(self.compressedList[i][1:])  
                elif (self.compressedList[i - 1][0] == '?'):
                    interceptList.append(self.compressedList[i][1:])  
       
        for i in range(len(sliceIndex)):
            # the last one
            if (i == len(sliceIndex) - 1):
                temp = [groupList[i], slopeList[i], interceptList[i]] + self.compressedList[(sliceIndex[i] + 1):]
                subList.append(temp)
            else:
                temp = [groupList[i], slopeList[i], interceptList[i]] + self.compressedList[(sliceIndex[i] + 1) : sliceIndex[i + 1]]
                subList.append(temp)   
        return subList    
   
    
   
    def recover_tree_chain(self, treeChain):
        tree = []
        branch = []
        for i in range(len(treeChain)):
            if (treeChain[i] == '!') :
                tree.append(branch)
                branch = []
            elif (i == len(treeChain) - 1):
                branch.append(treeChain[i])
                tree.append(branch)
                branch = []                
            else:
                branch.append(treeChain[i])     
        return tree
            
            
        
    def sircs_apca_decompression(self):
        timeString = self.get_time_index()
        subList = self.slice_group()
        nameDict = {}
        recoveredDict = {}
        outputDict = {}
        for i in range(len(subList)):
            sliceList = subList[i]
            treeChain = sliceList[0]
            slopeList = sliceList[1]
            interceptList = sliceList[2]
            tree = self.recover_tree_chain(treeChain)
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
                recoveredDict[key] = resumeList
            APCARecoveredDict = {}
            for branch in tree:
                for index in range(len(branch)):
                    #skip if encounter base signal or shared node signal
                    if branch[index] in APCARecoveredDict:
                        continue
                    #start compression
                    else:   
                        slope = float(slopeList[int(branch[index])])
                        intercept = float(interceptList[int(branch[index])])
                        
                        #base
                        if (slope == 0) and (intercept == 0):
                            resumeList = []
                            for i in range(len(recoveredDict[branch[index]])):
                                temp = int(float(recoveredDict[branch[index]][i]))
                                resumeList.append(temp)                     
                            if (branch[index] in APCARecoveredDict):
                                APCARecoveredDict[branch[index]]  += resumeList
                            else:
                                APCARecoveredDict[branch[index]]  = resumeList 
                        #residual
                        else:
                            resumeList = []   
                            for i in range(len(recoveredDict[branch[index]])):
                                res = float(recoveredDict[branch[index]][i])
                                origin = float(APCARecoveredDict[branch[index - 1]][i])
                                if(res == Zero):
                                    temp = 0
                                else:
                                    temp = int(origin * slope + intercept + res)
                                resumeList.append(temp) 
                            """
                            if(branch[index] == '2'):
                                print(slope)
                                print(intercept)
                                print(APCARecoveredDict[branch[index - 1]])
                                print(recoveredDict[branch[index]])
                            """
                            if (branch[index] in APCARecoveredDict):
                                APCARecoveredDict[branch[index]]  += resumeList
                            else:
                                APCARecoveredDict[branch[index]]  = resumeList                             

            for key in APCARecoveredDict:
                if (key in outputDict):
                    outputDict[key] += APCARecoveredDict[key]
                else:
                    outputDict[key] = APCARecoveredDict[key] 
        return [outputDict, timeString, nameDict]

    def sircs_swing_decompression(self):
        timeString = self.get_time_index()
        subList = self.slice_group()
        nameDict = {}
        recoveredDict = {}
        outputDict = {}
        for i in range(len(subList)):
            sliceList = subList[i]
            treeChain = sliceList[0]
            slopeList = sliceList[1]
            interceptList = sliceList[2]
            tree = self.recover_tree_chain(treeChain)
            package = self.slice_list(sliceList)
            sortedDict = package[0]
            nameDict = package[1]
            for key in sortedDict:
                resumeList = []
                compressedList = sortedDict[key]
                for i in compressedList:
                    if (len(i) == 1):
                        if(i[0] == Zero):
                            resumeList.append(Zero)
                        else:
                            resumeList.append(float(i[0]))
                    elif (len(i) == 2):
                        if(i[1] == Zero):
                            for a in range(int(i[0])):
                                resumeList.append(Zero)
                        else:
                            for a in range(int(i[0])):
                                resumeList.append(float(i[1]))                
                    else:
                        for index in range(int(i[2])):
                            y = float(i[0]) + index * float(i[1])
                            resumeList.append(y)
                recoveredDict[key] = resumeList
            SWINGRecoveredDict = {}
            for branch in tree:
                for index in range(len(branch)):
                    #skip if encounter base signal or shared node signal
                    if branch[index] in SWINGRecoveredDict:
                        continue
                    #start compression
                    else:   
                        slope = float(slopeList[int(branch[index])])
                        intercept = float(interceptList[int(branch[index])])

                        #base
                        if (slope == 0) and (intercept == 0):
                            resumeList = []
                            for i in range(len(recoveredDict[branch[index]])):
                                temp = int(float(recoveredDict[branch[index]][i]))
                                resumeList.append(temp)                     
                            if (branch[index] in SWINGRecoveredDict):
                                SWINGRecoveredDict[branch[index]]  += resumeList
                            else:
                                SWINGRecoveredDict[branch[index]]  = resumeList 
                        #residual
                        else:
                            resumeList = []   
                            for i in range(len(recoveredDict[branch[index]])):
                                res = float(recoveredDict[branch[index]][i])
                                origin = float(SWINGRecoveredDict[branch[index - 1]][i])
                                if(res == Zero):
                                    temp = 0
                                else:
                                    temp = int(origin * slope + intercept + res)
                                resumeList.append(temp) 
                            """
                            if(branch[index] == '2'):
                                print(slope)
                                print(intercept)
                                print(SWINGRecoveredDict[branch[index - 1]])
                                print(recoveredDict[branch[index]])
                            """
                            if (branch[index] in SWINGRecoveredDict):
                                SWINGRecoveredDict[branch[index]]  += resumeList
                            else:
                                SWINGRecoveredDict[branch[index]]  = resumeList                             

            for key in SWINGRecoveredDict:
                if (key in outputDict):
                    outputDict[key] += SWINGRecoveredDict[key]
                else:
                    outputDict[key] = SWINGRecoveredDict[key] 
        return [outputDict, timeString, nameDict]