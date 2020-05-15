#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"

//#define VERBOSE



RF24 radio(7,8);

const uint8_t	radio_retries = 15;
const uint8_t	radio_retry_delay = 5; //1.5 ms

const uint8_t	channel_enumerate = 0;
const uint64_t	pipe_in_enumerate = 0x656E756D4F; //Swapped on the RPi
const uint64_t	pipe_out_enumerate = 0x656E756D49;

const uint8_t	type_cmd = 0x00;
const uint8_t	type_data = 0x01;
const uint8_t	type_stream = 0x02;

const uint8_t	cmd_enumerate = 0x0E;				
const uint8_t	cmd_start = 0x0A;		
const uint8_t	cmd_end = 0x0F;				
const uint8_t	cmd_close_stream = 0x0C;		

const uint8_t	cmd_set_acc_rate = 0x02;
const uint8_t	cmd_set_gyr_rate = 0x03;
const uint8_t	cmd_set_acc_range = 0x04;
const uint8_t	cmd_set_gyr_range = 0x05;
const uint8_t	cmd_get_acc = 0x06;
const uint8_t	cmd_get_gyr = 0x07;
const uint8_t	cmd_stream_accel = 0x08;
const uint8_t	cmd_stream_gyro = 0x09;

const uint8_t 	data_enumerate = 0x0E;
const uint8_t	data_enumerate_length = 8;

const uint8_t	enumerate_chip_unknown = 0;
const uint8_t	enumerate_chip_MPU6050 = 1; //MPU6050; LI3DH; LSM303DLHC; etc...
const uint8_t	enumerate_chip_LIS3DH = 2;
const uint8_t	enumerate_LSM303DHC = 3;

const uint8_t	enumerate_cap_rf = (1 << 0);
const uint8_t	enumerate_cap_acc = (1 << 1);
const uint8_t	enumerate_cap_gyro = (1 << 2);
const uint8_t	enumerate_cap_magnet = (1 << 3);

const uint8_t	info_accel_resolutions_MPU6050[] = {16};
const uint16_t	info_accel_ranges[] = {2, 4, 8, 16};
const uint16_t	info_accel_max_data_rate = 1000;

const uint8_t	info_gyro_resolutions_MPU6050[] = {16};
const uint16_t	info_gyro_ranges[] = {250, 500, 1000, 2000};
const uint16_t	info_gyro_max_data_rate = 8000;


const uint32_t ID = 0x2B4D4B31;
const uint8_t CAP = enumerate_cap_rf | enumerate_cap_acc | enumerate_cap_gyro;
const uint8_t CHIP = enumerate_chip_MPU6050;


uint8_t Buffer[32];

void setup()
{

  Serial.begin(115200);
  Serial.println("RFAccel");
  
  radio.begin();

  radio.setAutoAck(true);
  radio.setDataRate(RF24_2MBPS);
  radio.enableDynamicPayloads();
  radio.setRetries(radio_retry_delay, radio_retries);

  radio.setChannel(channel_enumerate);
  radio.openWritingPipe(pipe_out_enumerate);
  radio.openReadingPipe(1, pipe_in_enumerate);

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
					Buffer[1] = data_enumerate;
					Buffer[2] = (ID >> 0) & 0xFF;
					Buffer[3] = (ID >> 8) & 0xFF;
					Buffer[4] = (ID >> 16)& 0xFF;
					Buffer[5] = (ID >> 24)& 0xFF;
					Buffer[6] = CHIP;
					Buffer[7] = CAP;

					radio.write(Buffer, data_enumerate_length);
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

