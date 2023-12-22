#All simulation results given in .txt form lists the lifespan of each simulated networks
#This code reads the data and calculates mortality rates then plots them with respect to time

#Simulation data import function
import numpy as np
import matplotlib.pyplot as plt

def data_import(path):
    def Convert(string):
        li = list(string.split(", "))
        return li

    with open(path, 'r') as f:
        contents = f.readlines()
        living_times_1 = contents[0]
        living_times_2 = contents[1]
        net_couple_num = int(contents[2])
        N1 = int(contents[3])
        gamma_s1_0 = str(contents[4])
        gamma_1_1 = str(contents[5])
        C_1 = str(contents[6])
        d_1 = str(contents[7])
        N2 = int(contents[8])
        gamma_s2_0 = str(contents[9])
        gamma_2_1 = str(contents[10])
        C_2 = str(contents[11])
        d_2 = str(contents[12])
        state_1 = str(contents[13])
    
    living_times_1 = Convert(living_times_1)
    living_times_2 = Convert(living_times_2)
    state_1 = Convert(state_1)

    living_times_1[0] = living_times_1[0].translate({ ord("["): None })
    living_times_1[-1] = living_times_1[-1].translate({ ord("]"): None })

    living_times_2[0] = living_times_2[0].translate({ ord("["): None })
    living_times_2[-1] = living_times_2[-1].translate({ ord("]"): None })
    
    state_1[0] = state_1[0].translate({ ord("["): None })
    state_1[-1] = state_1[-1].translate({ ord("]"): None })

    living_times_1 = list(map(int, living_times_1))
    living_times_2 = list(map(int, living_times_2))
    state_1 = list(map(int, state_1))
        
    mu_vals_1 = []
    living_nets_1 = net_couple_num
    for time in range(max(living_times_1)+1):
        occur = living_times_1.count(time)
        mu = occur/living_nets_1
        mu_vals_1.append(mu)
        living_nets_1 = living_nets_1-occur
    
    mu_vals_2 = []
    living_nets_2 = net_couple_num
    for time in range(max(living_times_2)+1):
        occur = living_times_2.count(time)
        mu = occur/living_nets_2
        mu_vals_2.append(mu)
        living_nets_2 = living_nets_2-occur
    return mu_vals_1, mu_vals_2, net_couple_num, N1, gamma_s1_0, gamma_1_1, C_1, d_1, N2, gamma_s2_0, gamma_2_1, C_2, d_2, living_times_1, living_times_2, state_1

#Import data from below directory
data_1 = data_import('figure_2/figure_2_mortality_a.txt')
mu_vals_1_1 = data_1[0]
living_times_1 = data_1[14]

data_2 = data_import('figure_2/figure_2_mortality_b.txt')
mu_vals_1_2 = data_2[0]
living_times_2 = data_2[14]

#Cut the end of the mortality rate functions to get rid of noise
mean_1 = np.mean(mu_vals_1_1)
sd_1 = np.std(mu_vals_1_1)
cut_mu_1 = []
for i in range(len(mu_vals_1_1)):
    cut_mu_1.append(mu_vals_1_1[i])
    if mu_vals_1_1[i] > (mean_1 + sd_1*0.75):
        break
mu_vals_1_1 = cut_mu_1
mean_2 = np.mean(mu_vals_1_2)
sd_2 = np.std(mu_vals_1_2)
cut_mu_2 = []
for i in range(len(mu_vals_1_2)):
    cut_mu_2.append(mu_vals_1_2[i])
    if mu_vals_1_2[i] > (mean_2 + sd_2*0.75):
        break
mu_vals_1_2 = cut_mu_2

#Plot mortality with respect to time
fig = plt.figure(figsize=(6,7))
time_steps_1_1 = np.arange(0, len(mu_vals_1_1), 1)
plt.plot(time_steps_1_1, mu_vals_1_1, '-', alpha=1.0 , label = ('Co-aging networks'), color= '#377eb8', linewidth=2.5)
time_steps_1_2 = np.arange(0, len(mu_vals_1_2), 1)
plt.plot(time_steps_1_2, mu_vals_1_2, '-', alpha=1.0 , label = ('Typically-aging networks'), color= '#984ea3', linewidth=2.5)
plt.axvline(x=np.mean(living_times_1), ymin=0.0, ymax=1.0, linestyle='--', linewidth=1.2, alpha = 1, color='#e41a1c')

plt.yscale('log')
plt.xlim(left=0.0, right=250)
plt.ylim(bottom=0.00015, top=0.35)
plt.tick_params(labelsize=14)
plt.xlabel('Time', fontsize = 14)
plt.ylabel('Mortality of A, $\mu_A(t)$', fontsize = 14)
plt.legend(fontsize=14, loc='upper right', ncol = 1, frameon=False, labelspacing=0.2, handlelength=1)
plt.savefig('fig1_mortality.png', dpi=1100, bbox_inches='tight')
plt.show()