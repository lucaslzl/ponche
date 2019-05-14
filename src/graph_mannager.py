import networkx as nx
from bs4 import BeautifulSoup



def build_road_graph(network):
    # Input   
    f = open(network)
    data = f.read()
    soup = BeautifulSoup(data, "xml")
    f.close()

    
    edges_length = {}
    
    for edge_tag in soup.findAll("edge"):
        lane_tag = edge_tag.find("lane")
        
        edge_id = edge_tag["id"]
        edge_length = int(float(lane_tag["length"]))
        
        edges_length[edge_id] = edge_length
    
    graph = nx.DiGraph()            
    
    # Connections
    for connection_tag in soup.findAll("connection"):
        source_edge = connection_tag["from"]        
        dest_edge = connection_tag["to"]
        
        if source_edge != dest_edge:
            if source_edge.startswith(":") or dest_edge.startswith(":"): continue
            graph.add_edge(source_edge.encode("ascii"), dest_edge.encode("ascii"), id=source_edge, length=edges_length[source_edge], weight=0)

    # # Junctions
    # for junction_tag in soup.findAll("junction"):
    #     junc_id = junction_tag["id"]
    #     lanes = junction_tag['incLanes']

    #     for lane in lanes.split():
    #         lane = lane.split('_')[0]
    #         if junc_id.startswith(":") or lane.startswith(":"): continue
    #         graph.add_edge(junc_id.encode("ascii"), lane.encode("ascii"), weight=0)
            
    return graph
