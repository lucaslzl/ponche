from bs4 import BeautifulSoup
import os
from os import listdir
import numpy as np
import matplotlib.pyplot as plt


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

		return results


	def calculate_metrics(self, result):

		# Metrics
		duration, route_length, waiting_time, waiting_count, time_loss = [], [], [], [], []

		tripinfos = result.find('tripinfos')

		for info in tripinfos.findAll('tripinfo'):
			
			duration.append(float(info['duration']))
			route_length.append(float(info['routeLength']))
			waiting_time.append(float(info['waitingTime']))
			waiting_count.append(float(info['waitingCount']))
			time_loss.append(float(info['timeLoss']))

		return {'duration': (np.std(duration), np.mean(duration)), 
				'route_length': (np.std(route_length), np.mean(route_length)),
				'waiting_time': (np.std(waiting_time), np.mean(waiting_time)),
				'waiting_count': (np.std(waiting_count), np.mean(waiting_count)),
				'time_loss': (np.std(time_loss), np.mean(time_loss))}


	def process_results(self, results):

		processed_results = {}

		for r in results:
			processed_results[r] = self.calculate_metrics(results[r])

		return processed_results


	def separate_mean_std(self, just_to_plot, metric, ordered_keys):

		means, stds = [], []

		for key in ordered_keys:
			means.append(just_to_plot[key][metric][0])
			stds.append(just_to_plot[key][metric][1])

		return means, stds

	def plot_bars(self, just_to_plot, metric):

		if not os.path.exists('plots'):
		    os.makedirs('plots')

		ordered_keys = just_to_plot.keys()
		ordered_keys.sort()

		plt.clf()
		ax = plt.subplot(111)

		xlabels = ['Austin #1', 'Austin #2', 'Austin #3', 'Austin #4', 
						'Chicago #1', 'Chicago #2', 'Chicago #3', 'Chicago #4']
		colors = ['#800000', '#469990', '#000075', '#e6194B', '#4363d8', '#911eb4', '#aaffc3', '#e6beff']

		means, stds = self.separate_mean_std(just_to_plot, metric, ordered_keys)
		
		for index, key in enumerate(ordered_keys):
			plt.plot(index, means[index], 'o')
		#ax.bar(xlabels, means, yerr=stds, align='center', alpha=0.7, color=colors, ecolor='gray', capsize=5)
		#ax.bar(xlabels, means, align='center', alpha=0.7, color=colors, capsize=5)

		plt.xticks(np.arange(0, len(xlabels)), xlabels, rotation=50)

		plt.savefig('plots/{0}.pdf'.format(metric), bbox_inches="tight", format='pdf')


	def plot(self, just_to_plot):

		ex_key = just_to_plot.keys()[0]
		metrics = just_to_plot[ex_key].keys()
		
		for metric in metrics:
			self.plot_bars(just_to_plot, metric)


if __name__ == '__main__':

	hp = HarryPlotter()
	results = hp.read_all_folders()
	just_to_plot = hp.process_results(results)
	hp.plot(just_to_plot)
