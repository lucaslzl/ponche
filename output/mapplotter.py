import os
from os import listdir

import pandas as pd
import numpy as np
import json
import simplejson

import geopy.distance
import gmplot


class MapPlotter:


	def colors(self, n):
		ret = []
		for i in range(n):
			r = int(random.random() * 256)
			g = int(random.random() * 256)
			b = int(random.random() * 256)
			r = int(r) % 256
			g = int(g) % 256
			b = int(b) % 256
			ret.append('#{:02X}{:02X}{:02X}'.format(r,g,b)) 
		return ret


	def read_clusters(self, folder, file):

		print(folder+file)
		with open(folder+file, 'r') as json_file:
			day_data = json.load(json_file)

		return day_data


	def get_coords(self, cluster):

		lat, lon = [], []
		for i in cluster:
			lat.append(i[0])
			lon.append(i[1])
		return lat, lon


	def plot_dots(self, clusters, file):

		if len(clusters) > 0:
			gmap = gmplot.GoogleMapPlotter(clusters[0][0][0], clusters[0][0][1], 11)

			color_list = self.colors(len(clusters))
			indx = 0
			for cluster in clusters:

				lat, lon = self.get_coords(cluster)
				gmap.scatter(lat, lon, color_list[indx], edge_width=5, marker=False)
				indx += 1

			if not os.path.exists('plottest'):
				os.makedirs('plottest')
			#gmap.draw('plottest/' + file + '.html')


	def plot(self):

		folder = '../timewindow/clusters/'
		for file in listdir(folder):
			if 'tuesday' in file: continue

			day_data = self.read_clusters(folder, file)
			for key in day_data.keys():
				self.plot_dots(day_data[key], file)

if __name__ == '__main__':

	mp = MapPlotter()
	mp.plot()
