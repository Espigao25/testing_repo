import numpy as np
import pylab
import matplotlib.pyplot as plt
from astropy.io import ascii

debug0 = False		# See the raw signal
debug = False		# Set to true to plot graphs
debug1 = True		# Set to true to plot graphs
debug2 = False		# Good and bad examples
debug3 = True		# deltas heatmap


step1 = True
step2 = True


def compare_signal(signal, samples_per_symbol, packet_size, samples_between_packets):

	#signal = signal[50000:-1]
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
			zcc.append(int(max(passed)))
			#zcc.append(int((max(passed)+x)/2))
		if signal_zero_centered[x+1] < 0:
			passed = (y for y in zero_crossings_diff if y > x)
			zcc.append(int(min(passed)))
			#zcc.append(int((min(passed)+x)/2))

	#zcc = zero_crossings
	print("zero_crossings:			" + str(len(zcc)))



	if debug0 == True:
		plt.plot(signal)
		plt.axhline(y=threshold, color='k', linestyle='-')
		threshold_scatter = [threshold] * len(zcc)
		plt.scatter(zcc, threshold_scatter, color= 'red')
		plt.title('Raw Signal')
		plt.ylabel('Quantization')
		plt.xlabel('Sample Index')
		plt.show()

	##################	##################	##################	##################	##################	##################
	##Ensinar a distinção aqui   STEP 1 BEGINS
	##################	##################	##################	##################	##################	##################




	correct_point = 99492			#HALF TRANSITION
	wrong_point = 67004

	#correct_point = 133584			#HALF TRANSITION
	#wrong_point = 66930

	correct_index = zcc.index(correct_point)
	wrong_index = zcc.index(wrong_point)


	if(step1 == True or step2 == True):

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

		heatmap = [[[ 0 for y in mh] for x in ml] for z in range(len(zcc))]
		heatmap_total = [[ 0 for y in mh] for x in ml]
		data = ascii.write(key, format = 'fixed_width_no_header', delimiter = '||')

	##################	##################	##################	##################	##################	##################
	# STEP 1 BEGINS
	##################	##################	##################	##################	##################	##################


	if step1 == True:

		surveil_range= 5
		cutoff = surveil_range * B + (A*packet_size)
		resolution = 128
		margin = int(cutoff/(resolution*2)*4)
		print('margin = ' + str(margin))
		number_of_bins = surveil_range * resolution
		all_bins = np.linspace(-cutoff, cutoff, number_of_bins)

		all_differences = []
		correct_point_differences = []
		wrong_point_differences = []
		for x in zcc:
			for y in zcc:
				if abs(x-y) < cutoff:
					all_differences.append(y-x)
			delta_correct = abs(zcc[correct_index]-x)
			delta_wrong = abs(zcc[wrong_index]-x)
			if delta_correct < cutoff:
				correct_point_differences.append(zcc[correct_index]-x)
			if delta_wrong < cutoff:
				wrong_point_differences.append(zcc[wrong_index]-x)



		p = np.digitize(all_differences, all_bins)
		all_binned = [0 for x in range(number_of_bins)]
		for w in range(len(p)):
			all_binned[p[w]] +=1


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
					if abs(z-temp) < margin:
						trust[x] += 1

		compensation_range = packet_size*surveil_range
		for x in range(len(trust[0:packet_size*surveil_range])):
			trust[x] = int( trust[x] / min(1, ((compensation_range+x)/(compensation_range))))


		zcc2 = [x for x in zcc]
		trust2 = [x for x in trust]
		trust3 = [n/max(trust)*max(signal) for n in trust]
		count = len(trust2) -1
		maximum = max(trust2)
		cutoff_ratio = 0.25
		cutoff_line = maximum * cutoff_ratio
		while count > 0:
			if trust2[count] < cutoff_line:
				trust2.pop(count)
				zcc2.pop(count)
			count -= 1



		if debug3 == True:


			all_differences= [i for i in all_differences if i != 0]
			z_all_differences = np.hstack(all_differences).tolist()
			z_correct_point_differences = np.hstack(correct_point_differences).tolist()
			z_wrong_point_differences = np.hstack(wrong_point_differences).tolist()


			plt.subplot(311)
			plt.hist(z_all_differences, bins=all_bins) 				 	# arguments are passed to np.histogram
			for w in peaks:
				center = (w - int(cutoff/number_of_bins))
				plt.axvline(x=center, color='k', linestyle='-')
			plt.title('Histogram of all deltas of all points')
			plt.subplot(312)
			plt.title('All deltas of a correct transition')
			plt.ylim([0, 1])
			plt.hist(z_correct_point_differences, bins=all_bins) 	 	# arguments are passed to np.histogram
			for w in peaks:
				center = (w - int(cutoff/number_of_bins))
				plt.axvspan(center-margin, center+margin, color='red', alpha=0.5)
			plt.subplot(313)
			plt.title('All deltas of a wrong transition')
			plt.ylim([0, 1])
			plt.hist(z_wrong_point_differences, bins=all_bins)		  	# arguments are passed to np.histogram
			for w in peaks:
				center = (w - int(cutoff/number_of_bins))
				plt.axvspan(center-margin, center+margin, color='red', alpha=0.5)

			plt.show()

	print('\n\n\n\n\n')


	##################	##################	##################	##################	##################	##################
	# STEP 1 ENDS
	# STEP 2 BEGINS
	##################	##################	##################	##################	##################	##################

	if step2 == True:

		allmargins = []
		error_margin = 5
		aux = range(error_margin*2+1)
		possible_errors = [x-error_margin for x in aux]
		#print(possible_errors)

		for x in range(len(zcc2)):
			#print(x)
			c1 = 0
			c2 = len(zcc2)-1
			while (zcc2[c1] < zcc2[x] + key[0][0]):
				c1 += 1
			while (zcc2[c2] > zcc2[x] + key[-1][-1]):
				c2 -= 1

			passed = zcc2[c1:c2]
			#passed = (y for y in zcc if (abs(y - zcc[x] < key[-1][-1]+error_margin)))
			#print(passed)
			for a in ml:
				for b in mh:
					#print(delta)
					sum = zcc2[x] + key[a][b]
					for h in possible_errors:
						if sum+h in passed:
							heatmap[x][a][b] = 1

			heatmap[x][packet_fade][(packet_size-1)] = 'X'

			hitsum2 = [0 for x in range(len(zcc2))]
			for z in range(len(zcc2)):
				heatmap_buffer = [[ heatmap[z][x][y] for y in mh] for x in ml]
				for a in ml:
					for b in mh:
						if type(heatmap_buffer[a][b]) == int :
							heatmap_total[a][b] += heatmap_buffer[a][b]
							hitsum2[z] += heatmap_buffer[a][b]

		hitsum = [(u/max(hitsum2))*max(signal) for u in hitsum2]

	##################	##################	##################	##################	##################	##################

	allindexes = []
	chosen_samples = []
	for a in range(len(zcc2)-1):
		index = int(zcc2[a] + round(samples_per_symbol*0.45))
		while(index < (zcc2[a+1] - (samples_per_symbol*0.1))):
			allindexes.append(index)
			chosen_samples.append(signal_zero_centered[index])
			index += round(samples_per_symbol)

	##################	##################	##################	##################	##################	##################


	if debug1 == True:
		signal_samples = []
		for x in range(len(allindexes)):
			signal_samples.append(signal[allindexes[x]])
		#pylab.subplot(211)

		#plt.scatter(zcc2, hitsum , color='red')
		#plt.scatter(zcc, trust3 , color='red')
		#plt.plot(signal)
		#plt.title('Trust levels of transitions')

		#for x in range(len(zcc)):
			#line = zcc[x] + 7790
		#plt.axvline(x=105797, color='red', linestyle='-')


		#pylab.plot(diff_signal1)											# signal'

		#plt.axhline(y=threshold, color='k', linestyle='-')
		#plt.axhline(y=0, color='k', linestyle='-')
		#plt.scatter(allindexes, signal_samples, color='orange')			# AMOSTRAS COLHIDAS
		#threshold_scatter = [threshold] * len(zcc2)
		#threshold_scatter_diff = [threshold] * len(zero_crossings_diff)
		#plt.scatter(zero_crossings_diff, threshold_scatter_diff , color='black')


		#plt.subplot(212)
		threshold_scatter = [threshold] * len(zcc2)
		plt.scatter(zcc2, hitsum, color='red')
		plt.plot(signal)
		plt.title('Transition pattern search')
		for y in matrix_height:
			for x in matrix_length:
				plt.axvline(x=correct_point, color='red', linestyle='-')
				plt.axvline(x=key[x][y]+correct_point+error_margin, color='green', linestyle='--')
				plt.axvline(x=key[x][y]+correct_point-error_margin, color='green', linestyle='--')
		#plt.ylim([0, 100])

		#ax = plt.gca()
		#ax.yaxis.grid(True)
		#fft_signal = np.fft(signal)
		#pylab.plot(fft_signal)

		#plt.subplot(313)
		#plt.scatter(zcc2, hitsum)
		#ax = plt.gca()
		#ax.yaxis.grid(True)

		pylab.show()


	result = np.where(np.asarray(chosen_samples) > 0, 1, 0)

	return result
