import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

### Script to plot the pt100 temperature measurement

filedate = '2018-08-22_17-27-25'

IR_images = ['2018-08-22_17:30:00', '2018-08-22_18:27:00', '2018-08-22_19:44:00']
IR_pic = []
for ir in IR_images:
    IR_pic.append(datetime.strptime(ir, '%Y-%m-%d_%H:%M:%S'))

names = ['SiGlued1', 'SiGlued2', 'SiGlued3', 'SiClamped', 'PeltierClamped', 'Peltier']

Time, SiGlued1, SiGlued2, SiGlued3, SiClamped, PeltierClamped, Peltier = np.genfromtxt(filedate + '.txt', skip_header = 2, skip_footer = 1, usecols = np.arange(0,7), dtype = 'unicode', unpack = True)

# Convert the temperatures to floats and the dates to datetime objects.
for name in names:
    vars()[name] = vars()[name].astype(np.float)
time = []
for T in Time:
    time.append(datetime.strptime(T, '%Y-%m-%d_%H:%M:%S'))

# Plot
colors = plt.cm.jet(np.linspace(0,1,6))
c = {}
for k in range(0,6):
    c[names[k]] = colors[k]
for name in names:
    plt.plot(time, vars()[name], color = c[name], linewidth=0.8, label = name)
for ir in IR_pic:
    plt.axvline(x=ir, color = 'k', linestyle = '--')
plt.gcf().autofmt_xdate(rotation=45)
plt.ylabel('T in C')
plt.xlim(time[0], time[-1])
plt.title('Temperatures at ' + datetime.strftime(time[0], '%Y-%m-%d'))
plt.legend(loc='best')
plt.tight_layout()
plt.show()
