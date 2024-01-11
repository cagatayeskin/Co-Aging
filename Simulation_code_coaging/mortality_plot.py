#This script takes data from output of co-aging_nets.py and plots mortality rate 

import numpy as np
import matplotlib.pyplot as plt

def data_import(path):
    def Convert(string):
        li = list(string.split(", "))
        return li

    with open(path, 'r') as f:
        contents = f.readlines()
        times_A = contents[0]
        times_B = contents[1]
        simul_num = int(contents[2])
        NA = int(contents[3])
        dA = str(contents[4])
        CA = str(contents[5])
        rA = str(contents[6])
        fA = str(contents[7])
        NB = int(contents[8])
        dB = str(contents[9])
        CB = str(contents[10])
        rB = str(contents[11])
        fB = str(contents[12])
    
    times_A = Convert(times_A)
    times_B = Convert(times_B)

    times_A[0] = times_A[0].translate({ ord("["): None })
    times_A[-1] = times_A[-1].translate({ ord("]"): None })

    times_B[0] = times_B[0].translate({ ord("["): None })
    times_B[-1] = times_B[-1].translate({ ord("]"): None })

    times_A = list(map(int, times_A))
    times_B = list(map(int, times_B))
    
    # Print time evolution of mortality rate mu(t) of spiecies type A
    mu_vals_A = []
    living_nets_A = simul_num
    for time in range(max(times_A)+1):
        occur = times_A.count(time)
        mu = occur/living_nets_A
        mu_vals_A.append(mu)
        living_nets_A = living_nets_A-occur
    
    # Print time evolution of mortality rate mu(t) of spiecies type B
    mu_vals_B = []
    living_nets_B = simul_num
    for time in range(max(times_B)+1):
        occur = times_B.count(time)
        mu = occur/living_nets_B
        mu_vals_B.append(mu)
        living_nets_B = living_nets_B-occur       
    
    return mu_vals_A, mu_vals_B, simul_num, NA, dA, rA, CA, fA, NB, dB, rB, CB, fB, times_A, times_B

data = data_import('output.txt')
mu_vals_A, mu_vals_B, simul_num, NA, dA, rA, CA, fA, NB, dB, rB, CB, fB = [data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11], data[13]]

fig = plt.figure(figsize=(5,4))
time_steps_A = np.arange(0, len(mu_vals_A), 1)
plt.plot(time_steps_A, mu_vals_A, '-', alpha=1.0 , label = ('$C_A=$' + str(CA)), color= '#e41a1c', linewidth = 2.5)

plt.yscale('log')
#plt.xlim(left=10, right=170)
#y = np.array([0.0008,0.01, 0.015, 0.02, 0.03, 0.05, 0.07, 0.1, 0.15, 0.2])
#values = [0.0008,0.01, 0.015, 0.02, 0.03, 0.05, 0.07, 0.1, 0.15, 0.2]
#plt.yticks(y,values)
#plt.ylim(bottom=0.0001, top=0.2)
#plt.grid()
plt.tick_params(labelsize=18)
plt.xlabel('Time', fontsize = 18)
plt.ylabel('Mortality of $A$, $\mu_A(t)$', fontsize = 18)
#plt.legend(fontsize=8,bbox_to_anchor=(0, 1.08, 1., .102), loc='lower left',
#                      ncol=4, mode="expand", borderaxespad=0.)
plt.legend(fontsize=18, ncol=1, frameon=False, labelspacing=0.1, handlelength=1, loc = 'best')
#plt.title('Mortality curves of type $A$', fontsize=16)
#plt.savefig('plot.png', dpi=1100, bbox_inches='tight')
plt.show()