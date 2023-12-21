#Code requires graph-tool library to work. To download it please visit: https://git.skewed.de/count0/graph-tool/-/wikis/installation-instructions

from graph_tool.all import *
import graph_tool.all as gt
import matplotlib.pyplot as plt
import numpy as np
import random

#Build a network with a given node number (N)
rng = np.random.default_rng()
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

#Initiate two networks (G) with given node number (N) and initial percentage of unfunctional nodes (d)
def net_init(GA, GB, NA, NB, dA, dB):
    G1 = Graph(GA)
    G2 = Graph(GB)
    
    vertex_state1 = G1.new_vertex_property("int16_t")
    vertex_state2 = G2.new_vertex_property("int16_t")
    
    indexes = rng.choice(NA, size = int(round(dA*NA/100)), replace=False)
    for index in indexes:
        vertex_state1[G1.vertex(index)] = 1 

    indexes = rng.choice(NB, size = int(round(dB*NB/100)), replace=False)
    for index in indexes:
        vertex_state2[G2.vertex(index)] = 1    
    return G1, vertex_state1, G2, vertex_state2

#Vitality calculation for a given network
def vitality(G, N, vertex_state):
    phi = N
    for vertex in G.get_vertices():
        if vertex_state[vertex] == True:
            phi += -1
    return phi/N

#Co-aging function with given parameters
# G: networks, vertex_state: array giving the state of each node, N: node number
# C: co-aging constant, gamma_s_0: intrinsic aging rate, gamma__1: repair rate
def coaging(G1, vertex_state1, G2, vertex_state2, N_1, N_2, C_1, gamma_s1_0, gamma_1_1, C_2, gamma_s2_0, gamma_2_1):
    phi_1 = vitality(G1, N_1, vertex_state1)
    phi_2 = vitality(G2, N_2, vertex_state2)
    phis_1 = [phi_1]
    phis_2 = [phi_2]
    
    history_1 = []
    history_2 = []
    
    ##Intrinsic aging
    while phi_1>0.1 or phi_2>0.1:
        for vertex in G1.get_vertices():
            if vertex_state1[vertex] == 0:
                if (np.random.random() < gamma_s1_0) == True:
                    vertex_state1[vertex] = 1
                    if (np.random.random() < gamma_1_1) == True:
                        vertex_state1[vertex] = 0

        for vertex in G2.get_vertices():
            if vertex_state2[vertex] == 0:
                if (np.random.random() < gamma_s2_0) == True:
                    vertex_state2[vertex] = 1
                    if (np.random.random() < gamma_2_1) == True:
                        vertex_state2[vertex] = 0

        ###Propagate the damage
        while True:
            broken_nodes = False
            for vertex in G1.get_vertices():
                if vertex_state1[vertex] == 0:
                    liv_pred_1 = 0
                    neigh_1 = 0
                    natural_dead = 0
                    damage_dead = 0
                    
                    for pred in G1.get_in_neighbors(vertex):
                        neigh_1 += 1
                        if vertex_state1[pred] == 0:
                            liv_pred_1 += 1
                        elif vertex_state1[pred] == 1:
                            natural_dead += 1
                        elif vertex_state1[pred] == 2:
                            damage_dead += 1
                            
                    if liv_pred_1/neigh_1 < 0.5:
                        vertex_state1[vertex] = 1
                        broken_nodes = True                         
            if broken_nodes == False:
                break
        
        while True:
            broken_nodes = False
            for vertex in G2.get_vertices():
                if vertex_state2[vertex] == 0:
                    liv_pred_2 = 0
                    neigh_2 = 0
                    natural_dead = 0
                    damage_dead = 0
                    
                    for pred in G2.get_in_neighbors(vertex):
                        neigh_2 += 1
                        if vertex_state2[pred] == 0:
                            liv_pred_2 += 1
                        elif vertex_state2[pred] == 1:
                            natural_dead += 1
                        elif vertex_state2[pred] == 2:
                            damage_dead += 1
                            
                    if liv_pred_2/neigh_2 < 0.5:
                        vertex_state2[vertex] = 1
                        broken_nodes = True
            if broken_nodes == False:
                break

        ###Save the ratio of functional, unfunctional due to natural aging, and due to co-aging
        ratio_0_1 = 0
        ratio_1_1 = 0
        ratio_2_1 = 0
        for vertex in G1.get_vertices():
            if vertex_state1[vertex] == 0:
                ratio_0_1 += 1
            if vertex_state1[vertex] == 1:
                ratio_1_1 += 1
            if vertex_state1[vertex] == 2:
                ratio_2_1 += 1      
        ratio_0_1 = ratio_0_1/N_1
        ratio_1_1 = ratio_1_1/N_1
        ratio_2_1 = ratio_2_1/N_1
                
        ratio_0_2 = 0
        ratio_1_2 = 0
        ratio_2_2 = 0
        for vertex in G2.get_vertices():
            if vertex_state2[vertex] == 0:
                ratio_0_2 += 1
            if vertex_state2[vertex] == 1:
                ratio_1_2 += 1
            if vertex_state2[vertex] == 2:
                ratio_2_2 += 1       
        ratio_0_2 = ratio_0_2/N_2
        ratio_1_2 = ratio_1_2/N_2
        ratio_2_2 = ratio_2_2/N_2
        
        ###Check if both networks are dead 
        if ratio_0_1 < 0.1 and ratio_0_2 < 0.1:
            phis_1.append(0)
            phis_2.append(0)
            history_1.append([round(ratio_1_1,3), round(ratio_2_1,3)])
            history_2.append([round(ratio_1_2,3), round(ratio_2_2,3)])
            break

        ##Co-aging

        ### Calculate probability for a node to get unfunctional due to co-aging
        gamma_c1_0 = C_1*phi_2
        gamma_c2_0 = C_2*phi_1
        
        for vertex in G1.get_vertices():
            if vertex_state1[vertex] == 0:
                if (np.random.random() < gamma_c1_0) == True:
                    vertex_state1[vertex] = 2
                    if (np.random.random() < gamma_1_1) == True:
                        vertex_state1[vertex] = 0
                        
        for vertex in G2.get_vertices():
            if vertex_state2[vertex] == 0:
                if (np.random.random() < gamma_c2_0) == True:
                    vertex_state2[vertex] = 2
                    if (np.random.random() < gamma_2_1) == True:
                        vertex_state2[vertex] = 0           
        
        ###Propagate the damage        
        while True:
            broken_nodes = False
            for vertex in G1.get_vertices():
                if vertex_state1[vertex] == 0:
                    liv_pred_1 = 0
                    neigh_1 = 0
                    natural_dead = 0
                    damage_dead = 0
                    
                    for pred in G1.get_in_neighbors(vertex):
                        neigh_1 += 1
                        if vertex_state1[pred] == 0:
                            liv_pred_1 += 1
                        elif vertex_state1[pred] == 1:
                            natural_dead += 1
                        elif vertex_state1[pred] == 2:
                            damage_dead += 1
                            
                    if liv_pred_1/neigh_1 < 0.5:
                        vertex_state1[vertex] = 2
                        broken_nodes = True                         
            if broken_nodes == False:
                break
        
        ###Save the ratio of functional, nonfunctional due to natural aging, and due to co-aging      
        ratio_0_1 = 0
        ratio_1_1 = 0
        ratio_2_1 = 0
        for vertex in G1.get_vertices():
            if vertex_state1[vertex] == 0:
                ratio_0_1 += 1
            if vertex_state1[vertex] == 1:
                ratio_1_1 += 1
            if vertex_state1[vertex] == 2:
                ratio_2_1 += 1        
        ratio_0_1 = ratio_0_1/N_1
        ratio_1_1 = ratio_1_1/N_1
        ratio_2_1 = ratio_2_1/N_1
        
        ###Check if the first network is dead
        if ratio_0_1 > 0.1:
            history_1.append([round(ratio_1_1,3), round(ratio_2_1,3)])
        phi_1 = ratio_0_1
        if phi_1 > 0.1:
            phis_1.append(phi_1)
        else:
            phi_1 = 0 
            
        ###Propagate the damage for the second network
        while True:
            broken_nodes = False
            for vertex in G2.get_vertices():
                if vertex_state2[vertex] == 0:
                    liv_pred_2 = 0
                    neigh_2 = 0
                    natural_dead = 0
                    damage_dead = 0
                    
                    for pred in G2.get_in_neighbors(vertex):
                        neigh_2 += 1
                        if vertex_state2[pred] == 0:
                            liv_pred_2 += 1
                        elif vertex_state2[pred] == 1:
                            natural_dead += 1
                        elif vertex_state2[pred] == 2:
                            damage_dead += 1
                            
                    if liv_pred_2/neigh_2 < 0.5:
                        vertex_state2[vertex] = 2
                        broken_nodes = True
            if broken_nodes == False:
                break
        
        ###Save the ratio of functional, nonfunctional due to natural aging, and due to co-aging 
        ratio_0_2 = 0
        ratio_1_2 = 0
        ratio_2_2 = 0
        for vertex in G2.get_vertices():
            if vertex_state2[vertex] == 0:
                ratio_0_2 += 1
            if vertex_state2[vertex] == 1:
                ratio_1_2 += 1
            if vertex_state2[vertex] == 2:
                ratio_2_2 += 1     
        ratio_0_2 = ratio_0_2/N_2
        ratio_1_2 = ratio_1_2/N_2
        ratio_2_2 = ratio_2_2/N_2
        
        ###Check if the second network dead
        if ratio_0_2 > 0.1:
            history_2.append([round(ratio_1_2,3), round(ratio_2_2,3)])  
        phi_2 = ratio_0_2
        if phi_2 > 0.1:
            phis_2.append(phi_2)
        else:
            phi_2 = 0
    
        ###Check if both networks are dead
        if phi_1 < 0.1 and phi_2 < 0.1:
            phis_1.append(0)
            phis_2.append(0)
            history_1.append([round(ratio_1_1,3), round(ratio_2_1,3)])
            history_2.append([round(ratio_1_2,3), round(ratio_2_2,3)])

    return phis_1, phis_2, history_1[-1], history_2[-1]

#Co-age networks and plot vitality
N1 = 800 #node number
phi_1 = []
living_times_1 = []

N2 = 500 #node number
phi_2 = []
living_times_2 = []

##Probabilities for the aging networks
gamma_s1_0 = 0.002 #intrinsic aging damage rate
gamma_1_1 = 0.015 #repair rate
C_1 = 0.001 #co-aging constant
d_1 = 0.0 #initial damage percentage

gamma_s2_0 = 0.003 #intrinsic aging damage rate
gamma_2_1 = 0.0 #repair rate
C_2 = 0.0015 #co-aging constant
d_2 = 0.0 #initial damage percentage

##Build networks
G_A = build_net(N1)
G_B = build_net(N2) 

##Set number of network couple (S)
net_couple_num = 1

for net in range(net_couple_num): # this loop builds then ages all the networks
    G1, init_state1, G2, init_state2 = net_init(G_A, G_B, N1, N2, d_1, d_2) #initiate networks
    data = coaging(G1, init_state1, G2, init_state2, N1, N2, C_1, gamma_s1_0, gamma_1_1 , C_2, gamma_s2_0, gamma_2_1)
    phi_1.append(data[0]) #vitality rate development
    phi_2.append(data[1]) 
    history_1 = data[2] #percentage of nonfunctional nodes at the time of death
    history_2 = data[3]
    living_times_1.append(len(data[0])) #time of death to be used in mortality calculation
    living_times_2.append(len(data[1])) 
      
##Plot the change of vitality wrt. time
fig = plt.figure(figsize=(4,4))
for i in range(net_couple_num):
    time_steps_1 = np.arange(0, len(phi_1[i]), 1)
    time_steps_2 = np.arange(0, len(phi_2[i]), 1)
    plt.plot(time_steps_1, phi_1[i], alpha=1, color='#e41a1c', label = 'Network A')
    plt.plot(time_steps_2, phi_2[i], '-', alpha=1, color='#377eb8', label = 'Network B') 
plt.tick_params(labelsize=15)
plt.xlabel('t', fontsize = 15)
plt.ylabel('$\phi$', fontsize = 15)
plt.legend(fontsize=13, loc='best')
plt.show()

#Calculate mortality rate for networks A
mu_vals_1 = []
living_nets_1 = net_couple_num
for time in range(max(living_times_1)+1):
    occur = living_times_1.count(time)
    mu = occur/living_nets_1
    mu_vals_1.append(mu)
    living_nets_1 = living_nets_1-occur

#Calculate mortality rate for networks B
mu_vals_2 = []
living_nets_2 = net_couple_num
for time in range(max(living_times_2)+1):
    occur = living_times_2.count(time)
    mu = occur/living_nets_2
    mu_vals_2.append(mu)
    living_nets_2 = living_nets_2-occur

print(mu_vals_1, mu_vals_2)