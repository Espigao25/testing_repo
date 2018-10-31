### Made by Diogo Batista (diogobatista@ua.pt) as part of my Integrated Master's thesis

#### If any issues arise, try :

	# First time setup? Issues with SDR kit compatibility? Check:  https://gist.github.com/floehopper/99a0c8931f9d779b0998

	# Issues with numpy module? On terminal: pip3 install --upgrade --ignore-installed --install-option '--install-data=/usr/local' numpy

from pylab import *   	#Graphical capabilities, network and debug outfiles
import queue			#FIFO/queue
import datetime			#timestamps for the outfiles
import os				#file management
import array
import sys
import pdata, PBZ_comparator			#comparator libraries
import time				#timestamps
import argparse			#argumment management
#import scipy.signal


########################################################################
### FUNCTIONS
########################################################################


def parityOf(int_type): # Check parity

	x = 0
	for bit in int_type:
		x = (x << 1) | bit

	parity = False
	while (x):
		parity = ~parity
		x = x & (x - 1)
	return(parity)


if __name__ == "__main__":


	end_result = []
	iteration_end = False        # At the end of the main cycle's iteration this flag turns true if the desired number of iterations has been reached
	iteration_count = 0

	sample_FIFO = queue.Queue(0)
	data = np.load("testing_samples.npy")
	framesize = 29767


	for x in range(20):
		slice = data[(x*framesize):((x+1)*framesize)-1]
		sample_FIFO.put_nowait(slice)

	while sample_FIFO.empty() == False: # Are there any samples in the harvesting FIFO?

		this_frame = sample_FIFO.get_nowait()
		demod_signal = pdata.process_data(this_frame, 226000/3600, len(this_frame)) 	# Demodulation
		#demod_signal = PBZ_comparator.compare_signal(this_frame, 226000/3600)
		end_result.extend(demod_signal)												# O resultado obtido da desmodulação é anexado ao fim do array end_result

	flipped_endresult = [1 - x for x in end_result]

########################################################################
### INFORMATION PARSING
########################################################################

	sucesses = 0
	flipped_sucesses = 0
	preamble_detections = 0
	message_result = []
	desired_result = [1,0,1,0,0,0,1,0,0,0,1,0,1,1]			# This is the sequence of bits that the program will interpret as a "Success"
	preamble = [1,0,1,0]									# This is the sequence of bits that the program will interpret as the start of a packet

	info_size = 8											# The information part of the packet consists of 2 hexadecimal chars, 8 bits
	packet_size = len(preamble) + info_size + 2				# Parity + 2 hexa chars + parity bit + stop bit



	# Count the number of sucesses

	for x in range(len(end_result) - len(desired_result)):
		if end_result[x:x+len(desired_result)] == desired_result:
			sucesses += 1

	for x in range(len(flipped_endresult) - len(desired_result)):
		if flipped_endresult[x:x+len(desired_result)] == desired_result:
			flipped_sucesses += 1

	for x in range(len(end_result) - len(preamble)):				# Detects preambles
		if end_result[x:x+len(preamble)] == preamble:
			preamble_detections += 1                                # Counts them
			if parityOf(end_result[x:x+packet_size-1]):             # Checks for parity in the whole packet
				message_result.append(end_result[x+len(preamble):x+len(preamble)+info_size])        #if validaded adds to the output batch



	print("\n\n")
	print(end_result)


	print("\nFINISHED   \n\n  \nFrame: 			" + str(desired_result) + "\nPreamble: 		" + str(preamble) + "\nSucesses: 		" + str(sucesses) + "\nFlipped Sucesses: 	" + str(flipped_sucesses) + "" )

	sys.exit()
