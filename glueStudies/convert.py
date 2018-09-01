import numpy as np

timestamps = ['1121', '1141', '1203', '1228', '1250', '1308', '1324', '1340', '1350', '1358', '1409', '1418']
ID = np.genfromtxt('MessungGlued180823 - ' + timestamps[0] + '.tsv', skip_header=0, usecols=0, dtype=str, unpack = True)
# Remove the first elements ('ID', 'Avg')
ID = ID[1:]
# Write header
txtfile  = open('Data.txt', "w")
txtfile.write('#time ')
for name in ID:
    txtfile.write(name + '100 ')
for name in ID:
    txtfile.write(name + '095 ')
txtfile.write('\n')
txtfile.close()
# Write values
for time in timestamps:
    Avg100, Avg095 = np.genfromtxt('MessungGlued180823 - ' + time + '.tsv', skip_header=0, usecols=(1,7), dtype = (str,str), unpack = True)
    # Remove the first elements ('Avg')
    Avg100 = Avg100[1:]
    Avg095 = Avg095[1:]
    for k in range(0,len(Avg100)):
        Avg100[k] = float(str(Avg100[k]).replace(",", "."))
        Avg095[k] = float(str(Avg095[k]).replace(",", "."))
    txtfile = open('Data.txt', "a")
    txtfile.write(time + ' ')
    for value in Avg100:
        txtfile.write(str(value) + ' ')
    for value in Avg095:
        txtfile.write(str(value) + ' ')
    txtfile.write('\n')
    txtfile.close()


