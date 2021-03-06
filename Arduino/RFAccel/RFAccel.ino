#define ARDUINO_ARCH_AVR
#include <SPI.h>
#include "RF24.h"
#include "printf.h"

#define VERBOSE



RF24 radio(7,8);

const uint8_t radio_retries = 15;
const uint8_t radio_retry_delay = 5; //1.5 ms

const uint8_t channel_enumerate = 0;
const uint64_t  pipe_in_enumerate = 0x656E756D4F; //Swapped on the RPi
const uint64_t  pipe_out_enumerate = 0x656E756D49;

const uint8_t type_cmd = 0x00;
const uint8_t type_data = 0x01;
const uint8_t type_stream = 0x02;

const uint8_t cmd_enumerate = 0x0E;       
const uint8_t cmd_connect = 0x0A;  
const uint8_t cmd_ping = 0x0B;
const uint8_t cmd_disconnect = 0x0F;        
const uint8_t cmd_close_stream = 0x0C;    

const uint8_t cmd_set_rate = 0x02;
const uint8_t cmd_set_range = 0x03;
const uint8_t cmd_get = 0x04;
const uint8_t cmd_stream = 0x05;

const uint8_t data_enumerate = 0x0E;
const uint8_t data_enumerate_length = 8;

const uint8_t enumerate_chip_unknown = 0;
const uint8_t enumerate_chip_MPU6050 = 1; //MPU6050; LI3DH; LSM303DLHC; etc...
const uint8_t enumerate_chip_LIS3DH = 2;
const uint8_t enumerate_LSM303DHC = 3;

const uint8_t feature_rf = (1 << 0);
const uint8_t feature_acc = (1 << 1);
const uint8_t feature_gyro = (1 << 2);
const uint8_t feature_magnet = (1 << 3);

const uint8_t data_connect = 0x0C;
const uint8_t data_connect_length = 12;

const uint8_t connect_timestamp_none = 0x00;
const uint8_t connect_timestamp_ms = 0x01;
const uint8_t connect_timestamp_us = 0x02;

const uint8_t cmd_disconnect_length = 2;
const uint8_t cmd_ping_length = 2;

const uint8_t cmd_get_length = 3;

const uint8_t data_get = 0x0D;

const uint8_t info_accel_resolutions_MPU6050[] = {16};
const uint16_t  info_accel_ranges[] = {2, 4, 8, 16};
const uint16_t  info_accel_max_data_rate = 1000;

const uint8_t info_gyro_resolutions_MPU6050[] = {16};
const uint16_t  info_gyro_ranges[] = {250, 500, 1000, 2000};
const uint16_t  info_gyro_max_data_rate = 8000;


const uint32_t ID = 0x2B4D4B31;
const uint8_t CAP = feature_rf | feature_acc | feature_gyro;
const uint8_t CHIP = enumerate_chip_MPU6050;

const uint64_t  pipe_in = 0x6461746149;
const uint64_t  pipe_out = 0x646174614f;

const uint8_t timeout_connect = 250;


uint8_t Channel = 0;
bool connected = false;

uint8_t TimestampFormat = 0;
uint8_t Type = 0;

uint8_t Buffer[32];

uint32_t Timeout = 0;

void to_enumerate(){

	Channel = channel_enumerate;
    radio.setChannel(channel_enumerate);
    radio.openWritingPipe(pipe_out_enumerate);
    radio.openReadingPipe(1, pipe_in_enumerate);

    radio.startListening();

	#ifdef VERBOSE
	Serial.println("(Fallback) to enumerate channel.");
	#endif

}

void setup()
{

    Serial.begin(115200);
    printf_begin();
    Serial.println("RFAccel");
   
    if(!radio.begin()){
        Serial.println("Could not init NRF24L01!!!");
    }

    radio.setAutoAck(true);
    radio.setDataRate(RF24_2MBPS);
    radio.enableDynamicPayloads();
    radio.setRetries(radio_retry_delay, radio_retries);

	to_enumerate();

    radio.printDetails();
		    	
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
            {
            		 
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
            }

            case cmd_connect:
            {

            	radio.stopListening();

            	Channel = Buffer[2];
            	TimestampFormat = Buffer[3];

            	Serial.print("Connecting on channel ");
            	Serial.println(Channel);

            	Serial.print("Time Format: ");
            	switch(TimestampFormat){

            	case connect_timestamp_none:
            		Serial.println("none");
            		break;
            	case connect_timestamp_ms:
            		Serial.println("ms");
            		break;
            	case connect_timestamp_us:
            		Serial.println("us");
            		break;
            	default:
            		Serial.println("Invalid");
            		break;

            	}

            	Buffer[0] = type_data;
            	Buffer[1] = data_connect;

            	Buffer[2] = (pipe_out >> 0) & 0xFF;
            	Buffer[3] = (pipe_out >> 8) & 0xFF;
            	Buffer[4] = (pipe_out >> 16)& 0xFF;
            	Buffer[5] = (pipe_out >> 24)& 0xFF;
            	Buffer[6] = (pipe_out >> 32)& 0xFF;

            	Buffer[7] = (pipe_in >> 0) & 0xFF;
            	Buffer[8] = (pipe_in >> 8) & 0xFF;
            	Buffer[9] = (pipe_in >> 16)& 0xFF;
            	Buffer[10] = (pipe_in >> 24)& 0xFF;
            	Buffer[11] = (pipe_in >> 32)& 0xFF;
            
            	radio.write(Buffer, data_connect_length);
            	
            	radio.setChannel(Channel);
            	radio.openWritingPipe(pipe_out);
            	radio.openReadingPipe(1, pipe_in);
                
                radio.printDetails();

    
            	Buffer[0] = type_cmd;
            	Buffer[1] = cmd_ping;
            
            	radio.write(Buffer, cmd_ping_length);
            	Serial.println("Sent test_channel packet.");
            
                radio.startListening();
                
                Timeout = millis() + timeout_connect;
                
                while(!(millis() >= Timeout) && !radio.available());
                
                if(radio.available()){

                	uint8_t len = radio.getDynamicPayloadSize();
        			radio.read( Buffer, len );

        			if(Buffer[0] == type_cmd && Buffer[1] == cmd_ping){
                		Serial.println("Received test_channel packet.");
                		connected = true;
        			}
        			else{

                 		Serial.println("Corrupt or no test_channel packet.");

                    	radio.setChannel(channel_enumerate);
                    	Channel = channel_enumerate;
                    	radio.openWritingPipe(pipe_out_enumerate);
                    	radio.openReadingPipe(1, pipe_in_enumerate);

        			}

                }

                else if(millis() >= Timeout){
                    Serial.println("Timeout when waiting for ping");
					to_enumerate();
                    continue;
                    
                }                
                break;
            }
			case cmd_disconnect:
			{
				radio.stopListening();
				Serial.println("Disconnecting.");
				connected = false;

				Buffer[0] = type_cmd;
				Buffer[1] = cmd_disconnect;

				radio.write(Buffer, cmd_disconnect_length);

				to_enumerate();
				
				break;

			}
            case cmd_get:
            {
            	radio.stopListening();

            	Type = Buffer[2];

            	uint8_t packetlength = 2;

            	if(Type == 0x00){
            		Serial.println("Get command without any set dataflag");
            		break;
            	}
            	else{
            		if(Type & feature_acc)
            			packetlength += 6;
            		if(Type & feature_gyro)
            			packetlength += 6;
            		if(Type & feature_magnet)
            			packetlength += 6;
            		Serial.println("Data requested...");
            	}


            	Buffer[0] = type_data;
            	Buffer[1] = data_get;
            
            	radio.write(Buffer, packetlength);

            	Serial.print("Count of bytes: ");
            	Serial.println(packetlength - 2);

            	radio.startListening();
                
                break;
        	}
                
            default:
                break;
                
            }
            
            break;

    	default:
    	    break;
    	
        }
       
    }
}
