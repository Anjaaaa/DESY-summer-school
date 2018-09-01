import numpy as np
import matplotlib.pyplot as plt


timestamp_pt100_180730, T_amb_180730, V_left_180730, V_right_180730, I_left_180730, I_right_180730, H_180730, T_chill_180730, pt100_pl_180730, pt100_pr_180730, pt100_tl_180730, pt100_tr_180730 = np.genfromtxt('Messung180730.txt', unpack = True)

timestamp_pt100_180808, T_amb_180808, V_left_180808, V_right_180808, I_left_180808, I_right_180808, H_180808, T_chill_180808, pt100_pl_180808, pt100_pr_180808, pt100_tl_180808, pt100_tr_180808 = np.genfromtxt('Messung180808.txt', unpack = True)

timestamp_pt100_180809, T_amb_180809, V_left_180809, V_right_180809, I_left_180809, I_right_180809, H_180809, T_chill_180809, pt100_pl_180809, pt100_pr_180809, pt100_tl_180809, pt100_tr_180809 = np.genfromtxt('Messung180809.txt', unpack = True)

### Intensity vs Voltage
plt.plot(I_left_180730, V_left_180730, 'r', linestyle = ':', label = '30.07.18')
plt.plot(I_right_180730, V_right_180730, 'r', linestyle = '--')#, label = 'Right')
plt.plot(I_left_180808, V_left_180808, 'b', linestyle = ':', label = '08.08.18')
plt.plot(I_right_180808, V_right_180808, 'b', linestyle = '--')#, label = 'Right')
plt.plot(I_left_180809, V_left_180809, 'g', linestyle = ':', label = '09.08.18')
plt.plot(I_right_180809, V_right_180809, 'g', linestyle = '--')#, label = 'Right')

plt.legend(loc='best')
plt.xlabel('Intensity in A')
plt.ylabel('Voltage in V')

plt.savefig('Peltier/Peltier.pdf')
plt.show()


### Intensity Temperature
plt.plot(I_left_180730, pt100_pl_180730, 'r', linestyle = ':', label = 'PL')
plt.plot(I_right_180730, pt100_pr_180730, 'b', linestyle = ':', label = 'PR')
plt.plot(I_left_180730, pt100_tl_180730, 'g', linestyle = ':', label = 'TL')
plt.plot(I_right_180730, pt100_tr_180730, 'y', linestyle = ':', label = 'TR')

plt.plot(I_left_180808, pt100_pl_180808, 'r', linestyle = '--')#, label = 'PL')
plt.plot(I_right_180808, pt100_pr_180808, 'b', linestyle = '--')#, label = 'PR')
plt.plot(I_left_180808, pt100_tl_180808, 'g', linestyle = '--')#, label = 'TL')
plt.plot(I_right_180808, pt100_tr_180808, 'y', linestyle = '--')#, label = 'TR')

#plt.plot(I_left_180809, pt100_pl_180809, 'r', linestyle = '-.')#, label = 'PL')
plt.plot(I_right_180809, pt100_pr_180809, 'b', linestyle = '-.')#, label = 'PR')
plt.plot(I_left_180809, pt100_tl_180809, 'g', linestyle = '-.')#, label = 'TL')
plt.plot(I_right_180809, pt100_tr_180809, 'y', linestyle = '-.')#, label = 'TR')

plt.xlim(1.5,4.75)


plt.legend(loc='best')
plt.xlabel('Intensity in A')
plt.ylabel('Temperature in C')

plt.savefig('Peltier/PeltierTemp.pdf')
plt.show()

