#!/usr/bin/env python

from __future__ import division, print_function

import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from joblib import Memory

import paths
from ..files import ensure_dir_exists
from . import viz

_memory = Memory('./', verbose=1)

NUM_RECORDINGS = 594
NUM_COLS = 80
DATA_DIR = paths.MSRC_12
# OUTPUT_DATA_DIR = './data'

join = os.path.join


FIG_SAVE_DIR = join('figs', 'msrc')
SAVE_DIR_LINE_GRAPH = join(FIG_SAVE_DIR, 'line')
SAVE_DIR_IMG = join(FIG_SAVE_DIR, 'img')
SAVE_DIR_DELTA = join(FIG_SAVE_DIR, 'delta')

# Notes:
#     -Tagstream times are sort of in the middle of the gesture, but
#     not really; they're sometimes very close to the beginning or
#     the end; basically, they don't seem to be super-consistent,
#     objective ground truth
#     -Many of these recordings include a bunch of extra material
#     (in some cases even 10 instances of two totally different
#     things at different times...)
#    -The number of gestures in a given recording varies; typically
#    10, but plotting recordings reveals numbers from 8-13
#     -It's not clear what every 4th column of the data matrix is;
#    columns 1-3 + 4k, k = {0..19} are x,y,z position, but I can't
#     find what the remaining fourth of the columns are...


CLASS_IDS_2_NAMES = {
    1: "Start system",
    2: "Duck",
    3: "Push right",
    4: "Goggles",
    5: "Wind it up",
    6: "Shoot",
    7: "Bow",
    8: "Throw",
    9: "Had enough",
    10: "Change weapon",
    11: "Beat both arms",
    12: "Kick"
}


def all_file_names():
    # get paths of all data files
    dataFiles = glob.glob('%s/*.csv' % DATA_DIR)
    tagstreamFiles = glob.glob('%s/*.tagstream' % DATA_DIR)

    # there should be 594 of each
    assert(len(dataFiles) == NUM_RECORDINGS), \
        "missing data files: should be %d in %s" \
        % (NUM_RECORDINGS, DATA_DIR)
    assert(len(tagstreamFiles) == NUM_RECORDINGS), \
        "missing tagstream files: should be %d in %s" \
        % (NUM_RECORDINGS, DATA_DIR)

    return (dataFiles, tagstreamFiles)


def parse_time(time):
    # I have no idea what their time stamps mean, but this magic
    # line from their matlab code converts things to...microseconds?
    return (int(time)*1000 + 49875//2)//49875


def parse_file_name(fName):
    # file names are of form P#_#_#[A]_P#.csv
    # print("reading file: %s" % fName)
    fName = fName.split("/")[-1]
    # print("file name: %s" % fName)
    noSuffix = fName.split(".")[0]
    fields = noSuffix.split("_")
    # form is P%d_%d - no clear mapping to actual instruction modalities...
    instruction = ''.join(fields[0:2])
    gestureId = fields[2]        # form is %d
    subjId = int(fields[3][1:])  # form is p%d
    if (gestureId[-1] == 'A'):
        twoModalities = True
        gestureId = gestureId[:-1]
    else:
        twoModalities = False
    gestureId = int(gestureId)

    return (instruction, gestureId, subjId, twoModalities)


def read_answer_times(tagFile):
    times = []
    with open(tagFile, 'r') as f:
        f.readline()      # first line is garbage, not data
        for line in f:
            time, gesture = line.split(';')
            times.append(parse_time(time))
    return times


@_memory.cache
def read_data_file(dataFile):
    contents = np.genfromtxt(dataFile, delimiter=' ')
    timeStamps = contents[:, 0]
    data = contents[:, 1:]
    rowSums = np.sum(data, 1)
    nonZeroRowIdxs = np.where(rowSums != 0)
    data = data[nonZeroRowIdxs]
    timeStamps = timeStamps[nonZeroRowIdxs]     # no need to convert these
    # print(data.shape)
    # print(timeStamps.shape)
    assert data.shape[0] == timeStamps.shape[0]
    return data, timeStamps


@_memory.cache
def _create_recording(*args, **kwargs):
    return Recording(*args, **kwargs)


@_memory.cache
def all_recordings(idxs=None, only_valid=True):
    dataFiles, tagFiles = all_file_names()
    recs = []
    if idxs is None:
        idxs = range(len(dataFiles))
    num_valid_recordings = 0
    for i in idxs:
        try:
            r = _create_recording(dataFiles[i], tagFiles[i], recID=i,
                                  needs_label_times=only_valid)
            recs.append(r)
            num_valid_recordings += 1
        except IOError:
            print("skipping broken recording #{}".format(i))
        except IndexError:  # we only get this if only_valid=True
            print("skipping broken recording #{}".format(i))
            continue
    print("number of valid recordings {}/{}".format(
        num_valid_recordings, len(dataFiles)))
    return recs


def _compute_label_idxs(labelTimes, sampleTimes):
    """Throws IndexError if any label time is outside range of sample times"""
    labelIdxs = np.empty(len(labelTimes), dtype=np.int)
    # print("sampleTimes shape: ", sampleTimes.shape)
    for i, time in enumerate(labelTimes):
        # extra [0] to unpack where()
        # print("raw where output: ", np.where(sampleTimes >= time))
        labelIdxs[i] = np.where(sampleTimes >= time)[0][0]
    return labelIdxs


# def _uniformlyResample1D(x, y):
#     interpFunc = interp.interp1d(x, y)
#     uniformX = np.linspace(np.min(x), np.max(x), len(x))
#     return interpFunc(uniformX)

# def _uniformlyResample(x, Y):
#     Ynew = np.empty(Y.T.shape)
#     for i, col in enumerate(Y.T):
#         Ynew[i] = _uniformlyResample1D(x, col)
#     return Ynew.T


class Recording:

    def __init__(self, dataFile, tagFile, recID=-1, needs_label_times=True):
        print("creating recording #{}".format(recID))
        self.id = recID
        self.fileName = dataFile.split('.')[0]
        self.instruction, self.gestureId, self.subjId, self.twoModalities = \
            parse_file_name(dataFile)
        self.gestureLabel = CLASS_IDS_2_NAMES[self.gestureId]
        self.gestureTimes = read_answer_times(tagFile)

        self.data, self.sampleTimes = read_data_file(dataFile)
        # self.rawData, self.sampleTimes = read_data_file(dataFile)
        # self.data = _uniformlyResample(self.sampleTimes, self.rawData)

        # print("instruction: {}".format(self.instruction))

        try:
            self.gestureIdxs = _compute_label_idxs(
                self.gestureTimes, self.sampleTimes)
        except IndexError as e:
            if needs_label_times:
                raise e
            else:
                self.gestureIdxs = np.array([])

        # self.name = "{}_subj={}_instr={}".format(
        #     self.gestureLabel.replace(' ', '-'), self.subjId, self.instruction)
        self.name = "{}_subj={}_idx={}".format(
            # self.gestureLabel.replace(' ', '-'), self.subjId, self.fileName)
            self.gestureLabel.replace(' ', '-'), self.subjId, self.id)
        # self.name += self.fileName
        # self.name += "_{}".format(self.instruction)

        if len(self.data.shape) < 2 or self.data.shape[0] < 2 or \
                self.data.shape[1] < NUM_COLS:
            raise IOError("Broken file "
                          "'{}' for recording '{}'; data shape = {}".format(
                            dataFile, self.name, self.data.shape))

    def __str__(self):
        s1 = "instruction: %s\ngestureId: %s\nsubjId: %s\n" \
            % (self.instruction, self.gestureId, self.subjId)
        s2 = "data sz: %d x %d" % self.data.shape
        s3 = str(self.gestureTimes) + str(self.data)
        return s1 + s2 + s3

    def plot(self, saveDir=None):
        plt.figure()
        plt.autoscale(tight=True)
        plt.plot(self.sampleTimes, self.data)
        minVal = np.min(self.data) - .2
        maxVal = np.max(self.data) + .2
        for time in self.gestureTimes:
            plt.plot([time, time], [minVal, maxVal],
                     color='k', linestyle='--', linewidth=1)
        plt.title(self.gestureLabel)
        if saveDir:
            ensure_dir_exists(saveDir)
            fileName = "%s_%d" % (self.gestureLabel, self.id)
            fileName = join(saveDir, fileName)
            plt.savefig(fileName)


def main():
    # dataFiles, tagFiles = all_file_names()
    # # for i in range(len(dataFiles)):
    # # for i in range(11,550,40):  # just an arbitrary, evenly-spaced, subset
    # # for i in range(11,550,500):  # just an arbitrary, evenly-spaced, subset
    # # for i in range(0, 550, 3):  # just an arbitrary, evenly-spaced, subset
    # for i in range(5, 15, 2):
    #     r = Recording(dataFiles[i], tagFiles[i], i)
    #     # print(r)
    #     # r.plot(saveDir=SAVE_DIR_LINE_GRAPH)
    #     r.plot()
    # plt.show()

    # recs = all_recordings(idxs=np.arange(5, 15, 2))
    recs = all_recordings(idxs=np.arange(11, 550, 40))
    # recs = all_recordings(idxs=np.arange(2))
    print("recording 0 shape: ", recs[0].data.shape)
    # viz.plot_recordings(recs, interval_len=600, savedir=SAVE_DIR_DELTA)


if __name__ == "__main__":
    main()
