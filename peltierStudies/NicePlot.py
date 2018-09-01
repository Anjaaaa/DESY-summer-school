import numpy as np
import matplotlib.pyplot as plt
import scipy.integrate as integrate
import random
from matplotlib import cm


# Magnus-Formula Wikipedia 'Taupunkt'
def DewPoint(T, h):
    # Above water:
    K2 = 17.62
    K3 = 243.12
    Zahler = (K2*T)/(K3-T)+np.log(h/100)
    Nenner = (K2*K3)/(K3+T)-np.log(h/100)
    return K3 * Zahler/Nenner


filedates = ['180730', '180808', '180809']

# to automatically plot the point of ice formation
noice = {}
noice[filedates[0]] = 5
noice[filedates[1]] = 4
noice[filedates[2]] = -1



for filedate in filedates:
    ### Read data
    timestamp_pt100, T_amb, V_left, V_right, I_left, I_right, H, T_chill, pt100_PL, pt100_PR, pt100_TL, pt100_TR = np.genfromtxt('data/' + filedate + '.txt', unpack = True)
    timestamp_camera, Tcam_PL, Tcam_PR, Tcam_TL, Tcam_TR, Pcam_PL, Pcam_PR, Pcam_TL, Pcam_TR = np.genfromtxt('data/' + filedate + '_eps100_camera.txt', unpack = True)
    TK, eps_Tape, eps_Paint = np.genfromtxt('../emissivity/emissivity' + filedate + '.txt', unpack = True)

    ### Average of emissvities
    eps_Tape = np.mean(eps_Tape)
    eps_Paint = np.mean(eps_Paint)

    ### Conversion to Kelvin
    pos = ['TL', 'TR', 'PL', 'PR']
    T_amb += 273.15
    for p in pos:
        vars()['pt100_' + p] += 273.15
        vars()['Tcam_' + p] += 273.15

    ###################################################################    
    ### Plot background information
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(V_left, T_amb)
    ax1.set_ylabel('T in C')
    
    ax2 = ax1.twinx()
    ax2.plot(V_left, H, 'r-')
    ax2.set_ylabel('Relative Humidity', color='r')
    plt.xlabel('Voltage in V')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    
    plt.savefig(filedate + '/background.pdf')
    plt.cla()
    plt.clf()

    ###################################################################    
    ### Plot intensity vs voltage
    plt.plot(I_left, V_left, 'b', label = 'Left')
    plt.plot(I_right, V_right, 'r', label = 'Right')
    plt.legend(loc='best')
    plt.xlabel('Intensity in A')
    plt.ylabel('Voltage in V')
    plt.savefig(filedate + '/Peltier.pdf')
    plt.cla()


    ###################################################################  
    ### Plot temperatures of pt100 and camera measurement
    c = cm.jet(np.linspace(0,1,4))
    if (filedate == '180809'):
        pt100_Avg = (pt100_PR + pt100_TL + pt100_TR)/3
    else:
        pt100_Avg = (pt100_PL + pt100_PR + pt100_TL + pt100_TR)/4
    fig, (ax1, ax2) = plt.subplots(2,1,gridspec_kw = {'height_ratios':[2,1]}, figsize = (8,6), dpi=100) 
    time, T_eps95_TL, T_eps95_TR, T_eps95_PL, T_eps95_PR = np.genfromtxt('data/' + filedate + '_eps095_temp.txt', unpack = True)
    ### EMISSIVITY
    eps_paint = '092'
    for k in range(0,4):
        if (filedate == '180808'):
            time, T_eps98_TL, T_eps98_TR, T_eps98_PL, T_eps98_PR = np.genfromtxt('data/' + filedate + '_eps' + eps_paint + '_temp.txt', unpack = True)
        if (pos[k] == 'TR' or pos[k] == 'TL'):
            vars()['T_' + pos[k]] = vars()['T_eps95_' + pos[k]]
        elif (filedate == '180808' and (pos[k] == 'PR' or pos[k] == 'PL')):
            vars()['T_' + pos[k]] = vars()['T_eps98_' + pos[k]]
        else:
            vars()['T_' + pos[k]] = vars()['T_eps95_' + pos[k]]
        ax1.plot(pt100_Avg[0:noice[filedate]]-273.15, vars()['T_' + pos[k]][0:noice[filedate]], color = c[k], marker = 'x', linewidth = 0, label = pos[k] + ' cam')
        if not (filedate == '180809' and pos[k] == 'PL'):
            ax1.plot(pt100_Avg[0:noice[filedate]]-273.15, vars()['pt100_' + pos[k]][0:noice[filedate]]-273.15, color = c[k], marker = '.',linewidth = 0,  label = pos[k])
            ax2.plot(pt100_Avg[0:noice[filedate]]-273.15, vars()['pt100_' + pos[k]][0:noice[filedate]] - 273.15 - vars()['T_' + pos[k]][0:noice[filedate]], color =  c[k], linewidth = 0.3, marker = 'o', label = pos[k])

    ax1.legend(loc='best')
    ax2.legend(loc='best')
    plt.xlabel('temperature in C (PT100)')
    ax1.set_ylabel('temperature in C')
    ax2.set_ylabel('temperature difference in C')
    plt.suptitle('eps_tape = 0.95, eps_paint=0.' + eps_paint[1:])
    plt.tight_layout()
    plt.subplots_adjust(top=0.95)  # Otherwise tight_layout() destroys the position of the title
    plt.savefig(filedate + '/Intensity_Temperature.pdf')
    plt.cla()
    plt.clf()
