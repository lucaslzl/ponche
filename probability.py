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
	sumoCmd = [sumoBinary, "-c", "sumo/spider.sumocfg"]

	vehID = '0'

	traci.start(sumoCmd)
	traci.vehicle.subscribe(vehID, (tc.VAR_ROAD_ID, tc.VAR_LANEPOSITION))

	for step in range(1000):
		traci.simulationStep()

		print(traci.vehicle.getSubscriptionResults(vehID))
		
		if traci.inductionloop.getLastStepVehicleNumber("0") > 0:
			traci.trafficlight.setRedYellowGreenState("0", "GrGr")
		
	traci.close()

'''
Help Codes

x, y = traci.vehicle.getPosition(vehID)
lon, lat = traci.simulation.convertGeo(x, y)
x2, y2 = traci.simulation.convertGeo(lon, lat, fromGeo=True)

'''


if 'SUMO_HOME' in os.environ:
	tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
	sys.path.append(tools)
	import traci
	import traci.constants as tc
	main()
else:
	sys.exit("please declare environment variable 'SUMO_HOME'")