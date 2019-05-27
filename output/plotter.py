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
				time_loss.append(float(info['timeLoss']))

		return {'duration': (np.mean(duration), np.std(duration)),
				'route_length': (np.mean(route_length), np.std(route_length)),
				'time_loss': (np.mean(time_loss), np.std(time_loss))}


	def read_reroute_files(self, results):

		for city in ['austin', 'chicago']:

			for folder in listdir('./data/'+city):

				ires = self.read_xml_file('./data/{0}/{1}/reroute.xml'.format(city, folder))
				results['route_{0}_{1}'.format(city, folder)] = self.get_metrics(ires)

		return results


	def read_metric_files(self, results):

		for city in ['austin', 'chicago']:

			for folder in listdir('./data/'+city):

				ires = self.read_json_file('./data/{0}/{1}/metrics.json'.format(city, folder))
				results['context_{0}_{1}'.format(city, folder)] = ires

		return results


	def save_calculation(self, results):

		with open('all_results.json', "w") as write_file:
			json.dump(results, write_file, indent=4)


	def separate_mean_std(self, just_to_plot, metric, ordered_keys):

		means, stds = [], []

		for key in ordered_keys:
			means.append(just_to_plot[key][metric][0])
			stds.append(just_to_plot[key][metric][1])

		return means, stds


	def plot_bars(self, just_to_plot, metric):

		if not os.path.exists('metric_plots'):
		    os.makedirs('metric_plots')

		ordered_keys = just_to_plot.keys()
		ordered_keys.sort()

		plt.clf()
		ax = plt.subplot(111)

		xlabels = ['Austin #1', 'Austin #2', 'Austin #3', 'Austin #4', 'Austin #5', 'Austin #6', 'Austin #7',
						'Chicago #1', 'Chicago #2', 'Chicago #3', 'Chicago #4', 'Chicago #5', 'Chicago #6', 'Chicago #7']
		colors = ['#800000', '#469990', '#000075', '#e6194B', '#4363d8', '#911eb4', '#aaffc3', '#e6beff']

		means, stds = self.separate_mean_std(just_to_plot, metric, ordered_keys)
		
		for index, key in enumerate(ordered_keys):
			plt.plot(index, means[index], 'o--')
		#ax.bar(xlabels, means, yerr=stds, align='center', alpha=0.7, color=colors, ecolor='gray', capsize=5)
		#ax.bar(xlabels, means, align='center', alpha=0.7, color=colors, capsize=5)
		plt.xlabel('Execution Configuration')
		plt.ylabel('{0} ({1})'.format(metric.replace('_', ' ').capitalize(), self.METRIC_UNIT[metric]))
		plt.xticks(np.arange(0, len(xlabels)), xlabels, rotation=50)

		plt.savefig('metric_plots/{0}.pdf'.format(metric), bbox_inches="tight", format='pdf')


	def plot(self, results):

		print(results.keys())
		ex_key = results.keys()[0]
		metrics = results[ex_key].keys()
		
		contextual = [x for x in results.keys() if 'context' in x]
		print(contextual)

		#for metric in metrics:
		#	self.plot_bars(just_to_plot, metric)


if __name__ == '__main__':

	hp = HarryPlotter()
	
	results = {}

	hp.read_reroute_files(results)
	hp.read_metric_files(results)

	hp.save_calculation(results)

	hp.plot(results)
