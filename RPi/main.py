#!/usr/bin/env python

import time
import cmd
from RF24 import *
from RFAccel import *
import RPi.GPIO as GPIO


class RFAccelShell(cmd.Cmd): 

	intro = "rfaccel 0.1 shell.   Type help or ? to list commands.\n"
	prompt = "(rfaccel)"
	file = None

	retries = 15
	retry_delay = 4

	millis = lambda: int(round(time.time() * 1000))


	def do_init(self, arg):
		'Initialize rfaccel'
		self.init()

	def do_info(self, arg):
		'Print radio details'
		self.radio.printDetails()

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

	def close(self):
		pass

	def init(self):

	 	#Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 8Mhz
		self.radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

		self.TX_pipe = 0xF0F0F0F0D2
		self.RX_pipe = 0xF0F0F0F0E1

		self.radio.begin()
		self.radio.enableDynamicPayloads()
		self.radio.setRetries(self.retry_delay, self.retries)
		
		self.radio.openWritingPipe(self.TX_pipe)
		self.radio.openReadingPipe(1, self.RX_pipe)

		self.radio.stopListening()

if __name__ == "__main__":
	RFAccelShell().cmdloop()
