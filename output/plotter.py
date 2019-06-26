from bs4 import BeautifulSoup
import os
from os import listdir
import numpy as np
import matplotlib.pyplot as plt
import json
import math


class HarryPlotter:

	METRIC_UNIT = {'duration' : 'seconds',
					'route_length': 'meters',
					'time_loss': 'seconds',
					'traffic' : 'traffic load score',
					'crimes': 'insecurity level',
					'crashes': 'accident probability'}


	def read_xml_file(self, file):

		f = open(file)
		data = f.read()
		soup = BeautifulSoup(data, "xml")
		f.close()
		
		return soup


	def read_json_file(self, file):

		with open(file, "r") as file:
			return json.load(file)


	def mean_confidence_interval(self, data, confidence=0.95):
		a = 1.0 * np.array(data)
		n = len(a)
		m, se = np.mean(a), np.std(a)
		h = 1.96 * (se/math.sqrt(n))
		return (m, h)


	def get_reroute_metrics(self, ires):

		duration, route_length, time_loss = [], [], []

		tripinfos = ires.find('tripinfos')

		for info in tripinfos.findAll('tripinfo'):

			try:
				dur = float(info['duration'])
				rou = float(info['routeLength'])
				tim = float(info['timeLoss'])

				if dur > 10.00 and rou > 50.00:
					duration.append(dur)
					route_length.append(rou)
					time_loss.append(tim)
			except Exception:
				pass

		return np.mean(duration), np.mean(route_length), np.mean(time_loss)


	def calculate_reroute_metrics(self, accumulated):

		return {'duration': self.mean_confidence_interval(accumulated['duration']),
				'route_length': self.mean_confidence_interval(accumulated['route_length']),
				'time_loss': self.mean_confidence_interval(accumulated['time_loss'])}


	def read_reroute_files(self, results, days):

		for city in ['austin', 'chicago']:

			for folder in listdir('data/monday/{0}'.format(city)):

				accumulated = {'duration': [],
							'route_length': [],
							'time_loss': []}

				for day in days:

					for iterate in range(20):
						ires = self.read_xml_file('./data/{0}/{1}/{2}/{3}_reroute.xml'.format(day, city, folder, iterate))
						dur, rou, tim = self.get_reroute_metrics(ires)
						accumulated['duration'].append(dur)
						accumulated['route_length'].append(rou)
						accumulated['time_loss'].append(tim)
					
				results['reroute_{0}_{1}'.format(city, folder)] = self.calculate_reroute_metrics(accumulated)

		return results


	def get_contextual_metrics(self, ires):
		return float(ires['traffic']['mean']), float(ires['crimes']['mean']), float(ires['crashes']['mean'])


	def calculate_contextual_metrics(self, accumulated):

		return {'traffic': self.mean_confidence_interval(accumulated['traffic']),
				'crimes': self.mean_confidence_interval(accumulated['crimes']),
				'crashes': self.mean_confidence_interval(accumulated['crashes'])}


	def read_contextual_files(self, results, day):

		for city in ['austin', 'chicago']:

			for folder in listdir('data/monday/{0}'.format(city)):

				accumulated = {'traffic': [],
							'crimes': [],
							'crashes': []}

				for day in days:

					for iterate in range(20):
						ires = self.read_json_file('./data/{0}/{1}/{2}/{3}_metrics.json'.format(day, city, folder, iterate))
						tra, cri, cra = self.get_contextual_metrics(ires)
						accumulated['traffic'].append(tra)
						accumulated['crimes'].append(cri)
						accumulated['crashes'].append(cra)

				results['context_{0}_{1}'.format(city, folder)] = self.calculate_contextual_metrics(accumulated)

		return results


	def save_calculation(self, results, file='all'):

		if not os.path.exists('results'):
			os.makedirs('results')

		with open('results/{0}_results.json'.format(file), "w") as write_file:
			json.dump(results, write_file, indent=4)


	def read_calculation(self):

		results = {}

		for file in listdir('results/'):

			with open('results/{0}'.format(file), "r") as write_file:
				results[file] = json.load(write_file)

		return results


	def filter_keys(self, results, sfilter='context'):

		filtered_keys = [x for x in results.keys() if sfilter in x]

		filtered_dict = {}
		for f in filtered_keys:
			filtered_dict[f] = results[f]
		
		metrics = results[filtered_keys[0]].keys()

		return filtered_dict, metrics


	def separate_mean_std(self, just_to_plot, metric, keys_order):

		means, stds = [], []

		# Austin
		for key in keys_order:
			k = [x for x in just_to_plot if key in x and 'austin' in x][0]

			means.append(just_to_plot[k][metric][0])
			stds.append(just_to_plot[k][metric][1])

		# Chicago
		for key in keys_order:
			k = [x for x in just_to_plot if key in x and 'chicago' in x][0]

			means.append(just_to_plot[k][metric][0])
			stds.append(just_to_plot[k][metric][1])			

		return means, stds


	def plot_dots(self, just_to_plot, metric, file):

		if not os.path.exists('metric_plots'):
		    os.makedirs('metric_plots')

		plt.clf()
		ax = plt.subplot(111)

		cities = ['austin', 'chicago']
		keys_order = ['traffic', 'crimes', 'crashes', 'same', 'mtraffic', 'mcrimes', 'mcrashes', 'maxtraffic', 'maxcrimes', 'maxcrashes', 'baseline']

		xlabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'Baseline']

		means, stds = self.separate_mean_std(just_to_plot, metric, keys_order)
		
		#plt.plot(np.arange(0, 8), means[0:8], 'o-.', color='#1d4484', label='Austin')
		plt.errorbar(np.arange(0, 11), means[0:11], yerr=stds[0:11], fmt='o-.', color='#1d4484', label='Austin', capsize=5)
		#plt.plot(np.arange(8, 16), means[8:16], 'o-.', color='#7c0404', label='Chicago')
		plt.errorbar(np.arange(0, 11), means[11:22], yerr=stds[11:22], fmt='s-.', color='#7c0404', label='Chicago', capsize=5)
		
		plt.xlabel('Execution Configuration', fontweight='bold', fontsize=12)
		plt.ylabel('{0} ({1})'.format(metric.replace('_', ' ').capitalize(), self.METRIC_UNIT[metric]), fontweight='bold', fontsize=12)
		plt.xticks(np.arange(0, len(xlabels)), xlabels, rotation=50, fontweight='bold', fontsize=12)

		ax.legend()

		plt.savefig('metric_plots/{0}_{1}.pdf'.format(file.split('.')[0], metric), bbox_inches="tight", format='pdf')


	def plot(self, results, file):
		
		contextual, cmetrics = self.filter_keys(results)
		mobility, mmetrics = self.filter_keys(results, sfilter='reroute')

		for metric in cmetrics:
			self.plot_dots(contextual, metric, file)

		for metric in mmetrics:
			self.plot_dots(mobility, metric, file)


if __name__ == '__main__':

	hp = HarryPlotter()

	# calls
	results = {}
	'''days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
	
	hp.read_reroute_files(results, days)
	hp.read_contextual_files(results, days)
	hp.save_calculation(results)

	for day in days:

		results = {}
		hp.read_reroute_files(results, [day])
		hp.read_contextual_files(results, [day])
		hp.save_calculation(results, day)'''

	results = hp.read_calculation()
	for res in results:
		hp.plot(results[res], res)


