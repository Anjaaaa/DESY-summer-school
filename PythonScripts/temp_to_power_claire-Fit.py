#!/usr/bin/env python
#####################################################
# Script to plot the radiated power vs temperature 
# From self-computation using Planck's law
# to compare with IRBIS software internal conversion
#
# Author: Claire David
# Inspired from Anja Beck
# Date: August 2018
#####################################################
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
import random
from scipy.optimize import curve_fit

#------------------------------------------------------------------------
# C O N S T A N T S
#------------------------------------------------------------------------

C1      = 1.1910429526245744e-4*np.pi   # 2hc^2 [W.m^2]
C2      = 1.438775e4                    # hc/k [microm.K]
CtoK    = 273.15
N       = 100                           # nb data points for computed power
T_AMB   = 20                         # Celsius

minLambda = 8
maxLambda = 13


#------------------------------------------------------------------------
# P L A N C K   L A W
#------------------------------------------------------------------------

def reducedPlanck(Lambda, temp_K):
    return 1e12*C1/Lambda**5/np.expm1(C2/(Lambda*temp_K))
       
def reducedPlanckIntegral(minLambda, maxLambda, temp_K):
    return integrate.quad(lambda x: reducedPlanck(x, temp_K), minLambda, maxLambda)[0]

# Integrated power
def temp_to_power(minLambda, maxLambda, temp_K, temp_amb, eps, tau):
    return tau*(eps*reducedPlanckIntegral(minLambda, maxLambda, temp_K) + (1-eps)*reducedPlanckIntegral(minLambda, maxLambda, temp_amb))

# curve_fit requires the first parameter to be the variable.
def FIT(temp_K, *args):
    return temp_to_power(args[0], args[1], temp_K, args[2], args[3], args[4])

#------------------------------------------------------------------------

def usage():
    print ("Usage:\n")
    print ('python '+sys.argv[0]+' DATAFILEPATH_Eps100' + ' DATAFILEPATH_Eps095' + ' DATAFILEPATH_Eps090')
    print ('Example:\n')
    print ('python '+sys.argv[0]+' data/Messung180809_eps100.txt' + ' data/Messung180809_eps095.txt' + ' data/Messung180809_eps090.txt')
    sys.exit(2)

#------------------------------------------------------------------------

def main():
    # ------ Instructions
    if len(sys.argv[1:]) < 3:
        usage()
    filenameEps100    = sys.argv[1]
    filenameEps095    = sys.argv[2]
    filenameEps090    = sys.argv[3]
    

    # ----- Dic of list / key = measurement point
    # ----- Calculate min and max temperature
    # We are only using pr anyway.
    positions = ['pr']#['pl', 'pr', 'tl', 'tr']
    for A in ['100', '095', '090']:
        # ----- Get data
        timestamp, Tcam_tl, Tcam_tr, Tcam_pl, Tcam_pr, Pcam_tl, Pcam_tr, Pcam_pl, Pcam_pr = np.genfromtxt(vars()['filenameEps' + A], unpack = True)
        vars()['Tcam' + A] = {}
        vars()['Pcam' + A] = {}
        vars()['T' + A] = []
        for pos in positions:
            vars()['Tcam' + A][pos] = vars()['Tcam_' + pos]
            vars()['Pcam' + A][pos] = vars()['Pcam_' + pos]
            vars()['T' + A] = np.concatenate((vars()['T' + A],vars()['Tcam' + A][pos]),axis=None)
        vars()['minT' + A] = np.min(vars()['T' + A])
        vars()['maxT' + A] = np.max(vars()['T' + A])
        print('Min/ Max Temperatures for ' + A + ':')
        print(vars()['minT' + A], vars()['maxT' + A])
 

    #-----------------------------------------------
    # Camera vs computed T-to-P, for diff epsilon
    #-----------------------------------------------
    plt.cla()
    color = {}
    color['100'] = 'r'
    color['095'] = 'y'
    color['090'] = 'b'
    fig, (ax1, ax2) = plt.subplots(2,1, gridspec_kw = {'height_ratios':[2, 1]}, figsize=(6, 9), dpi=150)
    for A in ['100', '095', '090']:
        eps_str = A[0] + '.' + A[1:]
        eps = float(eps_str)
    ### FIT
        # A fit of one parameter in a multi-parameter function requires search ranges and starting values.
        guess = minLambda, maxLambda, T_AMB, eps, 0.5
        deltaLambda = 1e-10
        deltaT = 1e-10
        deltaEps = 1e-10
        lowerBound = minLambda-deltaLambda, maxLambda-deltaLambda, T_AMB-deltaT, eps-deltaEps, 0
        upperBound = minLambda+deltaLambda, maxLambda+deltaLambda, T_AMB+deltaT, eps+deltaEps, 1
        popt, pcov = curve_fit(np.vectorize(FIT), vars()['Tcam' + A]['pr']+273.15, vars()['Pcam' + A]['pr'], p0=guess, bounds=(lowerBound, upperBound))
        tau = popt[4]
        print('eps = ' + eps_str + ': tau = ' + "%.2f" % tau)
    ### Compute the power with the fitted function.
        temps = np.linspace(vars()['minT' + A], vars()['maxT' + A], N)
        calc_P = [temp_to_power(minLambda, maxLambda, T+CtoK, T_AMB+CtoK, eps, tau) for T in temps]
    ### Data Plot
        # Plot calculated data
        ax1.plot(temps, calc_P, color = color[A], linewidth = 0.8, label = 'comp, eps = ' + eps_str + ', tau = ' + "%.3f" % tau)
        # Plot camera data.
        ax1.plot(vars()['Tcam' + A]['pr'], vars()['Pcam' + A]['pr'], color = color[A], marker = 'x', linewidth = 0, label = 'cam')
        ax1.set_ylabel('Radiated power [W/m$^2$]')
        ax1.legend(loc='best')
    ### Ratio Plot
        calc_P_Ratio = [temp_to_power(minLambda, maxLambda, T+CtoK, T_AMB+CtoK, eps, tau) for T in vars()['Tcam' + A]['pr']]
        Ratio = calc_P_Ratio/vars()['Pcam' + A]['pr']
        ax2.plot(vars()['Tcam' + A]['pr'], Ratio, color = color[A], marker = '.', linewidth = 0, label = eps_str)
        ax2.set_ylabel('Ratio Comp/Cam')
        ax2.legend(loc='best')
    plt.xlabel('Temperature [$^\circ$C]')
    plt.tight_layout()
    outputname = 'T_to_P_Fit_' + os.path.splitext(os.path.basename(filenameEps100))[0] + '.pdf'
    plt.savefig(outputname)
    
#----------------------------------------------- 

if __name__ == '__main__':
    
    main()
