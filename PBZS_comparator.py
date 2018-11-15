import numpy as np
import pylab
import matplotlib.pyplot as plt
from astropy.io import ascii


debug = False		# Set to true to plot graphs
debug1 = False		# Set to true to plot graphs
debug2 = False		# Good and bad examples
debug3 = True		#deltas heatmap

def compare_signal(signal, samples_per_symbol, packet_size, samples_between_packets):

	signal = signal[50000:-1]
	print("samples:					" + str(len(signal)))
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


	#determine the PBZ points
	zero_crossings = np.where(np.diff(np.signbit(signal_zero_centered)))[0]
	zero_crossings = zero_crossings.tolist()
	#zero_crossings.append(len(signal_zero_centered))

	#determine the diff PBZ points

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
	print("zero_crossings:			" + str(len(zcc)))
	##################	##################	##################	##################	##################	##################
	##Ensinar a distinção aqui
	##################	##################	##################	##################	##################	##################
	correct_point = 168954
	wrong_point = 109381#105797

	correct_index = zcc.index(correct_point)
	wrong_index = zcc.index(wrong_point)



	packet_fade = 0

	A = samples_per_symbol													#number of samples expected in a symbol
	B = samples_per_symbol * packet_size + samples_between_packets	 	#number of samples expected between equivalent points in consecutive packets

	mh = range((packet_size-1)*2+1)
	matrix_height = [x-packet_size+1 for x in mh]


	ml = range(packet_fade*2+1)
	matrix_length = [x-packet_fade for x in ml]


	#criar a matriz de diferenças

	# The x travels in bit distance, the y travels in packet distance
	key = [[ int((x*B) + (y*A)) for y in matrix_height] for x in matrix_length]
	#print(key)
	heatmap = [[[ 0 for y in mh] for x in ml] for z in range(len(zcc))]
	heatmap_total = [[ 0 for y in mh] for x in ml]
	data = ascii.write(key, format = 'fixed_width_no_header', delimiter = '||')

	#for a in ml:
	#	for b in mh:
	#		print(key[a][b])


	surveil_range= 5
	cutoff = surveil_range * B + (A*packet_size)
	resolution = 128
	margin = int(cutoff/(resolution*2)*4)
	print('margin = ' + str(margin))
	number_of_bins = surveil_range * resolution
	all_bins = np.linspace(-cutoff, cutoff, number_of_bins)



	if debug3 == True:

		correct_point_differences = []
		wrong_point_differences = []
		all_differences = []
		for x in zcc:

			delta_correct = abs(zcc[correct_index]-x)
			delta_wrong = abs(zcc[wrong_index]-x)
			if delta_correct < cutoff:
				correct_point_differences.append(zcc[correct_index]-x)
			if delta_wrong < cutoff:
				wrong_point_differences.append(zcc[wrong_index]-x)
			for y in zcc:
				if abs(x-y) < cutoff:
					all_differences.append(y-x)



		p = np.digitize(all_differences, all_bins)
		all_binned = [0 for x in range(number_of_bins)]
		for w in range(len(p)):
			all_binned[p[w]] +=1

		correct_binned = np.digitize(correct_point_differences, all_bins)
		wrong_binned = np.digitize(wrong_point_differences, all_bins)

		count = 0
		v_lines = []

		local_maxima_index = (np.diff(np.sign(np.diff(all_binned))) < 0).nonzero()[0] + 1 # local max

		topN = [all_binned[w] for w in local_maxima_index] 	#	[VALUE OF LOCAL MAX, INDEX OF LOCAL MAX]
		topN_index = [w for w in local_maxima_index]		# has to be done this way to convert nparray to list

		#print(topN)

		while len(topN)>surveil_range*2+1:
			minimum = topN.index((min(topN)))
			topN.pop(minimum)
			topN_index.pop(minimum)



		peaks = [all_bins[w] for w in topN_index]
		peaks_nz = peaks
		peaks_nz.pop(int(len(peaks_nz)/2))  # same as peaks but without the indice that corresponds to the zero

		trust = [0 for x in zcc]
		for x in range(len(zcc)):
			for y in peaks_nz:
				temp = zcc[x] + y
				for z in zcc:
					if abs(z-temp) < 100:
						trust[x] += 1

		plt.scatter(zcc, trust)

		#trust2 = np.hstack(trust).tolist()
		#lt.hist(trust2, bins=20)
		plt.show()

		#print(local_maxima_index)
		#print(*all_bins, sep='\n')
		#print(*local_maxima, sep='\n')
		#print(*local_maxima, sep='\n')

		all_differences= [i for i in all_differences if i != 0]
		z_all_differences = np.hstack(all_differences).tolist()
		z_correct_point_differences = np.hstack(correct_point_differences).tolist()
		z_wrong_point_differences = np.hstack(wrong_point_differences).tolist()


		plt.subplot(311)
		plt.hist(z_all_differences, bins=all_bins)#max(all_differences))  # arguments are passed to np.histogram
		for w in peaks:
			center = (w - int(cutoff/number_of_bins))
			plt.axvline(x=center, color='k', linestyle='-')
		plt.title('Sum of all deltas of all points')
		plt.subplot(312)
		plt.title('All deltas of a correct transition')
		plt.hist(z_correct_point_differences, bins=all_bins)#max(all_differences))  # arguments are passed to np.histogram
		for w in peaks:
			center = (w - int(cutoff/number_of_bins))
			plt.axvspan(center-margin, center+margin, color='red', alpha=0.5)
		plt.subplot(313)
		plt.title('All deltas of a wrong transition')
		plt.hist(z_wrong_point_differences, bins=all_bins)#max(all_differences))  # arguments are passed to np.histogram
		for w in peaks:
			center = (w - int(cutoff/number_of_bins))
			plt.axvspan(center-margin, center+margin, color='red', alpha=0.5)
		#for y in matrix_height:
			#for x in matrix_length:
				#plt.axvline(x=key[x][y], color='k', linestyle='-')
		plt.show()





	allmargins = []
	error_margin = 7
	aux = range(error_margin*2+1)
	possible_errors = [x-error_margin for x in aux]
	#print(possible_errors)
	for x in range(len(zcc)):
		#print(x)
		c1 = 0
		c2 = len(zcc)-1
		while (zcc[c1] < zcc[x] + key[0][0]):
			c1 += 1
		while (zcc[c2] > zcc[x] + key[-1][-1]):
			c2 -= 1

		passed = zcc[c1:c2]
		#passed = (y for y in zcc if (abs(y - zcc[x] < key[-1][-1]+error_margin)))
		#print(passed)
		for a in ml:
			for b in mh:
				#print(delta)
				sum = zcc[x] + key[a][b]
				for h in possible_errors:
					if sum+h in passed:
						heatmap[x][a][b] = 1

		heatmap[x][packet_fade][(packet_size-1)] = 'X'


	print('\n\n\n\n\n')

	#plt.plot(allmargins)
	#plt.axhline(y=0, color='k', linestyle='--')
	#plt.show()
	hitsum2 = [0 for x in range(len(zcc))]
	for z in range(len(zcc)):
		heatmap_buffer = [[ heatmap[z][x][y] for y in mh] for x in ml]
		for a in ml:
			for b in mh:
				if type(heatmap_buffer[a][b]) == int :
					heatmap_total[a][b] += heatmap_buffer[a][b]
					hitsum2[z] += heatmap_buffer[a][b]


	#print(max(hitsum2))
	hitsum = [(u/max(hitsum2)) * 0.01 for u in hitsum2]
	#hitsum1 = [hitsum2] / max(hitsum2)
	#hitsum = [hitsum1] / max(signal)
	#for a in mh:
		#for b in ml:
			#heatmap_total[b][a] *= 100
			#heatmap_total[b][a] = round(heatmap_total[b][a]/len(zcc),1)


	data = ascii.write(heatmap_total, format = 'fixed_width_no_header', delimiter = '|')

	if debug2 == True:

		print('\n\nHeatmap of transition ' + str(correct_index) +' which is correct\n')
		heatmap_correct = [[ heatmap[correct_index][x][y] for y in mh] for x in ml]
		data = ascii.write(heatmap_correct, format = 'fixed_width_no_header', delimiter = '|')


		print('\n\nHeatmap of transition ' + str(wrong_index) +' which is wrong\n')
		heatmap_error = [[ heatmap[wrong_index][x][y] for y in mh] for x in ml]
		data = ascii.write(heatmap_error, format = 'fixed_width_no_header', delimiter = '|')
		#, col_starts=(0, 16, 31, 46), col_ends=(15, 30, 45, 60))

	if debug == True:
		for y in mh:
			for x in ml:
				line = key[x][y] + 4015
				plt.axvline(x=line, color='k', linestyle='-')


		pylab.show()
	##################	##################	##################	##################	##################	##################

	allindexes = []
	chosen_samples = []
	for a in range(len(zcc)-1):
		index = int(zcc[a] + round(samples_per_symbol*0.45))
		while(index < (zcc[a+1] - (samples_per_symbol*0.1))):
			allindexes.append(index)
			chosen_samples.append(signal_zero_centered[index])
			index += round(samples_per_symbol)


	if debug1 == True:
		signal_samples = []
		for x in range(len(allindexes)):
			signal_samples.append(signal[allindexes[x]])
		#pylab.subplot(2,1,1)
		plt.plot(signal)
		plt.scatter(zcc,hitsum)
		#for x in range(len(zcc)):
			#line = zcc[x] + 7790
		plt.axvline(x=105797, color='red', linestyle='-')
		for y in matrix_height:
			for x in matrix_length:
				plt.axvline(x=key[x][y]+105797+error_margin, color='green', linestyle='-')
				plt.axvline(x=key[x][y]+105797-error_margin, color='green', linestyle='-')

		#pylab.plot(diff_signal1)

		plt.axhline(y=threshold, color='k', linestyle='-')
		plt.axhline(y=0, color='k', linestyle='-')
		#plt.scatter(allindexes, signal_samples, color='orange')			# AMOSTRAS COLHIDAS
		threshold_scatter = [threshold] * len(zero_crossings)
		threshold_scatter_diff = [threshold] * len(zero_crossings_diff)
		#plt.scatter(zero_crossings_diff, threshold_scatter_diff , color='black')
		plt.scatter(zcc, threshold_scatter , color='red')

		#fft_signal = np.fft(signal)
		#pylab.plot(fft_signal)
		#pylab.subplot(2,1,2)
		#z2 = zcc[2:-1]
		#z3 = zcc[1:-2]

		#differences = np.subtract(z2,z3)
		#z4 = np.hstack(differences)
		#plt.hist(z4, bins=min(max(differences), 3000))  # arguments are passed to np.histogram
		#plt.title('Difference in samples between consecutive transitions')

		pylab.show()



	result = np.where(np.asarray(chosen_samples) > 0, 1, 0)

	return result
