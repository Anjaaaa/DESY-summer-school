import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

TOKEN = ''

#--------------------------------------------------------------
if (TOKEN == 'ALL'): 
    filedates = ['2018-07-27_17-14-47', '2018-08-08_14-42-53', '2018-08-22_17-27-25', '2018-07-30_15-34-39', '2018-08-09_13-54-32', '2018-08-23_10-56-34']
    IR_images = []
    IR_pic = []
    names = ['PaintLeft', 'PaintRight', 'TapeLeft', 'TapeRight']
    
else:
    filedates = ['2018-08-23_10-56-34']
    IR_images = ['2018-08-23_11:21:00', '2018-08-23_11:41:00', '2018-08-23_12:03:00', '2018-08-23_12:28:00', '2018-08-23_12:50:00', '2018-08-23_13:08:00', '2018-08-23_13:24:00', '2018-08-23_13:40:00', '2018-08-23_13:50:00', '2018-08-23_13:58:00', '2018-08-23_14:09:00', '2018-08-23_14:18:00']
    IR_pic = []
    for ir in IR_images:
        IR_pic.append(datetime.strptime(ir, '%Y-%m-%d_%H:%M:%S'))
    names = ['SiGlued1', 'SiGlued2', 'SiGlued3', 'SiClamped', 'PeltierClamped', 'Peltier']

#--------------------------------------------------------------
for ir in IR_images:
    IR_pic.append(datetime.strptime(ir, '%Y-%m-%d_%H:%M:%S'))

for filedate in filedates:
    if (TOKEN == 'ALL'):
        Time, PaintLeft, PaintRight, TapeLeft, TapeRight = np.genfromtxt(filedate + '.txt', skip_header = 2, usecols = np.arange(0,len(names)+1), dtype = 'unicode', unpack = True)
    else:
        Time, SiGlued1, SiGlued2, SiGlued3, SiClamped, PeltierClamped, Peltier = np.genfromtxt(filedate + '.txt', skip_header = 2, usecols = np.arange(0,len(names)+1), dtype = 'unicode', unpack = True)

    # Convert the temperatures to floats and the dates to datetime objects.
    for name in names:
        vars()[name] = vars()[name].astype(np.float)
    time = []
    for T in Time:
        time.append(datetime.strptime(T, '%Y-%m-%d_%H:%M:%S'))
    
    # Plot
    colors = plt.cm.jet(np.linspace(0,1,len(names)-2))
    c = {}
    for k in range(0,len(names)-2):
        c[names[k]] = colors[k]
    for name in names[0:-2]:
        if (vars()[name][-1]<100):
            plt.plot(time[40:], vars()[name][40:], color = c[name], linewidth=0.8, label = name)
    for ir in IR_pic:
        plt.axvline(x=ir, color = 'k', linewidth=0.7, linestyle = '--')
    plt.gcf().autofmt_xdate(rotation=45)
    plt.ylabel('temperature in C')
    plt.xlim(time[40], time[-1])
    plt.title('temperatures at ' + datetime.strftime(time[0], '%Y-%m-%d'))
    plt.legend(loc='best')
    plt.tight_layout()
    plt.savefig('Temp' + filedate + '.pdf')
    plt.cla()


    if not (TOKEN == 'ALL'):
        for name in names[0:-2]:
            if (vars()[name][-1]<100):
                plt.plot(time[180:240], vars()[name][180:240], color = c[name], linewidth=1, label = name)
        plt.gcf().autofmt_xdate(rotation=45)
        plt.ylabel('temperature in C')
        plt.xlim(time[180], time[240-1])
#        plt.title('temperatures at ' + datetime.strftime(time[0], '%Y-%m-%d'))
        plt.legend(loc='best')
        plt.tight_layout()
        plt.savefig('Temp_closeup.pdf')
        plt.cla()
