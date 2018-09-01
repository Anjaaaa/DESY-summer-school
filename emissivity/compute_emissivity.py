import numpy as np
import scipy.integrate as integrate
import matplotlib.pyplot as plt

C2 = 1.438775e4                             # hc/k [microm.K]
CtoK = 273.15

Lambda      = 10.5 
minLambda   = 7.5                           # lower bound of wavelength range
maxLambda   = 14                            # upper bound of wavelength range

epsT        = 0.95                          # emissivity tape
filedates = ['180730', '180808', '180809']  # to loop over the different measurements
positions = ['TL', 'TR', 'PL', 'PR']        # to loop over positions

colors = plt.cm.jet(np.linspace(0,1,4))     # nice colours for plots

#########################################################################
#########################################################################
### FUNCTIONS
#########################################################################

def reducedPlanck(Lambda, temp_K):
    # Planck radiation law
    # Lambda: wavelength (micron)
    # temp_K: object temperature (kelvin)
    return 1/np.expm1(C2/(Lambda*temp_K))

def reducedPlanckInt(minLambda, maxLambda, temp_K):
    # integrated Planck radiation law
    # min/maxLambda: wavelength boundaries (micron)
    # temp_K: object temperature (kelvin)
    return integrate.quad(lambda x: reducedPlanck(x, temp_K), minLambda, maxLambda)[0]

def getEmissivityAtLambda(epsT, Tamb, Ttrue, Tapparent, Lambda):
    # epsT: known emissivity
    # Tamb: ambiant temperature (celsius)
    # Ttrue: observed temperature (celsius) on the surface with emissivity epsT (software set to epsT)
    # Tapparent: observed temperature (celsius) on the other surface (software set to epsT)
    # Lambda: wavelength (micron)
    return epsT * (reducedPlanck(Lambda, Tapparent+CtoK) - (reducedPlanck(Lambda, Tamb+CtoK)))/( reducedPlanck(Lambda, Ttrue+CtoK) - (reducedPlanck(Lambda, Tamb+CtoK)))

def getEmissivityLambdaRange(epsT, Tamb, Ttrue, Tapparent, minLambda, maxLambda):
    # epsT: known emissivity
    # Tamb: ambiant temperature (celsius)
    # Ttrue: observed temperature (celsius) on the surface with emissivity epsT (software set to epsT)
    # Tapparent: observed temperature (celsius) on the other surface (software set to epsT)
    # min/maxLambda: wavelength boundaries (micron)
    return epsT * (reducedPlanckInt(minLambda, maxLambda, Ttrue+CtoK) - (reducedPlanckInt(minLambda, maxLambda, Tamb+CtoK)))/( reducedPlanckInt(minLambda, maxLambda, Tapparent+CtoK) - (reducedPlanckInt(minLambda, maxLambda, Tamb+CtoK)))
 
def DewPoint(T, h):
    # Magnus-Formula Wikipedia 'Taupunkt'
    # T: ambiant temperature (celsius)
    # h: relative humidity, so 8% should be h=8 (not h=0.08)
    # Above water:
    K2 = 17.62
    K3 = 243.12
    Zahler = (K2*T)/(K3-T)+np.log(h/100)
    Nenner = (K2*K3)/(K3+T)-np.log(h/100)
    return K3 * Zahler/Nenner


#########################################################################
#########################################################################
### Computation of the emissivities
#########################################################################

# Formation of ice:
# 180730: 1642 (= first 5)
# 180808: 1655 (= first 4)
# 180809: Not at all.

noice = [5,4,10]            # to automatically draw the 'ice formation' line

countF = 0                  # counts the filedate loops
for filedate in filedates:
    ### read data
    # non-camera data (for T_amb, humidity, pt100s)
    timestamp_pt100, T_amb, V_left, V_right, I_left, I_right, H, T_chill, pt100_PL, pt100_PR, pt100_TL, pt100_TR = np.genfromtxt('../peltierStudies/data/' + filedate + '.txt', unpack = True)
    # camera data
    timestamp_camera, Tcam_PL, Tcam_PR, Tcam_TL, Tcam_TR, Pcam_PL, Pcam_PR, Pcam_TL, Pcam_TR = np.genfromtxt('../peltierStudies/data/' + filedate + '_eps100_camera.txt', unpack = True)
    # Values with eps=0.95 in software
    time, T_eps_TR, T_eps_TL, T_eps_PL, T_eps_PR = np.genfromtxt('../peltierStudies/data/' + filedate + '_eps095_temp.txt', unpack = True)


    T_Amb = np.mean(T_amb)
    Length = len(timestamp_pt100)

    # pt100average (separately for 180809, because the paint left (PL) pt100 was brocken
    if (filedate == '180809'):
        PT100_Avg = (pt100_PR+pt100_TL+pt100_TR)/3
    else:
        PT100_Avg = (pt100_PL+pt100_PR+pt100_TL+pt100_TR)/4


    ### Loop through the positions to compute the emissivities and plot them.
    countPos = 0            # counts the position loops
    for pos in positions:
        vars()['eps_' + pos] = np.zeros(Length)         # new array for each position to save the emissivity at each temperature
        ### compute emissivity
        # differentiate between left and right (because Peltier did not heat symmetrically, angle of the camera, ...)
        if (pos == 'TR' or pos == 'PR'):
            for i in range(0,Length):
                vars()['eps_' + pos][i] = getEmissivityLambdaRange(epsT, T_Amb, T_eps_TR[i], vars()['T_eps_' + pos][i], minLambda, maxLambda)
        else:
            for i in range(0,Length):
                vars()['eps_' + pos][i] = getEmissivityLambdaRange(epsT, T_Amb, T_eps_TL[i], vars()['T_eps_' + pos][i], minLambda, maxLambda)
        ### plot emissivity
        if not (pos == 'PL' and filedate =='180809'): # On that day this PT100 was broken.
            plt.plot(vars()['pt100_' + pos][0:], vars()['eps_' + pos][0:], color=colors[countPos], linewidth = 0.3, marker = 'x', label = pos)
        countPos += 1
    # plot manufacturer value of the tape
    plt.axhline(y = 0.95, color = 'k', label = 'manufacturer: eps = 0.95', zorder=0)
    # plot theoretical dew point
    plt.axvline(x = DewPoint(np.mean(T_amb), np.mean(H)), color = 'k', ls = 'dashed', linewidth = 1, label = 'Dew Point', zorder=0)
    # plot visible ice formation
    if not (filedate == '180809'): # On that day this PT100 was broken.
        plt.axvline(x = (PT100_Avg[noice[countF]]+PT100_Avg[noice[countF]-1])/2, color = 'k', ls = 'dotted', label = 'Ice Formation', zorder=0)
    ### plotting foo
    plt.legend(loc='best')
    plt.xlabel('temperature in C (PT100)')
    plt.ylabel('emissivity')
    plt.title('minimal humidity: ' + str(min(H)))
    plt.savefig('Plots/emissivity_' + filedate + '.pdf')
    plt.cla()
    plt.clf()
    #------------------------------------------------------------------
    ### Calculate averages for each temperature
    eps_Tape = (eps_TL + eps_TR)/2
    if (filedate == '180809'):
        eps_Paint = eps_PR
    else:
        eps_Paint = (eps_PL + eps_PR)/2
    ### Save the averages in file (one file per date)
    textfile  = open('emissivity' + filedate + '.txt', "w") 
    textfile.write("#Temperature emissivity_Tape emissivity_Paint \n")
    for i in range(0,len(eps_Tape)):
        textfile.write(str(PT100_Avg[i]) + ' ' + str(eps_Tape[i]) + ' ' + str(eps_Paint[i]) + '\n')

    textfile.close()
    countF += 1


######################################################################
######################################################################
### AVERAGES
######################################################################
colors = plt.cm.jet(np.linspace(0.7,1, 3))

counter = 0 # counts loops through filedates
for filedate in filedates:
    # non-camera data
    # read emissivities
    vars()['T_' + filedate], vars()['eps_T_' + filedate], vars()['eps_P_' + filedate] = np.genfromtxt('emissivity' + filedate + '.txt', unpack = True)

    ### plotting (only paint because eps_tape is 0.95 by construction of the calculation anyway)
    plt.plot(vars()['T_' + filedate][1:noice[counter]], vars()['eps_P_' + filedate][1:noice[counter]], color=colors[counter], marker = '.', linewidth = 0.4, label = 'min. humidity: ' + str(min(H)))
    counter += 1

# Only take the emissivities without ice on the Peltier (on the IR image) and with enough (10 degrees?) distance to ambiant.
for k in range(0,3):
    vars()['eps_P_' + filedates[k] + '_noIce'] = vars()['eps_P_' + filedates[k]][1:noice[k]]
    vars()['eps_T_' + filedates[k] + '_noIce'] = vars()['eps_T_' + filedates[k]][1:noice[k]]

# compute absolute average
PAINT = np.concatenate((np.concatenate((eps_P_180730_noIce, eps_P_180808_noIce)), eps_P_180809))
TAPE = np.concatenate((np.concatenate((eps_T_180730_noIce, eps_T_180808_noIce)), eps_T_180809))
av_Paint = np.mean(PAINT)
av_Tape = np.mean(TAPE)
std_Paint = np.std(PAINT)
std_Tape = np.std(PAINT)

# plot absolute average
plt.axhline(y=av_Paint, color='k', linestyle = '--', label = 'Average', zorder=0)

# plotting blabla
plt.xlim(T_180809[-1]-1,max(T_180809[1], T_180808[1], T_180730[1])+1)
plt.legend(loc='right', bbox_to_anchor=(1, 0.625))
plt.xlabel('temperature in C (PT100)')
plt.ylabel('emissivity')
plt.title('emissivity of the paint')
plt.savefig('Plots/emissivity.pdf')
plt.cla()
plt.clf()

