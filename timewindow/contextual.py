import json
import pandas as pd
import numpy as np

from functools import reduce
import geopy.distance
from shapely.geometry import Point, shape, LinearRing, LineString
from shapely.geometry.polygon import Polygon

class Contextual:


	def load_clusters(self, day):
		with open("clusters/" + str(day) + '.json', "r") as file:
			return json.load(file)


	def __init__(self, day):
		self.clusters = self.load_clusters(day)


	def convex_hull_graham(self, points):
		TURN_LEFT, TURN_RIGHT, TURN_NONE = (1, -1, 0)

		def cmp(a, b):
			return int((a > b)) - int((a < b))

		def turn(p, q, r):
			return cmp((q[0] - p[0])*(r[1] - p[1]) - (r[0] - p[0])*(q[1] - p[1]), 0)

		def _keep_left(hull, r):
			while len(hull) > 1 and turn(hull[-2], hull[-1], r) != TURN_LEFT:
				hull.pop()
			if not len(hull) or hull[-1] != r:
				hull.append(r)
			return hull

		points = sorted(points)
		l = reduce(_keep_left, points, [])
		u = reduce(_keep_left, reversed(points), [])
		return l.extend(u[i] for i in range(1, len(u) - 1)) or l


	def calculate_unsafety(self, start, end):
		
		point_1 = Point(*start)
		point_2 = Point(*end)
		line = [point_1, point_2]

		clusters = None

		for c in clusters[hour]:

			centroid_point = Point(*c['centroid'])
			p_near = self.u.get_nearest_point_from_line(line, centroid_point)
			point_center_dist = geopy.distance.distance(p_near, c['centroid']).km

			if Point(*p_near).within(c['cluster_poly']):
				point_exterior = self.u.get_nearest_point(c['cluster_poly'], Point(*p_near))
				point_exterior_dist = geopy.distance.distance(p_near, point_exterior).km

				overall_prob.append(self.u.parzen_window(point_center_dist, point_center_dist + point_exterior_dist, self.u.get_normalized(cluster_density, c)))


	def calculate_crashy(self, start, end):
		pass


	def trade_off(self, traffic, start, end):

		security = self.calculate_unsafety(start, end)
		crashy = self.calculate_crashy(start, end)

		return (traffic + security*2 + crashy*0.5)

if __name__ == '__main__':
	
	res = Contextual().load_clusters()
	print(res['friday']['crimes_2018_chicago']['March']['THEFT'])