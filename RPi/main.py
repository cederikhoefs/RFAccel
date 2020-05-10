#!/usr/bin/env python

import time
import cmd
from RF24 import *
import RFAccel
import RPi.GPIO as GPIO


class RFAccelShell(cmd.Cmd): 

	intro = "rfaccel 0.1 shell.   Type help or ? to list commands.\n"
	prompt = "(rfaccel)"
	radio = None
	mode = RFAccel.mode_idle


	retries = 15
	retry_delay = 5

	enumerate_timeout = 1000

	millis = lambda: int(round(time.time() * 1000))


	def do_init(self, arg):
		'Initialize rfaccel'
		if (self.init()):
			print("Succesfully initialized NRF24L01+")
		else:
			print("No NRF24L01 connected")

	def do_info(self, arg):
		'Print radio details'
		if (self.radio):
			self.radio.printDetails()

	def do_enumerate(self, arg):
		'Get available devices'

		if (not (self.mode == RFAccel.mode_conn)):
			self.enum_mode()
			self.enumerate()			
		else:
			print("Still in connection.")

	def do_connect(self, arg):
		'Connect to remote device'
		pass

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

	 	#Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 8Mhz
		self.radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

		#if(not self.radio.isChipConnected()): #Does not work due do bad pyRF24 maintenance
		#	return False;

		self.radio.begin()
		self.radio.enableDynamicPayloads()
		self.radio.setRetries(self.retry_delay, self.retries)

		self.radio.setDataRate(RF24_2MBPS)
		self.radio.setPALevel(RF24_PA_MAX)
		
		self.enum_mode()

		return True;

	def enum_mode(self):

		self.mode = RFAccel.mode_enum

		self.radio.stopListening()
		self.radio.setChannel(RFAccel.enumerate_channel)

		self.radio.openWritingPipe(RFAccel.enumerate_pipe_out)
		self.radio.openReadingPipe(1, RFAccel.enumerate_pipe_in)

	def enumerate(self):
		if (self.mode == RFAccel.mode_enum):

			self.radio.write(bytes([type_cmd, cmd_enumerate])

			self.radio.startListening()

			wait_start = millis()

			timeout = False

			while (not timeout):

				if (self.radio.available()):
					length = radio.getDynamicPayloadSize()
					response = radio.read(length)
					print("Received " + str(length) + " bytes")

				elif (millis() - wait_start) > self.enumerate_timeout:
					timeout = True


if __name__ == "__main__":
	RFAccelShell().cmdloop()
