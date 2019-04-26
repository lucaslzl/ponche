import numpy as np
import pandas as pd
import sys
from functools import reduce

import geopy.distance
from shapely.geometry import Point, shape, LinearRing, LineString
from shapely.geometry.polygon import Polygon


class ClusterOperation:


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


	def filter_cluster_points(self, cluster):

		cluster_filtered = []
		for c in cluster:
			cluster_filtered.append([c[0], c[1]])

		if len(cluster_filtered) > 3:
			cluster_valid = self.convex_hull_graham(cluster_filtered)
			if len(cluster_valid) > 3:
				cluster_filtered = cluster_valid

		return Polygon(cluster_filtered)


	def get_clusters_info(self, clusters):

		clusters_info = []
		for counter, cluster in enumerate(clusters):

			if len(cluster) > 0:

				x = np.mean([x[0] for x in cluster])
				y = np.mean([y[1] for y in cluster])

				centroid = (x, y)

				len_cluster = len(cluster)			

				cluster_poly = self.filter_cluster_points(cluster)

				cluster_dict = {}
				cluster_dict['id'] = str(counter)
				cluster_dict['centroid'] = centroid
				cluster_dict['len'] = int(len_cluster)
				cluster_dict['cluster_poly'] = cluster_poly
				clusters_info.append(cluster_dict)
	 
		return clusters_info


	def find_cluster_minmax(self, clusters, mini, maxi):

		for cluster in clusters:

			if len(cluster) > maxi:
				maxi = len(cluster)
		
			if len(cluster) < mini:
				mini = len(cluster)

		return mini, maxi


	def calculate_density(self, clusters):

		mini, maxi = sys.maxsize, 0

		for ch in clusters:
			mini, maxi = self.find_cluster_minmax(clusters, mini, maxi)

		return (mini, maxi)


	def get_nearest_point(self, cluster, point):
		pol_ext = LinearRing(cluster.exterior.coords)
		d = pol_ext.project(point)
		p = pol_ext.interpolate(d)
		nearest = list(p.coords)[0]
		return [nearest[0], nearest[1]]


	def get_nearest_point_from_line(self, line, point):
		pol_ext = LineString(line)
		d = pol_ext.project(point)
		p = pol_ext.interpolate(d)
		nearest = list(p.coords)[0]
		return [nearest[0], nearest[1]]


	def get_normalized(self, lengcluster, cluster):

		normalized = 1 - (cluster['len'] - lengcluster[0]) / (lengcluster[1] - lengcluster[0])
		if normalized != 0:
			return normalized
		else:
			return 0.001
			

	def find_centroid_distance(self, cluster, line, cluster_max_density):

		center_dist, ext_dist = 0, 0

		centroid_point = Point(cluster['centroid'][0], cluster['centroid'][1])
		p_near = self.get_nearest_point_from_line(line, centroid_point)
		center_dist = geopy.distance.distance(p_near, cluster['centroid']).km

		if Point(*p_near).within(cluster['cluster_poly']):
			point_exterior = self.get_nearest_point(cluster['cluster_poly'], Point(*p_near))
			ext_dist = geopy.distance.distance(p_near, point_exterior).km
		else:
			return -1, -1, -1

		normalize_density = self.get_normalized(cluster_max_density, cluster)

		return center_dist, center_dist + ext_dist, normalize_density