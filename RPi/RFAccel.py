type_cmd =    0x00
type_ack =    0x01
type_data =   0x02
type_stream = 0x03


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

enumerate_channel = 0
enum_pipe_out = 0x656E756D4F
enum_pipe_in = 0x656E756D49

mode_idle = 0x0
mode_enum = 0x1
mode_conn = 0x2