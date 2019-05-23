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


	# https://en.wikipedia.org/wiki/Normal_distribution
	# First part = 1/sqrt()
	# Second part = euler**(...)
	def calculate_gaussian(self, x, density, p_mean, p_std):
		gaussian = (1/(np.sqrt(2*np.pi*(p_std**2)))) * np.exp(-(((x-p_mean)**2)/(2*(p_std**2))))
		return  gaussian #+ (density * 0.1)

	def find_last_window(self, windows, step_time):

		windows = list(map(int, windows))
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
				center_dist, density, p_mean, p_std = self.co.find_centroid_distance(cluster, line, cluster_max_density)
				if center_dist != -1:
					score.append(self.calculate_gaussian(center_dist, density, p_mean, p_std))

		# With type
		else:

			for types in self.all_clusters[key][self.month]:

				windows = list(self.all_clusters[key][self.month][types].keys())
				last_window = self.find_last_window(windows, step_time)

				clusters = self.all_clusters[key][self.month][types][last_window]
				cluster_max_density = self.co.calculate_density(clusters)

				for cluster in self.co.get_clusters_info(clusters):
					center_dist, density, p_mean, p_std = self.co.find_centroid_distance(cluster, line, cluster_max_density)
					if center_dist != -1:
						score.append(self.calculate_gaussian(center_dist, density, p_mean, p_std))

		return max(score)


	def prepare_to_return(self, traffic, scores, valid_keys):

		metrics = {}

		metrics['traffic'] = traffic

		for indx, score in enumerate(scores):
			metrics[valid_keys[indx].split('_')[0]] = score

		return metrics


	def trade_off(self, traffic, start, end, step_time, context_weight={'traffic': 1, 'crimes': 1, 'crashes': 1}):

		scores = []
		valid_keys = [str(x) for x in self.all_clusters if self.city in x]
		valid_keys.sort()
		
		for key in valid_keys:
			scores.append(self.calculate_score(start, end, key, step_time))

		overall_score = traffic*context_weight['traffic']
			
		for indx, score in enumerate(scores):
			overall_score += score*context_weight[valid_keys[indx].split('_')[0]]

		if overall_score < 1:
			overall_score = 1

		return overall_score, self.prepare_to_return(traffic, scores, valid_keys)
		

if __name__ == '__main__':
	
	res = Contextual().load_clusters()
	print(res['friday']['crimes_2018_chicago']['March']['THEFT'])