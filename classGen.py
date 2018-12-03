import queue			#FIFO/queue
import simGen           #The ability to simulate a signal
import rtlsdr			#SDR
import time				# measuring the harvest duration

class Signal:

	demod_signal = []

	def __init__(self,carrier_freq, sample_rate, software_gain, frame_size, frames_per_iteration, symbol_rate, silence_time, decimation_factor, simulator_mode):
		self.simulator_mode = simulator_mode

		self.carrier_freq = carrier_freq
		self.sample_rate = sample_rate
		self.frame_size = frame_size
		self.symbol_rate = symbol_rate
		self.symbol_period = 1/self.symbol_rate
		self.silence_time = silence_time
		self.silence_samples = int(silence_time * sample_rate)
		self.decimation_factor = decimation_factor
		self.frames_per_iteration = frames_per_iteration
		self.samples_per_symbol = (self.sample_rate / self.symbol_rate) / self.decimation_factor        # How many times each bit of information will be sampled by the SDR kit as it arrives. Lower means faster code executing speeds, higher means lower error rate. Should never be lower than 2
		self.samples_FIFO = queue.Queue(50)                                          # size 50 FIFO to store the samples between harvesting and comparating

		self.SDR = rtlsdr.RtlSdr()
		self.SDR.sample_rate = self.sample_rate						#These are default values, will be overriden in any case of user input, 'SoundGen -h' for help
		self.SDR.center_freq = self.carrier_freq
		self.SDR.gain = software_gain



	def collect_data(self):
		q = time.time()
		frame_counter = 0
		while frame_counter < self.frames_per_iteration :
			samples = abs(self.SDR.read_samples(self.frame_size))
			self.samples_FIFO.put_nowait(samples)  ## Harvests samples and stores their ABSOLUTE VALUES into a FIFO
			frame_counter += 1

		self.harvest_delta = time.time() - q

	def generate_data(self, Packet):

		frame_counter = 0
		while frame_counter < self.frames_per_iteration :
			samples = simGen.genr_samples(self, Packet)
			self.samples_FIFO.put_nowait(samples)  ## Harvests samples and stores their ABSOLUTE VALUES into a FIFO
			frame_counter += 1





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