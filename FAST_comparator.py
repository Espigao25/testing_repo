# This comparator was designed to work for a packet preamble of exactly [1,1,1,0], it was not tested under any other cases.

import numpy as np
import matplotlib.pyplot as plt
import time

debug = False				#Generate debugging plots

def compare_signal(signal, samples_per_bit, Packet):

	#t = time.time()

	SPB = int(samples_per_bit)
	ratio = 0.3
	max_signal = max(signal)
	min_signal = min(signal)

	#threshold =  max(max(signal), 0.006)*ratio
	threshold = (max_signal * ratio + min_signal * (1-ratio))

	index = -1
	end_result = [0] * int(len(signal)/samples_per_bit)

	packet_size_samples = int(Packet.packet_size * samples_per_bit)
	cooldown_margin = int(packet_size_samples * 1.2)
	#print(cooldown_margin)
	cooldown = -1 * packet_size_samples


	signal_zero_centered = [(x - threshold) for x in signal]
	signal_zero_centered = signal_zero_centered[0:-packet_size_samples]

	transitions = np.where(np.diff(np.signbit(signal_zero_centered)))[0]

	RPrP = []       #Relative preamble harvest positions
	RPaP = []       #Relative packet harvest positions

	y = int(samples_per_bit*0.5)
	for w in range(Packet.preamble_len):
		RPrP.append(round(w*samples_per_bit)+y)			#an in version cannot be used as the sucessive roundings will eventually cause a synchro error, hence not using variable SPB

	for w in range(Packet.packet_size):
		RPaP.append(round(w*samples_per_bit)+y)

	real_transitions = []
	#print(SPB)
	#print(RPaP)

	for x in transitions:
		#print(x-cooldown)
		if x - cooldown > cooldown_margin:
			real_transitions.append(x)
			preamble_match = []
			for i in range(len(RPrP)):
				preamble_match.append(binary_threshold(signal[x + RPrP[i]],threshold))
			if preamble_match == Packet.preamble :
				for i in range(len(RPaP)):
					position = x + RPaP[i]
					position2 = int(position/samples_per_bit)
					end_result[position2] = binary_threshold(signal[position], threshold)
				cooldown = x
				real_transitions.append(x)

	if debug == True:

		plt.plot(signal)

		POC = []  # Points of collection
		for y in real_transitions:
			for u in RPaP:
				POC.append(y+u)


		t_threshold = [threshold] * len(real_transitions)
		t2_signal = [(signal[x]) for x in POC]
		plt.axhline(y= threshold, color='k')
		plt.scatter(POC, t2_signal, color='orange')
		plt.scatter(real_transitions, t_threshold, color='black')


		plt.title('FAST Comparator', fontsize = 20)
		plt.xlabel('Sample index')
		plt.ylabel('Quantization level')



		#pylab.subplot(2,1,2)
		#fft_signal = np.fft(signal)
		#pylab.plot(fft_signal)
		plt.legend(['Signal', 'Threshold', 'Chosen samples', 'Temporal synchronization Points'], loc = 1)


		plt.show()


	#print(end_result)
	return end_result


def binary_threshold(value, threshold):
	if value>threshold:
		return 1
	else:
		return 0
