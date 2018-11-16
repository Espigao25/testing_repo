import numpy as np
import pylab
import matplotlib.pyplot as plt

debug = False		# Set to true to plot graphs

def compare_signal(signal, samples_per_symbol):


	signal_ceil = max(signal)
	signal_floor = min(signal)
	#print("\n\namplitude" + str(signal_ceil - signal_floor) + "\n\n")

	ratio = 0.25

	threshold = ((signal_ceil - signal_floor)*ratio)   + signal_floor



	#pylab.plot(signal)


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



	zero_crossings = zcc
	#print(zero_crossings)
	#print(type(zero_crossings))
	zero_crossings.append(len(signal_zero_centered))


	allindexes = []
	chosen_samples = []
	for a in range(len(zero_crossings)-1):
		index = zero_crossings[a] + round(samples_per_symbol*0.4)
		while(index < (zero_crossings[a+1] - (samples_per_symbol*0.1))):
			allindexes.append(index)
			chosen_samples.append(signal_zero_centered[index])
			index += round(samples_per_symbol)


	if debug == True:
		signal_samples = []
		for x in range(len(allindexes)):
			signal_samples.append(signal[allindexes[x]])
		#pylab.subplot(2,1,1)
		pylab.plot(signal)
		plt.axhline(y=threshold, color='k', linestyle='-')
		plt.scatter(allindexes, signal_samples, color='orange')
		#pylab.subplot(2,1,2)
		#fft_signal = np.fft(signal)
		#pylab.plot(fft_signal)
		pylab.show()



	result = np.where(np.asarray(chosen_samples) > 0, 1, 0)

	return result
