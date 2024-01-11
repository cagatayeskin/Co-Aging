#This script builds two networks, network_a, network_b with given number of nodes
from graph_tool.all import *
import graph_tool.all as gt
import numpy as np
import random

def build_net(N):
    G = Graph(directed=True)  
    for i in range(0, N):
        if i == 0:
            G.add_vertex()     
        else:
            G.add_vertex()
            poss_adjs = tuple(np.arange(0, i, 1))
            chosen_node_b = str(random.choice(poss_adjs))
            G.add_edge(G.vertex(chosen_node_b), G.vertex(i))
            chosen_node_c = str(random.choice(poss_adjs))
            G.add_edge(G.vertex(i), G.vertex(chosen_node_c))
    return G

NA = 800
NB = 500

G_A = build_net(NA)
G_A.save("network_a.gt.gz")
G_B = build_net(NB) 
G_B.save("network_b.gt.gz")
