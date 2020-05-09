#!/usr/bin/env python

import time
from RF24 import *
from RFAccel import *
import RPi.GPIO as GPIO

irq_gpio_pin = None

millis = lambda: int(round(time.time() * 1000))

retries = 15
retry_delay = 4


########### USER CONFIGURATION ###########
# See https://github.com/TMRh20/RF24/blob/master/pyRF24/readme.md

# CE Pin, CSN Pin, SPI Speed

# Setup for GPIO 22 CE and CE0 CSN with SPI Speed @ 8Mhz

def main():

	print("RFAccel 0.1")

	radio = RF24(RPI_V2_GPIO_P1_15, BCM2835_SPI_CS0, BCM2835_SPI_SPEED_8MHZ)

	TX_pipe = 0xF0F0F0F0D2
	RX_pipe = 0xF0F0F0F0E1

	radio.begin()
	radio.enableDynamicPayloads()
	radio.setRetries(retry_delay, retries)
	radio.printDetails()

	radio.openWritingPipe(TX_pipe)
	radio.openReadingPipe(1, RX_pipe)

	radio.stopListening()

	for i in range(10):
		print(str(i) + " returns " + str(radio.write(bytes([cmd, cmd_start]))))
	"""
	radio.startListening()

	wait_start = millis()
	timeout = False
	while (not radio.available()) and (not timeout):
		if (millis() - wait_start) > 500:
			timeout = True

	if timeout:
		print('Connection failed, response timed out.')
	else:
		length = radio.getDynamicPayloadSize()
		response = radio.read(length)

		print("Received " + str(length) + " bytes")
	"""

if __name__ == "__main__":
	main()
