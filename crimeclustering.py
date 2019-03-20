import pandas as pd
import numpy as np
import os, sys
import warnings

from scipy.signal import find_peaks
import hdbscan

class Clustering:

	'''
		Remove columns different from lat and long
	'''
	def encode(self, data):
		data = data.drop(['type', 'hour', 'minute'], axis=1)
		return data

	'''
		Clusterize crime data
	'''
	def clusterize(self, data, ep=0.01):

		data_formated = self.encode(data.copy())
		clustering = hdbscan.HDBSCAN(min_cluster_size=3).fit_predict(data_formated)
		data['cluster'] = clustering
		
		return data.sort_values('cluster')

######################################################################

class Util:

	MONTHS = {
				1  : 'January',
				2  : 'February',
				3  : 'March',
				4  : 'April',
				5  : 'May',
				6  : 'June',
				7  : 'July',
				8  : 'August',
				9  : 'September',
				10 : 'October',
				11 : 'November',
				12 : 'December',
	}

	def remove_invalid_coord(self, df): #[-90; 90]
		return df.query('lat >= -90 & lat <= 90').query('lon >= -90 & lat <= 90')

	def format_digits(self, number):

		if len(str(number)) < 2:
			number = '0' + str(number)
		return str(number)

	def format_clusters(self, data):

		clusters = []
		clusters.append([])
		lastid = 0

		if data is not None:

			data = data.query('cluster > -1')

			for indx, row in data.iterrows():
				if row['cluster'] > lastid:
					clusters.append([])
					lastid = row['cluster']
				clusters[-1].append((row['lat'], row['lon']))

		return clusters

	def read_data(self, day):

		data_file = open('data/' + day + '/crimes.csv', 'r')

		crime_list = []

		for line in data_file:
			line = line.strip().split(',')

			item = {}
			item['datetime'] = pd.to_datetime(str(line[0]), format='%Y/%m/%d %H:%M')
			item['hour'] = pd.to_datetime(str(line[0]), format='%Y/%m/%d %H:%M').hour
			item['minute'] = pd.to_datetime(str(line[0]), format='%Y/%m/%d %H:%M').minute
			item['lat'] = float(line[1])
			item['lon'] = float(line[2])
			item['type'] = line[3].strip()

			crime_list.append(item)

		df = pd.DataFrame(crime_list)
		df.set_index('datetime', inplace=True)

		return self.remove_invalid_coord(df)

	def write_clusters(self, clusters, month, day, start, crime):

		if not os.path.exists('clusters'):
			os.makedirs('clusters')

		output_file = open('clusters/{0}_{1}_{2}_{3}_clusters.txt'.format(self.MONTHS[month], str(day), crime, self.format_digits(str(start))), 'w')

		for cluster in clusters:
			for point in cluster:
				output_file.write(str(point[0]) + ' ' + str(point[1]) + '; ')

			output_file.write('\n')
		output_file.close()

######################################################################

class TimeMinutesClustering:

	def __init__(self):
		self.u = Util()

	def make_gauss(self, N=1, sig=1, mu=0):
		return lambda x: N/(sig * (2*np.pi)**.5) * np.e ** (-(x-mu)**2/(105 * sig**2))

	def calculate_difference(self, hour, minute, ref_hour, ref_minute):

		time = hour*60 + minute
		ref_time = ref_hour*60 + ref_minute

		xt = time - ref_time

		score = self.make_gauss()(xt)

		return float('%.5f' % (score))

	def normalize(self, window_scores):

		maxi = np.amax(window_scores)
		mini = np.amin(window_scores)

		for indx, w in enumerate(window_scores):
			window_scores[indx] = (w - mini) / (maxi - mini)

		return window_scores


	def calculate_score(self, crimes_filtered):

		window_scores = []

		for hour in range(0, 24):

			for minute in range(0, 60, 10):

				state_score = []
				for index, row in crimes_filtered.iterrows():
					state_score.append(self.calculate_difference(row['hour'], row['minute'], hour, minute))

				window_scores.append(np.sum(state_score))

		return self.normalize(window_scores)

	def identify_window(self, window_scores, peaks):

		last_peak = 0
		apeaks = []

		peaks.append(len(window_scores)-1)

		for peak in peaks:

			mini = last_peak + np.argmin(window_scores[last_peak:peak])

			if window_scores[mini] == 0.0:
				apeaks.append(mini)

				zero_indx = mini
				while zero_indx < len(window_scores) and window_scores[zero_indx] == 0.0:
					zero_indx += 1
				
				apeaks.append(zero_indx-1)

			else:
				apeaks.append(mini)

			last_peak = peak

		if apeaks[0] < 3:
			apeaks[0] = 0
		if apeaks[0] != 0:
			apeaks.insert(0, 0)

		if apeaks[-1] > len(window_scores) - 3:
			apeaks[-1] = len(window_scores) - 1
		elif apeaks[-1] != len(window_scores)-1:
			apeaks.append(len(window_scores)-1)

		return apeaks

	def get_window(self, start, end, crimes_filtered):

		start_hour = start * 10 // 60
		start_minute = start * 10 % 60

		end_hour = end * 10 // 60
		end_minute = end * 10 % 60

		# Filter the closed interval
		crimes_opened = crimes_filtered.query('hour > {0} & hour < {1}'.format(start_hour, end_hour))

		# Filter the opened interval
		crimes_closed_low = crimes_filtered.query('hour == {0} & minute >= {1}'.format(start_hour, start_minute))
		crimes_closed_high = crimes_filtered.query('hour == {0} & minute < {1}'.format(end_hour, end_minute))

		return pd.concat([crimes_opened, crimes_closed_low, crimes_closed_high])

	def format_clusters(self, data):

		clusters = []
		clusters.append([])
		lastid = 0

		data = data.query('Cluster > -1')

		for indx, row in data.iterrows():
			if row['Cluster'] > lastid:
				clusters.append([])
				lastid = row['Cluster']
			clusters[-1].append((row['lat'], row['lon']))

		return clusters

	def clusterize(self, month_crimes, clustering, month, day):

		crimes = month_crimes.groupby('type').all().index

		for crime in crimes:
			
			crimes_filtered = month_crimes.query("type == '%s'" % crime)
				
			window_scores = self.calculate_score(crimes_filtered)

			peaks = find_peaks(window_scores, distance=3)[0].tolist()

			if len(peaks) > 0:
			
				window = self.identify_window(window_scores, peaks)

				if len(window) > 0:

					iterwindow = iter(window)
					next(iterwindow)
					last_window = window[0]
					for iw in iterwindow:

						crimes_window = self.get_window(last_window, iw, crimes_filtered)

						cluster_crime = None
						if len(crimes_window) >= 3:
							cluster_crime = clustering.clusterize(crimes_window).query('cluster != -1')

						self.u.write_clusters(self.u.format_clusters(cluster_crime), month, day, iw, crime)

						last_window = iw

def main():

	u = Util()
	tmc = TimeMinutesClustering()
	clustering = Clustering()

	for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:

		print('### ' + day)

		day_crimes = u.read_data(day)
				
		for month in range(1, 13):

			print('#' + u.MONTHS[month])

			month_crimes = day_crimes['2018-' + str(month)]

			tmc.clusterize(month_crimes, clustering, month, day)

if __name__ == '__main__':
	warnings.simplefilter("ignore")
	main()
