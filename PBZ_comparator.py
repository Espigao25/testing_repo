import numpy as np
import pylab
import matplotlib.pyplot as plt

debug = True		# Set to true to plot graphs

def compare_signal(signal, samples_per_symbol):

	signal_ceil = max(signal)
	signal_floor = min(signal)
	#print("\n\namplitude" + str(signal_ceil - signal_floor) + "\n\n")

	ratio = 0.25
	threshold = ((signal_ceil - signal_floor)*ratio)   + signal_floor

	signal_zero_centered = [(x - threshold) for x in signal]

	zero_crossings = np.where(np.diff(np.signbit(signal_zero_centered)))[0]
	#np.append(zero_crossings, len(signal_zero_centered))
	zero_crossings = zero_crossings.tolist()

	#determine the diff PBZ points
	diff_signal = np.gradient(signal)
	zero_crossings_diff = np.where(np.diff(np.signbit(diff_signal)))[0]
	zero_crossings_diff = zero_crossings_diff.tolist()
	#zero_crossings_diff.append(len(diff_signal))

	zcc = []
	for x in zero_crossings:
		if signal_zero_centered[x+1] > 0:
			passed = (y for y in zero_crossings_diff if y < x)
			zcc.append(int((max(passed)+x)/2))
		if signal_zero_centered[x+1] < 0:
			passed = (y for y in zero_crossings_diff if y > x)
			zcc.append(int((min(passed)+x)/2))


	#zcc = zero_crossings
	#print(zero_crossings)
	#print(type(zero_crossings))
	zero_crossings.append(len(signal_zero_centered))

	allindexes = []
	chosen_samples = []
	for a in range(len(zcc)-1):
		index = zcc[a] + round(samples_per_symbol*0.4)
		while(index < (zcc[a+1] - (samples_per_symbol*0.1))):
			allindexes.append(index)
			chosen_samples.append(signal_zero_centered[index])
			index += round(samples_per_symbol)

	if debug == True:
		signal_samples = []
		for x in range(len(allindexes)):
			signal_samples.append(signal[allindexes[x]])
		threshold_scatter = [threshold] * len(zcc)

		#pylab.subplot(2,1,1)
		plt.title('Pass By Zero - Synchro and Sampling points')
		plt.ylabel('Quantization')
		plt.xlabel('Sample Index')
		pylab.plot(signal)
		plt.axhline(y=threshold, color='k', linestyle='--')
		plt.axhline(y=0, color='k', linestyle='-')
		plt.scatter(allindexes, signal_samples, color='black')
		plt.scatter(zcc, threshold_scatter, color= 'red')

		#plt.xlim([119300, 120700])  # FRAME
		plt.xlim([119450, 119708])
		#pylab.subplot(2,1,2)
		#pylab.plot(diff_signal*20, color= 'orange')
		pylab.show()

	result = np.where(np.asarray(chosen_samples) > 0, 1, 0)

	return result
