import json
import pandas as pd
import numpy as np
import os

from shapely.geometry import Point

from clusteroperation import ClusterOperation

class Contextual:


	def load_clusters(self, day):
		with open(str(os.path.dirname(os.path.abspath(__file__)))+"/clusters/" + str(day) + '.json', "r") as file:
			return json.load(file)


	def __init__(self, city='chicago', month='January', day='sunday'):
		
		self.city = city
		self.month = month
		self.day = day
		
		self.all_clusters = self.load_clusters(day)
		self.co = ClusterOperation()


	def parzen_window(self, x, center, stan_deviation):
		return (1/(np.sqrt(2*np.pi*stan_deviation))) * (np.exp(-(((x-center)**2)/2)*(stan_deviation**2)))


	def find_last_window(self, windows, step_time):

		windows.sort()
		last_window = 0
		for window in windows:
			if window > step_time:
				return str(last_window)

			last_window = window

		return str(last_window)


	def calculate_score(self, start, end, key, step_time):
		
		point_1 = Point(start[0], start[1])
		point_2 = Point(end[0], end[1])
		line = [point_1, point_2]
		score = [0]

		# Without type
		if self.all_clusters[key][self.month].keys()[0] == 'unknown':

			windows = list(self.all_clusters[key][self.month]['unknown'].keys())
			last_window = self.find_last_window(windows, step_time)

			clusters = self.all_clusters[key][self.month]['unknown'][last_window]
			cluster_max_density = self.co.calculate_density(clusters)
			for cluster in self.co.get_clusters_info(clusters):
				center_dist, ext_dist, density = self.co.find_centroid_distance(cluster, line, cluster_max_density)
				if center_dist != -1:
					score.append(self.parzen_window(center_dist, ext_dist, density))

		# With type
		else:

			for types in self.all_clusters[key][self.month]:

				windows = list(self.all_clusters[key][self.month][types].keys())
				last_window = self.find_last_window(windows, step_time)
				
				clusters = self.all_clusters[key][self.month][types][last_window]
				cluster_max_density = self.co.calculate_density(clusters)
				for cluster in self.co.get_clusters_info(clusters):
					center_dist, ext_dist, density = self.co.find_centroid_distance(cluster, line, cluster_max_density)
					if center_dist != -1:
						score.append(self.parzen_window(center_dist, ext_dist, density))

		return max(score)


	def trade_off(self, traffic, start, end, step_time, context_weight={'traffic': 1, 'crimes': 1.5, 'crashes': 0.5}):

		scores = []
		valid_keys = [x for x in self.all_clusters if self.city in x]
		for key in valid_keys:
			scores.append(self.calculate_score(start, end, key, step_time))

		overall_score = traffic*context_weight['traffic']
		if overall_score < 0:
			overall_score = 0
			
		for indx, score in enumerate(scores):
			overall_score += score*context_weight[valid_keys[indx].split('_')[0]]

		return overall_score
		

if __name__ == '__main__':
	
	res = Contextual().load_clusters()
	print(res['friday']['crimes_2018_chicago']['March']['THEFT'])