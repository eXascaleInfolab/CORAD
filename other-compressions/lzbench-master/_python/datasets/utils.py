#!/usr/bin/env/python

import os
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import Rectangle

DEFAULT_LABEL = 0

from synthetic import concatWithPadding, ensure2D
from ..utils.sequence import splitElementsBy, splitIdxsBy

# ================================================================ Plotting

def plotVertLine(x, ymin=None, ymax=None, ax=None, **kwargs):
	if ax and (not ymin or not ymax):
		ymin, ymax = ax.get_ylim()
	if not ax:
		ax = plt

	kwargs['color'] = kwargs.get('color') or 'k'
	kwargs['linestyle'] = kwargs.get('linestyle') or '--'
	kwargs['linewidth'] = kwargs.get('linewidth') or 2

	ax.plot([x, x], [ymin, ymax], **kwargs)


def plotRect(ax, xmin, xmax, ymin=None, ymax=None, alpha=.2,
	showBoundaries=True, color='grey', fill=True, **kwargs):
	if ax and (ymin is None or ymax is None):
		ymin, ymax = ax.get_ylim()
	if fill:
		ax.add_patch(Rectangle((xmin, ymin), xmax-xmin, ymax-ymin,
			facecolor=color, alpha=alpha))
	if showBoundaries:
		plotVertLine(xmin, ymin, ymax, ax=ax, color=color, **kwargs)
		plotVertLine(xmax, ymin, ymax, ax=ax, color=color, **kwargs)


# ================================================================ Concatenation

def groupDatasetByLabel(X, Y):
	return splitElementsBy(lambda i, x: Y[i], X)


def formGroupsOfSize(collection, groupSize=10, shuffle=False):
	# -note that having |group| = groupSize is not guaranteed;

	if shuffle:
		np.random.shuffle(collection)

	groups = []
	i = 0
	while i < len(collection):
		j = i + groupSize
		groups.append(collection[i:j])
		i += groupSize
	return groups


def concatedTsList(X, Y, instancesPerTs=10, datasetName="Dataset",
	enemyInstancesPerTs=0, **paddingKwargs):
	"""instances -> [LabeledTimeSeries], with each pure wrt class of instances"""
	groupedByClass = groupDatasetByLabel(X, Y)

	# we allow at most one instance of each other class so there's only one
	# repeating "pattern"
	numClasses = len(groupedByClass)
	if enemyInstancesPerTs > numClasses - 1:
		print("concatedTsList(): WARNING: "
			"enemyInstancesPerTs {} > num digits - 1; will be truncated".format(
				enemyInstancesPerTs))
		enemyInstancesPerTs = numClasses - 1

	tsList = []
	for clz, instances in groupedByClass.iteritems():
		groups = formGroupsOfSize(instances, instancesPerTs)

		for groupNum, group in enumerate(groups):

			otherClasses = groupedByClass.keys()
			otherClasses.remove(clz)
			lbls = [clz] * len(group)
			if enemyInstancesPerTs > 0:

				enemyLbls = np.random.choice(otherClasses, enemyInstancesPerTs)
				if enemyInstancesPerTs == 1:
					enemyLbls = [enemyLbls]
				else:
					enemyLbls = list(enemyLbls)
				for dgt in enemyLbls:
					whichRecording = np.random.choice(groupedByClass[dgt])
					group.append(whichRecording)
				allIdxs = np.arange(len(group))
				orderIdxs = np.random.choice(allIdxs, len(allIdxs))
				np.random.shuffle(orderIdxs)

				lbls = lbls + enemyLbls
				lbls = np.array(lbls, dtype=np.object)
				lbls = lbls[orderIdxs]
				groups = [group[idx] for idx in orderIdxs]

			concated, startIdxs, endIdxs = concatWithPadding(
				group, **paddingKwargs)
			name = "{}-class{}-group{}".format(datasetName, clz, groupNum)
			uniqId = hash(name)
			ts = LabeledTimeSeries(data=concated, startIdxs=startIdxs,
				endIdxs=endIdxs, labels=lbls, name=name, id=uniqId)
			tsList.append(ts)

	return tsList

# ================================================================ Data structs


class LabeledTimeSeries(object):

	def __init__(self, data, startIdxs, endIdxs=None, subseqLength=None,
		labels=None, name=None, id=0):
		self.data = ensure2D(data)
		self.startIdxs = np.asarray(startIdxs, dtype=np.int)
		self.labels = np.asarray(labels)
		self.name = name
		self.id = int(id)

		if endIdxs is not None:
			self.endIdxs = np.asarray(endIdxs, dtype=np.int)
			self.subseqLength = None
		elif subseqLength:
			self.endIdxs = self.startIdxs + subseqLength
			self.subseqLength = subseqLength
		else:
			raise ValueError("Either endIdxs or subseqLength must be specified!")

		if labels is None or len(labels) == 0:
			self.labels = np.zeros(len(startIdxs), dtype=np.int) + DEFAULT_LABEL

		if startIdxs is not None and endIdxs is not None:
			# equal lengths
			nStart, nEnd = len(startIdxs), len(endIdxs)
			if nStart != nEnd:
				raise ValueError("Number of start indices must equal number"
					"of end indices! {0} != {1}".format(nStart, nEnd))
			# starts before or equal to ends
			violators = np.where(startIdxs > endIdxs)[0]
			if np.any(violators):
				raise ValueError("Some start indices exceed end indices!"
					"Violators at {}".format(str(violators)))
			# valid indices
			violators = np.where(startIdxs < 0)[0]
			if np.any(violators):
				raise ValueError("Some start indices < 0!"
					"Violators at {}".format(str(violators)))
			violators = np.where(endIdxs > len(data))[0]
			if np.any(violators):
				violatorValues = endIdxs[violators]
				raise ValueError("Some end indices > length of data {}! "
					"Violators {} at {}".format(len(data),
						str(violatorValues), str(violators)))

	def clone(self):
		return LabeledTimeSeries(np.copy(self.data),
			np.copy(self.startIdxs),
			np.copy(self.endIdxs),
			subseqLength=self.subseqLength,
			labels=np.copy(self.labels),
			name=self.name,
			id=self.id
		)

	def plot(self, saveDir=None, capYLim=1000, ax=None, staggerHeights=True,
		yFrac=.9, showBounds=True, showLabels=True, useWhichLabels=None,
		linewidths=2., colors=None, **plotRectKwargs):

		xlimits = [0, len(self.data)]
		ylimits = [self.data.min(), min(capYLim, self.data.max())]
		yMin, yMax = ylimits

		if ax is None:
			plt.figure(figsize=(10, 6))
			ax = plt.gca()

		if not hasattr(linewidths, '__len__'):
			linewidths = np.zeros(self.data.shape[1]) + linewidths

		hasColors = colors is not None and len(colors)
		for i in range(self.data.shape[1]):
			if hasColors:
				ax.plot(self.data[:, i], lw=linewidths[i], color=colors[i])
			else:
				ax.plot(self.data[:, i], lw=linewidths[i])

		ax.set_xlim(xlimits)
		ax.set_ylim(ylimits)
		ax.set_title(self.name)

		hasUseWhichLabels = useWhichLabels is not None and len(useWhichLabels)

		# plot annotations
		if showLabels or showBounds:
			for i in range(len(self.startIdxs)):
				ts, te, label = self.startIdxs[i], self.endIdxs[i], self.labels[i]
				# print "label, useWhichLabels", label,
				if hasUseWhichLabels and label not in useWhichLabels:
					continue

				if showBounds:
					plotRect(ax, ts, te, **plotRectKwargs) # show boundaries

				if showLabels:
					x = ts + (te - ts) / 10
					if staggerHeights: # so labels don't end up on top of one another
						yFrac = .67
						yFrac += .04 * (i // 1 % 2)
						yFrac += .08 * (i // 2 % 2)
						yFrac += .16 * (i // 4 % 2)
					y = yFrac * (yMax - yMin) + yMin # use yFrac passed in if not staggering
					ax.annotate(label, xy=(x, y), xycoords='data')

		if saveDir:
			fileName = self.name + '.pdf'
			if not os.path.exists(saveDir):
				os.makedirs(saveDir)
			path = os.path.join(saveDir, fileName)
			plt.savefig(path)

		return ax

	def plotSubseqs(self, saveDir, **kwargs):
		generateVideos(self.data, dataName=self.name, saveInDir=saveDir,
			rangeStartIdxs=self.startIdxs, rangeEndIdxs=self.endIdxs,
			rangeLabels=self.labels, **kwargs)

# ================================================================ Main

if __name__ == '__main__':
	from doctest import testmod
	testmod()
