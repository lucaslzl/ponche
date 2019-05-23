from bs4 import BeautifulSoup
import os
from os import listdir
import numpy as np
import matplotlib.pyplot as plt


class HarryPlotter:

	METRIC_UNIT = {'duration' : 'Seconds',
					'route_length': 'Meters',
					'time_loss': 'Seconds',
					'traffic' : 'Traffic Level',
					'crimes': 'Insecurity Level',
					'crashes': 'Probability of Accident'}


	def normalize_data(self, results_log, city):

		metrics = results_log[results_log.keys()[0]].keys()
		normalized_mean = {}
		normalized_std = {}

		for m in metrics:
			normalized_mean[m] = []
			normalized_std[m] = []

		for key in [x for x in results_log if city in x]:
			for metric in results_log[key]:
				normalized_mean[metric].append(results_log[key][metric][0])
				normalized_std[metric].append(results_log[key][metric][1])

		for m in metrics:
			mini_m = min(normalized_mean[m])
			maxi_m = max(normalized_mean[m])
			mean_to_stand_m = np.mean(normalized_mean[m])
			std_to_stand_m = np.std(normalized_mean[m])

			mini_s = min(normalized_std[m])
			maxi_s = max(normalized_std[m])
			mean_to_stand_s = np.mean(normalized_std[m])
			std_to_stand_s = np.std(normalized_std[m])

			for key in [x for x in results_log if city in x]:
				value = results_log[key][m][0]
				#mean = (value - mini_m) / (maxi_m - mini_m)
				mean = (value - mean_to_stand_m) / std_to_stand_m

				value = results_log[key][m][1]
				#std = (value - mini_s) / (maxi_s - mini_s)
				std = (value - mean_to_stand_s) / std_to_stand_s

				results_log[key][m] = [mean, std]

		return results_log


	def read_results(self, file):

		f = open(file)
		data = f.read()
		soup = BeautifulSoup(data, "xml")
		f.close()
		
		return soup


	def process_line(self, line):
		
		mean = float(line.split('/')[0].split(':')[1])
		std = float(line.split('/')[1].split(':')[1])

		return [mean, std]


	def get_key(self, line):

		if 'Traffic' in line:
			return 'traffic'
		elif 'Crimes' in line:
			return 'crimes'
		else:
			return 'crashes'


	def read_log_results(self, file):
		
		read_next = False
		meansstds = {}
		metric = None
		with open(file) as fp:  
			for cnt, line in enumerate(fp):
	
				if read_next:
					meansstds[metric] = self.process_line(line)
					read_next = False

				if 'Traffic' in line or 'Crimes' in line or 'Crashes' in line:
					read_next = True
					metric = self.get_key(line)

		return meansstds


	def read_all_folders(self):

		results = {}

		for file in listdir('./'):

			if '_' in file:
				results[file] = self.read_results(file + '/reroute.xml')

		return results


	def read_log_files(self):

		results = {}

		for file in listdir('./'):

			if '_' in file:
				results[file] = self.read_log_results(file + '/sumo-launchd.log')

		return results


	def calculate_metrics(self, result):

		# Metrics
		duration, route_length, waiting_time, waiting_count, time_loss = [], [], [], [], []

		tripinfos = result.find('tripinfos')

		for info in tripinfos.findAll('tripinfo'):
			if 'duration' in info.attrs.keys() and 'routeLength' in info.attrs.keys() and 'timeLoss' in info.attrs.keys():
				duration.append(float(info['duration']))
				route_length.append(float(info['routeLength']))
				#waiting_time.append(float(info['waitingTime']))
				#waiting_count.append(float(info['waitingCount']))
				time_loss.append(float(info['timeLoss']))

		return {'duration': (np.std(duration), np.mean(duration)), 
				'route_length': (np.std(route_length), np.mean(route_length)),
				#'waiting_time': (np.std(waiting_time), np.mean(waiting_time)),
				#'waiting_count': (np.std(waiting_count), np.mean(waiting_count)),
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

		xlabels = ['Austin #1', 'Austin #2', 'Austin #3', 'Austin #4', 'Austin #5', 
						'Chicago #1', 'Chicago #2', 'Chicago #3', 'Chicago #4', 'Chicago #5']
		colors = ['#800000', '#469990', '#000075', '#e6194B', '#4363d8', '#911eb4', '#aaffc3', '#e6beff']

		means, stds = self.separate_mean_std(just_to_plot, metric, ordered_keys)
		
		for index, key in enumerate(ordered_keys):
			plt.plot(index, means[index], 'o--')
		#ax.bar(xlabels, means, yerr=stds, align='center', alpha=0.7, color=colors, ecolor='gray', capsize=5)
		#ax.bar(xlabels, means, align='center', alpha=0.7, color=colors, capsize=5)
		plt.xlabel('Execution Configuration')
		plt.ylabel(self.METRIC_UNIT[metric])
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
	results_log = hp.read_log_files()
	results_log = hp.normalize_data(results_log, 'Austin')
	results_log = hp.normalize_data(results_log, 'Chicago')
	just_to_plot = hp.process_results(results)

	for key in just_to_plot:
		just_to_plot[key] = results_log[key]

	print(just_to_plot)

	hp.plot(just_to_plot)
