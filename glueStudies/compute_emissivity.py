import numpy as np
import scipy.integrate as integrate
import matplotlib.pyplot as plt

#####################################################################
#####################################################################
#####################################################################
### Constants

C2 = 1.438775e4
CtoK = 273.15

Lambda      = 10.5 
minLambda   = 7.5
maxLambda   = 14.

epsT        = 0.95

#####################################################################
#####################################################################
#####################################################################
### Functions

def reducedPlanck(Lambda, temp_K):
    return 1/np.expm1(C2/(Lambda*temp_K))

def reducedPlanckInt(minLambda, maxLambda, temp_K):
    return integrate.quad(lambda x: reducedPlanck(x, temp_K), minLambda, maxLambda)[0]

def getEmissivityAtLambda(epsT, Tamb, Ttrue, Tapparent, Lambda):
    return epsT * (reducedPlanck(Lambda, Tapparent+CtoK) - (reducedPlanck(Lambda, Tamb+CtoK)))/( reducedPlanck(Lambda, Ttrue+CtoK) - (reducedPlanck(Lambda, Tamb+CtoK)))

def getEmissivityLambdaRange(epsT, Tamb, Ttrue, Tapparent, minLambda, maxLambda):
    return epsT * (reducedPlanckInt(minLambda, maxLambda, Ttrue+CtoK) - (reducedPlanckInt(minLambda, maxLambda, Tamb+CtoK)))/( reducedPlanckInt(minLambda, maxLambda, Tapparent+CtoK) - (reducedPlanckInt(minLambda, maxLambda, Tamb+CtoK)))

# Magnus-Formula Wikipedia 'Taupunkt'
def DewPoint(T, h):
    # Above water:
    K2 = 17.62
    K3 = 243.12
    Zahler = (K2*T)/(K3-T)+np.log(h/100)
    Nenner = (K2*K3)/(K3+T)-np.log(h/100)
    return K3 * Zahler/Nenner

#####################################################################
#####################################################################
#####################################################################

names = ['TapeLeft', 'TapeCentre', 'TapeRight', 'PaintLeft', 'PaintCentre', 'PaintRight', 'SiTopLeft', 'SiMiddleLeft', 'SiBottomLeft', 'SiTopRight', 'SiMiddleRight', 'SiBottomRight']

colors = plt.cm.jet([0,0.15,0.30, 0.60, 0.68, 0.76, 0.84, 0.92, 1])

# Read data
time, TapeLeft100, TapeRight100, PaintLeft100, PaintRight100, PaintCentre100, TapeCentre100, SiTopLeft100, SiTopRight100, SiMiddleLeft100, SiMiddleRight100, SiBottomLeft100, SiBottomRight100, TapeLeft095, TapeRight095, PaintLeft095, PaintRight095, PaintCentre095, TapeCentre095, SiTopLeft095, SiTopRight095, SiMiddleLeft095, SiMiddleRight095, SiBottomLeft095, SiBottomRight095 = np.genfromtxt('Data.txt', unpack = True)

# Define background data
T_Amb = [20.0, 19.4, 19.5, 19.9, 20.5, 21.0, 21.3, 21.7, 21.9, 22.1, 22.4, 22.6]
H = [10.0, 9.0, 7.0, 6.0, 6.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 4.0]


# Calculate emissivities
Length = len(time)
counter = 0
for name in names:
    # Proper values
    vars()['eps_' + name] = np.zeros(Length)
    # Left, Centre, and Right temperatures vary a lot, so look at them seperately.
    if (name == 'TapeLeft' or name == 'PaintLeft'):
        for i in range(0,Length):
            vars()['eps_' + name][i] = getEmissivityLambdaRange(0.95, T_Amb[i], TapeLeft095[i], vars()[name + '095'][i], minLambda, maxLambda)
    elif (name == 'TapeCentre' or name == 'PaintCentre'):
        for i in range(0,Length):
            vars()['eps_' + name][i] = getEmissivityLambdaRange(0.95, T_Amb[i], TapeCentre095[i], vars()[name + '095'][i], minLambda, maxLambda)
    else:
        for i in range(0,Length):
            vars()['eps_' + name][i] = getEmissivityLambdaRange(0.95, T_Amb[i], TapeRight095[i], vars()[name + '095'][i], minLambda, maxLambda)
    if not (name == 'TapeLeft' or name == 'TapeCentre' or name =='TapeRight'):
        plt.plot(vars()[name + '095'], vars()['eps_' + name], label = name, color = colors[counter], marker = '.', linewidth = 0.1)
        counter += 1

# Averages
eps_Tape = np.concatenate((np.concatenate((eps_TapeLeft, eps_TapeCentre)), eps_TapeRight))
eps_Tape = np.mean(eps_Tape)
eps_Paint = np.concatenate((np.concatenate((eps_PaintLeft, eps_PaintCentre)), eps_PaintRight))
eps_Paint = np.mean(eps_Paint)
eps_Si = np.concatenate((eps_SiTopLeft, eps_SiTopRight, eps_SiMiddleLeft, eps_SiMiddleRight, eps_SiBottomLeft, eps_SiBottomRight))
eps_Si = np.mean(eps_Si)

plt.axhline(y = eps_Paint, color = 'b', linestyle = '--', label = 'avg paint on Peltier')
plt.axhline(y = eps_Si, color = 'orange', linestyle = '--', label = 'avg paint on Si')
#plt.xlim(-20,15)
plt.xlabel('camera temperature in C')
plt.ylabel('emissivity')
lgd = plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=4)
plt.tight_layout()
plt.savefig('emissivity.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
