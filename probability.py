import json
import random
import operator
from functools import reduce
import sys
import os
from os import listdir
from dateutil.parser import parse
from statistics import mean

import pandas as pd
import numpy as np
import geopy.distance
from shapely.geometry import Point, shape, LinearRing, LineString
from shapely.geometry.polygon import Polygon


def main():
	
	sumoBinary = "/usr/share/sumo/bin/sumo-gui"
	sumoCmd = [sumoBinary, "-c", "spider.sumocfg"]

	traci.start(sumoCmd)

if __name__ == '__main__':
	if 'SUMO_HOME' in os.environ:
		tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
		sys.path.append(tools)
		import traci
		main()
	else:   
		sys.exit("please declare environment variable 'SUMO_HOME'")