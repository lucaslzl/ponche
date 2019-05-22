import traci
import logging
import networkx as nx
import random

#import log_mannager


def invert_coords(coord):
    return (coord[1], coord[0])


def update_context_on_roads(graph, contextual, step):

    all_metrics = []

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
        step_time = step // 10
        weight, metrics = contextual.trade_off(traffic, start, end, step_time)
        #weight, metrics = contextual.trade_off(traffic, start, end, step_time, context_weight={'traffic': 1, 'crimes': 2, 'crashes': 1})
        #weight, metrics = contextual.trade_off(traffic, start, end, step_time, context_weight={'traffic': 1, 'crimes': 1, 'crashes': 2})
        #weight, metrics = contextual.trade_off(traffic, start, end, step_time, context_weight={'traffic': 2, 'crimes': 1, 'crashes': 1})

        all_metrics.append(metrics)

        for successor_road in graph.successors(road):
            #graph.adj[road][successor_road]["weight"] = (graph.adj[road][successor_road]["weight"] + weight) / 2.0
            graph.adj[road][successor_road]["weight"] = weight

    return graph, all_metrics


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
            shortest_path = nx.algorithms.shortest_paths.weighted.bidirectional_dijkstra(graph, source, destination, "weight")
            #shortest_path = nx.algorithms.shortest_paths.astar.astar_path(graph, source, destination)
            
            try:
                total_count+=1
                traci.vehicle.setRoute(vehicle, shortest_path[1])
                #traci.vehicle.rerouteTraveltime(vehicle)
            except Exception, e:
                error_count+=1
                #print('\n\n ROUTE: {0} \n SHORTEST: {1}\n\n'.format(str(route), str(shortest_path)))

    return error_count, total_count

