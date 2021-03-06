import numpy as np
import pylab
import matplotlib.pyplot as plt

debug = True		# Set to true to plot graphs

def compare_signal(signal, samples_per_symbol):


	signal_ceil = max(signal)
	signal_floor = min(signal)
	#print("\n\namplitude" + str(signal_ceil - signal_floor) + "\n\n")

	ratio = 0.35

	threshold = ((signal_ceil - signal_floor)*ratio)   + signal_floor

	#pylab.plot(signal)

	signal_zero_centered = [(x - threshold) for x in signal]

	zero_crossings = np.where(np.diff(np.signbit(signal_zero_centered)))[0]
	#np.append(zero_crossings, len(signal_zero_centered))
	zero_crossings = zero_crossings.tolist()

	#print(zero_crossings)
	#print(type(zero_crossings))
	zero_crossings.append(len(signal_zero_centered))


	allindexes = []
	chosen_samples = []
	for a in range(len(zero_crossings)-1):
		index = zero_crossings[a] + round(samples_per_symbol*0.5)
		while(index < (zero_crossings[a+1] - (samples_per_symbol*0.1))):
			allindexes.append(index)
			chosen_samples.append(signal_zero_centered[index])
			index += round(samples_per_symbol)


	if debug == True:
		signal_samples = []
		for x in range(len(allindexes)):
			signal_samples.append(signal[allindexes[x]])
		ts = [threshold] * len(zero_crossings)
		#pylab.subplot(2,1,1)
		pylab.plot(signal)
		plt.axhline(y=threshold, color='k', linestyle='-')
		plt.scatter(allindexes, signal_samples, color='red')
		plt.scatter(zero_crossings, ts, color='black')
		plt.title('Pass-by-Zero algorithm', fontsize = 24)
		plt.xlabel('Sample index', fontsize=18)
		plt.ylabel('Quantization level',fontsize=18)



		#pylab.subplot(2,1,2)
		#fft_signal = np.fft(signal)
		#pylab.plot(fft_signal)
		plt.legend(['Signal', 'Threshold', 'Chosen samples', 'Temporal synchronization Points'], loc = 1)
		plt.ylim([0, 1.1])
		plt.xlim([107300, 108700])
		plt.show()



	result = np.where(np.asarray(chosen_samples) > 0, 1, 0)

	return result
