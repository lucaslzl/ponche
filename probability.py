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