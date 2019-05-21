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

from k_shortest_paths import k_shortest_paths
from optparse import OptionParser

import sumo_mannager
import graph_mannager
import log_mannager
import traffic_mannager
import traci

import os,sys,inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from timewindow.contextual import Contextual


def iterate_metrics(traffic, crimes, crashes, all_metrics):

    for metrics in all_metrics:
        traffic.append(metrics['traffic'])
        crimes.append(metrics['crimes'])
        crashes.append(metrics['crashes'])


              
def run(network, begin, end, interval, route_log, replication, p):

    logging.debug("Building road graph")         
    road_network_graph = graph_mannager.build_road_graph(network)
    
    error_count, total_count = 0, 0
    logging.debug("Reading contextual data")
    contextual = Contextual()
    
    logging.debug("Running simulation now")    
    step = 1
    # The time at which the first re-routing will happen
    # The time at which a cycle for collecting travel time measurements begins
    travel_time_cycle_begin = interval

    traffic, crimes, crashes = [], [], []

    while step == 1 or traci.simulation.getMinExpectedNumber() > 0:
        logging.debug("Minimum expected number of vehicles: %d" % traci.simulation.getMinExpectedNumber())
        traci.simulationStep()

        #log_densidade_speed(step)

        logging.debug("Simulation time %d" % step)

        # if step % 60 == 0:
        # logging.debug("Updating travel time on roads at simulation time %d" % step)
        # road_network_graph = traffic_mannager.update_context_on_roads(road_network_graph, contextual, step)
    
        if step >= travel_time_cycle_begin and travel_time_cycle_begin <= end and step%interval == 0:
            road_network_graph, all_metrics = traffic_mannager.update_context_on_roads(road_network_graph, contextual, step)
            iterate_metrics(traffic, crimes, crashes, all_metrics)
            logging.debug("Updating travel time on roads at simulation time %d" % step)

            error_count, total_count = traffic_mannager.reroute_vehicles(road_network_graph, p, error_count, total_count)           

        step += 1

    logging.debug('##### Route total count: ' + str(total_count))
    logging.debug('##### Route success count: ' + str(total_count - error_count))
    logging.debug('##### Route error count: ' + str(error_count))
    logging.debug('##### Traffic: \n {0} \n Mean: {1} / Std: {2}'.format(str(traffic), str(np.mean(traffic)), str(np.std(traffic))))
    logging.debug('##### Crimes: \n {0} \n Mean: {1} / Std: {2}'.format(str(crimes), str(np.mean(crimes)), str(np.std(crimes))))
    logging.debug('##### Crashes: \n {0} \n Mean: {1} / Std: {2}'.format(str(crashes), str(np.mean(crashes)), str(np.std(crashes))))
    
    #time.sleep(10)
    logging.debug("Simulation finished")
    traci.close()
    sys.stdout.flush()
    #time.sleep(10)
        
def start_simulation(sumo, scenario, network, begin, end, interval, output, summary, route_log, replication, p):
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
        run(network, begin, end, interval, route_log, replication, float(p))
    except Exception, e:
        logging.exception("Something bad happened")
    finally:
        logging.exception("Terminating SUMO")  
        sumo_mannager.terminate_sumo(sumo)
        unused_port_lock.__exit__()
        
def main():
    # Option handling

    pred_list = {}

    parser = OptionParser()
    parser.add_option("-c", "--command", dest="command", default="sumo", help="The command used to run SUMO [default: %default]", metavar="COMMAND")
    parser.add_option("-s", "--scenario", dest="scenario", default="../sumo/chicago.sumo.cfg", help="A SUMO configuration file [default: %default]", metavar="FILE")
    parser.add_option("-n", "--network", dest="network", default="../sumo/chicago.net.xml", help="A SUMO network definition file [default: %default]", metavar="FILE")    
    parser.add_option("-b", "--begin", dest="begin", type="int", default=1500, action="store", help="The simulation time (s) at which the re-routing begins [default: %default]", metavar="BEGIN")
    parser.add_option("-e", "--end", dest="end", type="int", default=7000, action="store", help="The simulation time (s) at which the re-routing ends [default: %default]", metavar="END")
    parser.add_option("-i", "--interval", dest="interval", type="int", default=250, action="store", help="The interval (s) of classification [default: %default]", metavar="INTERVAL")
    parser.add_option("-o", "--output", dest="output", default="reroute.xml", help="The XML file at which the output must be written [default: %default]", metavar="FILE")
    parser.add_option("-l", "--logfile", dest="logfile", default="sumo-launchd.log", help="log messages to logfile [default: %default]", metavar="FILE")
    parser.add_option("-m", "--summary", dest="summary", default="summary.xml", help="The XML file at which the summary output must be written [default: %default]", metavar="FILE")
    parser.add_option("-r", "--route-log", dest="route_log", default="route-log.txt", help="Log of the entire route of each vehicle [default: %default]", metavar="FILE")
    parser.add_option("-t", "--replication", dest="replication", default="1", help="number of replications [default: %default]", metavar="REPLICATION")
    parser.add_option("-p", "--percentage", dest="percentage", default="1", help="percentage of improvement on safety [default: %default]", metavar="REPLICATION")

    (options, args) = parser.parse_args()
    
    logging.basicConfig(filename=options.logfile, level=logging.DEBUG)
    logging.debug("Logging to %s" % options.logfile)
    
    if args:
        logging.warning("Superfluous command line arguments: \"%s\"" % " ".join(args))
        
    start_simulation(options.command, options.scenario, options.network, options.begin, options.end, options.interval, options.output, options.summary, options.route_log, options.replication, options.percentage)
    
if __name__ == "__main__":
    main()    
    
