from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import filterGen


#samples = np.load("outfile_samples.npy")
#samples2 = np.load("PBZS_stage1.npy")
pre_filter = np.load('outfile_samples.npy')


window = 65 * 30

start = 204750
start2 = 204750

sample_rate = 226000
symbol_rate = 3650

nyq_freq = sample_rate/2

filter_order = 2
low_cutoff = 1
high_cutoff = 3650

post_filter = filterGen.bp_butter(pre_filter, [low_cutoff, high_cutoff], filter_order, sample_rate)
print('post filter lenght: ' + str(len(post_filter)))

pre_filter = pre_filter[start:start+window]
post_filter = post_filter[start2:start2+window]

w1 = low_cutoff / nyq_freq          # For digital filters, Wn is normalized from 0 to 1, where 1 is the Nyquist frequency, pi radians/sample.
w2 = high_cutoff / nyq_freq         # (Wn is thus in half-cycles / sample.)

ratio = 5

b, a = signal.butter(filter_order, [w1, w2] , 'bandpass')
w, h = signal.freqz(b, a, worN = sample_rate)


fig = plt.figure()



fig.suptitle('Python filter simulator', fontsize=24)


SMALL_SIZE = 12
MEDIUM_SIZE = 10
BIGGER_SIZE = 16

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title




ax1 = fig.add_subplot(221)
plt.title('Bandpass over Power Spectral Density')
plt.axvline(low_cutoff, color='green') # cutoff frequency
plt.axvline(high_cutoff, color='green') # cutoff frequency
plt.xlim([0, high_cutoff*ratio])
pre_psd = plt.psd(pre_filter, NFFT=2048, Fs=sample_rate, Fc=0)
post_psd = plt.psd(post_filter, NFFT=2048, Fs=sample_rate, Fc=0)
plt.legend(['FcL','FcH','Pre-Filter', 'Post-Filter'])




ax2 = fig.add_subplot(222)
plt.title('Digital filter frequency response - Order: ' + str(filter_order))
plt.plot(w*nyq_freq, h, 'k')
plt.ylabel('Amplitude', color='k')
plt.xlabel('Frequency Hz')

plt.xlim([0, high_cutoff*ratio])
plt.axvline(low_cutoff, color='green')      # cutoff frequency
plt.axvline(high_cutoff, color='green')     # cutoff frequency
plt.legend(['Gain','Cutoff Frequencies'])
plt.grid()
#ax2 = ax1.twinx()
#angles = np.unwrap(np.angle(h))
#plt.plot(w, angles, 'g')
#plt.ylabel('Angle (radians)', color='g')

ax3 = fig.add_subplot(223)
plt.plot(pre_filter)
plt.title('Signal excerpt pre filtering')
plt.xlabel('Sample Index')
plt.ylabel('Quantization')

ax4 = fig.add_subplot(224)
plt.plot(post_filter)
plt.title('Signal excerpt post filtering')
plt.xlabel('Sample Index')
plt.ylabel('Quantization')

#plt.axis('tight')
plt.show()
