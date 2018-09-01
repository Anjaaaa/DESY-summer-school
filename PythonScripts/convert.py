import numpy as np

### convert the google docs spreadsheet data to python usable data

timestamps = ['1824', '1844', '1900']
ID, Avg = np.genfromtxt('Data' + timestamps[0] + '.tsv', skip_header=0, usecols=(0,1), dtype=(str, float), unpack = True)
# Remove the first elements ('ID', 'Avg')
ID = ID[1:]
Avg = Avg[1:]
# Write header
txtfile  = open('Data.txt', "w")
txtfile.write('#')
for name in ID:
    txtfile.write(name + ' ')
txtfile.write('\n')
txtfile.close()
# Write values
for time in timestamps:
    ID, Avg = np.genfromtxt('Data' + time + '.tsv', skip_header=0, usecols=(0,1), dtype=(str, float), unpack = True)
    # Remove the first elements ('ID', 'Avg')
    ID = ID[1:]
    Avg = Avg[1:]
    txtfile = open('Data.txt', "a")
    txtfile.write(time + ' ')
    for value in Avg:
        txtfile.write(str(value) + ' ')
    txtfile.write('\n')
    txtfile.close()

