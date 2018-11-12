import numpy as np
import pylab
import matplotlib.pyplot as plt
from astropy.io import ascii


debug = False		# Set to true to plot graphs
debug1 = False		# Set to true to plot graphs

def compare_signal(signal, samples_per_symbol, packet_size, samples_between_packets):

	print("samples_per_symbol:		" + str(samples_per_symbol))
	print("samples_between_packets:	" + str(samples_between_packets))


	diff_signal = np.gradient(signal)
	diff_signal1 = [x * 10 for x in diff_signal]

	signal_ceil = max(signal)
	signal_floor = min(signal)
	#print("\n\namplitude" + str(signal_ceil - signal_floor) + "\n\n")

	ratio = 0.20

	threshold = ((signal_ceil - signal_floor)*ratio)   + signal_floor

	#pylab.plot(signal)

	signal_zero_centered = [(x - threshold) for x in signal]


	#deterimine the PBZ points
	zero_crossings = np.where(np.diff(np.signbit(signal_zero_centered)))[0]
	zero_crossings = zero_crossings.tolist()
	#zero_crossings.append(len(signal_zero_centered))

	#determine the diff PBZ points

	zero_crossings_diff = np.where(np.diff(np.signbit(diff_signal)))[0]
	zero_crossings_diff = zero_crossings_diff.tolist()
	#zero_crossings_diff.append(len(diff_signal))

	zero_crossings_corrected = []
	for x in zero_crossings:
		if signal_zero_centered[x+1] > 0:
			passed = (y for y in zero_crossings_diff if y < x)
			zero_crossings_corrected.append((max(passed)+x)/2)
		if signal_zero_centered[x+1] < 0:
			passed = (y for y in zero_crossings_diff if y > x)
			zero_crossings_corrected.append((min(passed)+x)/2)


	##################	##################	##################	##################	##################	##################
	##Ensinar a distinção aqui
	##################	##################	##################	##################	##################	##################

	packet_fade = 4

	A = samples_per_symbol													#number of samples expected in a symbol
	B = samples_per_symbol * packet_size + samples_between_packets	 	#number of samples expected between equivalent points in consecutive packets

	mh = range(packet_size)
	matrix_height = [x-packet_size+1 for x in mh]


	ml = range(packet_fade)
	matrix_length = [x-packet_fade+1 for x in ml]


	#criar a matriz de diferenças

	# The x travels in bit distance, the y travels in packet distance
	key = [[ int((-y*B) + (-x*A)) for x in matrix_height] for y in matrix_length]
	heatmap = [[[ 0 for x in matrix_height] for y in matrix_length] for z in range(len(zero_crossings_corrected))]
	data = ascii.write(key, format = 'fixed_width_no_header', delimiter = '||')


	for x in range(len(zero_crossings_corrected)):
		for y in range(len(zero_crossings_corrected[1:x])):
			if abs(zero_crossings_corrected[y]-zero_crossings_corrected[x]) < key[0][0]:
				delta = abs(zero_crossings_corrected[y] - zero_crossings_corrected[x])
				result = delta
				#final_a = 0
				#final_b = 0
				for a in mh:
					for b in ml:
						point = key[b][a]
						difference = abs(delta-point)
						if difference <= 3:
							heatmap[b][a][x] += 1
							#result = difference
							#final_a = a
							#final_b = b
				#heatmap[final_b][final_a] += 1


	print('\n\n\n\n\n')
	data = ascii.write(heatmap, format = 'fixed_width_no_header', delimiter = '|')

	if debug == True:
		for x in mh:
			for y in ml:
				line = key[y][x]
				plt.axvline(x=line, color='k', linestyle='-')


		pylab.show()
	##################	##################	##################	##################	##################	##################

	allindexes = []
	chosen_samples = []
	for a in range(len(zero_crossings_corrected)-1):
		index = int(zero_crossings_corrected[a] + round(samples_per_symbol*0.45))
		while(index < (zero_crossings_corrected[a+1] - (samples_per_symbol*0.1))):
			allindexes.append(index)
			chosen_samples.append(signal_zero_centered[index])
			index += round(samples_per_symbol)


	if debug1 == True:
		signal_samples = []
		for x in range(len(allindexes)):
			signal_samples.append(signal[allindexes[x]])
		pylab.subplot(2,1,1)
		pylab.plot(signal)

		#pylab.plot(diff_signal1)

		plt.axhline(y=threshold, color='k', linestyle='-')
		plt.axhline(y=0, color='k', linestyle='-')
		plt.scatter(allindexes, signal_samples, color='orange')
		threshold_scatter = [threshold] * len(zero_crossings)
		threshold_scatter_diff = [threshold] * len(zero_crossings_diff)
		#plt.scatter(zero_crossings_diff, threshold_scatter_diff , color='black')
		plt.scatter(zero_crossings_corrected, threshold_scatter , color='red')

		#fft_signal = np.fft(signal)
		#pylab.plot(fft_signal)
		pylab.subplot(2,1,2)
		z2 = zero_crossings_corrected[2:-1]
		z3 = zero_crossings_corrected[1:-2]

		differences = np.subtract(z2,z3)
		z4 = np.hstack(differences)
		plt.hist(z4, bins=min(max(differences), 3000))  # arguments are passed to np.histogram
		plt.title('Difference in samples between consecutive transitions')

		pylab.show()



	result = np.where(np.asarray(chosen_samples) > 0, 1, 0)

	return result
