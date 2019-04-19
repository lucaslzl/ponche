import numpy as np
import pandas as pd
import os
from os import listdir


'''
	Read and separate crime data into two way:
	- Days of the week
	- Week and weekend
'''

class SplitData:

	DAYS   = { 0 : 'monday', 1 : 'tuesday', 2 : 'wednesday', 3 : 'thursday', 4 : 'friday', 5 : 'saturday', 6 : 'sunday' }
	
	'''
		Read crime data
	'''
	def read_data(self, file):

		data_file = open(file, 'r')

		crime_list = []
		for line in data_file:
			line = line.strip().split('\t')
			item = {}
			item['DateTime'] = pd.to_datetime(str(line[0]))
			item['Latitude'] = float(line[1])
			item['Longitude'] = float(line[2])
			item['Type'] = line[3]

			crime_list.append(item)
		data_file.close()

		df = pd.DataFrame(crime_list)

		df.set_index('DateTime')
		df['Dayofweek'] = df['DateTime'].dt.dayofweek

		return df

	def read_data_folder(self, folder):

		dfs = {}

		for file in listdir(folder):
			dfs[str(file)] = self.read_data(folder + file)

		return dfs

	'''
		Filter crime data according to day and time window
	'''
	def filtering_data(self, df, dayofweek):
		df_filtered = df.query('Dayofweek ==' + str(dayofweek))
		return df_filtered

	''' 
		Filter crime data according to week / weekend and time window
	'''
	def filtering_data_weekend(self, df, dayofweek):

		query = ''
		for day in dayofweek:
			query += 'Dayofweek == ' + str(day)
			if day != dayofweek[-1]:
				query += ' | '

		df_filtered = df.query(query)
		return df_filtered

	'''
		Save according to chosen day and time window
	'''
	def write_data(self, key, df, dayofweek):

		if not os.path.exists('data'):
		    os.makedirs('data')

		if not os.path.exists('data/' + self.DAYS[dayofweek]):
			os.makedirs('data/' + self.DAYS[dayofweek])

		output_file = open('data/' + self.DAYS[dayofweek] + '/' + key, 'w')

		for dateTime, row in df.iterrows():
			output_file.write('{0}, {1}, {2}, {3}'.format(str(row['DateTime']), str(row['Latitude']), str(row['Longitude']), str(row['Type'])) + '\n')

		output_file.close()

	'''
		Read and split data
	'''
	def split(self):

		print('Reading')
		dfs = self.read_data_folder('input_data/')
		weekend = False

		# weekend = True separa em 2 grupos: dias da semana e final de semana
		if weekend:
			for dayofweek in [[0, 1, 2, 3, 4], [5, 6]]:
				print(dayofweek)
				for key in dfs:
					print(key)
					df_filtered = self.filtering_data_weekend(dfs[key], dayofweek)
					self.write_data(key, df_filtered, dayofweek[0])
		else:
			for dayofweek in range(7):
				print(dayofweek)
				for key in dfs:
					print(key)
					df_filtered = self.filtering_data(dfs[key], dayofweek)
					self.write_data(key, df_filtered, dayofweek)

######################################################################

def main():

	sp = SplitData()
	sp.split()

if __name__ == '__main__':
	main()