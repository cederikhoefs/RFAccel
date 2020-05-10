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
	retry_delay = 5

	enumerate_channel = 0

	millis = lambda: int(round(time.time() * 1000))


	def do_init(self, arg):
		'Initialize rfaccel'
		if(self.init()):
			print("Succesfully initialized NRF24L01+")
		else:
			print("No NRF24L01 connected")

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
		return True;

	def close(self):
		pass

	def init(self):

	 	#Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 8Mhz
		self.radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

		#if(not self.radio.isChipConnected()): #Does not work due do bad pyRF24 maintenance
		#	return False;


		self.TX_pipe = 0xF0F0F0F0D2
		self.RX_pipe = 0xF0F0F0F0E1

		self.radio.begin()
		self.radio.enableDynamicPayloads()
		self.radio.setRetries(self.retry_delay, self.retries)

		self.radio.setChannel(enumerate_channel)
		self.radio.setDataRate(NRF24.BR_2MBPS)
		self.radio.setPALevel(NRF24.PA_MIN)
		
		self.radio.openWritingPipe(self.TX_pipe)
		self.radio.openReadingPipe(1, self.RX_pipe)

		self.radio.stopListening()

		return True;

if __name__ == "__main__":
	RFAccelShell().cmdloop()
