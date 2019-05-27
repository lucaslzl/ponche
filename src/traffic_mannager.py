import traci
import logging
import networkx as nx
import random

#import log_mannager

CONTEXT_CONFIG = {'0' : {'traffic': 1, 'crimes': 0, 'crashes': 0},
                  '1' : {'traffic': 0, 'crimes': 1, 'crashes': 0},
                  '2' : {'traffic': 0, 'crimes': 0, 'crashes': 1},
                  '3' : {'traffic': 1, 'crimes': 1, 'crashes': 1},
                  '4' : {'traffic': 2, 'crimes': 1, 'crashes': 1},
                  '5' : {'traffic': 1, 'crimes': 2, 'crashes': 1},
                  '6' : {'traffic': 1, 'crimes': 1, 'crashes': 2}}


def invert_coords(coord):
    return (coord[1], coord[0])


def update_road_map(road_map, road, metrics):

    road_map[road]['traffic'] = metrics['traffic']
    road_map[road]['crimes'] = metrics['crimes']
    road_map[road]['crashes'] = metrics['crashes']


def update_context_on_roads(graph, contextual, step, indx_config, road_map):

    for road in graph.nodes():

        if road not in road_map.keys():
            road_map[str(road)] = {'traffic': 0, 'crimes': 0, 'crashes': 0}

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
        step_time = step // 35
        weight, metrics = contextual.trade_off(traffic, start, end, step_time, context_weight=CONTEXT_CONFIG[str(indx_config)])
        update_road_map(road_map, str(road), metrics)

        for successor_road in graph.successors(road):
            #graph.adj[road][successor_road]["weight"] = (graph.adj[road][successor_road]["weight"] + weight) / 2.0
            graph.adj[road][successor_road]["weight"] = weight

    return graph


def reroute_vehicles(graph, p, error_count, total_count, road_map):

    vehicles = list(set(traci.vehicle.getIDList()))
    vehicles.sort()

    acumulated_context = []

    for vehicle in vehicles:

        context_metrics = {'traffic': 0, 'crimes': 0, 'crashes': 0}

        source = traci.vehicle.getRoadID(vehicle)
        if source.startswith(":"): continue
        route = traci.vehicle.getRoute(vehicle)
        destination = route[-1]

        if source != destination:

            logging.debug("Calculating optimal path for pair (%s, %s)" % (source, destination))
            shortest_path = nx.algorithms.shortest_paths.weighted.bidirectional_dijkstra(graph, source, destination, "weight")

            try:
                total_count+=1
                traci.vehicle.setRoute(vehicle, shortest_path[1])

                for vertex in list(shortest_path[1]):
                    context_metrics['traffic'] += road_map[vertex]['traffic']
                    context_metrics['crimes'] += road_map[vertex]['crimes']
                    context_metrics['crashes'] += road_map[vertex]['crashes']

                acumulated_context.append(context_metrics)

                #traci.vehicle.rerouteTraveltime(vehicle)
            except Exception, e:
                error_count+=1
                #print('\n\n ROUTE: {0} \n SHORTEST: {1}\n\n'.format(str(route), str(shortest_path)))

    return error_count, total_count, acumulated_context

