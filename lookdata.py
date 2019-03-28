import pandas as pd
import numpy as np
import os, sys
import warnings
import matplotlib.pyplot as plt


def remove_invalid_coord(df): #[-90; 90]
	return df.query('lat >= -90 & lat <= 90').query('lon >= -90 & lat <= 90')

def read_data(day):

	data_file = open('data/' + day + '/crimes.csv', 'r')

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

def read_all_data():

	df = []

	for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
		
		if len(df) == 0:
			df = read_data(day)
		else:
			df = pd.concat([df, read_data(day)])

	return df


# Le os dados
df = read_all_data()
#print(df.head())

# Export
df.groupby(['month', 'type']).count()['export'].to_csv('density.csv')

# Plot
plt.figure()

#print(df.groupby(['month', 'type']).count().head())

filtered = df.groupby(['month', 'type']).count()

plt.xticks(range(len(filtered)), ['' for i in range(len(filtered))])
filtered.plot(y='export')

plt.show()