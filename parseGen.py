########################################################################
### SIGNAL PARSING
########################################################################



def binary_parse(symbol_list, preamble, packet_size, payload_size):


	flipped_symbol_list = [1 - x for x in symbol_list]

	desired_result = [1,0,1,0,0,0,1,0,1,0,0,0,0,0,0,1,0]			# This is the sequence of bits that the program will interpret as a "Success", for calibration purposes only
	sucesses = 0
	flipped_sucesses = 0
	preamble_detections = 0
	message_result = []


	# CRC
	CRC_divisor = [1,0,1,0]


	# Count the number of sucesses

	#for x in range(len(symbol_list) - len(desired_result)):
	#	if symbol_list[x:x+len(desired_result)] == desired_result:
	#		sucesses += 1

	#for x in range(len(flipped_symbol_list) - len(desired_result)):
	#	if flipped_symbol_list[x:x+len(desired_result)] == desired_result:
	#		flipped_sucesses += 1



	for x in range(len(symbol_list) - len(preamble)):														# Detects preambles
		if symbol_list[x:x+len(preamble)] == preamble:
			preamble_detections += 1                                										# Counts them
			if crc_check(symbol_list[x+len(preamble):x+packet_size-1],CRC_divisor):             			# Checks for parity in the whole packet, soon to be replaced by CRC
				message_result.append(symbol_list[x+len(preamble):x+len(preamble)+payload_size])        	# If validaded adds to the output batch
				sucesses += 1

	return message_result, sucesses, flipped_sucesses, preamble_detections

def crc_check(payload_crc, binary_divisor):	#CRC validation

	#print("payload + crc = " + str(payload_crc))

	validity = [ 0 for x in range(len(binary_divisor)-1)]

	for x in range(len(payload_crc) - (len(binary_divisor)-1)):			# For an indepth explanation of this function visit the wikipedia page: Cyclic Redundancy Check
		if payload_crc[x] == 1:
			for y in range(len(binary_divisor)-1):
				payload_crc[x+y] = payload_crc[x+y] ^ binary_divisor[y]		# ^ = XOR

	#print("FINAL CRC = " + str(payload_crc[-4:-1]))
	#print("validity = " + str(validity))

	return payload_crc[-4:-1] == validity
	#return True


def parityOf(int_type): 							#Parity validation


	for bit in int_type:
		x = (x << 1) | bit

	parity = False
	while (x):
		parity = ~parity
		x = x & (x - 1)
	return(parity)
