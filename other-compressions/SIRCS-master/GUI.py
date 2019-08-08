from tkinter import *
from compress import *
from exe import *
from DATA import *
import pandas as pd
import tkinter.messagebox
from tkinter.filedialog import *
import time
import os


class DataClean():
   def __init__(self, fileList, timeIndex, group):    
      self.fileDict = fileList
      self.timeIndex = timeIndex
      self.group = group

      
   def data_initialization(self):
      data = DATA(self.timeIndex[0], self.timeIndex[1], self.timeIndex[2], self.timeIndex[3], self.timeIndex[4], self.timeIndex[5], self.fileDict, 'time', 'power (W)')
      dataPackage = data.group_clean(self.group)     
      return dataPackage
   
class Compression():
   def __init__(self, dataPackage, fileNameDict, algorithmSelection, espmax, savefile, timeIndex):
      #list of all locations' name
      self.keyList = dataPackage[0]
      #dictionary with [[values], nomalization]
      self.dataDict = dataPackage[1]
      #Correct size of one single data
      self.dataLength = dataPackage[2]
      #get real time index
      self.timeIndex = dataPackage[3]
      #get raw base dict to initiate r squared matrix
      self.rawBaseDict = dataPackage[4]
      #original size for the compression ratio
      self.totalSize = dataPackage[5]
      
      self.algorithm = algorithmSelection[1]
      self.espmax = espmax
      self.savetopath = savefile   
      self.openFileName = ''
      self.fileNameDict = fileNameDict
      self.timeRange = timeIndex
      
   def process_request(self):
      if(self.algorithm == 3):
         d = apca_compress(self.keyList, self.dataDict, self.fileNameDict, self.dataLength, self.timeIndex, self.espmax, self.savetopath, self.openFileName, self.timeRange, self.totalSize)
      elif(self.algorithm == 4):
         d = swing_compress(self.keyList, self.dataDict, self.fileNameDict, self.dataLength, self.timeIndex, self.espmax, self.savetopath, self.openFileName, self.timeRange, self.totalSize)
      elif(self.algorithm == 7):
         d = sircs_apca_compress(self.keyList, self.dataDict, self.rawBaseDict, self.fileNameDict, self.dataLength, self.timeIndex, self.espmax, self.savetopath, self.openFileName, self.timeRange, self.totalSize)      
      elif(self.algorithm == 8):
         d = sircs_swing_compress(self.keyList, self.dataDict, self.rawBaseDict, self.fileNameDict, self.dataLength, self.timeIndex, self.espmax, self.savetopath, self.openFileName, self.timeRange, self.totalSize)            
      elif(self.algorithm == 9):
         d = gamps_compress(self.keyList, self.dataDict, self.fileNameDict, self.dataLength, self.timeIndex, self.espmax, self.savetopath, self.openFileName, self.timeRange, self.totalSize)      
      return d
class Decompression():
   def __init__(self, savefile, openFileName):
      self.savetopath = savefile   
      self.openFileName = openFileName
      self.al = (self.openFileName.split('/')[-1]).split('_')[0]
      
      
   def process_request(self):
      if(self.al == 'apca'):
         apca_decompress(self.savetopath, self.openFileName)
      elif(self.al == 'swing'):
         swing_decompress(self.savetopath, self.openFileName) 
      elif(self.al == 'gamps'):
         gamps_decompress(self.savetopath, self.openFileName)       
      elif(self.al == 'sircsapca'):
         sircs_apca_decompress(self.savetopath, self.openFileName)         
      elif(self.al == 'sircsswing'):
         sircs_swing_decompress(self.savetopath, self.openFileName)

class Framework():   
   def __init__(self, root):
      self.root = root
      #message shown on frame
      self.fpmess = StringVar()
      self.samess = StringVar()
      self.almess = StringVar()
      self.cdmess = StringVar()
      
      #parameters str
      self.tsmess = StringVar()
      self.espmess = StringVar()
      self.grmess = StringVar()
      self.finalmess = StringVar()
      #1st layer frame to show file and path message
      #readfilepath and save file path     
      self.upperframe = Frame(self.root)
      self.upperframe.pack( side = TOP, expand = True)
      #2nd layer frame to select group or single
      #type of the algorithm
      #compression or decompression
      self.middleframe = Frame(self.root)
      self.middleframe.pack( side = TOP, expand = True)
      #sub middle frame for grouping type
      self.middleleft = Frame(self.middleframe)
      self.middleleft.pack( side = LEFT, expand = True )
      #sub middle frame for algorithm selection
      self.middleright = Frame(self.middleframe)
      self.middleright.pack( side = LEFT, expand = True )      
      #show the current compress or decompressed status
      self.bottomframe = Frame(self.root)
      self.bottomframe.pack( side = TOP, expand = True )
      #timeIndex
      self.bottom1 = Frame(self.bottomframe)
      self.bottom1.pack( side = LEFT, expand = True )    
      #expmax
      self.bottom2 = Frame(self.bottomframe)
      self.bottom2.pack( side = LEFT, expand = True )   
      #grouping
      self.bottom3 = Frame(self.bottomframe)
      self.bottom3.pack( side = LEFT, expand = True )       
             
      
      #operational button, open file save file and test file
      self.superbottomframe = Frame(self.root)
      self.superbottomframe.pack( side = TOP, expand = True )    
      #expmax
      self.bottom4 = Frame(self.superbottomframe)
      self.bottom4.pack( side = LEFT, expand = True )   
      #grouping
      self.bottom5 = Frame(self.superbottomframe)
      self.bottom5.pack( side = LEFT, expand = True )       
      
      #initialze every settings
      self.initialization()
      
   def initialization(self):        
      # the data structure of the menu 
      #compress or decompress --> algorithm selection
      self.algorithmSelection = [0, 0]
      #parameters
      self.timeIndex = []
      self.espmax = 1
      self.group = 1
      #append file list with the index number
      self.fileListCounter = 0
      self.fileList = {}
      self.fileNameDict = {}
      self.totalsize = 0
      self.decomFileName = ""
      self.openFileTitle = "File Path: Choose Operation Type First."
      self.saveFileTitle = "Save Path: /Users/GaryYe/Desktop/"
      self.filename = ""
      self.savefile = "/Users/GaryYe/Desktop/" 
      self.fpmess.set(self.openFileTitle)
      self.samess.set(self.saveFileTitle)
      self.cdmess.set("Operation Type: Not selected")
      self.almess.set("Algorithm: Not selected")
      
      self.tsmess.set("Time Index")
      self.espmess.set("Error = 1%")
      self.grmess.set("Group = 1")  
      self.finalmess.set("Welcome to the Gary's Compression Hub!")
   """
   set compression as one
   """
   def select_com(self):
      self.initialization()
      self.cdmess.set("Compression")
      self.algorithmSelection[0] = 1
   """
   set decompression as two
   """
   def select_decom(self):
      self.initialization()
      self.cdmess.set("Decompression")
      self.algorithmSelection[0] = 2
      #print(self.algorithmSelection)

   
   """
   Create message box for read file path and save file path
   Input: None
   Output: Two-row message box ready to show the information
   """
   def createmessagebox(self):
      fileopt = Message( self.upperframe, textvariable=self.fpmess, relief=RAISED, width = 800 )
      self.fpmess.set(self.openFileTitle)
      fileopt.pack(side=TOP, anchor=W, fill=Y, expand=True)

      saveopt = Message( self.upperframe, textvariable=self.samess, relief=RAISED, width = 800 )
      self.samess.set(self.saveFileTitle)
      saveopt.pack(side=TOP, anchor=W, fill=Y, expand=True)
      
   """
   menu button lies in the middle frame, it has
   group type selection,
   algorithm selection,
   compression or decompression selection
   """
   def createmenubutton(self):
      mb = Menubutton (self.middleleft, text="Compress Or Decompress", relief=RAISED )
      mb.grid()
      mb.menu =  Menu (mb, tearoff = 0 )
      mb["menu"] =  mb.menu
      a1Var = IntVar()
      a2Var = IntVar()
      mb.menu.add_checkbutton ( label="Compression",
                                variable=a1Var , command = self.select_com)
      mb.menu.add_checkbutton ( label="Decompression",
                                variable=a2Var, command = self.select_decom)
      mb.pack(side=LEFT, anchor=N, fill=Y, expand=YES)
      # the label showing current status of the algorithm menu
      label1 = Message( self.middleleft, textvariable=self.cdmess, relief=RAISED, width = 200 )
      # initial
      self.cdmess.set("Operation Type: Not selected")
      label1.pack(side=LEFT, anchor=W, fill=Y, expand = YES) 
   """
   command for compression depending on the group and compress type
   """
   def al3(self):
      self.almess.set("APCA")
      self.algorithmSelection[1] = 3
   def al4(self):
      self.almess.set("SWING")
      self.algorithmSelection[1] = 4 
   def al7(self):
      self.almess.set("SIRCS (APCA)")
      self.algorithmSelection[1] = 7
   def al8(self):
      self.almess.set("SIRCS (SWING)")
      self.algorithmSelection[1] = 8
   def al9(self):
      self.almess.set("GAMPS")
      self.algorithmSelection[1] = 9
 
   """
   Depending on the group selection, create the menu bar on the right side of the middle frame with 
   corresponding algorithm type
   """
   def select_algorithm_menu(self):
      mb = Menubutton (self.middleright, text="Algorithm Selection", relief=RAISED )
      #mb.grid()
      mb.menu =  Menu ( mb, tearoff = 0 )
      mb["menu"] =  mb.menu
      t1Var = IntVar()
      t2Var = IntVar()         
      mb.menu.add_checkbutton ( label="APCA",
                                variable=t1Var , command = self.al3)
      mb.menu.add_checkbutton ( label="SWING",
                                variable=t1Var , command = self.al4) 
      mb.menu.add_checkbutton ( label="SIRCS (APCA)",
                                variable=t1Var , command = self.al7)
      mb.menu.add_checkbutton ( label="SIRCS (SWING)",
                                variable=t1Var , command = self.al8)  
      mb.menu.add_checkbutton ( label="GAMPS",
                                variable=t1Var , command = self.al9) 
                 
         
      mb.pack(side=LEFT, anchor=N, fill=Y, expand=YES)
      label2 = Message( self.middleright, textvariable=self.almess, relief=RAISED, width = 300 )
      self.almess.set("Compressing type: Not selected")
      label2.pack(side=LEFT, anchor=W, fill=Y, expand=YES)    
   
   
   def data1(self):
      self.tsmess.set("11-10-11-29-2017")
      self.timeIndex = [2017,11,10,2017,11,29]  
   def data2(self):
      self.tsmess.set("11-19-11-29-2017")
      self.timeIndex = [2017,11,19,2017,11,29]   
   def data3(self):
      self.tsmess.set("1-21-2018")
      self.timeIndex = [2018,1,21,2018,1,21]   
   def data4(self):
      self.tsmess.set("5-1-5-15-2018")
      self.timeIndex = [2018,5,1,20178,5,15]   
   def data5(self):
      self.tsmess.set("6-1-6-10-2018")
      self.timeIndex = [2018,6,1,2017,6,10]   
   def data6(self):
      self.tsmess.set("6-2-2018")
      self.timeIndex = [2018,6,2,2018,6,2]   
   def data7(self):
      self.tsmess.set("6-5-2018")
      self.timeIndex = [2018,6,5,2018,6,5]   
   def data8(self):
      self.tsmess.set("6-1-6-30-2018")
      self.timeIndex = [2018,6,1,2018,6,30]   
 
   
   
   
   """
   The bottom frame is to input the parameters
   parameter button lies in the bottom frame, it has
   time index selection,
   espmax selection,
   coefficient c selection
   decima
   """
   def timeindexmenubutton(self):
      mb = Menubutton (self.bottom1, text="Time Index", relief=RAISED )
      mb.grid()
      mb.menu =  Menu (mb, tearoff = 0 )
      mb["menu"] =  mb.menu
      a1Var = IntVar()
      a2Var = IntVar()
      mb.menu.add_checkbutton ( label="11-10-11-29-2017",
                                variable=a1Var , command = self.data1)
      mb.menu.add_checkbutton ( label="11-19-11-29-2017",
                                variable=a2Var, command = self.data2)
      mb.menu.add_checkbutton ( label="1-21-2018",
                                variable=a1Var , command = self.data3)
      mb.menu.add_checkbutton ( label="5-1-5-15-2018",
                                variable=a2Var, command = self.data4)
      mb.menu.add_checkbutton ( label="6-1-6-10-2018",
                                variable=a1Var , command = self.data5)
      mb.menu.add_checkbutton ( label="6-2-2018",
                                variable=a2Var, command = self.data6)   
      mb.menu.add_checkbutton ( label="6-5-2018",
                                variable=a2Var, command = self.data7) 
      mb.menu.add_checkbutton ( label="6-1-6-30-2018",
                                variable=a2Var, command = self.data8)       
      mb.pack(side=LEFT, anchor=N, fill=Y, expand=YES)
      # the label showing current status of the algorithm menu
      label1 = Message( self.bottom1, textvariable=self.tsmess, relief=RAISED, width = 200 )
      # initial
      self.tsmess.set("Time Index")
      label1.pack(side=LEFT, anchor=W, fill=Y, expand = YES)    
   
   def esp1(self):
      self.espmess.set("esp = 1%")
      self.espmax = 1
   def esp2(self):
      self.espmess.set("esp = 2%")
      self.espmax = 2
   def esp3(self):
      self.espmess.set("esp = 3%")
      self.espmax = 3
   def esp4(self):
      self.espmess.set("esp = 4%")
      self.espmax = 4
   def esp5(self):
      self.espmess.set("esp = 5%")
      self.espmax = 5   
   """
   Configure the expmax menu
   """
   def espmenubutton(self):
      mb = Menubutton (self.bottom2, text="Group Allocation", relief=RAISED )
      mb.grid()
      mb.menu =  Menu (mb, tearoff = 0 )
      mb["menu"] =  mb.menu
      a1Var = IntVar()
      a2Var = IntVar()
      mb.menu.add_checkbutton ( label="esp = 1%",
                                variable=a1Var , command = self.esp1)
      mb.menu.add_checkbutton ( label="esp = 2%",
                                variable=a2Var, command = self.esp2)
      mb.menu.add_checkbutton ( label="esp = 3%",
                                variable=a1Var , command = self.esp3)
      mb.menu.add_checkbutton ( label="esp = 4%",
                                variable=a2Var, command = self.esp4)
      mb.menu.add_checkbutton ( label="esp = 5%",
                                variable=a1Var , command = self.esp5)
      
      mb.pack(side=LEFT, anchor=N, fill=Y, expand=YES)
      # the label showing current status of the algorithm menu
      label1 = Message( self.bottom2, textvariable=self.espmess, relief=RAISED, width = 200 )
      # initial
      self.espmess.set("Error = 1%")
      label1.pack(side=LEFT, anchor=W, fill=Y, expand = YES)
   def gr1(self):
      self.grmess.set("Group = 1")
      self.group = 1
   def gr2(self):
      self.grmess.set("Group = 2")
      self.group = 2
   def gr3(self):
      self.grmess.set("Group = 3")
      self.group = 3
   def gr4(self):
      self.grmess.set("Group = 5")
      self.group = 5
   def gr5(self):
      self.grmess.set("Group = 10")
      self.group = 10
   def gr6(self):
      self.grmess.set("Group = 15")
      self.group = 15   
   """
   Configure the group menu
   """
   def groupmenubutton(self):
      mb = Menubutton (self.bottom3, text="Group", relief=RAISED )
      mb.grid()
      mb.menu =  Menu (mb, tearoff = 0 )
      mb["menu"] =  mb.menu
      a1Var = IntVar()
      a2Var = IntVar()
      mb.menu.add_checkbutton ( label="Group = 1",
                                variable=a1Var , command = self.gr1)
      mb.menu.add_checkbutton ( label="Group = 2",
                                variable=a2Var, command = self.gr2)
      mb.menu.add_checkbutton ( label="Group = 3",
                                variable=a1Var , command = self.gr3)
      mb.menu.add_checkbutton ( label="Group = 5",
                                variable=a2Var, command = self.gr4)
      mb.menu.add_checkbutton ( label="Group = 10",
                                variable=a1Var , command = self.gr5)
      mb.menu.add_checkbutton ( label="Group = 15",
                                variable=a1Var , command = self.gr6)      
      
      mb.pack(side=LEFT, anchor=N, fill=Y, expand=YES)
      # the label showing current status of the algorithm menu
      label1 = Message( self.bottom3, textvariable=self.grmess, relief=RAISED, width = 200 )
      # initial
      self.grmess.set("Group = 1")
      label1.pack(side=LEFT, anchor=W, fill=Y, expand = YES)    
   
   def check(self):
      if (self.algorithmSelection[0] == 0):
         self.finalmess.set("Please select operational type!")
      #compression
      elif(self.algorithmSelection[0] == 1): 

         if(self.timeIndex == []):
            self.finalmess.set("Please select time index!")
         elif(self.fileList == {}):
            self.finalmess.set("Please select the file!")
         elif(self.algorithmSelection[1] == 0):
            self.finalmess.set("Please select the algorithm!")   
         else:     
            da = DataClean(self.fileList, self.timeIndex, self.group)
            dataPackage = da.data_initialization()
            com = Compression(dataPackage, self.fileNameDict, self.algorithmSelection, self.espmax, self.savefile, self.timeIndex)
            [CR, RMSE, CT] = com.process_request()
            messagebox.showinfo("Compression Performance", "Compression Ratio: " + str("{0:.4f}".format(CR)) + "\nNRMSE: " + str("{0:.4f}".format(RMSE)) + "%\nCompression Time: " + str("{0:.4f}".format(CT)) + 's')
            self.initialization()
 
            
      elif(self.algorithmSelection[0] == 2):
         if(self.decomFileName == ''):
            self.finalmess.set("Please select the file!")
         else:
            decom = Decompression(self.savefile, self.decomFileName)
            decom.process_request()  
            self.initialization()
   def openfile(self):
      currentFile = askopenfilename()
      if(currentFile != ''):
         if(self.algorithmSelection[0] == 1):
            if(currentFile[-3:] != 'csv'):
               self.openFileTitle = "Error: can\'t find file or read data.\n"
            else:
               #first check if it's inside the package
               if(currentFile in self.fileList.values()):
                  self.openFileTitle = "This File is Already Selected. | Total File Selected: " + str(len(self.fileList)) + ' | Total Size: ' + str(self.totalsize) + ' bytes\n'
               else:
                  #append the file list and counter only if the file is valid
                  self.fileList[str(self.fileListCounter)] = currentFile
                  self.fileNameDict[str(self.fileListCounter)] = currentFile.split('/')[-1]
                  self.fileListCounter += 1
                  self.totalsize += os.path.getsize(currentFile)
                  self.openFileTitle = "This File is added. | Total File Selected: " + str(len(self.fileList)) + ' | Total Size: ' + str(self.totalsize) + ' bytes\n'
                  self.filename += str(self.fileListCounter) + ":" + currentFile + '\n'                       
               
            self.fpmess.set(self.openFileTitle + self.filename)
            #print(self.fileNameDict)
         elif(self.algorithmSelection[0] == 2):
            if(currentFile[-3:] != 'txt'):
               self.openFileTitle = "Error: can\'t find file or read data.\n"
               #append the file list and counter only if the file is valid
               self.decomFileName = ''
               self.fileListCounter = 0
               self.filename = ''            
            else:
               #append the file list and counter only if the file is valid
               self.decomFileName = currentFile
               self.fileListCounter == 1
               self.openFileTitle = "This File is added.\n"
               self.filename = str(self.fileListCounter) + ":" + currentFile + '\n'     
            self.fpmess.set(self.openFileTitle + self.filename)  
            #print(self.decomFileName)
         else:
            self.finalmess.set("Select Operation Type Before File Selection.") 
         
   def savethefile(self):
      savefile = askdirectory(parent=self.root,initialdir="/", title='Please select a directory.')
      if(savefile != ''):
         self.savefile = savefile+'/'
         print(self.savefile)
         self.samess.set("Save Path:" + savefile+'/')   
   
   
   
      
   """
   create the file menu with 
   1. open
   2. save 
   3. submit
   """
   def createfilemenu(self) :
      openbutton = Button(self.bottom4, text="Open File", fg="red", command = self.openfile)
      openbutton.pack(side=LEFT, anchor=W, fill=Y, expand=YES)
      savebutton = Button(self.bottom4, text="Save As", fg="red", command = self.savethefile)
      savebutton.pack(side=LEFT, anchor=W, fill=Y, expand=YES)
      okbutton = Button(self.bottom4, text="OK", fg="red", command = self.check)
      okbutton.pack(side=LEFT, anchor=W, fill=Y, expand=YES)   
      
      fileopt = Message(self.bottom5, textvariable=self.finalmess, relief=RAISED, width = 800 )
      self.finalmess.set("Welcome to the Gary's Compression Hub!")
      fileopt.pack(side=LEFT, anchor=W, fill=Y, expand= True)      
   
   def initial_frame(self):
      self.createmessagebox()
      # Algorithm selection, type selection
      self.createmenubutton()
      self.select_algorithm_menu()
      #bottom frame design
      self.timeindexmenubutton()
      self.espmenubutton()
      self.groupmenubutton()
      #men = FileMenu(bottomframe,fpmess,samess,almess, tymess)
      self.createfilemenu()




