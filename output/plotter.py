from bs4 import BeautifulSoup
import os
from os import listdir
import numpy as np


class HarryPlotter:


	def read_results(self, file):

		f = open(file)
		data = f.read()
		soup = BeautifulSoup(data, "xml")
		f.close()
		
		return soup


	def read_all_folders(self):

		results = {}

		for file in listdir('./'):

			if '_' in file:
				results[file] = self.read_results(file + '/reroute.xml')

		print(results.keys())


	def calculate_metrics(self, result):

		# Metrics
		duration, route_length, waiting_time, waiting_count, time_loss = [], [], [], [], []

		tripinfos = result.find('tripinfos')

		for info in tripinfos.findAll('tripinfo'):
			
			duration.append(info['duration'])
			route_length.append(info['routeLength'])
			waiting_time.append(info['waitingTime'])
			waiting_count.append(info['waitingCount'])
			time_loss.append(info['timeLoss'])

		return {'duration': (np.std(duration) np.mean(duration)), 
				'route_length': (np.std(route_length) np.mean(route_length)),
				'waiting_time': (np.std(waiting_time) np.mean(waiting_time)),
				'waiting_count': (np.std(waiting_count) np.mean(waiting_count)),
				'time_loss': (np.std(time_loss) np.mean(time_loss))}


	def process_results(self, results):

		processed_results = {}

		for r in results:
			processed_results[r] = self.calculate_metrics(results[r])

		return processed_results


if __name__ == '__main__':

	hp = HarryPlotter()
	results = hp.read_all_folders()
	just_to_plot = hp.process_results(results)
