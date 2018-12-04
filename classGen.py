import queue			#FIFO/queue
import simGen           #The ability to simulate a signal
#import rtlsdr			#SDR
import time				# measuring the harvest duration

class Signal:

	allsamples = []

	demod_signal = []

	def __init__(self, generate, carrier_freq, sample_rate, filter_cutoffs, filter_order, software_gain, frame_size, FIFO_size, symbol_rate, silence_time, decimation_factor, simulator_mode):
		self.simulator_mode = simulator_mode


		self.use_simulator =  generate
		self.carrier_freq = carrier_freq
		self.sample_rate = sample_rate
		self.filter_cutoffs = filter_cutoffs
		self.filter_order = filter_order
		self.frame_size = frame_size
		self.symbol_rate = symbol_rate
		self.symbol_period = 1/self.symbol_rate
		self.silence_time = silence_time
		self.silence_samples = int(silence_time * sample_rate)
		self.decimation_factor = decimation_factor
		self.FIFO_size = FIFO_size
		self.samples_per_symbol = (self.sample_rate / self.symbol_rate) / self.decimation_factor        # How many times each bit of information will be sampled by the SDR kit as it arrives. Lower means faster code executing speeds, higher means lower error rate. Should never be lower than 2

		self.harvest_delta = 0 						# variable init, time it takes to harvest the signal

		self.SDR_RECT = queue.Queue(self.FIFO_size)                                          # size 50 FIFO to store the samples between harvesting and comparating
		self.RECT_FILT = queue.Queue(self.FIFO_size)
		self.FILT_DECI = queue.Queue(self.FIFO_size)
		self.DECI_COMP = queue.Queue(self.FIFO_size)
		self.COMP_PARS = queue.Queue(self.FIFO_size)

		#self.SDR = rtlsdr.RtlSdr()
		#self.SDR.sample_rate = self.sample_rate						#These are default values, will be overriden in any case of user input, 'SoundGen -h' for help
		#self.SDR.center_freq = self.carrier_freq
		#self.SDR.gain = software_gain



	def collect_data(self, Packet):

		if self.use_simulator:

			while self.FIFO_size > self.SDR_RECT.qsize():
				q = time.time()
				samples = simGen.genr_samples(self, Packet)
				self.SDR_RECT.put(samples, True, 0.1)  								## Harvests samples and stores their ABSOLUTE VALUES into a FIFO
				#print(self.SDR_RECT.qsize())
				self.harvest_delta = time.time() - q
				q = 0

		else:

			while self.FIFO_size > self.SDR_RECT.qsize():
				q = time.time()
				#samples = self.SDR.read_samples(self.frame_size)
				self.SDR_RECT.put(samples, True, 0.1) 									 ## Harvests samples and stores their ABSOLUTE VALUES into a FIFO
				#print(self.SDR_RECT.qsize())
				self.harvest_delta = time.time() - q
				q = 0





class Packet:
    def __init__(self, preamble, payload_size, CRC_divisor, STOP_bits):
        self.preamble = preamble#[1,0,1,0]
        self.preamble_len = len(self.preamble)
        self.payload_size =  payload_size#8
        self.CRC_divisor = CRC_divisor#[1,0,1,0]
        self.CRC_len = len(self.CRC_divisor) -1
        self.STOP_bits = STOP_bits
        self.STOP_len = len(self.STOP_bits)
        self.packet_size = self.preamble_len + self.payload_size + self.CRC_len + self.STOP_len
