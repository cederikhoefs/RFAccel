#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"


RF24 radio(7,8);

const uint8_t  enumerate_channel = 0;
const uint64_t enumerate_pipe_in = 0x656E756D4F;
const uint64_t enumerate_pipe_out = 0x656E756D49;

const uint8_t retries = 15;
const uint8_t retry_delay = 5; //1.5 ms

uint32_t Buffer[32];

void setup()
{

  Serial.begin(115200);
  Serial.println("RFAccel");
  
  radio.begin();

  radio.setAutoAck(false);
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

      Serial.print(F("Got packet of "));
      Serial.print(len);
      Serial.println(" bytes");
    }
}

