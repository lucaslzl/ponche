import traci
import logging
import networkx as nx
import random

import log_mannager


def update_traffic_on_roads(graph): #, safety_file_name):

    for road in graph.nodes_iter():

        average_speed = traci.edge.getLastStepMeanSpeed(road)
        max_speed = traci.lane.getMaxSpeed(str(road) + "_0")
        dummy_speed = float(max_speed - average_speed) / float(max_speed)
        #dummy_speed = max_speed - average_speed

        for successor_road in graph.successors_iter(road):

            if road[0] != ':':
                graph.edge[road][successor_road]["weight"] = (graph.edge[road][successor_road]["weight"] + dummy_speed) / 2.0

            else: 
                graph.edge[road][successor_road]["weight"] = (graph.edge[road][successor_road]["weight"] + dummy_speed) / 2.0
                
    return graph

# x, y = traci.vehicle.getPosition(vehID)
# print(traci.simulation.convertGeo(x, y))
def update_safety_on_roads(graph, safety):

    for road in graph.nodes_iter():

        logging.debug("Road: " + str(road))
        break

def building_route(s, t, r, pred_list, safety_index_list, G):
    route = []
    route.append(t)

    while s != t:
        pred = pred_list[(t, r)]
        route.insert(0, pred)
        edge_id = G.edge[pred][t]["id"]
        t = pred
        r = r - safety_index_list[edge_id]

    return route


def reroute_vehicles(graph, safety_index_list, p):


    for vehicle in traci.vehicle.getIDList():
        source = traci.vehicle.getRoadID(vehicle)
        if source.startswith(":"): continue
        route = traci.vehicle.getRoute(vehicle)
        destination = route[-1]

        if source != destination:

            logging.debug("Calculating optimal path for pair (%s, %s)" % (source, destination))

            shortest_path = nx.dijkstra_path(graph, source, destination, "weight")     
            traci.vehicle.setRoute(vehicle, shortest_path)
