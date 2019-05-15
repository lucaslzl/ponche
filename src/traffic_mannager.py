import traci
import logging
import networkx as nx
import random

import log_mannager


def update_traffic_on_roads(graph): #, safety_file_name):

    for road in graph.nodes():

        average_speed = traci.edge.getLastStepMeanSpeed(road)
        max_speed = traci.lane.getMaxSpeed(str(road) + "_0")

        dummy_speed = float(max_speed - average_speed) / float(max_speed)
        #dummy_speed = max_speed - average_speed
        if dummy_speed < 0:
            dummy_speed = 0

        for successor_road in graph.successors(road):
            graph.adj[road][successor_road]["weight"] = (graph.adj[road][successor_road]["weight"] + dummy_speed) / 2.0
                
    return graph


def invert_coords(coord):
    return (coord[1], coord[0])


def update_context_on_roads(graph, contextual, step):

    for road in graph.nodes():

        # Traffic
        average_speed = traci.edge.getLastStepMeanSpeed(road)
        max_speed = traci.lane.getMaxSpeed(str(road) + "_0")
        traffic = float(max_speed - average_speed) / float(max_speed)

        # Geo coordinates
        lane_coords = traci.lane.getShape(str(road) + "_0")
        start = traci.simulation.convertGeo(*lane_coords[0])
        end = traci.simulation.convertGeo(*lane_coords[1])

        start = invert_coords(start)
        end = invert_coords(end)
        
        # Trade-off
        step_time = step // 100
        weight = contextual.trade_off(traffic, start, end, step_time, context_weight={'traffic': 1, 'crimes': 1, 'crashes': 1})
        #weight = contextual.trade_off(traffic, start, end, step_time, context_weight={'traffic': 1, 'crimes': 2, 'crashes': 1})
        #weight = contextual.trade_off(traffic, start, end, step_time, context_weight={'traffic': 1, 'crimes': 1, 'crashes': 2})
        #weight = contextual.trade_off(traffic, start, end, step_time, context_weight={'traffic': 2, 'crimes': 1, 'crashes': 1})

        for successor_road in graph.successors(road):
            graph.adj[road][successor_road]["weight"] = (graph.adj[road][successor_road]["weight"] + weight) / 2.0

    return graph


def building_route(s, t, r, pred_list, safety_index_list, G):
    route = []
    route.append(t)

    while s != t:
        pred = pred_list[(t, r)]
        route.insert(0, pred)
        edge_id = G.adj[pred][t]["id"]
        t = pred
        r = r - safety_index_list[edge_id]

    return route


def reroute_vehicles(graph, p, error_count, total_count):

    vehicles = list(set(traci.vehicle.getIDList()))
    vehicles.sort()

    for vehicle in vehicles:
        source = traci.vehicle.getRoadID(vehicle)
        if source.startswith(":"): continue
        route = traci.vehicle.getRoute(vehicle)
        destination = route[-1]

        if source != destination:

            logging.debug("Calculating optimal path for pair (%s, %s)" % (source, destination))
            shortest_path = nx.dijkstra_path(graph, source, destination, "weight")

            try:
                total_count+=1
                traci.vehicle.setRoute(vehicle, shortest_path)
                #traci.vehicle.rerouteEffort(vehicle)

                print('\n\n')
                print(str(source))
                print(str(destination))
                print(str(route))
                print(str(shortest_path))
                print('\n\n')

                #exit()

            except Exception, e:
                error_count+=1

    return error_count, total_count
