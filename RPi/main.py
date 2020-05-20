#!/usr/bin/env python

import time
import struct
import cmd
from RF24 import *
import RFAccel
import RPi.GPIO as GPIO

millis = lambda: int(round(time.time() * 1000))

class RFAccelShell(cmd.Cmd): 

	intro = "rfaccel 0.1 shell.   Type help or ? to list commands.\n"
	prompt = "(rfaccel)"
	radio = None
	connected = False
	remotes = []
	remote_device = None

	retries = 15
	retry_delay = 5

	enumerate_timeout = 1000
	connect_timeout = 100

	pipe_in = None
	pipe_out = None

	def do_init(self, arg):
		'Initialize rfaccel'
		if (self.init()):
			print("Succesfully initialized NRF24L01+")
		else:
			print("Already initialized.")

	def do_info(self, arg):
		'Print radio details'
		if (self.radio):
			self.radio.printDetails()
		else:
			print("Not yet initialized.")

	def do_enumerate(self, arg):
		'Get available devices'
		if(self.radio):
			if (not self.connected):
				self.enumerate()			
			else:
				print("Still in connection.")
		else:
			print("Not yet initialized.")
			
	def do_connect(self, arg):
		'Connect to remote device'
		if (self.radio):
			if(arg == ''):
				if(len(self.remotes) == 0):
					print("No devices enumerated.")
					return
				elif (len(self.remotes) == 1):
					d_id = self.remotes.keys()[0]			
				else:
					print("Please specify a device to connect to.")
					return
			else:
				d_id = int(arg, 0)

			if (not self.connected):
				if (d_id in self.remotes):
					if (self.connect(d_id)):
						print("Connected succesfully.")
					else:
						print("Could not connect.")
				else:
					print("Such a device was not enumerated.")
			else:
				print("Still in connection.")
		else:
			print("Not yet initialized.")

	def complete_connect(self, text, line, begidx, idx):
		'Yields list of enumerated ID'
		possible_ids = []
		for c_id in self.remotes.keys():
			if(hex(c_id).startswith(text)):
				possible_ids.append(hex(c_id))
		return possible_ids

	def do_calibrate(self, arg):
		'Calibrate the stationary remote device'
		pass

	def do_get(self, arg):
		'Get remote data'
		if (self.radio):
			if (self.connected):

				options = arg.split()

				if(len(options) != 1 and len(options) != 3):
					print("Wrong argument count.")
					print("count and delay are optional, but you have to specify the data type.")
					return

				datatype = options[0]

				get_accel	= 'a' in datatype
				get_gyro	= 'g' in datatype
				get_magnet	= 'm' in datatype

				if ((not get_accel) and (not get_gyro) and (not get_magnet)):
					print("No data type requested.")
					return

				if (len(options) == 3):
					count = int(options[1])
					delay = int(options[2]) # in ms
				else:
					count = 1
					delay = 0

				for i in range(count):

					data = self.get(get_accel, get_gyro, get_magnet)

					print("#{}: {}".format(i, data))

					time.sleep(delay / 1000) #in ms

			else:
				print("Not in a connection.")
		else:
			print("Not yet initialized.")


	def do_exit(self, arg):
		'Exits the shell'
		print("Closing rfaccel")
		self.close()
		return True;

	def close(self):
		pass

	def init(self):
		if(self.radio == None):
		 	#Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 8Mhz
			self.radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

			#if(not self.radio.isChipConnected()): #Does not work due do bad pyRF24 maintenance
			#	return False;

			self.radio.begin()
			self.radio.setAutoAck(True)
			self.radio.enableDynamicPayloads()
			self.radio.setRetries(self.retry_delay, self.retries)

			self.radio.setDataRate(RF24_2MBPS)
			self.radio.setPALevel(RF24_PA_MAX)

			self.Connected = False;

			return True;
		else:
			return False;
	

	def enumerate(self):

		if (not self.Connected):

			self.radio.stopListening()
			self.radio.setChannel(RFAccel.channel_enumerate)

			self.radio.openWritingPipe(RFAccel.pipe_out_enumerate)
			self.radio.openReadingPipe(1, RFAccel.pipe_in_enumerate)

			self.remotes = {}

			self.radio.write(bytearray([RFAccel.type_cmd, RFAccel.cmd_enumerate]))

			self.radio.startListening()

			wait_start = millis()

			timeout = False

			while (not timeout):

				if (self.radio.available()):

					length = self.radio.getDynamicPayloadSize()

					if (length == RFAccel.data_enumerate_length):

						response = self.radio.read(length)
						r_type = response[0]
						r_cmd = response[1]
						r_id = struct.unpack("<I", bytearray(response[2:6]))[0]
						r_chip = RFAccel.enumerate_chip_names[response[6]]
						r_cap = response[7]

						if ((response[0] == RFAccel.type_data) and (response[1] == RFAccel.data_enumerate)):
							self.remotes[r_id] = [r_chip, r_cap]
							print("Found device with ID " + hex(r_id) + " with chip " + r_chip + " and capatibilities " + bin(r_cap))

						else:
							print("Invalid enumeration response with correct size...")

					else:
						print("Received invalid enumeration response length: " + str(length) + " bytes")

				elif (millis() - wait_start) > self.enumerate_timeout:
					timeout = True

	def connect(self, d_id, channel = 18):
		
		self.radio.stopListening()

		self.radio.write(bytearray([RFAccel.type_cmd, RFAccel.cmd_connect, channel, RFAccel.connect_timestamp_ms]))
		self.radio.startListening()

		wait_start = millis()

		timeout = False

		while ((not timeout) and (not self.radio.available())):
			if (millis() - wait_start) > self.connect_timeout:
				timeout = True

		if (timeout):

			print("Connect response timed out.")
			return False;

		length = self.radio.getDynamicPayloadSize()

		if (length == RFAccel.data_connect_length):

			response = self.radio.read(length)

			r_type = response[0]
			r_cmd = response[1]

			self.pipe_in =  struct.unpack("<I", bytearray(response[2:6]))[0] # workaround for struct.unpack only accepting power of two bytes
			self.pipe_in |= (struct.unpack("<B", bytearray([response[6]]))[0] << 32)

			self.pipe_out = struct.unpack("<I", bytearray(response[7:11]))[0]
			self.pipe_out |= (struct.unpack("<B", bytearray([response[11]]))[0] << 32)

			if ((r_type == RFAccel.type_data) and (r_cmd == RFAccel.data_connect)):
				
				print("Connecting to device " + hex(d_id) + " on channel " + str(channel) + "; I/" + hex(self.pipe_in) +"; O/" + hex(self.pipe_out))

				self.radio.setChannel(channel)

				self.radio.openWritingPipe(self.pipe_out)
				self.radio.openReadingPipe(1, self.pipe_in)

				self.radio.startListening()

				while ((not timeout) and (not self.radio.available())):
					if (millis() - wait_start) > self.enumerate_timeout:
						timeout = True

				if (timeout):

					self.radio.stopListening()
					self.radio.setChannel(RFAccel.channel_enumerate)

					self.radio.openWritingPipe(RFAccel.pipe_out_enumerate)
					self.radio.openReadingPipe(1, RFAccel.pipe_in_enumerate)

					print("No test packet on given channel, falling back to enumerate channel.")
					return False

				length = self.radio.getDynamicPayloadSize()

				if (length == RFAccel.cmd_test_length):

					response = self.radio.read(length)

					r_type = response[0]
					r_cmd = response[1]

					if((r_type == RFAccel.type_cmd) and (r_cmd == RFAccel.cmd_test_channel)):
						print("Received test channel command on new channel.")
						self.radio.stopListening()
						self.radio.write(bytearray([RFAccel.type_cmd, RFAccel.cmd_test_channel]))
						print("Sent test channel command on new channel.")

						self.connected = True
						self.remote_device = d_id

						return True;

				else:
					print("Received ivalid test channel command length: " + str(length) + " bytes")
					self.connected = False
					self.remote_device = None
					return False

			else:
				print("Invalid connect response with correct size...")
				self.connected = False
				self.remote_device = None
				return False

		else:
			print("Received invalid connect response length: " + str(length) + " bytes")
			self.connected = False
			self.remote_device = None

			return False

	def get(self, a = True, g = True, m = False):
		if self.connected:
			
			self.radio.stopListening()

			typeflags = 0x00
			responselength = RFAccel.data_get_length

			if a:
				typeflags |= RFAccel.get_type_acc
				responselength += 6			#2 bytes per axis
			if g:
				typeflags |= RFAccel.get_type_gyro
				responselength += 6
			if m:
				typeflags |= RFAccel.get_type_magnet
				responselentgh += 6

			self.radio.write(bytearray([RFAccel.type_cmd, RFAccel.cmd_get, typeflags]))
			self.radio.startListening()

			wait_start = millis()

			timeout = False

			while ((not timeout) and (not self.radio.available())):
				if (millis() - wait_start) > self.connect_timeout:
					timeout = True

			if (timeout):

				print("Get command response timed out.")
				return None

			length = self.radio.getDynamicPayloadSize()

			if(length == responselength):
				print("Got data packet of right size.")
				return []

			else:
				print("Got invalid get response length ")
				return None

		else:
			return None

if __name__ == "__main__":
	RFAccelShell().cmdloop()
