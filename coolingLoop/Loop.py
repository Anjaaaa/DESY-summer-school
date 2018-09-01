import numpy as np
import matplotlib.pyplot as plt

colors = plt.cm.jet(np.linspace(0.1,0.9,5))


setpoints = ['22', '25', '35', '45', '56']   # in bar
pics = ['Left', 'CentreLeft', 'CentreRight', 'Right']

### Read values automatedly
### Format: e.g. Left45, CentreRight22
for pic in pics:
    for setpoint in setpoints:
        # Read labels and values separately because labels need to be strings.
        labels = np.genfromtxt('values' + pic + setpoint + '.txt', unpack = True, dtype = str, delimiter = ' ', usecols=0)
        values = np.genfromtxt('values' + pic + setpoint + '.txt', unpack = True, usecols=1)
        # Generate Variable names. Format: e.g. Left45, CentreRight22
        vars()['Labels' + pic] = labels
        vars()[pic + setpoint] = values


### Some values are measured on two pictures. Remove the excess ones (must be chosen visually from IR image).
keepLeftTop = range(1,23)
keepLeftBottom = []
keepCentreLeftTop = range(1,18) #[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 , 12, 13, 14, 15, 16 ,17]
keepCentreLeftBottom = list(reversed(range(22, 36))) + list(range(41,51))  #[35, 34, 33, 32, 31, 30, 29, 28, 27, 26, 25, 24, 23, 22, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50]
keepCentreRightTop = list(range(11, 22)) + list(range(68, 88)) #[11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87]
keepCentreRightBottom = list(reversed(range(44,68))) + list(range(40,41)) + list(range(30,31)) + list(reversed(range(22,26))) + list(range(31,32)) + list(reversed(range(26,30))) #[67, 66, 65, 64, 63, 62, 61, 60, 59, 58, 57, 56, 55, 54, 53, 52, 51, 50, 49, 48, 47, 46, 45, 44, 40, 30, 25, 24, 23, 22, 31, 29, 28, 27, 26]
keepRightTop =  list(range(49,53)) + list(range(34,49)) + list(range(78,81)) + list(reversed(range(75,78))) + list(reversed(range(30,34))) + list(reversed(range(69,75))) + list(reversed(range(18,30))) #[49, 50, 51, 52, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 78, 79, 80, 77, 76, 75, 33, 32, 31, 30, 74, 73, 72, 71, 70, 69, 29, 28, 27, 26, 25, 24, 23, 22, 21, 20, 19, 18]
keepRightBottom = []


# How many values are kept in total:
keep = len(keepLeftTop) + len(keepLeftBottom) + len(keepCentreLeftTop) + len(keepCentreLeftBottom) + len(keepCentreRightTop) + len(keepCentreRightBottom) + len(keepRightTop) + len(keepRightBottom)
INDEX = range(0, keep)


# Generate data arrays
Labels = []
T22 = []
T25 = []
T35 = []
T45 = []
T56 = []


plt.figure(num=None, figsize=(10, 5), facecolor='w', edgecolor='k')

# Plot thermocouples and holders as orientation.
thermocouple = [22+17+11+10+4+15+3+3+4+0.5]
holder = [18.5]
DontKnow = [22+17+11+10+0.5, 22+17+11+10+4+15+3+0.5, keep-10+0.5]
for t in thermocouple:
    plt.axvline(x=t, linestyle = 'dashed', color = 'k', label = 'Thermocouple')
for h in holder:
    plt.axvline(x=h, linestyle = 'dotted', color = 'k', label = 'Holder')
for DN in DontKnow:
    plt.axvline(x=DN, linestyle = 'dashdot', color = 'k', label = '?')


# Plot data.
counter = 0
for setpoint in setpoints:
    for pic in pics:
        keepTop = vars()['keep' + pic + 'Top']
        if (len(keepTop) > 0):               # IF is needed because otherwise there is problems with empty sets.
            keepTop -= np.ones(len(keepTop)) # python starts counting at 0.
        ### Append the values with the order in the keep arrays.
        for kt in keepTop:
            kt = int(kt)                     # We want indices to be integers.
            # Seperate the steps to have it less messy.
            A = vars()[pic + setpoint]
            a = A[kt]
            vars()['T' + setpoint].append(a)
            # Also keep track of the labels. This only needs to be done for one setpoint because we use the same labels for all the setpoints.
            if (setpoint=='22'):
#                label = vars()['Labels' + pic]
#                l = label[kt]
                vars()['Labels'].append('T' + pic + str(kt+1))
                print('T' + pic + str(kt+1))

    for pic in reversed(pics):
        keepBottom = vars()['keep' + pic + 'Bottom']
        if (len(keepBottom) > 0):
            keepBottom -= np.ones(len(keepBottom))
        for kb in keepBottom:
            kb = int(kb)
            B = vars()[pic + setpoint]
            b = A[kb]
            vars()['T' + setpoint].append(b)
            if (setpoint=='22'):
#                label = vars()['Labels' + pic]
#                l = label[kt]
                vars()['Labels'].append('B' + pic + str(kb+1))
                print('B' + pic + str(kb+1))

    data = vars()['T' + setpoint]
    plt.plot(INDEX, data, label = setpoint, color = colors[counter])
    counter += 1
    

# Don't print all the x-labels.
which_labels = [INDEX[i] for i in INDEX if i%5 == 0]
l = [Labels[i] for i in INDEX if i%5 == 0]
plt.xticks(which_labels, l, size='small', rotation='60')


plt.grid(alpha=0.5)
plt.ylabel('Temperature in T')
plt.xlim(INDEX[0], INDEX[-1])
plt.tight_layout()
lgd = plt.legend(bbox_to_anchor=(0,1.02,1,0.2), loc="lower left", mode="expand", borderaxespad=0, ncol=3)
plt.savefig('test.pdf', bbox_extra_artists=(lgd,), bbox_inches='tight')
#plt.show()

