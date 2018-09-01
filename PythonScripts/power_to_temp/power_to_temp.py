filedate = '180730'
skipH = 1
skipF = 1

import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
import random
from matplotlib import cm
#------------------------------------------------------------------------
### CONSTANTS
C1 = 1.1910429526245744e-4*np.pi # = 2hc^2 # unit = Joule . micrometer^2 / second
C2 = 1.438775e4 # = hc/k # unit = micromiter . Kelvin
CtoK = 273.15

### IR-RANGE
Lambda = 10.5
minLambda = 7.5
maxLambda = 14


#------------------------------------------------------------------------
### FUNCTIONS
#def reducedPlanck(Lambda, temp_K):
#    return C1/Lambda**5/np.expm1(C2/(Lambda*temp_K))

#def reducedPlanckInt(minLambda, maxLambda, temp_K):
#    return integrate.quad(lambda x: reducedPlanck(x, temp_K), minLambda, maxLambda)[0]

def power_to_temp(Lambda, power, eps, temp_amb_K):
    A = (1-eps)/eps / (np.expm1(C2/Lambda/temp_amb_K)-1)
    B = power*Lambda**5/eps/C1
    return C2/Lambda / (np.log(1/(B-A)+1))

#Magnus-Formula Wikipedia 'Taupunkt'
def DewPoint(T, h):
    # Above water:
    K2 = 17.62
    K3 = 243.12
    Zahler = (K2*T)/(K3-T)+np.log(h/100)
    Nenner = (K2*K3)/(K3+T)-np.log(h/100)
    return K3 * Zahler/Nenner

#########################################################################
#########################################################################
#########################################################################
### FUNCTIONS TO GET THE INTEGRATED POWER FROM THE TEMPERATURE
#########################################################################

def reducedPlanck(Lambda, temp_K):
    return C1/Lambda**5/np.expm1(C2/(Lambda*temp_K))

def reducedPlanckInt(minLambda, maxLambda, temp_K):
    return integrate.quad(lambda x: reducedPlanck(x, temp_K), minLambda, maxLambda)[0]

def temp_to_power(Lambda, temp_K, eps):
    return eps*reducedPlanck(Lambda,temp_K) + (1-eps)*reducedPlanck(Lambda, T_amb)

def temp_to_power_INT(minLambda, maxLambda, temp_K, eps, temp_amb):
    return eps*reducedPlanckInt(minLambda, maxLambda, temp_K) + (1-eps)*reducedPlanckInt(minLambda, maxLambda, temp_amb)

#def temp_to_power_INT_sum(minLambda, maxLambda, temp_K, eps, temp_amb, steps):
#    domain = np.linspace(minLambda, maxLambda, steps)
#    return sum(temp_to_power_INT(domain[i], domain[i+1], temp_K, eps, temp_amb) for i in range(0,steps-1))
    

#########################################################################
#########################################################################
#########################################################################
### 'HOMEMADE' INTEGRATOR ###############################################
#########################################################################
### INPUT
# Integrated power and temperature as measured resp. computed by the camera. Temperature in K, power in W/m^2

timestamp_pt100, T_amb, V_left, V_right, I_left, I_right, H, T_chill, pt100_PL, pt100_PR, pt100_TL, pt100_TR = np.genfromtxt('Messung' + filedate + '.txt', unpack = True)
timestamp_camera, Tcam_PL, Tcam_PR, Tcam_TL, Tcam_TR, Pcam_PL, Pcam_PR, Pcam_TL, Pcam_TR = np.genfromtxt('Messung' + filedate + '_Camera.txt', unpack = True)


TK, eps_Tape, eps_Paint = np.genfromtxt('../emissivity_calc/emissivity' + filedate + '.txt', unpack = True)

eps_Tape = np.mean(eps_Tape)
eps_Paint = np.mean(eps_Paint)


### Conversion to Kelvin
pos = ['TL', 'TR', 'PL', 'PR']
T_amb += 273.15
for p in pos:
    vars()['pt100_' + p] += 273.15
    vars()['Tcam_' + p] += 273.15


### COMPUTING
threshold = 1e-2
counter_threshold = 100
#n = 500

c = cm.jet(np.linspace(0,1,4))

T_calc = np.zeros((4,len(timestamp_pt100)))
   

#########################################################################
#########################################################################
#########################################################################
### Power -> Temp


### Iterating over the different datapoints
for j in range(0,4):
    Datapoint = pos[j]
    T = vars()['Tcam_' + pos[j]]
    T_PT100 = vars()['pt100_' + pos[j]]
    P = vars()['Pcam_' + pos[j]]
    if (pos[j] == 'PL' or pos[j] == 'PR'):
        eps = eps_Paint
    else:
        eps = eps_Tape
    print('-------------------------------------------')
    print('COMPUTATION FOR DATAPOINT ' + Datapoint + '\n')
    print('Temperatures: ', T)
    print('Powers: ', P)
    # Defining the range.
    T_min = 200 #min(T) - 5
    T_max = 100000 #max(T) + 5

    # Iterating over the temperatures within one datapoint
    for i in range(0,len(T)):
        print('Computing temperature ', i+1, ' of ', len(T), ': T = ', T[i], ', P = ', P[i])
        lower_limit = T_min
        upper_limit = T_max
        counter = 0
        temp = T[i]
        M = temp_to_power_INT(minLambda, maxLambda, temp, eps, T_amb[j])*1e12
        while (abs(M-P[i])>threshold):
            if (counter%10 == 0 ):
                print('Step ', counter, ': Computed power = ', M)
# Option to end the iteration if a certain amount of steps have been taken.
            if (counter>counter_threshold):
                break;
            elif (upper_limit == lower_limit):
                break;
            elif (M>P[i]):
                upper_limit = temp
            elif (M<P[i]):
                lower_limit = temp
            else:
                print("Error in the Computation: M=P[i]")
            temp = (upper_limit + lower_limit)/2
            M = temp_to_power_INT(minLambda, maxLambda, temp, eps, T_amb[j])*1e12
            counter += 1

        T_calc[j,i] = temp

    print('Camera temperatures: ', T)
    print('Calculated temperatures: ', T_calc[j,:])
    print('Number of iteration steps:', counter, '\n\n')




#########################################################################
#########################################################################
#########################################################################
### PLOTTING


### Plot power vs camera temperature/ calculated temperature
for k in range(0,4):
    plt.plot(vars()['Pcam_' + pos[k]], vars()['Tcam_' + pos[k]]-273.15, color = c[k], marker = "x", linewidth = 0, label = pos[k] + ' cam')
    plt.plot(vars()['Pcam_' + pos[k]], T_calc[k,:]-273.15, color = c[k], marker = ".", linewidth = 0, label = pos[k] + ' calc')
    ax2.plot()
plt.legend(loc='best')
plt.xlabel('power in W \ $m^2$')
plt.ylabel('temperature in C')
plt.title('eps_Tape = ' + str(eps_Tape) + ', eps_Paint = ' + str(eps_Paint))
plt.savefig(filedate + '/Power_Temperature_epsvar.pdf')
plt.cla()
plt.clf()

#########################################################################
#########################################################################
#########################################################################
### Plots for Graham (only using the paint/spray)

plt.figure(num=1,figsize=(4, 3), dpi=100)
### Comparison of measuremnts.
plt.subplot(211)
plt.plot(I_right, Tcam_pr-273.15, label = 'Camera')
plt.plot(I_right, pt100_pr-273.15, label = 'Contact')
plt.ylabel('Temperature in C')

### Temperature Difference.
#plt.figure(num=2,figsize=(4, 3), dpi=100)
plt.subplot(212)
plt.plot(I_right, Tcam_pr-pt100_pr)

plt.legend(loc='best')
plt.xlabel('Peltier-Current in A')
plt.ylabel('Temperaturedifference in C')
#plt.title('Temperature difference of PT100 and Camera(-Software) \n (left and right intensities separately) \n The Peltier-Element reached the Dewpoint around I=2A')
plt.tight_layout()

plt.savefig('../../Graham/Difference.pdf')
plt.show()


### Equation
plt.figure(num=3,figsize=(5, 3/4*5), dpi=100)
Power = np.zeros(len(Tcam_pr))
for i in range(0,len(Tcam_pr)):
    Power[i] = temp_to_power_INT(minLambda, maxLambda, Tcam_pr[i], eps_Paint, T_amb[i])
plt.plot(Tcam_pr-273.15, Power*1e12, label = 'Equation')
plt.plot(Tcam_pr-273.15, Tcam_pr**4*5.670373*1e-8, label = 'Boltzmann Law')
plt.plot(Tcam_pr-273.15, Pcam_pr, label = 'Software')

plt.legend(loc='best')
plt.xlabel('Temperatures given by the Camera in C')
plt.ylabel('Power in W/m^2')
#plt.title('Temperature difference of PT100 and Camera(-Software) \n (left and right intensities separately) \n The Peltier-Element reached the Dewpoint around I=2A')
plt.tight_layout()

plt.savefig('../../Graham/Equation.pdf')
plt.show()

