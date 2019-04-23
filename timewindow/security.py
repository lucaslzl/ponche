import json

class Security:

	def load_clusters(self):

		data = {}

		for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:
			with open("clusters/" + str(day) + '.json', "r") as file:
				data[day] = json.load(file)
		return data


	def __init__(self):
		self.clusters = self.load_clusters()

	def calculate_security(self, geos):
		pass

	def calculate_crashy(self, geos):
		pass

	def trade_off(self, geos):

		security = self.calculate_security(geos)
		crashy = self.calculate_crashy(geos)

		return security + crashy

if __name__ == '__main__':
	
	res = Security().load_clusters()
	print(res['friday']['crimes_2018_chicago']['March']['THEFT'])