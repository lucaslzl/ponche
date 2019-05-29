from bs4 import BeautifulSoup
import os
from os import listdir
import numpy as np
import matplotlib.pyplot as plt
import json


class HarryPlotter:

	METRIC_UNIT = {'duration' : 'seconds',
					'route_length': 'meters',
					'time_loss': 'seconds',
					'traffic' : 'vehicle density',
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


	def mean_confidence_interval(data, confidence=0.95):
		a = 1.0 * np.array(data)
		n = len(a)
		m, se = np.mean(a), scipy.stats.sem(a)
		h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
		return m, m-h, m+h


	def get_metrics(self, ires):

		duration, route_length, time_loss = [], [], []

		tripinfos = ires.find('tripinfos')

		for info in tripinfos.findAll('tripinfo'):
			if 'duration' in info.attrs.keys() and 'routeLength' in info.attrs.keys() and 'timeLoss' in info.attrs.keys():
				duration.append(float(info['duration']))
				route_length.append(float(info['routeLength']))
				try:
					time_loss.append(float(info['timeLoss']))
				except Exception, e:
					time_loss.append(0.0)

		return {'duration': (np.mean(duration), np.std(duration)),
				'route_length': (np.mean(route_length), np.std(route_length)),
				'time_loss': (np.mean(time_loss), np.std(time_loss))}


	def calculate_metrics(self, accumulated):

		mean_duration, mean_route_length, mean_time_loss = [], [], []
		std_duration, std_route_length, std_time_loss = [], [], []


		for ires in accumulated:
			mean_duration.append(ires['duration'][0])
			std_duration.append(ires['duration'][1])
			
			mean_route_length.append(ires['route_length'][0])
			std_route_length.append(ires['route_length'][1])
			
			mean_time_loss.append(ires['time_loss'][0])
			std_time_loss.append(ires['time_loss'][1])

		return {'duration': (np.mean(mean_duration), np.mean(std_duration)),
				'route_length': (np.mean(mean_route_length), np.mean(std_route_length)),
				'time_loss': (np.mean(mean_time_loss), np.mean(std_time_loss))}


	def calculate_contextual_metrics(self, accumulated):

		mean_traffic, mean_crimes, mean_crashes = [], [], []
		std_traffic, std_crimes, std_crashes = [], [], []

		for ires in accumulated:
			mean_traffic.append(ires['traffic']['mean'])
			std_traffic.append(ires['traffic']['std'])

			mean_crimes.append(ires['crimes']['mean'])
			std_crimes.append(ires['crimes']['std'])

			mean_crashes.append(ires['crashes']['mean'])
			std_crashes.append(ires['crashes']['std'])

		return {'traffic': (np.mean(mean_traffic), np.mean(std_traffic)),
				'crimes': (np.mean(mean_crimes), np.mean(std_crimes)),
				'crashes': (np.mean(mean_crashes), np.mean(std_crashes))}


	def read_reroute_files(self, results):

		for city in ['austin', 'chicago']:

			for folder in listdir('data/' + city):

				accumulated = []

				for iterate in range(33):
					ires = self.read_xml_file('./data/{0}/{1}/{2}_reroute.xml'.format(city, folder, iterate))
					accumulated.append(self.get_metrics(ires))
				
				results['route_{0}_{1}'.format(city, folder)] = self.calculate_metrics(accumulated)

		return results


	def read_metric_files(self, results):

		for city in ['austin', 'chicago']:

			for folder in listdir('data/' + city):

				accumulated = []

				for iterate in range(33):
					ires = self.read_json_file('./data/{0}/{1}/{2}_metrics.json'.format(city, folder, iterate))
					accumulated.append(ires)

				results['context_{0}_{1}'.format(city, folder)] = self.calculate_contextual_metrics(accumulated)

		return results


	def save_calculation(self, results):

		with open('all_results.json', "w") as write_file:
			json.dump(results, write_file, indent=4)


	def separate_mean_std(self, just_to_plot, metric, keys_order):

		means, stds = [], []

		# Austin
		for key in keys_order:
			k = [x for x in just_to_plot if key in x and 'austin' in x][0]

			means.append(just_to_plot[k][metric][0])
			stds.append(just_to_plot[k][metric][1])

		for key in keys_order:
			k = [x for x in just_to_plot if key in x and 'chicago' in x][0]

			means.append(just_to_plot[k][metric][0])
			stds.append(just_to_plot[k][metric][1])			

		return means, stds


	def plot_bars(self, just_to_plot, metric):

		if not os.path.exists('metric_plots'):
		    os.makedirs('metric_plots')

		plt.clf()
		ax = plt.subplot(111)

		# xlabels = ['Austin #1', 'Austin #2', 'Austin #3', 'Austin #4', 'Austin #5', 'Austin #6', 'Austin #7',
		# 				'Chicago #1', 'Chicago #2', 'Chicago #3', 'Chicago #4', 'Chicago #5', 'Chicago #6', 'Chicago #7']
		colors = ['#800000', '#469990', '#000075', '#e6194B', '#4363d8', '#911eb4', '#aaffc3', '#e6beff']

		cities = ['austin', 'chicago']
		keys_order = ['traffic', 'crimes', 'crashes', 'same', 'mtraffic', 'mcrimes', 'mcrashes']

		xlabels = ['Atraffic', 'Acrimes', 'Acrashes', 'Asame', 'Amtraffic', 'Amcrimes', 'Amcrashes',
		 				'Ctraffic', 'Ccrimes', 'Ccrashes', 'Csame', 'Cmtraffic', 'Cmcrimes', 'Cmcrashes']

		means, stds = self.separate_mean_std(just_to_plot, metric, keys_order)
		
		for index, key in enumerate(xlabels):
			plt.plot(index, means[index], 'o--')
		#ax.bar(xlabels, means, yerr=stds, align='center', alpha=0.7, color=colors, ecolor='gray', capsize=5)
		#ax.bar(xlabels, means, align='center', alpha=0.7, color=colors, capsize=5)
		plt.xlabel('Execution Configuration')
		plt.ylabel('{0} ({1})'.format(metric.replace('_', ' ').capitalize(), self.METRIC_UNIT[metric]))
		plt.xticks(np.arange(0, len(xlabels)), xlabels, rotation=50)

		plt.savefig('metric_plots/{0}.pdf'.format(metric), bbox_inches="tight", format='pdf')


	def filter_keys(self, results, sfilter='context'):

		filtered_keys = [x for x in results.keys() if sfilter in x]

		filtered_dict = {}
		for f in filtered_keys:
			filtered_dict[f] = results[f]
		
		metrics = results[filtered_keys[0]].keys()

		return filtered_dict, metrics


	def plot(self, results):
		
		contextual, cmetrics = self.filter_keys(results)
		mobility, mmetrics = self.filter_keys(results, sfilter='route')

		for metric in cmetrics:
			self.plot_bars(contextual, metric)

		for metric in mmetrics:
			self.plot_bars(mobility, metric)


if __name__ == '__main__':

	hp = HarryPlotter()
	
	results = {}

	hp.read_reroute_files(results)
	hp.read_metric_files(results)
	hp.save_calculation(results)

	hp.plot(results)
