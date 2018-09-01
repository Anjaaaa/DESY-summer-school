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

#------------------------------------------------------------------------
# C O N S T A N T S
#------------------------------------------------------------------------

C1      = 1.1910429526245744e-4*np.pi   # 2hc^2 [W.m^2]
C2      = 1.438775e4                    # hc/k [microm.K]
CtoK    = 273.15
N       = 100                           # nb data points for computed power
T_AMB   = 20                            # Celcius


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

#------------------------------------------------------------------------

def usage():
    print ("Usage:\n")
    print ('python '+sys.argv[0]+' DATAFILEPATH_BadRange' + ' DATAFILEPATH_GoodRange')
    print ('Example:\n')
    print ('python '+sys.argv[0]+' data/Messung180730_Camera.txt' + ' data/Messung180730RealRange.txt')
    sys.exit(2)

#------------------------------------------------------------------------

def main():
    # ------ Instructions
    if len(sys.argv[1:]) < 2:
        usage()
    filenameBadRange    = sys.argv[1]
    filenameGoodRange = sys.argv[2]

    # ----- Get data
    timestamp_cameraB, TcamB_pl, TcamB_pr, TcamB_tl, TcamB_tr, PcamB_pl, PcamB_pr, PcamB_tl, PcamB_tr = np.genfromtxt(filenameBadRange, unpack = True)
    timestamp_cameraG, TcamG_tl, TcamG_tr, TcamG_pl, TcamG_pr, PcamG_tl, PcamG_tr, PcamG_pl, PcamG_pr = np.genfromtxt(filenameGoodRange, unpack = True)
    
    # ----- Dic of list / key = measurement point
    # ----- Calculate min and max temperature
    positions = ['pl', 'pr', 'tl', 'tr']
    for A in ['B', 'G']:
        vars()['Tcam' + A] = {}
        vars()['Pcam' + A] = {}
        vars()['T' + A] = []
        for pos in positions:
            vars()['Tcam' + A][pos] = vars()['Tcam' + A + '_' + pos]
            vars()['Pcam' + A][pos] = vars()['Pcam' + A + '_' + pos]
            vars()['T' + A] = np.concatenate((vars()['T' + A],vars()['Tcam' + A][pos]),axis=None)
        vars()['minT' + A] = np.min(vars()['T' + A])
        vars()['maxT' + A] = np.max(vars()['T' + A])
        print('Min/ Max Temperatures for ' + A + ':')
        print(vars()['minT' + A], vars()['maxT' + A])
 
    # ----- Plotting
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    
    c = ["C1", "C3", "C2", "b"]
    linetype = {}
    linetype['B'] = '--'
    linetype['G'] = '-'
    markerstyle = {}
    markerstyle['B'] = '.'
    markerstyle['G'] = 'o'
    for A in ['G', 'B']:
        temps = np.linspace(vars()['minT' + A], vars()['maxT' + A], N)
        if (A == 'B'):
            LambdaMin = 8.0
            LambdaMax = 13.0
        else:
            LambdaMin = 7.5
            LambdaMax = 14.0
        calc_P = [temp_to_power(LambdaMin, LambdaMax, T+CtoK, T_AMB+CtoK, 1., 1.) for T in temps]

        #------------------------------------
        # 4 areas + 1 calculated power
        #------------------------------------
        counter = 0
        for pos in positions:
            # Plot temperature and power as given by the camera.
            plt.plot(vars()['Tcam' + A][pos], vars()['Pcam' + A][pos], c[counter]+markerstyle[A], label = pos + ' Cam ' + A)
            counter += 1
        # Plot calculated power for pr.
        plt.plot(temps, calc_P, c[1]+linetype[A], label = 'PR Calc ' + A)
    
    plt.legend(loc='best', frameon=False)
    plt.xlabel('Temperature [$^\circ$C]')
    plt.ylabel('Radiated power [W/m$^2$]')

    outputname = 'T_to_P_4pts_' + os.path.splitext(os.path.basename(filenameBadRange))[0] + '.pdf'
    plt.savefig(outputname)

    #-----------------------------------------------
    # Camera vs computed T-to-P, for diff lambdas
    #-----------------------------------------------
    plt.cla()
    color = {}
    color['B'] = 'r'
    color['G'] = 'g'
    Range = {}
    Range['B'] = '8 - 13 $\mu$m'
    Range['G'] = '7.5 - 14.0 $\mu$m'
    fig, (ax1, ax2) = plt.subplots(2,1, gridspec_kw = {'height_ratios':[2, 1]}, figsize=(6, 9), dpi=150)
    for A in ['B', 'G']:
        if (A == 'B'):
            LambdaMin = 8.0
            LambdaMax = 13.0
        else:
            LambdaMin = 7.5
            LambdaMax = 14.0
        temps = np.linspace(vars()['minT' + A], vars()['maxT' + A], N)
        calc_P = [temp_to_power(LambdaMin, LambdaMax, T+CtoK, T_AMB+CtoK, 1., 1.) for T in temps]
        calc_P_Ratio = [temp_to_power(LambdaMin, LambdaMax, T+CtoK, T_AMB+CtoK, 1., 1.) for T in vars()['Tcam' + A]['pr']]
        ### Data Plot
        # Plot calculated data
        ax1.plot(temps, calc_P, color[A] + '-', linewidth = 0.8, label = 'Computed power ' + Range[A])
        # Plot camera data.
        ax1.plot(vars()['Tcam' + A]['pr'], vars()['Pcam' + A]['pr'], color[A] + 'x', label = 'IR camera data ' + Range[A])
        ax1.set_ylabel('Radiated power [W/m$^2$]')
        ax1.legend(loc='best')
        ### Ratio Plot
        ax2.plot(vars()['Tcam' + A]['pr'], calc_P_Ratio/vars()['Pcam' + A]['pr'], color[A] + '.', label = Range[A])
        ax2.set_ylabel('Ratio Comp/Cam')
        ax2.legend(loc='best')
    plt.xlabel('Temperature [$^\circ$C]')
    plt.tight_layout()
    outputname = 'T_to_P_Ranges_' + os.path.splitext(os.path.basename(filenameBadRange))[0] + '.pdf'
    plt.savefig(outputname)
    
#----------------------------------------------- 

if __name__ == '__main__':
    
    main()
