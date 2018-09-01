#!/usr/bin/env python

##################################################

# Plotting temperatures and pressures of thermal cycle
# x axis = labels corresponding to 
#	- TRACI set points in bars
#	- TRACI inlet Temp in C

# Author: Claire David
# Date: October 2017
# Status: in dev

##################################################

import os,sys
import matplotlib.pyplot as plt

from datetime import datetime
from array import array
from copy import deepcopy

the_path = ('/').join(os.getcwd().split('/')[:-2])
sys.path.append(the_path)
sys.path.append("%s/utils/"%the_path)
sys.path.append("%s/macros/markers/"%the_path)

import cycle_set_points_reader
import marker 
from utils import utils

#-----------------------------------
#   P A R A M E T E R S 
#-----------------------------------

fontsize = 10
plt.rcParams['lines.linewidth'] = 1
plt.rc('figure', titlesize=18)
plt.rc('axes', titlesize=18, labelsize=16)
plt.rc('legend', frameon=False, fontsize=14, scatterpoints=1, numpoints=1)

outFilePrefix = "unwrapped_cycle_" 
outDir = "%s/plots/thermal_cycles/" % (the_path)

#-----------------------------------

def usage():
    print "Usage:\n"
    print 'python '+sys.argv[0]+' CYCLEREF'
    print '\t2 = thermal cycle 20170802-03'
    print '\t9 = thermal cycle 20170809-10'
    sys.exit(2)

#-----------------------------------

def indicesSublist(listAll, sublist):
    enumerate_listAll = enumerate(listAll)
    for subitem in sublist:
        for i, itemAll in enumerate_listAll:
            if subitem == itemAll:

                # patch: lowest point, take the second occurence: 
                yield i+1 if subitem=='13' else i
                break

#-----------------------------------

def main():
    
    if len(sys.argv[1:]) < 1:
        usage()

    cycle = int(sys.argv[1])

    # Getting all files
    path_thermograms    = ""
    file_cycle_data     = ""
    file_KeithleyTRACI  = ""
    file_markers        = ""

    if cycle == 2:
        path_thermograms    = "%s/data/cycle_20170802/AVG_asc_files_petalCycle_20170802/TempScale/" %(the_path)
        file_cycle_data     = "%s/data/cycle_20170802/data_setpoints_petalCycle_20170802.txt" %(the_path)
        file_KeithleyTRACI  = "%s/data/cycle_20170802/KeithleyTRACI_data_2017-08-02_17-52-27.txt" %(the_path)
        file_markers        = "%s/data/cycle_20170802/BT_Markers_20170802.mdf" %(the_path)
    elif cycle == 9:
        path_thermograms    = "%s/data/cycle_20170809/AVG_asc_files_petalCycle_20170809/TempScale/" %(the_path) 
        file_cycle_data     = "%s/data/cycle_20170809/data_setpoints_petalCycle_20170809.txt" %(the_path)
        file_KeithleyTRACI  = "%s/data/cycle_20170809/KeithleyTRACI_data_2017-08-09_15-51-01.txt" %(the_path)
        file_markers        = "%s/data/cycle_20170809/BT_Markers_20170809.mdf" %(the_path)
    else:
        print "Cycle not known! Exiting."
        sys.exit(2)
    
    # Getting coordinates markers to compare with PT100 thermocouples
    markers = {}
    if cycle == 2:
        markers['TSiMid_marker']    = marker.get_marker('TC_Ch3', file_markers)
        markers['TSiBorder_marker'] = marker.get_marker('TC_Ch2', file_markers)
    elif cycle == 9:
        markers['R0_marker']        = marker.get_marker('TC_R0', file_markers)
        markers['R1_marker']        = marker.get_marker('TC_R1', file_markers)
        markers['R3b_marker']       = marker.get_marker('TC_R3b', file_markers)
        markers['R3m_marker']       = marker.get_marker('TC_R3m', file_markers)
        markers['R4_marker']        = marker.get_marker('TC_R4', file_markers)
        markers['R5_marker']        = marker.get_marker('TC_R5', file_markers)

    # Fill dict with all data
    dataCycle = cycle_set_points_reader.readData(cycle, file_cycle_data)
    cycle_set_points_reader.printData(dataCycle)

    # X axis: labels and indices
    setPointXi = []
    setPointXLabels = [] 
    
    setPointXiOff = []
    setPointXLabelsOff = []
    
    T_Series = dict()
    if cycle == 2:
        T_Series = {'Tinlet':[], 'Toutlet':[], 'TT103':[], 'TT106':[], 'TSiBorder_marker':[], 'TSiBorder':[], 'TSiMid_marker':[], 'TSiMid':[]} 
    elif cycle == 9:
        T_Series = {'Inlet':[], 'Outlet':[], 'TT103':[], 'TT106':[], 'R0':[], 'R0_marker':[], 'R1':[], 'R1_marker':[], 'R3b':[], 'R3b_marker':[], 'R3m':[], 'R3m_marker':[], 'R4':[], 'R4_marker':[], 'R5':[], 'R5_marker':[]}
    
    T_SeriesOFF = deepcopy(T_Series)

    for i in range(len(dataCycle['setPoint'])):
        
        # Get only "official" thermocycle points = Elec BOTH, and Position either GD, LO, RU
        if dataCycle['Position'][i] in ['GD','LO','RU']:

            # Line plotting when petal powered on both sides:
            if dataCycle['Elec'][i] == 'BOTH':
                setPointXLabels.append(str(dataCycle['setPoint'][i]))
                
                for key in T_Series:
                    if "_marker" in key:
                        T_Series[key].append(utils.KtoC(marker.get_marker_temp(markers[key], path_thermograms, dataCycle['TempThermograms'][i])))
                    else:
                        T_Series[key].append(dataCycle[key][i])
            
            # Scatter plot when petal not powered:
            elif dataCycle['Elec'][i] == 'OFF':
                setPointXLabelsOff.append(str(dataCycle['setPoint'][i]))

                for key in T_Series:
                    if "_marker" in key:
                        T_SeriesOFF[key].append(utils.KtoC(marker.get_marker_temp(markers[key], path_thermograms, dataCycle['TempThermograms'][i])))
                    else:
                        T_SeriesOFF[key].append(dataCycle[key][i])


    N = len(setPointXLabels)
    setPointXi = list(range(N))
    print "%d data points (with electronic on)" %(N)
    
    setPointXiOff = list(indicesSublist(setPointXLabels, setPointXLabelsOff)) 
   
    print "Set points (indices and pressure in bars):"
    print setPointXi
    print setPointXLabels
    print "\nOff series (indices and pressures in bars):"
    print setPointXiOff
    print setPointXLabelsOff

    #--------------------------
    #   Plotting
    #--------------------------

    fig = plt.figure(figsize=(12,5))
    axL = plt.subplot(111)

    plt.xticks(setPointXi, setPointXLabels)

    # Plot tuple: ( key, color, linestyle, marker, markerfacecolor, label)
    plotSeries = []
    
    if cycle == 2:
        plotSeries.append(('TT103',             'deepskyblue',  '-',    'o',     'deepskyblue', '$\mathregular{CO_2}$ entering petal'))
        plotSeries.append(('Tinlet',            'deepskyblue',  '--',   'o',     'None',        'inlet pipe (PT100)'))
        plotSeries.append(('TT106',             'blue',         '-',    'o',     'blue',        '$\mathregular{CO_2}$ leaving petal'))
        plotSeries.append(('Toutlet',           'blue',         '--',   'o',     'None',        'outlet pipe (PT100)'))

        plotSeries.append(('TSiMid_marker',     'red',          '-',    'o',     'red',         'R3 sensor, middle'))
        plotSeries.append(('TSiMid',            'red',          '--',   'o',     'None',        'R3 sensor, middle (PT100)'))
        plotSeries.append(('TSiBorder_marker',  'darkorange',   '-',    'o',     'darkorange',  'R3 sensor, border')) 
        plotSeries.append(('TSiBorder',         'darkorange',   '--',   'o',     'None',        'R3 sensor, border (PT100)'))
    
    elif cycle == 9:
        plotSeries.append(('TT103',             'deepskyblue',  '-',    'o',     'deepskyblue', '$\mathregular{CO_2}$ entering petal'))
        plotSeries.append(('Inlet',             'deepskyblue',  '--',   'o',     'None',        'inlet pipe (PT100)'))
        plotSeries.append(('TT106',             'blue',         '-',    'o',     'blue',        '$\mathregular{CO_2}$ leaving petal'))
        plotSeries.append(('Outlet',            'blue',         '--',   'o',     'None',        'outlet pipe (PT100)'))

        plotSeries.append(('R0_marker',         'fuchsia',      '-',    'o',     'fuchsia',     'R0 sensor'))
        plotSeries.append(('R0',                'fuchsia',      '--',   'o',     'None',        'R0 sensor (PT100)'))
        plotSeries.append(('R1_marker',         'darkviolet',   '-',    'o',     'darkviolet',  'R1 sensor'))
        plotSeries.append(('R1',                'darkviolet',   '--',   'o',     'None',        'R1 sensor (PT100)'))
        plotSeries.append(('R3m_marker',        'red',          '-',    'o',     'red',         'R3 sensor, middle'))
        plotSeries.append(('R3m',               'red',          '--',   'o',     'None',        'R3 sensor, middle (PT100)'))
        plotSeries.append(('R3b_marker',        'darkorange',   '-',    'o',     'darkorange',  'R3 sensor, border'))
        plotSeries.append(('R3b',               'darkorange',   '--',   'o',     'None',        'R3 sensor, border (PT100)'))
        plotSeries.append(('R4_marker',         'yellowgreen',  '-',    'o',     'yellowgreen', 'R4 sensor'))
        plotSeries.append(('R4',                'yellowgreen',  '--',   'o',     'None',        'R4 sensor (PT100)'))
        plotSeries.append(('R5_marker',         'green',        '-',    'o',     'green',       'R5 sensor'))
        plotSeries.append(('R5',                'green',        '--',   'o',     'None',        'R5 sensor (PT100)'))

    cycle_set_points_reader.printData(T_Series)
    
    # Line series (elec on)
    for p in plotSeries: # line only, no marker
        axL.plot(setPointXi, T_Series[p[0]], color=p[1], linestyle=p[2], marker='', label=p[5])

    handlerLines, labels = axL.get_legend_handles_labels()

    # Scatter series (electronic off at start, lowest point, end of cycle) 
    for p in plotSeries:
        axL.scatter(setPointXiOff, T_SeriesOFF[p[0]], marker=p[3], facecolors=p[4], edgecolors=p[1]) #, facecolors=p[4])

    # Artist dummy: grey round marker for legend
    dummyMarkerElecOff  = plt.Line2D((0,1),(0,0), marker='o', mfc='grey', mec='grey', linestyle='None')
    linePlain_IRcam     = plt.Line2D((0,1),(0,0), marker='', c='grey', linestyle='-')
    lineDash_PT100      = plt.Line2D((0,1),(0,0), marker='', c='grey', linestyle='--')

    
    # Legend line
    # inlet/outlet:
    legIO = axL.legend( [handle for i,handle in enumerate(handlerLines) if i<4], 
                        [label for i,label in enumerate(labels) if i<4],
                        loc=(1.04, 0.7), title="Temperatures:")
    
    # Sensors: one general entry, later dummy legend will diff the IRcam from PT100 measurements
    yLegPos = 0.0 if cycle == 9 else 0.1
    plt.legend([handle for i,handle in enumerate(handlerLines) if i>3 and i%2 == 0] +   [dummyMarkerElecOff, linePlain_IRcam, lineDash_PT100 ], 
                      [label for i,label in enumerate(labels) if i>3 and i%2 == 0]  +   ['\nPetal not powered', 'Black tape (IR camera)', 'Thermocouple (PT100)'], 
                      loc=(1.04, yLegPos))
    plt.gca().add_artist(legIO)
    plt.setp(legIO.get_title(),fontsize='16')
    
    # General plot info:
    sidePetal = "unpolished" if cycle == 2 else "polished"
    plt.title('Thermal cycle of %s side, August %d, 2017'%(sidePetal, cycle), y=1.05)
    plt.xlabel('Set point [bar]')
    plt.ylabel('Temperature [$^\circ$C]')
    plt.grid(alpha=0.5)
    
    # Shrink current x axis:
    fig.subplots_adjust(right=0.65)

    # Output file:
    outstamp    = '{:%Y%m%d%H%M}'.format(datetime.now())
    outputname  = outDir + outFilePrefix + str(cycle)  + "_" + outstamp + ".pdf"

    plt.savefig(outputname)    
    print "Figure saved as ", outputname


#----------------------------------------------- 
if __name__ == '__main__':
    
    main()

