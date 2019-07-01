#!/usr/bin/env python

from __future__ import division

import subprocess
import os
import logging
import sys
import tempfile
import math
import random
import time
import numpy as np
import json
import warnings
import multiprocessing as mp

from k_shortest_paths import k_shortest_paths
from optparse import OptionParser

import sumo_mannager
import graph_mannager
#import log_mannager
import traffic_mannager
import traci
import time

import inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from timewindow.contextual import Contextual


def iterate_metrics(all_metrics):

    traffic, crimes, crashes = [], [], []

    for metrics in all_metrics:
        traffic.append(metrics['traffic'])
        crimes.append(metrics['crimes'])
        crashes.append(metrics['crashes'])

    return traffic, crimes, crashes


def create_output_file(total_count, success_count, error_count, traffic, crimes, crashes, iterate, config, city, day):

    traffic_ms = (np.mean(traffic), np.std(traffic))
    crimes_ms = (np.mean(crimes), np.std(crimes))
    crashes_ms = (np.mean(crashes), np.std(crashes))

    metrics = {}
    metrics['total_count'] = total_count
    metrics['success_count'] = success_count
    metrics['error_count'] = error_count

    metrics['out_traffic'] = traffic
    metrics['out_crimes'] = crimes
    metrics['out_crashes'] = crashes

    metrics['traffic'] = {'mean': traffic_ms[0], 'std': traffic_ms[1]}
    metrics['crimes'] = {'mean': crimes_ms[0], 'std': crimes_ms[1]}
    metrics['crashes'] = {'mean': crashes_ms[0], 'std': crashes_ms[1]}

    with open('../output/data/{0}/{1}/{2}/{3}_metrics.json'.format(day, city, config, iterate), "w") as write_file:
        json.dump(metrics, write_file, indent=4)


def run(network, begin, end, interval, route_log, replication, p, iterate, indx_config, config, city, day):

    logging.debug("Building road graph")
    road_network_graph = graph_mannager.build_road_graph(network)
    
    error_count, total_count = 0, 0
    logging.debug("Reading contextual data")
    contextual = Contextual(city=city, day=day)
    
    logging.debug("Running simulation now")
    step = 1
    # The time at which the first re-routing will happen
    # The time at which a cycle for collecting travel time measurements begins
    travel_time_cycle_begin = interval

    road_map = {}
    all_metrics = []

    start_time = time.time()

    while step == 1 or traci.simulation.getMinExpectedNumber() > 0:
        logging.debug("Minimum expected number of vehicles: %d" % traci.simulation.getMinExpectedNumber())
        traci.simulationStep()

        logging.debug("Simulation time %d" % step)
    
        if step >= travel_time_cycle_begin and travel_time_cycle_begin <= end and step%interval == 0:

            road_network_graph = traffic_mannager.update_context_on_roads(road_network_graph, contextual, step, indx_config, road_map)
            logging.debug("Updating travel time on roads at simulation time %d" % step)

            error_count, total_count, acumulated_context = traffic_mannager.reroute_vehicles(road_network_graph, p, error_count, total_count, indx_config, road_map)
            all_metrics += acumulated_context

        step += 1

    traffic, crimes, crashes = iterate_metrics(all_metrics)

    create_output_file(total_count, total_count - error_count, error_count, traffic, crimes, crashes, iterate, config, city, day)

    final_time = time.time()
    print('########### TIME: ', float(final_time - start_time))
    
    #time.sleep(10)
    logging.debug("Simulation finished")
    traci.close()
    sys.stdout.flush()
    #time.sleep(10)
        
def start_simulation(sumo, scenario, network, begin, end, interval, output, summary, route_log, replication, p, iterate, indx_config, config, city, day):
    logging.debug("Finding unused port")
    
    unused_port_lock = sumo_mannager.UnusedPortLock()
    unused_port_lock.__enter__()
    remote_port = sumo_mannager.find_unused_port()
    
    logging.debug("Port %d was found" % remote_port)
    
    logging.debug("Starting SUMO as a server")
    
    sumo = subprocess.Popen([sumo, "-W", "-c", scenario, "--tripinfo-output", output, "--device.emissions.probability", "1.0", "--summary-output", summary,"--remote-port", str(remote_port)], stdout=sys.stdout, stderr=sys.stderr)    
    unused_port_lock.release()
            
    try:     
        traci.init(remote_port)    
        run(network, begin, end, interval, route_log, replication, float(p), iterate, indx_config, config, city, day)
    except Exception, e:
        logging.exception("Something bad happened")
    finally:
        logging.exception("Terminating SUMO")  
        sumo_mannager.terminate_sumo(sumo)
        unused_port_lock.__exit__()


def parallel_main_loop(city, iterate, config, day, indx_config):
    
    pred_list = {}

    parser = OptionParser()
    parser.add_option("-c", "--command", dest="command", default="sumo", help="The command used to run SUMO [default: %default]", metavar="COMMAND")
    parser.add_option("-s", "--scenario", dest="scenario", default="../scenario/cfgs/{0}_{1}.sumo.cfg".format(city, iterate), help="A SUMO configuration file [default: %default]", metavar="FILE")
    parser.add_option("-n", "--network", dest="network", default="../scenario/{0}.net.xml".format(city), help="A SUMO network definition file [default: %default]", metavar="FILE")    
    parser.add_option("-b", "--begin", dest="begin", type="int", default=1500, action="store", help="The simulation time (s) at which the re-routing begins [default: %default]", metavar="BEGIN")
    parser.add_option("-e", "--end", dest="end", type="int", default=7000, action="store", help="The simulation time (s) at which the re-routing ends [default: %default]", metavar="END")
    parser.add_option("-i", "--interval", dest="interval", type="int", default=250, action="store", help="The interval (s) of classification [default: %default]", metavar="INTERVAL")
    parser.add_option("-o", "--output", dest="output", default="../output/data/{0}/{1}/{2}/{3}_reroute.xml".format(day, city, config, iterate), help="The XML file at which the output must be written [default: %default]", metavar="FILE")
    parser.add_option("-l", "--logfile", dest="logfile", default="sumo-launchd.log", help="log messages to logfile [default: %default]", metavar="FILE")
    parser.add_option("-m", "--summary", dest="summary", default="../output/data/{0}/{1}/{2}/{3}_summary.xml".format(day, city, config, iterate), help="The XML file at which the summary output must be written [default: %default]", metavar="FILE")
    parser.add_option("-r", "--route-log", dest="route_log", default="../output/data/{0}/{1}/{2}/{3}_route-log.txt".format(day, city, config, iterate), help="Log of the entire route of each vehicle [default: %default]", metavar="FILE")
    parser.add_option("-t", "--replication", dest="replication", default="1", help="number of replications [default: %default]", metavar="REPLICATION")
    parser.add_option("-p", "--percentage", dest="percentage", default="1", help="percentage of improvement on safety [default: %default]", metavar="REPLICATION")

    (options, args) = parser.parse_args()
    
    logging.basicConfig(filename=options.logfile, level=logging.DEBUG)
    logging.debug("Logging to %s" % options.logfile)
    
    if args:
        logging.warning("Superfluous command line arguments: \"%s\"" % " ".join(args))
        
    start_simulation(options.command, options.scenario, options.network, options.begin, 
        options.end, options.interval, options.output, options.summary, options.route_log, 
        options.replication, options.percentage, iterate, indx_config, config, city, day)
    
    #if os.path.exists('sumo-launchd.log'):
    #    os.remove('sumo-launchd.log')
        
def main():
    # Option handling

    for day in ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']:

        for city in ['austin', 'chicago']:
        
            if not os.path.exists('../output/data'):
                os.makedirs('../output/data')
            
            if not os.path.exists('../output/data/{0}/{1}'.format(day, city)):
                os.makedirs('../output/data/{0}/{1}'.format(day, city))

            for indx_config, config in enumerate(['traffic', 'crimes', 'crashes', 'same', 'mtraffic', 'mcrimes', 'mcrashes', 'maxtraffic', 'maxcrimes', 'maxcrashes', 'baseline']):
    
                if not os.path.exists('../output/data/{0}/{1}/{2}'.format(day, city, config)):
                    os.makedirs('../output/data/{0}/{1}/{2}'.format(day, city, config))

                processes = [mp.Process(target=parallel_main_loop, args=(city, iterate, config, day, indx_config)) for iterate in range(20)]

                # Run processes
                for p in processes:
                    p.start()

                # Exit the completed processes
                for p in processes:
                    p.join()

                    
                    
if __name__ == "__main__":
    warnings.simplefilter("ignore")
    main()    
    
