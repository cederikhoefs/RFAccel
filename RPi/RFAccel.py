channel_enumerate = 0

pipe_out_enumerate = 0x656E756D4F
pipe_in_enumerate = 0x656E756D49

type_cmd =    0x00
type_data =   0x01
type_stream = 0x02

cmd_enumerate = 0x0E				#Sent on 'enumerate' channel for device discovery
cmd_start = 0x0A					#Starts a connection between RPi and Arduino on specified radio channel
cmd_end = 0x0F						#Ends the connection, lets the arduino return to the enumerate channel
cmd_close_stream = 0x0C				#Stops the current stream, sent as an ackPayload

cmd_set_acc_rate = 0x02
cmd_set_gyr_rate = 0x03
cmd_set_acc_range = 0x04
cmd_set_gyr_range = 0x05
cmd_get_acc = 0x06
cmd_get_gyr = 0x07
cmd_stream_accel = 0x08
cmd_stream_gyro = 0x09

data_enumerate = 0x0E
data_enumerate_length = 8			#change this when adding parameters to enumeration response packet
	
enumerate_chip_names	= {0: "Unknown", 1: "MPU6050", 1:"LIS3DH", 2:"LSM303DLHC"}
enumerate_cap_rf 		= 1 << 0		#must always be true, otherwise we couldn't talk.
enumerate_cap_acc		= 1 << 1		#accelerometer available
enumerate_cap_gyro		= 1 << 2		#gyroscope available
enumerate_cap_magnet	= 1 << 3		#magnetometer available

