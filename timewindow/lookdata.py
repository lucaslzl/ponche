import pandas as pd
import numpy as np
import os, sys
import warnings
import matplotlib.pyplot as plt
import gmplot
from sklearn.cluster import DBSCAN
import random
import json


def remove_invalid_coord(df): #[-90; 90]
	#return df.query('lat >= -90 & lat <= 90').query('lon >= -90 & lat <= 90')
	return df.query('lat != 0 & lon != 0')

def read_data(day='monday', city='chicago', types='crimes'):

	data_file = open('data/{0}/{1}_2018_{2}.csv'.format(day, types, city), 'r')

	crime_list = []

	for line in data_file:
		line = line.strip().split(',')

		item = {}
		item['datetime'] = pd.to_datetime(str(line[0]), format='%Y/%m/%d %H:%M')
		item['month'] = pd.to_datetime(str(line[0]), format='%Y/%m/%d %H:%M').month
		item['hour'] = pd.to_datetime(str(line[0]), format='%Y/%m/%d %H:%M').hour
		item['lat'] = float(line[1])
		item['lon'] = float(line[2])
		item['type'] = line[3].strip()
		item['export'] = 0

		crime_list.append(item)

	df = pd.DataFrame(crime_list)
	df.set_index('datetime', inplace=True)

	return remove_invalid_coord(df)

def read_all_data(city='chicago', types='crimes'):

	df = []

	for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
		
		if len(df) == 0:
			df = read_data(day, city=city, types=types)
		else:
			df = pd.concat([df, read_data(day, city=city, types=types)])

	return df


def see_density():
	# Le os dados
	df = read_all_data()
	#print(df.head())

	df_month_type = df.groupby(['month', 'type']).count()

	#print(min(df_month_type['export']))
	#print(max(df_month_type['export']))

	crimes = df.groupby('type').all().index

	# for c in crimes:

		# df_crime = df.query("type == '%s'" % c)

		# filtered = df_crime.groupby(['month']).count()

		# plt.figure()

		# months = ['', 'Jan.', 'Feb.', 'Mar.', 'Apr.', 'May', 'Jun.', 
		# 			'Jul.', 'Aug.', 'Sep.', 'Oct.', 'Nov.', 'Dec.']

		# filtered['export'].plot(legend=None, title=c, style='.:')
		
		# plt.xlabel('Months')
		# plt.ylabel('Quantity of Crimes')
		# plt.xticks(range(13), months, rotation=50)
		# plt.yticks(range(0, 7000, 500), [x for x in range(0, 7000, 500)])

		# if not os.path.exists('density'):
		# 	os.makedirs('density')

		# plt.savefig('density/'+ c + '.pdf', bbox_inches="tight", format='pdf')

		# plt.clf()

	# Export
	df.groupby(['month', 'type']).count()['export'].to_csv('density_austin.csv')


###############################################################################################################

###############################################################################################################

###############################################################################################################

def colors(n):
	ret = []
	for i in range(n):
		r = int(random.random() * 256)
		g = int(random.random() * 256)
		b = int(random.random() * 256)
		r = int(r) % 256
		g = int(g) % 256
		b = int(b) % 256
		ret.append('#{:02X}{:02X}{:02X}'.format(r,g,b)) 
	return ret


def plot_heat(clusters, day, city, types):

	plt.clf()
	gmap = gmplot.GoogleMapPlotter(clusters.iloc[0]['lat'], clusters.iloc[0]['lon'], 11)

	lats, longs = [], []
			
	for indx, cluster in clusters.iterrows():
		lats.append(float(cluster['lat']))
		longs.append(float(cluster['lon']))

	gmap.heatmap(lats, longs)

	if not os.path.exists('plottest'):
		os.makedirs('plottest')
	gmap.draw('plottest/{0}_{1}_{2}.html'.format(city, types, day))


def see_distribution():

	city='chicago'
	types='crimes'

	# for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
	# 	df = read_data(day, city, types)
	# 	df = df.drop(['type', 'hour', 'month', 'export'], axis=1)
	# 	clustering = DBSCAN(eps=0.001, min_samples=3).fit_predict(df)
	# 	df['cluster'] = clustering
	# 	plot_heat(df.query('cluster != -1'), day, city, types)


	df = read_all_data(city, types)
	
	df = df.drop(['type', 'hour', 'month', 'export'], axis=1)
	clustering = DBSCAN(eps=0.001, min_samples=3).fit_predict(df)
	df['cluster'] = clustering
	plot_heat(df.query('cluster != -1'), 'all', city, types)


###############################################################################################################

###############################################################################################################

###############################################################################################################

def format_clusters(data):

	clusters = []
	clusters.append([])
	lastid = 0

	data = data.query('cluster > -1')

	for indx, row in data.iterrows():
		if row['cluster'] > lastid:
			clusters.append([])
			lastid = row['cluster']
		clusters[-1].append((row['lat'], row['lon']))

	return clusters


def get_coords(cluster):

	lat, lon = [], []
	for i in cluster:
		lat.append(i[0])
		lon.append(i[1])
	return lat, lon


def plot_dots(clusters, day, city, types, each):

	plt.clf()
	if len(clusters) > 0 and len(clusters[0]) > 0:
		gmap = gmplot.GoogleMapPlotter(float(clusters[0][0][0]), float(clusters[0][0][1]), 11)

		color_list = colors(len(clusters))
		indx = 0
		for cluster in clusters:

			lat, lon = get_coords(cluster)
			gmap.scatter(lat, lon, color_list[indx], edge_width=5, marker=False)
			indx += 1
			#break

		if not os.path.exists('plottest'):
			os.makedirs('plottest')
		gmap.draw('plottest/{0}_{1}_{2}_{3}_dots.html'.format(city, types, day, each))


def load_clusters(day):
		with open(str(os.path.dirname(os.path.abspath(__file__)))+"/clusters/" + str(day) + '.json', "r") as file:
			return json.load(file)


def see_maps():

	city='austin'
	types='crashes'
	day='monday'

	clusters = load_clusters(day)['{0}_2018_{1}'.format(types, city)]['January']['unkown']

	for each in clusters:
		plot_dots(clusters[each], day, city, types, each)



see_distribution()
#see_maps()
