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

	retries = 15
	retry_delay = 5

	enumerate_timeout = 1000

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
			if (not self.Connected):
				self.enumerate()			
				print(self.remotes)
			else:
				print("Still in connection.")
		else:
			print("Not yet initialized.")
			
	def do_connect(self, arg):
		'Connect to remote device'
		pass

	def complete_connect(self, text, line, begidx, idx):
		'Yields list of enumerated ID'
		possible_ids = []
		for c_id in self.remotes.keys():
			print(hex(c_id))
			if(hex(c_id).startswith(text)):
				possible_ids.append(hex(c_id))
		return possible_ids

	def do_calibrate(self, arg):
		'Calibrate the stationary remote device'
		pass

	def do_get_accel(self, arg):
		'Get remote accelerometer data'
		pass

	def do_get_gyro(self, arg):
		'Get remote gyroscope data'
		pass


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

	def connect(self):
		pass


if __name__ == "__main__":
	RFAccelShell().cmdloop()
