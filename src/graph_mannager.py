import networkx as nx
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


def plot_graph(graph):

    pos = nx.spring_layout(graph)

    nx.draw_networkx_nodes(graph, pos, cmap=plt.get_cmap('jet'), node_size=500)
    nx.draw_networkx_labels(graph, pos)
    nx.draw_networkx_edges(graph, pos, edgelist=graph.edges, arrows=True)
    plt.show()
    

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

    #plot_graph(graph)
    #input(';')

    return graph
