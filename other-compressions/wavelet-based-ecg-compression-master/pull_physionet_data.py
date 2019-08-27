#!/usr/bin/env python
# coding: utf-8

# Import stuff

# In[1]:


import matplotlib.pyplot as plt
import numpy as np
import os
import shutil
import pandas as pd
import pdb

#install wfdb from https://github.com/MIT-LCP/wfdb-python
import wfdb


# The .apn files are (binary) annotation files, containing an annotation for each minute of each recording indicating the presence or absence of apnea at that time; these are available for the 35 learning set recordings only
#
# ECG sampling rate is 100Hz

# In[6]:


#grab data from https://www.physionet.org/physiobank/database/apnea-ecg/
#record = wfdb.rdrecord('a01', pb_dir='apnea-ecg/')
#data = pd.DataFrame(record.p_signal)

datasetPath = '../../../Datasets/UCRArchive_2018/Yoga/Yoga_TEST.tsv'
# datasetPath = '../../../Datasets/archive_ics/gas-sensor-array-temperature-modulation/20160930_203718.csv'
#datasetPath = '../../../Datasets/UCRArchive_2018/PigAirwayPressure/PigAirwayPressure_TEST.tsv'


df_data = pd.read_csv(datasetPath, sep='\t')
#df_data = pd.read_csv(datasetPath)

#print(df_data.info(verbose=True))

##df_data.plot()
#plt.show()
#annotation = wfdb.rdann('a01', 'apn', pb_dir='apnea-ecg/')

df_data.to_pickle('Yoga_TEST.pkl')


# In[3]:


# df_data.plot()
# plt.show()


# In[ ]:
