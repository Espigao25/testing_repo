### Made by Diogo Batista (diogobatista@ua.pt) as part of my Integrated Master's thesis

#### If any issues arise, try :

	# First time setup? Issues with SDR kit compatibility? Check:  https://gist.github.com/floehopper/99a0c8931f9d779b0998

	# Issues with numpy module? On terminal: pip3 install --upgrade --ignore-installed --install-option '--install-data=/usr/local' numpy

from pylab import *   	#Graphical capabilities, network and debug outfiles
from rtlsdr import *	#SDR
from scipy import signal #Signal Filtering
import queue			#FIFO/queue
import threading		#Multi-threading
import RPi.GPIO as GPIO	#LED's
import array
import sys
import DEEP_comparator, PBZ_comparator, filterGen, parseGen, fileGen, gpioGen		#demodulating library
import time				#time deltas
import argparse			#argumment management
#import scipy.signal

########################################################################
### PARSING INPUT ARGUMENTS
########################################################################

parser = argparse.ArgumentParser(prog = 'SoundGen', description='Made by Diogo Batista, diogobatista@ua.pt', epilog=' ',)

parser.add_argument('-f','--freq', help='Center Frequency',type=int, required=True)
parser.add_argument('-s','--samp', help='Sampling rate, default is 226kHz', type=int, required=False, default = 226000)
parser.add_argument('-g','--gain', help='Gain, [0 50], default is 15', type=int,required=False, default = 15)
parser.add_argument('-sf','--sfram', help='Frame size, default is 32k', type=int, required=False, default = 320*1024)
parser.add_argument('-nf','--nfram', help='Number of frames to be collected before program ends, default is 1, must be 1 or greater', type=int, required=False, default = 1)
parser.add_argument('-it','--itnum', help='Number of iterations before program ends, default is 1, must be 1 or greater', type=int, required=False, default = 1)
parser.add_argument('-db','--dbug', help='DebugMode, default is False', required=False, type=bool, default = False)
parser.add_argument('-i','--infi', help='InfiniteMode, default is True', required=False, default = True)
parser.add_argument('-sym','--symb', help='Symbol Rate of expected ASK signal', type=int, required=True, default = 3650)
args = vars(parser.parse_args())

#args['freq'] will contain the value of arg '-f'
#args['samp'] will contain the value of optional argument '-s' if any value was passed
#etc

print(args)

########################################################################
### DECLARING VARIABLES
########################################################################


# Initialize SDR kit
sdr = RtlSdr()

# configure SDR device
sdr.sample_rate = int(args['samp'])						#These are default values, will be overriden in any case of user input, 'SoundGen -h' for help
sdr.center_freq = args['freq']
#sdr.gain = 'auto'
sdr.gain = args['gain']


global frame_size
frame_size = args['sfram']


#signal characteristics

decimation_factor = 1		 							# It might be possible to increase efficiency by decimating the signal before it gets passed along to the pdata library, paceholder for now
symbol_rate = args['symb']								# Baseband frequency of the desired signal it should be no higher than one tenth of the SDR kit sampling rate

symbol_period = 1/symbol_rate
samples_per_symbol = (sdr.sample_rate * symbol_period) / decimation_factor	# How many times each bit of information will be sampled by the SDR kit as it arrives. Lower means faster code executing speeds, higher means lower error rate. Should never be lower than 2


preamble = [1,0,1,0]									# This is the sequence of bits that the program will interpret as the start of a packet

payload_size = 8										# The information part of the packet consists of 2 hexadecimal chars, 8 bits
packet_size = len(preamble) + payload_size + 4				# Parity + 2 hexa chars + 3 CRC bits + 2 stop bits


buffer_size = 0  										# Size of the FIFO (in bits) where the samples are stored between harvesting and plotting, zero means infinite size
global sample_FIFO
sample_FIFO = queue.Queue(buffer_size)


## Flow control

global iteration_counter, stop_at, debug
iteration_counter = 0									# Counts the number of frames collected so far
stop_at = args['nfram']									# How many frames of data the program will collect and process before it ends
infinite_loop = True									# Flag that controls wether the program will leave the main loop
debug = args['dbug']									# Debug capabilities switch

## Led Setup

USE_LEDS = True
heartbeat = True

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(3, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(7, GPIO.OUT)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)


## Debugging variables

allsamples = array.array('f',[0])


########################################################################
### FUNCTIONS
########################################################################



def collectData(): 	#Collect samples

	global frame_size
	global stop_at
	frame_counter = 0
	t = time.time()
	while frame_counter < stop_at :
		samples = sdr.read_samples(frame_size)
		samples2 = abs(samples)
		sample_FIFO.put_nowait(samples2)  ## Harvests samples and stores their ABSOLUTE VALUES into a FIFO
        #print("\n###   TERMINEI A RECOLHA DE AMOSTRAS EM " + str(round(time.time() -t, 2)) + ". TEMPO IDEAL = " +str(round((frame_size*stop_at)/sdr.sample_rate, 2)) + "   ###\n")
		frame_counter += 1


def threadInit():	#Initialize threads
	global t_collector
	t_collector = threading.Thread(target=collectData, name="Collector", args=[])



if __name__ == "__main__":

	while infinite_loop == True:
		t = time.time()

		threadInit()  # Initialize the required threads.

		t_collector.start()

		end_result = []
		iteration_end = False        # At the end of the main cycle's iteration this flag turns true if the desired number of iterations has been reached
		iteration_count = 0


		while sample_FIFO.empty == True:   # Wait until there is at least 1 item in the FIFO
			pass

		while t_collector.isAlive() or sample_FIFO.empty() == False:  	# Cycle until collector thread is alive OR FIFO isn't empty


			if sample_FIFO.empty() == False: # Are there any samples in the harvesting FIFO?

				this_frame = sample_FIFO.get_nowait()

				this_frame =  filterGen.bp_butter(this_frame, [15, 3600*2], 2, sdr.sample_rate)	# Apply butterworth, 2nd order band pass filter. The filter order should be changed with care, a simulation can be run with the help of the "ZXC.py" script

				if decimation_factor > 1:
					 this_frame = signal.decimate(this_frame, decimation_factor)				# Decimate if decimation order > 1


				this_frame = this_frame[int(12500/decimation_factor):-1]							# Filtering the frame introduces artifacts in the first few samples, those samples are removed here in order to facilitate the comparator work.


				#demod_signal = DEEP_comparator.compare_signal(this_frame, samples_per_symbol) 		#Deep Demodulation
				demod_signal = PBZ_comparator.compare_signal(this_frame, samples_per_symbol)							#PBZ Demodulation

				end_result.extend(demod_signal)							# The comparator's output is concatenated to the array end_result


				if debug == True:
					allsamples.extend(this_frame)           			# Keep storing samples for later dump if demod is activated



########################################################################
### INFORMATION PARSING
########################################################################

		message_result, sucesses, flipped_sucesses, preamble_detections = parseGen.binary_parse(end_result, preamble , packet_size , payload_size)


########################################################################
### NETWORK INTEGRATION
########################################################################


		fileGen.save_payload(message_result, debug, allsamples, end_result, samples_per_symbol)


########################################################################
### RPI GPIO UPDATING
########################################################################


		temporal_window = (1/sdr.sample_rate)*frame_size
		packet_starts_t_delta = 0.0152									# Time in seconds between start of consecutive packets,

		max_sucesses = max(sucesses, flipped_sucesses)
		success_ratio = max_sucesses / (temporal_window/packet_starts_t_delta)

		if USE_LEDS == True:

			gpioGen.update(success_ratio)


########################################################################
### VERBOSE
########################################################################



		runtime = round(time.time() -t, 3)
		print("\nFINISHED   \n\nTemporal Window 	" + str(round(temporal_window, 3)) + "\nIterations: 		" +  str(iteration_counter) + "\nSamples processed: 	" + str(frame_size) + "\nPreambles detected: 	" + str(preamble_detections) + "\nSucesses: 		" + str(sucesses) + "\nFlipped Sucesses: 	" + str(flipped_sucesses) + "\nSuccess Rate: 		" +str(round(success_ratio,1)) + "\nRuntime: 		"  +  str(runtime)  + "\nPackets per second: 	"  +  str(round(max_sucesses / max(temporal_window,runtime), 2) ))

		print('Debug value is ' + str(debug))
		print('Loop value is ' + str(args['infi']))


########################################################################


		iteration_counter += 1
		if iteration_counter >= args['itnum']:
			infinite_loop = False

		infinite_loop = args['infi'] 			# -i argument takes precedente over -it argument, thus is updated later, in order to overwrite.

	sys.exit(main(sys.argv))
