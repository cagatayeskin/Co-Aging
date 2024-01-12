#Code requires graph-tool library to work. To download it please visit: https://git.skewed.de/count0/graph-tool/-/wikis/installation-instructions
#This version of the code requires networks created using 'network_build.py'
#Running the code will export results in the form of lifetime for each network to a .txt file
#Using 'mortality_plot.py', mortality curves can be plotted

from graph_tool.all import *
import graph_tool.all as gt
import matplotlib.pyplot as plt
import numpy as np
import random
import time
from multiprocessing import Pool, current_process
import multiprocessing
import os

# #Build networks. Uncomment if you are not using prebuilt networks
# def build_net(N):
#     G = Graph(directed=True)
#     for i in range(0, N):
#         if i == 0:
#             G.add_vertex()          
#         else:
#             G.add_vertex()
#             poss_adjs = tuple(np.arange(0, i, 1))
#             chosen_node_b = str(random.choice(poss_adjs))
#             G.add_edge(G.vertex(chosen_node_b), G.vertex(i))
#             chosen_node_c = str(random.choice(poss_adjs))
#             G.add_edge(G.vertex(i), G.vertex(chosen_node_c))
#     return G

#Initiate networks with a prenatal damage fA, fB
rng = np.random.default_rng()
def net_init(GA, NA, fA, GB, NB, fB):
    GA = Graph(GA)
    GB = Graph(GB)
    vertex_stateA = GA.new_vertex_property("int16_t")
    vertex_stateB = GB.new_vertex_property("int16_t")
    
    for index in rng.choice(NA, size = int(round(fA*NA/100)), replace=False):
        vertex_stateA[index] = 1
    #vertex_stateA.a[rng.choice(NA, size=int(round(fA * NA / 100)), replace=False)] = 1: alternative of above where .a 
    
    for index in rng.choice(NB, size = int(round(fB*NB/100)), replace=False):
        vertex_stateB[index] = 1

    return GA, vertex_stateA, GB, vertex_stateB

#Calculate vitality
def vitality(G, N, vertex_state):
    phi = sum(1 for vertex in G.iter_vertices() if vertex_state[vertex] == 0)
    return phi / N

#This is for generating unique seed for every parallel process
def generate_unique_seed():
    process_id = os.getpid()
    timestamp = int(time.time() * 1000000)  # Microseconds for higher precision
    return hash((process_id, timestamp)) % (2**32 - 1)

#Co-aging function with given parameters
def coaging(GA, NA, vertex_stateA, dA, CA, rA, GB, NB, vertex_stateB, dB, CB, rB):
    seed = generate_unique_seed()
    np.random.seed(seed)

    phiA = vitality(GA, NA, vertex_stateA)
    phiB = vitality(GB, NB, vertex_stateB)
    phisA = [phiA]
    phisB = [phiB]

    death_cause_A = 0
    death_cause_B = 0
    
    ## Node labels: functional=0, unfunctional due to intrinsic aging=1, due to co-aging:=2
    #INTRINSIC AGING#
    while phiA>0.1 or phiB>0.1:
        for vertex in GA.get_vertices():
            if vertex_stateA[vertex] == 0 and (np.random.random() < dA):
                    vertex_stateA[vertex] = 1
                    if (np.random.random() < rA):
                        vertex_stateA[vertex] = 0

        for vertex in GB.get_vertices():
            if vertex_stateB[vertex] == 0 and (np.random.random() < dB):
                    vertex_stateB[vertex] = 1
                    if (np.random.random() < rB):
                        vertex_stateB[vertex] = 0

        #Propagate the damage for network A
        while True:
            broken_nodes = False
            for vertex in GA.get_vertices():
                if vertex_stateA[vertex] == 0:
                    live_neigh = 0
                    neigh = 0
                    for neighbor in GA.get_in_neighbors(vertex):
                        neigh += 1
                        if vertex_stateA[neighbor] == 0:
                            live_neigh += 1               
                    if live_neigh/neigh < 0.5:
                        vertex_stateA[vertex] = 1
                        broken_nodes = True                         
            if broken_nodes == False:
                break
        
        #Propagate the damage for network B
        while True:
            broken_nodes = False
            for vertex in GB.get_vertices():
                if vertex_stateB[vertex] == 0:
                    live_neigh = 0
                    neigh = 0
                    for neighbor in GB.get_in_neighbors(vertex):
                        neigh += 1
                        if vertex_stateB[neighbor] == 0:
                            live_neigh += 1
                    if live_neigh/neigh < 0.5:
                        vertex_stateB[vertex] = 1
                        broken_nodes = True
            if broken_nodes == False:
                break

        #Save the ratio of functional, nonfunctional due to natural aging, and due to co-aging 
        ratio_func_A = sum(1 for vertex in GA.iter_vertices() if vertex_stateA[vertex] == 0)/NA
        ratio_aging_A = sum(1 for vertex in GA.iter_vertices() if vertex_stateA[vertex] == 1)/NA
        ratio_coaging_A = sum(1 for vertex in GA.iter_vertices() if vertex_stateA[vertex] == 2)/NA

        ratio_func_B = sum(1 for vertex in GB.iter_vertices() if vertex_stateB[vertex] == 0)/NB
        ratio_aging_B = sum(1 for vertex in GB.iter_vertices() if vertex_stateB[vertex] == 1)/NB
        ratio_coaging_B = sum(1 for vertex in GB.iter_vertices() if vertex_stateB[vertex] == 2)/NB
        
        #Check if both networks are dead and save the cause of death
        if ratio_func_A < 0.1 and ratio_func_B < 0.1:
            phisA.append(0)
            phisB.append(0)
            #network is marked 0 if the reason of death is intrinsic aging and 1 if it is co-aging
            death_cause_A = 0 if ratio_aging_A>ratio_coaging_A else 1
            death_cause_B = 0 if ratio_aging_B>ratio_coaging_B else 1
            break

        #CO-AGING#
        #Calculate probability for a node to get unfunctional due to co-aging
        alphaA = CA*phiB
        alphaB = CB*phiA
        
        for vertex in GA.get_vertices():
            if vertex_stateA[vertex] == 0 and (np.random.random() < alphaA):
                    vertex_stateA[vertex] = 2
                    if (np.random.random() < rA) == True:
                        vertex_stateA[vertex] = 0
                        
        for vertex in GB.get_vertices():
            if vertex_stateB[vertex] == 0 and (np.random.random() < alphaB):
                    vertex_stateB[vertex] = 2
                    if (np.random.random() < rB) == True:
                        vertex_stateB[vertex] = 0           
        
        #Propagate the damage for network A       
        while True:
            broken_nodes = False
            for vertex in GA.get_vertices():
                if vertex_stateA[vertex] == 0:
                    live_neigh = 0
                    neigh = 0
                    for neighbor in GA.get_in_neighbors(vertex):
                        neigh += 1
                        if vertex_stateA[neighbor] == 0:
                            live_neigh += 1
                    if live_neigh/neigh < 0.5:
                        vertex_stateA[vertex] = 2
                        broken_nodes = True                         
            if broken_nodes == False:
                break
        
        #Save the ratio of functional, nonfunctional due to natural aging, and due to co-aging      
        ratio_func_A = sum(1 for vertex in GA.iter_vertices() if vertex_stateA[vertex] == 0)/NA
        ratio_aging_A = sum(1 for vertex in GA.iter_vertices() if vertex_stateA[vertex] == 1)/NA
        ratio_coaging_A = sum(1 for vertex in GA.iter_vertices() if vertex_stateA[vertex] == 2)/NA

        #Update vitality
        phiA = ratio_func_A
        if phiA > 0.1:
            phisA.append(phiA)
        else:
            phiA = 0 
            
        #Propagate the damage for the network B
        while True:
            broken_nodes = False
            for vertex in GB.get_vertices():
                if vertex_stateB[vertex] == 0:
                    live_neigh = 0
                    neigh = 0
                    for neighbor in GB.get_in_neighbors(vertex):
                        neigh += 1
                        if vertex_stateB[neighbor] == 0:
                            live_neigh += 1
                    if live_neigh/neigh < 0.5:
                        vertex_stateB[vertex] = 2
                        broken_nodes = True
            if broken_nodes == False:
                break
        
        #Save the ratio of functional, nonfunctional due to natural aging, and due to co-aging 
        ratio_func_B = sum(1 for vertex in GB.iter_vertices() if vertex_stateB[vertex] == 0)/NB
        ratio_aging_B = sum(1 for vertex in GB.iter_vertices() if vertex_stateB[vertex] == 1)/NB
        ratio_coaging_B = sum(1 for vertex in GB.iter_vertices() if vertex_stateB[vertex] == 2)/NB
         
        #Update vitality
        phiB = ratio_func_B
        if phiB > 0.1:
            phisB.append(phiB)
        else:
            phiB = 0
    
        #Check if both networks are dead
        if phiA < 0.1 and phiB < 0.1:
            phisA.append(0)
            phisB.append(0)
            #network is marked 0 if the reason of death is intrinsic aging and 1 if it is co-aging
            death_cause_A = 0 if ratio_aging_A>ratio_coaging_A else 1
            death_cause_B = 0 if ratio_aging_B>ratio_coaging_B else 1

        # #Uncomment if you are working on chess fits. This cuts the game early when one of them wins
        # if phiA < 0.1 and phiB > 0.1:
        #     break
        # if phiA > 0.1 and phiB < 0.1:
        #     break

    return len(phisA), len(phisB), death_cause_A, death_cause_B #length of each vitality array gives network's lifetime

#Simulation parameters
simul_num = 100
NA, dA, CA, rA, fA = [800, 0.005, 0.01, 0.015, 2.0]
NB, dB, CB, rB, fB = [500, 0.006, 0.015, 0.0, 0.0]

#Main that simulates two networks co-aging each other. This function will be parallelized
def simulate_one_net(_):
    GA = load_graph("network_a.gt.gz")
    GB = load_graph("network_b.gt.gz")
    GA, init_stateA, GB, init_stateB = net_init(GA, NA, fA, GB, NB, fB)
    output = coaging(GA, NA, init_stateA, dA, CA, rA, GB, NB, init_stateB, dB, CB, rB)
    return output

#Parallelization
if __name__ == '__main__':
    start = time.time()
    with Pool(processes=multiprocessing.cpu_count()) as pool:
        results = pool.map_async(simulate_one_net, range(simul_num))
        results = results.get()

    # Extract times_A and times_B from results
    times_A = [result[0] for result in results]
    times_B = [result[1] for result in results]
    death_cause_A = [result[2] for result in results]
    death_cause_B = [result[3] for result in results]

    # Write the output to a file
    output_data = [
        ("times_A", times_A),
        ("times_B", times_B),
        ("simul_num", simul_num),
        ("NA", NA),
        ("dA", dA),
        ("CA", CA), 
        ("rA", rA),
        ("fA", fA),
        ("NB", NB),
        ("dB", dB),
        ("CB", CB), 
        ("rB", rB),
        ("fB", fB),
        ("death_cause_A", death_cause_A),
        ("death_cause_B", death_cause_B),
    ]
    with open("output.txt", "w") as output:
        for label, value in output_data:
            #output.write(f"{label}: {value}\n") #uncomment if you want the output with names
            output.write(f"{value}\n")

        end = time.time()
        print(end - start)
