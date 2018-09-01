filedate = '180809'

import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate

#------------------------------------------------------------------------
### CONSTANTS
C1 = 1.1910429526245744e-4*np.pi # = 2hc^2 # unit = Joule . micrometer^2 / second
C2 = 1.438775e4 # = hc/k # unit = micromiter . Kelvin
CtoK = 273.15

### IR-RANGE in mm, therefore check unit of power
Lambda = 10.5
minLambda = 7.5
maxLambda = 14
eps = 1

#------------------------------------------------------------------------
### INPUT

timestamp_pt100, T_amb, V_left, V_right, I_left, I_right, H, T_chill, pt100_pl, pt100_pr, pt100_tl, pt100_tr = np.genfromtxt('Messung180730.txt', unpack = True)
timestamp_camera, Tcam_pl, Tcam_pr, Tcam_tl, Tcam_tr, Pcam_pl, Pcam_pr, Pcam_tl, Pcam_tr = np.genfromtxt('Messung180730_Camera.txt', unpack = True)

eps_Tape, eps_Paint = np.genfromtxt('../emissivity_calc/emissivity.txt', unpack = True)

timestamp, realT_tl, realT_tr, realT_pl, realT_pr, realP_tl, realP_tr, realP_pl, realP_pr = np.genfromtxt('Messung180809RealRange.txt', unpack = True)


### Conversion to Kelvin

T_amb += 273.15
pt100_pl += 273.15
pt100_pr += 273.15
pt100_tl += 273.15
pt100_tr += 273.15
Tcam_pl += 273.15
Tcam_pr += 273.15
Tcam_tl += 273.15
Tcam_tr += 273.15
realT_tl+= 273.15
realT_tr+= 273.15
realT_pl+= 273.15
realT_pr+= 273.15



#------------------------------------------------------------------------
### FUNCTIONS
def reducedPlanck(Lambda, temp_K):
    return C1/Lambda**5/np.expm1(C2/(Lambda*temp_K))

def reducedPlanckInt(minLambda, maxLambda, temp_K):
    return integrate.quad(lambda x: reducedPlanck(x, temp_K), minLambda, maxLambda)[0]

def temp_to_power(Lambda, temp_K, T_amb, eps):
    return eps*reducedPlanck(Lambda,temp_K) + (1-eps)*reducedPlanck(Lambda, T_amb)

def temp_to_power_INT(minLambda, maxLambda, temp_K, T_amb, eps):
    return eps*reducedPlanckInt(minLambda, maxLambda, temp_K) + (1-eps)*reducedPlanckInt(minLambda, maxLambda, T_amb)

#------------------------------------------------------------------------
#### TEST TO SEE IF THE WAVELENGTH IS IMPORTANT
#plt.plot(T, temp_to_power(minLambda, T, 1), color = "red", label= "$\lambda=8$")
#plt.plot(T, temp_to_power(Lambda, T, 1), color = "green", label= "$\lambda=10.5$")
#plt.plot(T, temp_to_power(maxLambda, T, 1), color = "blue", label= "$\lambda=13$")


#plt.plot(273, temp_to_power(minLambda, 273, 1), color = "red", marker = "x", label = temp_to_power(minLambda, 273, 1))
#plt.plot(273, temp_to_power(Lambda, 273, 1), color = "green", marker = "x", label = temp_to_power(Lambda, 273, 1))
#plt.plot(273, temp_to_power(maxLambda, 273, 1), color = "blue", marker = "x", label = temp_to_power(maxLambda, 273, 1))


#plt.legend(loc='best')
#plt.ylabel("Power in $W \ / \ \mu m^3$")
#plt.xlabel("$T$ in $K$")
#plt.title("Is the wavelength relevant?")
#plt.show()


#------------------------------------------------------------------------
P_INT_pl = np.zeros(len(Tcam_pl))
P_INT_pr = np.zeros(len(Tcam_pr))
P_INT_tl = np.zeros(len(Tcam_tl))
P_INT_tr = np.zeros(len(Tcam_tr))

for i in range(0,len(Tcam_pl)):
    P_INT_pl[i] = temp_to_power_INT(minLambda, maxLambda, Tcam_pl[i], T_amb[i], eps) * 1e12
    P_INT_pr[i] = temp_to_power_INT(minLambda, maxLambda, Tcam_pr[i], T_amb[i], eps) * 1e12
    P_INT_tl[i] = temp_to_power_INT(minLambda, maxLambda, Tcam_tl[i], T_amb[i], eps) * 1e12
    P_INT_tr[i] = temp_to_power_INT(minLambda, maxLambda, Tcam_tr[i], T_amb[i], eps) * 1e12

# Also plot Boltzmann-Law (there might be a factor 4 missing due to the angular integration)
# To take account of an emissivity <1, multiply by eps.
sigma = 5.670373*1e-8 # Boltzmann constant, unit: W/m^2/K^4
Pbol_pl = eps*sigma*Tcam_pl**4
Pbol_pr = eps*sigma*Tcam_pr**4
Pbol_tl = eps*sigma*Tcam_tl**4
Pbol_tr = eps*sigma*Tcam_tr**4


plt.plot(Tcam_pl, P_INT_pl, 'g.', label = 'PL Calc')
plt.plot(Tcam_pl, Pcam_pl, 'gx', label = 'PL Cam')
plt.plot(Tcam_pl, Pbol_pl, 'g^', label = 'PL Bol')

plt.plot(Tcam_pr, P_INT_pr, 'r.', label = 'PR Calc')
plt.plot(Tcam_pr, Pcam_pr, 'rx', label = 'PR Cam')
plt.plot(Tcam_pr, Pbol_pr, 'r^', label = 'PR Bol')

plt.plot(Tcam_tl, P_INT_tl, 'b.', label = 'TL Calc')
plt.plot(Tcam_tl, Pcam_tl, 'bx', label = 'TL Cam')
plt.plot(Tcam_tl, Pbol_tl, 'b^', label = 'TL Bol')

plt.plot(Tcam_tr, P_INT_tr, 'y.', label = 'TR Calc')
plt.plot(Tcam_tr, Pcam_tr, 'yx', label = 'TR Cam')
plt.plot(Tcam_tr, Pbol_tr, 'y^', label = 'TR Bol')

plt.legend(loc='best')
plt.xlabel('T in K')
plt.ylabel('P in W \ $m^2$')
plt.savefig(filedate + '/tempTOpower.pdf')
plt.show()


#------------------------------------------------------------------------
#------------------------------------------------------------------------
#------------------------------------------------------------------------
# Real Wavelength Range
Preal_INT_pl = np.zeros(len(realT_pl))
Preal_INT_pr = np.zeros(len(realT_pr))
Preal_INT_tl = np.zeros(len(realT_tl))
Preal_INT_tr = np.zeros(len(realT_tr))

positions = ['pl', 'pr', 'tl', 'tr']
counter = 0
colors = ['g', 'r', 'b', 'y']
for pos in positions:
    for i in range(0,len(vars()['realT_' + pos])):
        vars()['Preal_INT_' + pos][i] = temp_to_power_INT(minLambda, maxLambda, vars()['realT_' + pos][i], T_amb[i], eps) * 1e12

    plt.plot(vars()['realT_' + pos], vars()['Preal_INT_' + pos], colors[counter] + 'o', label = 'Calc ' + pos)
    plt.plot(vars()['realT_' + pos], vars()['realP_' + pos], colors[counter] + 'x', label = 'Cam ' + pos)
    plt.plot(vars()['Tcam_' + pos], vars()['P_INT_' + pos], colors[counter] + '*', label = 'Calc ' + pos + ' old')
    plt.plot(vars()['Tcam_' + pos], vars()['Pcam_' + pos], colors[counter] + '.', label = 'Cam ' + pos + ' old')

    counter += 1

lgd = plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=3)
#plt.legend(loc='best')
plt.xlabel('Temperature in K')
plt.ylabel('Power in W \ $m^2$')
plt.savefig(filedate + '/tempTOpower.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
#plt.savefig(filedate + '/tempTOpower.pdf')
plt.show()




exit()


print("Select calculation:")
print("1. Emitted power for a fixed wavelength (e.g 10.5 micrometer)")
print("2. Emitted power over IR camera range: 8 - 13 micrometers")

option = input("Enter calculation [1/2] ") 
print("Option is %s" % option)

Temp = float(input("Enter the temperature in Celsius: "))
Eps = float(input("Enter the emissivity: "))


if option == "1":
    print("Emitted power at lambda ", Lambda, ", temperature ", Temp, ", and emissivity ", Eps, " is: %e \n\nExiting." % temp_to_power(Lambda, Temp+CtoK, Eps))

elif option == "2":
    print("Emitted power over IR range at temperature ", Temp, " and emissivity ", Eps, " is : %e \n\nExiting." % temp_to_power_INT(minLambda, maxLambda, Temp+CtoK, Eps))
else:
    print("Invalid input")
