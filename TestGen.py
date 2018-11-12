from pylab import *   	#Graphical capabilities
import queue			#FIFO/queue
import threading		#Multi-threading
import time
import os
import numpy as np
import matplotlib.pyplot as plt
import time
import DEEP_comparator, PBZS_comparator, filterGen, parseGen, fileGen		#demodulating library




sample_rate = 226000
symbol_rate = 3650
samples_per_symbol = int(sample_rate/symbol_rate)


samples_between_packets = 10.8e-3 * sample_rate
frame_size = 320*1024
decimation_factor = 1

preamble = [1,0,1,0]
packet_size = 16
payload_size = 8

if __name__ == "__main__":

	samples = np.load('outfile_samples.npy')

	sample_FIFO = queue.Queue(0)


	for n in range((int(len(samples)/frame_size))):
		one_slice = samples[((n)* frame_size):((n+1)* frame_size)]
		#print('slice size: ' + str(len(one_slice)))
		sample_FIFO.put_nowait(one_slice)

	end_result = []

	while sample_FIFO.empty() == False: # Are there any samples in the harvesting FIFO?

		this_frame = sample_FIFO.get_nowait()

		this_frame =  filterGen.bp_butter(this_frame, [15, 3600], 2, sample_rate)	# Apply butterworth, 2nd order band pass filter. The filter order should be changed with care, a simulation can be run with the help of the "ZXC.py" script

		if decimation_factor > 1:
			 this_frame = signal.decimate(this_frame, decimation_factor)				# Decimate if decimation order > 1


		this_frame = this_frame[int(12500/decimation_factor):-1]							# Filtering the frame introduces artifacts in the first few samples, those samples are removed here in order to facilitate the comparator work.

		#demod_signal = PBZ_comparator.compare_signal(this_frame, samples_per_symbol)							#PBZ Demodulation
		demod_signal = PBZS_comparator.compare_signal(this_frame, samples_per_symbol, packet_size, samples_between_packets)							#PBZ Demodulation
		print('\n\n\n\n\n\n\n\n')

		end_result.extend(demod_signal)							# The comparator's output is concatenated to the array end_result
		#print(len(end_result))


	message_result, sucesses, flipped_sucesses, preamble_detections = parseGen.binary_parse(end_result, preamble , packet_size , payload_size)


print('Preambles:	' + str(preamble_detections))
print('Sucesses:	' + str(sucesses))
