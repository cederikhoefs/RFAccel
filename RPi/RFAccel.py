channel_enumerate = 0

pipe_out_enumerate = 0x656E756D4F
pipe_in_enumerate = 0x656E756D49

type_cmd =    0x00
type_data =   0x01
type_stream = 0x02

cmd_enumerate = 0x0E				#Sent on 'enumerate' channel for device discovery
cmd_connect = 0x0A					#Starts a connection between RPi and Arduino on specified radio channel
cmd_disconnect = 0x0F				#Ends the connection, lets the arduino return to the enumerate channel
cmd_ping = 0x0B				        #Sent on actual device channel to test connection
cmd_close_stream = 0x0C				#Stops the current stream, sent as an ackPayload

cmd_set_rate = 0x02
cmd_set_range = 0x03
cmd_get = 0x04
cmd_stream = 0x05

data_enumerate = 0x0E
data_enumerate_length = 8			#change this when adding parameters to enumeration response packet
	
enumerate_chip_names	= {0: "Unknown", 1: "MPU6050", 2:"LIS3DH", 3:"LSM303DLHC"}
feature_rf	= 1 << 0
feature_acc	= 1 << 1		#accelerometer
feature_gyro	= 1 << 2		#gyroscope
feature_magnet	= 1 << 3		#magnetometer

data_connect = 0x0C
data_connect_length = 12

connect_timestamp_none = 0x00
connect_timestamp_ms = 0x01
connect_timestamp_us = 0x02

cmd_disconnect_length = 2

cmd_test_length = 2

cmd_get_length = 3

feature_acc	= 1 << 1		#accelerometer
feature_gyro	= 1 << 2		#gyroscope
feature_magnet	= 1 << 3		#magnetometer

data_get = 0x0D
data_get_length = 2				#considering only the command and flags, not the variable data length
