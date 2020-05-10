#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"

//#define VERBOSE


RF24 radio(7,8);


const uint8_t  enumerate_channel = 0;
const uint64_t enumerate_pipe_in = 0x656E756D4F;
const uint64_t enumerate_pipe_out = 0x656E756D49;

const uint8_t retries = 15;
const uint8_t retry_delay = 5; //1.5 ms

const uint8_t type_cmd = 0x00;
const uint8_t type_data = 0x01;
const uint8_t type_stream = 0x02;

const uint8_t cmd_enumerate = 0x0E;				
const uint8_t cmd_start = 0x0A;		
const uint8_t cmd_end = 0x0F;				
const uint8_t cmd_close_stream = 0x0C;		

const uint8_t cmd_set_acc_rate = 0x02;
const uint8_t cmd_set_gyr_rate = 0x03;
const uint8_t cmd_set_acc_range = 0x04;
const uint8_t cmd_set_gyr_range = 0x05;
const uint8_t cmd_get_acc = 0x06;
const uint8_t cmd_get_gyr = 0x07;
const uint8_t cmd_stream_accel = 0x08;
const uint8_t cmd_stream_gyro = 0x09;

const uint8_t data_enumeration = 0x0E;
const uint8_t enum_accel_MPU6050 = 0; //MPU6050; LI3DH; LSM303DLHC; etc...
const uint8_t enum_accel_LIS3DH = 1;

const uint8_t info_accel_resolutions_MPU6050[] = {16};
const uint16_t info_accel_ranges[] = {2, 4, 8, 16};
const uint16_t info_accel_max_data_rate = 1000;

const uint8_t info_gyro_resolutions_MPU6050[] = {16};
const uint16_t info_gyro_ranges[] = {250, 500, 1000, 2000};
const uint16_t info_gyro_max_data_rate = 8000;


uint8_t Buffer[32];

void setup()
{

  Serial.begin(115200);
  Serial.println("RFAccel");
  
  radio.begin();

  radio.setAutoAck(true);
  radio.setDataRate(RF24_2MBPS);
  radio.enableDynamicPayloads();
  radio.setRetries(retry_delay, retries);

  radio.setChannel(enumerate_channel);
  radio.openWritingPipe(enumerate_pipe_out);
  radio.openReadingPipe(1, enumerate_pipe_in);

  radio.printDetails();
  

  radio.startListening();
  
}

void loop()
{

    while ( radio.available() )
    {

      uint8_t len = radio.getDynamicPayloadSize();

      radio.read( Buffer, len );
      
      #ifdef VERBOSE

      Serial.print(F("Got packet of "));
      Serial.print(len);
      Serial.println(" bytes");
      
      for(int i = 0; i < len; i++){
        Serial.print((int)Buffer[i], HEX);
        Serial.print(";");
      }
      Buffer[len] = 0;
      Serial.println((char*)Buffer);
      
      #endif
      
      if(len < 2){
        continue;
      }
      
      switch(Buffer[0]){

		case type_cmd:

			switch(Buffer[1]){

				case cmd_enumerate:
                                         
					Serial.println("Enumeration requested!");
					      
					radio.stopListening();

					Buffer[0] = type_data;
					Buffer[1] = data_enumeration;
					Buffer[2] = enum_accel_MPU6050;

					radio.write(Buffer, 3);
					radio.startListening();
					break;
				default:
					break;
			}

			break;
          
        default:
        	break;
        
      }

    }
}

