from bs4 import BeautifulSoup
import os
from os import listdir
import numpy as np
import matplotlib.pyplot as plt
import json
import scipy.stats
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
		m, se = np.mean(a), scipy.stats.sem(a)
		#h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
		h = 1.96 * (se/math.sqrt(140))
		return m, h, m-h, m+h


	def mean_confidence_interval_day(self, data, confidence=0.95):
		a = 1.0 * np.array(data)
		n = len(a)
		m, se = np.mean(a), scipy.stats.sem(a)
		h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
		return (m, h)


	def get_metrics(self, ires):

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

		return {'duration': (np.mean(duration), np.std(duration)),
				'route_length': (np.mean(route_length), np.std(route_length)),
				'time_loss': (np.mean(time_loss), np.std(time_loss))}


	def calculate_metrics(self, accumulated):

		duration, route_length, time_loss = [], [], []


		for ires in accumulated:
			duration.append(ires['duration'][0])
			route_length.append(ires['route_length'][0])
			time_loss.append(ires['time_loss'][0])

		return {'duration': self.mean_confidence_interval_day(duration),
				'route_length': self.mean_confidence_interval_day(route_length),
				'time_loss': self.mean_confidence_interval_day(time_loss)}


	def calculate_contextual_metrics(self, accumulated):

		traffic, crimes, crashes = [], [], []

		for ires in accumulated:
			traffic.append(ires['traffic']['mean'])
			crimes.append(ires['crimes']['mean'])
			crashes.append(ires['crashes']['mean'])

		return {'traffic': self.mean_confidence_interval_day(traffic),
				'crimes': self.mean_confidence_interval_day(crimes),
				'crashes': self.mean_confidence_interval_day(crashes)}


	def read_reroute_files(self, results, day):

		for city in ['austin', 'chicago']:

			for folder in listdir('data/{0}/{1}'.format(day, city)):

				accumulated = []

				for iterate in range(20):
					ires = self.read_xml_file('./data/{0}/{1}/{2}/{3}_reroute.xml'.format(day, city, folder, iterate))
					accumulated.append(self.get_metrics(ires))
				
				results['route_{0}_{1}'.format(city, folder)] = self.calculate_metrics(accumulated)

		return results


	def read_metric_files(self, results, day):

		for city in ['austin', 'chicago']:

			for folder in listdir('data/{0}/{1}'.format(day, city)):

				accumulated = []

				for iterate in range(20):
					ires = self.read_json_file('./data/{0}/{1}/{2}/{3}_metrics.json'.format(day, city, folder, iterate))
					accumulated.append(ires)

				results['context_{0}_{1}'.format(city, folder)] = self.calculate_contextual_metrics(accumulated)

		return results


	def save_calculation(self, results, day):

		if not os.path.exists('results'):
			os.makedirs('results')

		with open('results/{0}_results.json'.format(day), "w") as write_file:
			json.dump(results, write_file, indent=4)


	def read_calculation(self, day):

		with open('results/{0}_results.json'.format(day), "r") as write_file:
			return json.load(write_file)


	def filter_keys(self, results, sfilter='context'):

		filtered_keys = [x for x in results.keys() if sfilter in x]

		filtered_dict = {}
		for f in filtered_keys:
			filtered_dict[f] = results[f]
		
		metrics = results[filtered_keys[0]].keys()

		return filtered_dict, metrics

	def format_plot_pattern(self, results, contextual, cmetrics, mobility, mmetrics):

		formatted_res_cont = {}
		formatted_res_mob = {}

		for key in contextual:

			formatted_res_cont[key] = {}

			for cm in cmetrics:

				all_values = []

				for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:

					all_values.append(results[day][key][cm][0])

				mean, height, hp, hm = self.mean_confidence_interval(all_values)
				formatted_res_cont[key][cm] = (mean, height)

		for key in mobility:

			formatted_res_mob[key] = {}

			for mm in mmetrics:

				all_values = []

				for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:

					all_values.append(results[day][key][mm][0])

				mean, height, hp, hm = self.mean_confidence_interval(all_values)
				formatted_res_mob[key][mm] = (mean, height)

		return formatted_res_cont, formatted_res_mob


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


	def plot_dots(self, just_to_plot, metric):

		if not os.path.exists('metric_plots'):
		    os.makedirs('metric_plots')

		plt.clf()
		ax = plt.subplot(111)

		cities = ['austin', 'chicago']
		keys_order = ['traffic', 'crimes', 'crashes', 'same', 'mtraffic', 'mcrimes', 'mcrashes', 'baseline']

		xlabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'Baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'Baseline']

		means, stds = self.separate_mean_std(just_to_plot, metric, keys_order)
		
		#plt.plot(np.arange(0, 8), means[0:8], 'o-.', color='#1d4484', label='Austin')
		plt.errorbar(np.arange(0, 8), means[0:8], yerr=stds[0:8], fmt='o-.', color='#1d4484', label='Austin', capsize=5)
		#plt.plot(np.arange(8, 16), means[8:16], 'o-.', color='#7c0404', label='Chicago')
		plt.errorbar(np.arange(8, 16), means[8:16], yerr=stds[8:16], fmt='o-.', color='#7c0404', label='Chicago', capsize=5)
		
		plt.xlabel('Execution Configuration')
		plt.ylabel('{0} ({1})'.format(metric.replace('_', ' ').capitalize(), self.METRIC_UNIT[metric]))
		plt.xticks(np.arange(0, len(xlabels)), xlabels, rotation=50)

		ax.legend()

		plt.savefig('metric_plots/{0}.pdf'.format(metric), bbox_inches="tight", format='pdf')


	def plot_dots_day(self, just_to_plot, metric, day):

		if not os.path.exists('metric_plots'):
		    os.makedirs('metric_plots')

		plt.clf()
		ax = plt.subplot(111)

		cities = ['austin', 'chicago']
		keys_order = ['traffic', 'crimes', 'crashes', 'same', 'mtraffic', 'mcrimes', 'mcrashes', 'baseline']

		xlabels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'Baseline', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'Baseline']

		means, stds = self.separate_mean_std(just_to_plot, metric, keys_order)
		
		#plt.plot(np.arange(0, 8), means[0:8], 'o-.', color='#1d4484', label='Austin')
		plt.errorbar(np.arange(0, 8), means[0:8], yerr=stds[0:8], fmt='o-.', color='#1d4484', label='Austin', capsize=5)
		#plt.plot(np.arange(8, 16), means[8:16], 'o-.', color='#7c0404', label='Chicago')
		plt.errorbar(np.arange(8, 16), means[8:16], yerr=stds[8:16], fmt='o-.', color='#7c0404', label='Chicago', capsize=5)
		
		plt.xlabel('Execution Configuration')
		plt.ylabel('{0} ({1})'.format(metric.replace('_', ' ').capitalize(), self.METRIC_UNIT[metric]))
		plt.xticks(np.arange(0, len(xlabels)), xlabels, rotation=50)

		ax.legend()

		plt.savefig('metric_plots/{0}_{1}.pdf'.format(day, metric), bbox_inches="tight", format='pdf')


	def plot(self, results):
		
		contextual, cmetrics = self.filter_keys(results['sunday'])
		mobility, mmetrics = self.filter_keys(results['sunday'], sfilter='route')

		contextual, mobility = self.format_plot_pattern(results, contextual, cmetrics, mobility, mmetrics)

		for metric in cmetrics:
			self.plot_dots(contextual, metric)

		for metric in mmetrics:
			self.plot_dots(mobility, metric)


	def plot_day(self, results, day):
		
		contextual, cmetrics = self.filter_keys(results)
		mobility, mmetrics = self.filter_keys(results, sfilter='route')

		for metric in cmetrics:
			self.plot_dots_day(contextual, metric, day)

		for metric in mmetrics:
			self.plot_dots_day(mobility, metric, day)


if __name__ == '__main__':

	hp = HarryPlotter()
	
	results = {}

	for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
		hp.read_reroute_files(results, day)
		hp.read_metric_files(results, day)
		hp.save_calculation(results, day)
		results[day] = hp.read_calculation(day)
		hp.plot_day(results[day], day)
	
	hp.plot(results)

