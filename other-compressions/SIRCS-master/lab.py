from tkinter import *
from compress import *
from GUI import *
from exe import *
from DATA import *
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
import random
import itertools
import os
from prettytable import PrettyTable

dataset = 1
group = 2
savefile = "/Users/GaryYe/Desktop/lab/com/"
performanceLabel = ['Error Tolerance (%)', 'APCA', 'SWING', 'SIRCS (APCA, g = ' + str(group) + ')', 'SIRCS (SWING, g = ' + str(group) + ')', 'GAMPS (c = 0.4, d = 5, g = ' + str(group) + ')']
precisionLabel = ['Compression Ratio (raw / compressed)', 'APCA', 'SWING', 'SIRCS (APCA, g = ' + str(group) + ')', 'SIRCS (SWING, g = ' + str(group) + ')', 'GAMPS (c = 0.4, d = 5, g = ' + str(group) + ')']
groupingLabel = ['Error Tolerance (%)', 'g = 1', 'g = 2', 'g = 4', 'g = 5', 'g = 10', 'g = 20']
groupingLabel1 = ['Compression Ratio (raw / compressed)', 'g = 1', 'g = 2', 'g = 4', 'g = 5', 'g = 10', 'g = 20']
nodeLabel = ['Number of Sensors', 'e = 1%', 'e = 3%', 'e = 5%', 'e = 7%', 'e = 9%']

package_cr = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/performance_Compression_Ratio.csv",
              'Compression Ratio', 'Error Tolerance (%)', 'Compression Ratio (raw / compressed)']
package_rmse = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/performance_NRMSE.csv",
              'NRMSE', 'Error Tolerance (%)', 'NRMSE (%)']
package_ct = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/performance_Compression_Time.csv",
              'Compression Time', 'Error Tolerance (%)', 'Compression Time (s)']
package_pre = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/precision_test.csv",
              'Precision Test', 'Compression Ratio (raw / compressed)', 'NRMSE (%)']

package_node_apca = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/0_node_test.csv",
              'Network Density SICS (APCA)', 'Number of Sensors', 'Compression Ratio (raw / compressed)']
package_node_swing = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/1_node_test.csv",
              'Network Density SICS (SWING)', 'Number of Sensors', 'Compression Ratio (raw / compressed)']
package_node_gamps = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/2_node_test.csv",
              'Network Density GAMPS', 'Number of Sensors', 'Compression Ratio (raw / compressed)']

package_pre_gr_apca = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/pregr_sircsapca_test.csv",
              'Group Precision Test (SIRCS APCA)', 'Compression Ratio (raw / compressed)', 'NRMSE (%)']
package_pre_gr_swing = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/pregr_sircsswing_test.csv",
              'Group Precision Test (SIRCS SWING)', 'Compression Ratio (raw / compressed)', 'NRMSE (%)']
package_pre_gr_gamps = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/pregr_gamps_test.csv",
              'Group Precision Test (GAMPS)', 'Compression Ratio (raw / compressed)', 'NRMSE (%)']

package_gr_apca1 = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/1_grouping_sircsapca_test.csv",
              'Grouping Test CR', 'Error Tolerance (%)', 'Compression Ratio (raw / compressed)']
package_gr_apca2 = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/2_grouping_sircsapca_test.csv",
              'Grouping Test NRMSE', 'Error Tolerance (%)', 'NRMSE (%)']
package_gr_apca3 = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/3_grouping_sircsapca_test.csv",
              'Grouping Test CT', 'Error Tolerance (%)', 'Compression Time (s)']

package_gr_swing1 = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/1_grouping_sircsswing_test.csv",
              'Grouping Test CR', 'Error Tolerance (%)', 'Compression Ratio (raw / compressed)']
package_gr_swing2 = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/2_grouping_sircsswing_test.csv",
              'Grouping Test NRMSE', 'Error Tolerance (%)', 'NRMSE (%)']
package_gr_swing3 = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/3_grouping_sircsswing_test.csv",
              'Grouping Test CT', 'Error Tolerance (%)', 'Compression Time (s)']

package_gr_gamps1 = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/1_grouping_gamps_test.csv",
              'Grouping Test CR', 'Error Tolerance (%)', 'Compression Ratio (raw / compressed)']
package_gr_gamps2 = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/2_grouping_gamps_test.csv",
              'Grouping Test NRMSE', 'Error Tolerance (%)', 'NRMSE (%)']
package_gr_gamps3 = ["/Users/GaryYe/Desktop/lab/11-10-11-29/no_gamps_g_1/3_grouping_gamps_test.csv",
              'Grouping Test CT', 'Error Tolerance (%)', 'Compression Time (s)']

#1-21-2018 
if (dataset == 1):
    pathChange = "../../Data/st-lucia-1-21/"
    filelistDay = {"0": pathChange + "18012100.csv", 
                        "1": pathChange + "18012100-2.csv", 
                        "2": pathChange + "18012100-3.csv",             
                "3": pathChange + "18012100-4.csv",         
                "4": pathChange + "18012100-5.csv", 
                "5": pathChange + "18012100-6.csv",
                "6": pathChange + "18012100-7.csv",
                "7": pathChange + "18012100-8.csv",
                "8": pathChange + "18012100-9.csv",
                "9": pathChange + "18012100-10.csv",
                "10": pathChange + "18012100-11.csv",
                "11": pathChange + "18012100-12.csv",
                "12": pathChange + "18012100-13.csv",
                "13": pathChange + "18012100-14.csv",
                "14": pathChange + "18012100-15.csv",
                "15": pathChange + "18012100-16.csv",
                "16": pathChange + "18012100-17.csv",
                "17": pathChange + "18012100-18.csv",
                "18": pathChange + "18012100-19.csv",
                "19": pathChange + "18012100-20.csv",
                "20": pathChange + "18012100-21.csv",
                "21": pathChange + "18012100-22.csv",
                "22": pathChange + "18012100-23.csv",
                "23": pathChange + "18012100-24.csv",
                "24": pathChange + "18012100-25.csv",
                "25": pathChange + "18012100-26.csv",
                "26": pathChange + "18012100-27.csv"                }
    
    name =  {"0":"18012100.csv", 
             "1": "18012100-2.csv", 
                "2": "18012100-3.csv",             
                "3": "18012100-4.csv",         
                "4": "18012100-5.csv", 
                "5": "18012100-6.csv",
                "6": "18012100-7.csv",
                "7": "18012100-8.csv",
                "8": "18012100-9.csv",
                "9": "18012100-10.csv",
                "10": "18012100-11.csv",
                "11": "18012100-12.csv",
                "12": "18012100-13.csv",
                "13": "18012100-14.csv",
                "14": "18012100-15.csv",
                "15": "18012100-16.csv",
                "16": "18012100-17.csv",
                "17": "18012100-18.csv",
                "18": "18012100-19.csv",
                "19": "18012100-20.csv",
                "20": "18012100-21.csv",
                "21": "18012100-22.csv",
                "22": "18012100-23.csv",
                "23": "18012100-24.csv",
                "24": "18012100-25.csv",
                "25": "18012100-26.csv",
                "26": "18012100-27.csv"                }
    timeRange = [2018,1,21,2018,1,21]
    csv = "/Users/GaryYe/Desktop/lab/1-21/"
#6-2-2018
elif (dataset == 2):
    pathChange = "../../Data/st-lucia-6-2/"
    filelistDay = {"0": pathChange + "18060200.csv", 
                        "1": pathChange + "18060200-2.csv", 
                        "2": pathChange + "18060200-3.csv",             
                "3": pathChange + "18060200-4.csv",         
                "4": pathChange + "18060200-5.csv", 
                "5": pathChange + "18060200-6.csv",
                "6": pathChange + "18060200-7.csv",
                "7": pathChange + "18060200-8.csv",
                "8": pathChange + "18060200-9.csv",
                "9": pathChange + "18060200-10.csv",
                "10": pathChange + "18060200-11.csv",
                "11": pathChange + "18060200-12.csv",
                "12": pathChange + "18060200-13.csv",
                "13": pathChange + "18060200-14.csv",
                "14": pathChange + "18060200-15.csv",
                "15": pathChange + "18060200-16.csv",
                "16": pathChange + "18060200-17.csv",
                "17": pathChange + "18060200-18.csv"}
    
    name =  {"0":"18060200.csv", 
             "1": "18060200-2.csv", 
                "2": "18060200-3.csv",             
                "3": "18060200-4.csv",         
                "4": "18060200-5.csv", 
                "5": "18060200-6.csv",
                "6": "18060200-7.csv",
                "7": "18060200-8.csv",
                "8": "18060200-9.csv",
                "9": "18060200-10.csv",
                "10": "18060200-11.csv",
                "11": "18060200-12.csv",
                "12": "18060200-13.csv",
                "13": "18060200-14.csv",
                "14": "18060200-15.csv",
                "15": "18060200-16.csv",
                "16": "18060200-17.csv",
                "17": "18060200-18.csv"}    
    timeRange = [2018,6,2,2018,6,2]
    csv = "/Users/GaryYe/Desktop/lab/6-2/"
#11-10-11-29-2017
elif (dataset == 3):
    pathChange = "../../Data/st-lucia-1110-1129-solar/"
    filelistDay = {"0": pathChange + "pe20171110-20171129.csv", 
                        "1": pathChange + "pe20171110-20171129-2.csv", 
                        "2": pathChange + "pe20171110-20171129-3.csv",             
                "3": pathChange + "pe20171110-20171129-4.csv",         
                "4": pathChange + "pe20171110-20171129-5.csv", 
                "5": pathChange + "pe20171110-20171129-6.csv",
                "6": pathChange + "pe20171110-20171129-7.csv",
                "7": pathChange + "pe20171110-20171129-8.csv",
                "8": pathChange + "pe20171110-20171129-9.csv",
                "9": pathChange + "pe20171110-20171129-10.csv",
                "10": pathChange + "pe20171110-20171129-11.csv",
                "11": pathChange + "pe20171110-20171129-12.csv",
                "12": pathChange + "pe20171110-20171129-13.csv",
                "13": pathChange + "pe20171110-20171129-14.csv",
                "14": pathChange + "pe20171110-20171129-15.csv",
                "15": pathChange + "pe20171110-20171129-16.csv",
                "16": pathChange + "pe20171110-20171129-17.csv",
                "17": pathChange + "pe20171110-20171129-18.csv"}
    name =  {"0":"pe20171110-20171129.csv", 
             "1": "pe20171110-20171129-2.csv", 
             "2": "pe20171110-20171129-3.csv",             
                "3": "pe20171110-20171129-4.csv",         
                "4": "pe20171110-20171129-5.csv", 
                "5": "pe20171110-20171129-6.csv",
                "6": "pe20171110-20171129-7.csv",
                "7": "pe20171110-20171129-8.csv",
                "8": "pe20171110-20171129-9.csv",
                "9": "pe20171110-20171129-10.csv",
                "10": "pe20171110-20171129-11.csv",
                "11": "pe20171110-20171129-12.csv",
                "12": "pe20171110-20171129-13.csv",
                "13": "pe20171110-20171129-14.csv",
                "14": "pe20171110-20171129-15.csv",
                "15": "pe20171110-20171129-16.csv",
                "16": "pe20171110-20171129-17.csv",
                "17": "pe20171110-20171129-18.csv"}
    timeRange = [2017,11,10,2017,11,29]    
    csv = "/Users/GaryYe/Desktop/lab/11-10-11-29/"

"""
Graphic Reconstruction
"""
def recreate_csv_graph(package, labelList, xRange):
    filename = package[0]
    title = package[1]
    xlabel = package[2]
    ylabel = package[3]
    markerList = itertools.cycle(('x-', '^-', 'D-', 'o-', 'p-', '+-', '*-', 's-', 'h-'))
    lineList = itertools.cycle((1, 2, 1, 2, 3))
    time_series = pd.read_csv(filename)  
    ts = pd.DataFrame(time_series) 
    graphDict = {}
    for i in range(xRange[0], xRange[1]):
        for key in labelList:
            if key in graphDict:
                
                graphDict[key] += [ts[key][i]]
            else:
                graphDict[key] = [ts[key][i]]
    plt.figure(title)
    Key = graphDict[xlabel]
    for key in graphDict:
        if (key != xlabel):
            plt.plot(Key, graphDict[key], markerList.__next__(), label = key, linewidth = lineList.__next__())
    plt.legend()
    plt.grid(True)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)


"""
Write the data into the csv file
"""
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
    df.to_csv("/Users/GaryYe/Desktop/" + filename, index = False) 
    
    

"""
Wirte the data from the compression performance test into a csv file
Draw the graph from the data
"""
def print_performance(evaDict, title, xlabel, ylabel, group):
    header = [xlabel, 'APCA', 'SWING', 'SIRCS (APCA, g = ' + str(group) + ')', 'SIRCS (SWING, g = ' + str(group) + ')', 'GAMPS (c = 0.4, d = 5, g = ' + str(group) + ')']
    csvList = [] 
    APCA = []
    SWING = []
    SIRCSAPCA = []
    SIRCSSWING = []
    GAMPS = []
    Key = []
    t = PrettyTable(header)
    for key in evaDict:
        t.add_row([key, '{:.2f}'.format(evaDict[key][0]),'{:.2f}'.format(evaDict[key][1]),'{:.2f}'.format(evaDict[key][2]), '{:.2f}'.format(evaDict[key][3]), '{:.2f}'.format(evaDict[key][4])])
        csvList.append((key ,evaDict[key][0] , evaDict[key][1], evaDict[key][2], evaDict[key][3], evaDict[key][4]))#'GAMPS (static, c = 0.4, d = 5)'
        APCA.append(evaDict[key][0])
        SWING.append(evaDict[key][1])
        SIRCSAPCA.append(evaDict[key][2])
        SIRCSSWING.append(evaDict[key][3]) 
        GAMPS.append(evaDict[key][4]) 
        Key.append(key)
    df = pd.DataFrame.from_records(csvList, columns=header) 
    
    plt.figure(title)
    plt.plot(Key, APCA, 'x-', label = header[1])
    plt.plot(Key, SWING,'^-', label = header[2])
    plt.plot(Key, SIRCSAPCA, 'D-', label = header[3])
    plt.plot(Key, SIRCSSWING, 'o-', label = header[4])
    plt.plot(Key, GAMPS, 'p-', label = header[5])
    plt.legend()
    plt.grid(True)
    plt.title(title + ' Performance ')
    plt.ylabel(ylabel)
    plt.xlabel('Maximum Error Guarantee (%)')
    
    write_in_csv(df, "performance_" + title + ".csv")
    return t


"""
Execute the performance test by operating each compression scheme
"""
def performance_test(dataSet, group):
    flag = [1, 1, 1, 1, 1]
    #test esp list
    espList = [0.5, 1, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    
    #data cleansing
    print("Data cleansing ... \n")
    da = DataClean(filelistDay, timeRange, group)
    dataPackage = da.data_initialization()
    print("Accomplish data cleansing\n") 
    evaRMSE = {}
    evaCR = {}
    evaT= {}
    
    for espmax in espList:
        rmse = []
        cr = []
        ct = [] 
        if(flag[0] == 1):
            com = Compression(dataPackage, name, [1, 3], espmax, savefile , timeRange)
            d = com.process_request()             
        else:
            d = [0, 0, 0]
        cr.append(d[0])
        rmse.append(d[1])
        ct.append(d[2])
        if(flag[1] == 1):
            com = Compression(dataPackage, name, [1, 4], espmax, savefile , timeRange)
            d = com.process_request()             
        else:
            d = [0, 0, 0]
        cr.append(d[0])
        rmse.append(d[1])
        ct.append(d[2])      
        if(flag[2] == 1):
            com = Compression(dataPackage, name, [1, 7], espmax, savefile , timeRange)
            d = com.process_request()             
        else:
            d = [0, 0, 0]
        cr.append(d[0])
        rmse.append(d[1])
        ct.append(d[2])
        if(flag[3] == 1):
            com = Compression(dataPackage, name, [1, 8], espmax, savefile , timeRange)
            d = com.process_request()             
        else:
            d = [0, 0, 0]
        cr.append(d[0])
        rmse.append(d[1])
        ct.append(d[2])
        
        if(flag[4] == 1):
            com = Compression(dataPackage, name, [1, 9], espmax, savefile , timeRange)
            d = com.process_request()             
        else:
            d = [0, 0, 0]
        cr.append(d[0])
        rmse.append(d[1])
        ct.append(d[2]) 
        print("Accomplish Evaluation of e = " + str(espmax) + ' ...\n')
        
        evaCR[espmax] = cr
        evaRMSE[espmax] = rmse
        evaT[espmax] = ct    
    
    print('NRMSE')
    print(print_performance(evaRMSE, 'NRMSE', 'Error Tolerance (%)', 'NRMSE (%)', group))
    print('CR')
    print(print_performance(evaCR, 'Compression_Ratio', 'Error Tolerance (%)', 'Compression Ratio (Original / Compressed)', group))
    print('CT')
    print(print_performance(evaT, 'Compression_Time', 'Error Tolerance (%)', 'Compression Time (s)', group))    



"""
Goal seek function is to fix one benchmark value and show the values of the rest
"""
def goal_seek_cr(dataPackage, cr, Type): 
    #0，0.5， 0.25， 0.125，0.0625, 0.03125, 0.015625, 0.0078125 8 time to stablize two digits
    #-1: smaller than cr; 1: bigger than cr
    maxesp = 100
    minesp = 0
    if(cr <= 0.25):
        espmax = 50
    elif(cr > 0.25) and (cr <= 0.5):
        espmax = 5
    elif(cr > 0.5) and (cr <= 0.75):
        espmax = 2.5
    else:
        espmax = 0.5
    rmse = 0
    time = 0
    counter = 0
    while True:
        counter += 1
        if(Type == 0):
            com = Compression(dataPackage, name, [1, 3], espmax, savefile , timeRange)
            temp = com.process_request()
            print("<APCA>: Iteration: " + str(counter) + "| RMSE: " + str(temp[1]) + "| CR: " + str(float(round(Decimal(1 / temp[0]),2))) + "| TIME: " + str(temp[2]) + "| Esp: " + str(espmax))                
        elif(Type == 1):
            com = Compression(dataPackage, name, [1, 4], espmax, savefile , timeRange)
            temp = com.process_request()
            print("<<SWING>: Iteration: " + str(counter) + "| RMSE: " + str(temp[1]) + "| CR: " + str(float(round(Decimal(1 / temp[0]),2))) + "| TIME: " + str(temp[2]) + "| Esp: " + str(espmax))                
        elif(Type == 2):
            com = Compression(dataPackage, name, [1, 7], espmax, savefile , timeRange)
            temp = com.process_request()
            print("<SIRCS_APCA>: Iteration: " + str(counter) + "| RMSE: " + str(temp[1]) + "| CR: " + str(float(round(Decimal(1 / temp[0]),2))) + "| TIME: " + str(temp[2]) + "| Esp: " + str(espmax))     
        elif(Type == 3):
            com = Compression(dataPackage, name, [1, 8], espmax, savefile , timeRange)
            temp = com.process_request()
            print("<SIRCS_SWING>: Iteration: " + str(counter) + "| RMSE: " + str(temp[1]) + "| CR: " + str(float(round(Decimal(1 / temp[0]),2))) + "| TIME: " + str(temp[2]) + "| Esp: " + str(espmax)) 
        elif(Type == 4):
            com = Compression(dataPackage, name, [1, 9], espmax, savefile , timeRange)
            temp = com.process_request()
            print("<GAMPS>: Iteration: " + str(counter) + "| RMSE: " + str(temp[1]) + "| CR: " + str(float(round(Decimal(1 / temp[0]),2))) + "| TIME: " + str(temp[2]) + "| Esp: " + str(espmax))             
    
        tempcr = float(round(Decimal(1 / temp[0]),2))       
        if(tempcr < cr):
            if(espmax < maxesp):
                maxesp = espmax
            tempesp = (maxesp + minesp)/2
            espmax = tempesp        
        elif(tempcr > cr):
            if(espmax > minesp): 
                minesp = espmax
            tempesp = (maxesp + minesp)/2
            espmax = tempesp 
        else:
            print("Locked the deal! \n")
            rmse = temp[1]
            time = temp[2]
            break                
            
        if(counter == 15):
            print("Current compression ratio cannot be achieved. \n")
            rmse = temp[1]
            time = temp[2]
            break
    return [espmax, rmse, cr, time] 


"""
Cruise the presision test
"""
def precision_test(dataSet, group):
    flag = [1, 1, 1, 1, 1]
    #compression ratio list
    #crl = [0.05]
    crl = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    #data cleansing
    print("Data cleansing ... \n")
    da = DataClean(filelistDay, timeRange, group)
    dataPackage = da.data_initialization()
    print("Accomplish data cleansing\n")     
    ax = []
    ay = []
    sx = []
    sy = []
    lmax = []
    lmay = []
    lmsx = []
    lmsy = []       
    gx = []
    gy = []
    csvList = [] 
    evaRMSE = {}
    header = ['Compression Ratio (raw / compressed)', 'APCA', 'SWING', 'SIRCS (APCA, g = ' + str(group) + ')', 'SIRCS (SWING, g = ' + str(group) + ')', 'GAMPS (c = 0.4, d = 5, g = ' + str(group) + ')']
    for cr in crl:
        #apca
        if (flag[0] == 1):
            a = goal_seek_cr(dataPackage, cr, 0)
        else:
            a = [0, 0, cr, 0]
        ax.append(1/a[2])
        ay.append(a[1]) 
        #swing
        if (flag[1] == 1):
            s = goal_seek_cr(dataPackage, cr, 1)
        else:
            s = [0, 0, cr, 0]
        sx.append(1/s[2])
        sy.append(s[1])  
        #sircs apca
        if (flag[2] == 1):
            lma = goal_seek_cr(dataPackage, cr, 2)
        else:
            lma = [0, 0, cr, 0]
        lmax.append(1/lma[2])
        lmay.append(lma[1]) 
        #sircs swing
        if (flag[3] == 1):
            lms = goal_seek_cr(dataPackage, cr, 3)
        else:
            lms = [0, 0, cr, 0]
        lmsx.append(1/lms[2])
        lmsy.append(lms[1]) 
        #gamps
        if (flag[4] == 1):
            g = goal_seek_cr(dataPackage, cr, 4)
        else:
            g = [0, 0, cr, 0]
        gx.append(1/g[2])
        gy.append(g[1])   
        evaRMSE[float(round(Decimal(1 / cr),2))] = [a[1], s[1], lma[1], lms[1], g[1]]
        
    #table and csv   
    t = PrettyTable(header)
    for key in evaRMSE:
        t.add_row([key, '{:.2f}'.format(evaRMSE[key][0]),'{:.2f}'.format(evaRMSE[key][1]),'{:.2f}'.format(evaRMSE[key][2]), '{:.2f}'.format(evaRMSE[key][3]), '{:.2f}'.format(evaRMSE[key][4])])
        csvList.append((key ,evaRMSE[key][0] , evaRMSE[key][1], evaRMSE[key][2], evaRMSE[key][3], evaRMSE[key][4]))#'GAMPS (static, c = 0.4, d = 5)'    
    df = pd.DataFrame.from_records(csvList, columns=header) 
    write_in_csv(df, "precision_test.csv")
    print(t)
    #graph
    plt.figure('Precision Test')

    plt.plot(ax, ay, 'x-', label = header[1], linewidth=1.0)
    plt.plot(sx, sy,'^-', label = header[2], linewidth=1.0)
    plt.plot(lmax, lmay, 'D-', label = header[3], linewidth=1.0)
    plt.plot(lmsx, lmsy, 'o-', label = header[4], linewidth=1.0)
    plt.plot(gx, gy, 'p-', label = header[5], linewidth=1.0)
    plt.legend()
    plt.grid(True)
    plt.title('Precision Test')
    plt.ylabel('NRMSE (%)')
    plt.xlabel('Compression Ratio (Raw / Compressed)')   



"""
Grouping test evaluate the grouping impact on GAMPS and SIRCS compression performance
"""
def group_test(dataSet, Type):
    if(Type == 0):
        filename = "grouping_sircsapca_test.csv"
        selection = 7
    elif(Type == 1):
        filename = "grouping_sircsswing_test.csv"
        selection = 8
    elif(Type == 2):
        filename = "grouping_gamps_test.csv"  
        selection = 9
    #header
    header = ['Error Tolerance (%)', 'g = 1', 'g = 2', 'g = 4', 'g = 5', 'g = 10', 'g = 20']
    #grouping list
    groupList = [1, 2, 4, 5, 10, 20]
    #groupList = [1, 2, 2, 2, 2, 2]
    #test esp list
    espList = [1, 3, 5, 7, 9, 11, 13]
    #espList = [15, 17, 19, 21, 23, 25, 27]
    evaCR = {}
    evaRMSE = {} 
    evaCT = {}
      
    for gr in groupList:
        print("Data cleansing ... \n")
        da = DataClean(filelistDay, timeRange, gr)
        dataPackage = da.data_initialization()
        print("Accomplish data cleansing\n")  
        for espmax in espList:
            com = Compression(dataPackage, name, [1, selection], espmax, savefile , timeRange)
            d = com.process_request()  
            print("Accomplish Evaluation of e = " + str(espmax) + ' ...\n')
            if espmax in evaCR:
                evaCR[espmax] += [d[0]]
            else:
                evaCR[espmax] = [d[0]] 
                
            if espmax in evaRMSE:
                evaRMSE[espmax] += [d[1]]
            else:
                evaRMSE[espmax] = [d[1]] 
                
            if espmax in evaCT:
                evaCT[espmax] += [d[2]]
            else:
                evaCT[espmax] = [d[2]]   
                
    #table and csv   
    
    evaList = [evaCR, evaRMSE, evaCT]
    counter = 0
    for evaDict in evaList:
        counter += 1
        csvList = []  
        t = PrettyTable(header)
        for key in evaDict:
            t.add_row([key, '{:.2f}'.format(evaDict[key][0]),'{:.2f}'.format(evaDict[key][1]),'{:.2f}'.format(evaDict[key][2]), '{:.2f}'.format(evaDict[key][3]), '{:.2f}'.format(evaDict[key][4]), '{:.2f}'.format(evaDict[key][5])])
            csvList.append((key ,evaDict[key][0] , evaDict[key][1], evaDict[key][2], evaDict[key][3], evaDict[key][4], evaDict[key][5]))#'GAMPS (static, c = 0.4, d = 5)'    
        df = pd.DataFrame.from_records(csvList, columns=header) 
        write_in_csv(df, str(counter) + '_' + filename)
        print(t)    
    


"""
Grouping test evaluate the grouping impact on GAMPS and SIRCS compression performance
"""
def group_precision_test(dataSet, Type):
    if(Type == 0):
        filename = "pregr_sircsapca_test.csv"
        selection = 2
    elif(Type == 1):
        filename = "pregr_sircsswing_test.csv"
        selection = 3
    elif(Type == 2):
        filename = "pregr_gamps_test.csv"  
        selection = 4
    #header
    header = ['Compression Ratio (raw / compressed)', 'g = 1', 'g = 2', 'g = 4', 'g = 5', 'g = 10', 'g = 20']
    #grouping list
    groupList = [1, 2, 4, 5, 10, 20]
    #groupList = [1, 2, 2, 2, 2, 2]
    #test esp list
    crl = [0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    evaRMSE = {} 
      
    for gr in groupList:
        print("Data cleansing ... \n")
        da = DataClean(filelistDay, timeRange, gr)
        dataPackage = da.data_initialization()
        print("Accomplish data cleansing\n")  
        for cr in crl:
            cri = float(round(Decimal(1 / cr),2))
            a = goal_seek_cr(dataPackage, cr, selection)
            if cri in evaRMSE:
                evaRMSE[cri] += [a[1]]
            else:
                evaRMSE[cri] = [a[1]]          
    #table and csv   
    csvList = []  
    t = PrettyTable(header)
    for key in evaRMSE:
        t.add_row([key, '{:.2f}'.format(evaRMSE[key][0]),'{:.2f}'.format(evaRMSE[key][1]),'{:.2f}'.format(evaRMSE[key][2]), '{:.2f}'.format(evaRMSE[key][3]), '{:.2f}'.format(evaRMSE[key][4]), '{:.2f}'.format(evaRMSE[key][5])])
        csvList.append((key ,evaRMSE[key][0] , evaRMSE[key][1], evaRMSE[key][2], evaRMSE[key][3], evaRMSE[key][4], evaRMSE[key][5]))#'GAMPS (static, c = 0.4, d = 5)'    
    df = pd.DataFrame.from_records(csvList, columns=header) 
    write_in_csv(df, filename)
    print(t)    
    










def node_test(dataSet, Type):
    index = [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24,26]
    #index = [4, 6]
    #test esp list
    espList = [1, 3, 5, 7, 9]  
    markerList = itertools.cycle(('x-', '^-', 'D-', 'o-', 'p-', '+-', '*-', 's-', 'h-'))
    evaCR = {}  
    csvList = []
    header = ['Number of Sensors', 'e = 1%', 'e = 3%', 'e = 5%', 'e = 7%', 'e = 9%']
    for i in index:
        testDict = {}
        testName = {}
        counter = 0
        for key in filelistDay:
            testDict[key] = filelistDay[key]
            testName[key] = name[key]
            counter += 1
            if (counter == i):
                break
        print("Data cleansing ... \n")
        da = DataClean(testDict, timeRange, group)
        dataPackage = da.data_initialization()
        print("Accomplish data cleansing\n")  
        cr = []
        for espmax in espList:       
            if(Type == 0):
                #
                com = Compression(dataPackage, name, [1, 7], espmax, savefile , timeRange)
                d = com.process_request()
            if(Type == 1):
                #
                com = Compression(dataPackage, name, [1, 8], espmax, savefile , timeRange)
                d = com.process_request()                
            if(Type == 2):
                com = Compression(dataPackage, name, [1, 9], espmax, savefile , timeRange)
                d = com.process_request()             
            cr.append(d[0])
            print("Accomplish Evaluation of e = " + str(espmax) + ' ...\n')
        evaCR[i] = cr
    #table and csv  
    t = PrettyTable(header)
    for key in evaCR:
        t.add_row([key, '{:.2f}'.format(evaCR[key][0]),'{:.2f}'.format(evaCR[key][1]),'{:.2f}'.format(evaCR[key][2]), '{:.2f}'.format(evaCR[key][3]), '{:.2f}'.format(evaCR[key][4])])
        csvList.append((key ,evaCR[key][0] , evaCR[key][1], evaCR[key][2], evaCR[key][3], evaCR[key][4]))#'GAMPS (static, c = 0.4, d = 5)'    
    df = pd.DataFrame.from_records(csvList, columns=header) 
    write_in_csv(df, str(Type) +"_node_test.csv")
    '''
    print(t)
    #graph
    plt.figure('Network Density Test')
    for i in range(len(espList)):
        x = index
        y = []
        for key in evaCR:
            y.append(evaCR[key][i])
        plt.plot(index, y, markerList.__next__(), label = header[i + 1], linewidth=1.5)
    plt.legend()
    plt.grid(True)
    plt.title('Network Density Test')
    plt.ylabel('Compression Ratio (Raw / Compressed)')
    plt.xlabel('Number of Sensors')   
    '''
    return evaCR 

            
            


"""
Operational Deck
"""
#1. performance test: cr, rmse, ct:
#performance_test(dataset, group)

#2. precision test: rmse against cr:
#precision_test(dataset, group)

#3. grouping test:
#group_test(dataset, 0)
#group_test(dataset, 1)
#group_test(dataset, 2)
#group_precision_test(dataset, 0)
#group_precision_test(dataset, 1)
#group_precision_test(dataset, 2)

#4. node test:
node_test(dataset, 0)
node_test(dataset, 1)
#node_test(dataset, 2)

#11-10-11-29-2018 graphic reconstruction
#recreate_csv_graph(package_cr, performanceLabel, [0, 14])
#recreate_csv_graph(package_rmse, performanceLabel, [0, 14])
#recreate_csv_graph(package_ct, performanceLabel, [0, 14])

#recreate_csv_graph(package_pre, precisionLabel[0:2], [0, 11])

#recreate_csv_graph(package_gr_apca1, groupingLabel, [0, 7])
#recreate_csv_graph(package_gr_apca2, groupingLabel, [0, 7])
#recreate_csv_graph(package_gr_apca3, groupingLabel, [0, 7])

#recreate_csv_graph(package_gr_swing1, groupingLabel, [0, 7])
#recreate_csv_graph(package_gr_swing2, groupingLabel, [0, 7])
#recreate_csv_graph(package_gr_swing3, groupingLabel, [0, 7])

#recreate_csv_graph(package_gr_gamps1, groupingLabel, [0, 7])
#recreate_csv_graph(package_gr_gamps2, groupingLabel, [0, 7])
#recreate_csv_graph(package_gr_gamps3, groupingLabel, [0, 7])

#recreate_csv_graph(package_pre_gr_apca, groupingLabel1, [0, 11])
#recreate_csv_graph(package_pre_gr_swing, groupingLabel1, [0, 11])
#recreate_csv_graph(package_pre_gr_gamps, groupingLabel1, [0, 11])

#recreate_csv_graph(package_node_apca, nodeLabel, [0, 8])
#recreate_csv_graph(package_node_swing, nodeLabel, [0, 8])
#recreate_csv_graph(package_node_gamps, nodeLabel, [0, 8])




