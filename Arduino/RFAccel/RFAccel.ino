#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"


RF24 radio(7,8);

const uint64_t TX_pipe = 0xF0F0F0F0E1LL;
const uint64_t RX_pipe = 0xF0F0F0F0D2LL;

const uint8_t retries = 1;
const uint8_t retry_delay = 4; //1 ms


uint32_t Buffer[32];

void setup()
{

  Serial.begin(115200);

  radio.begin();


  //radio.enableDynamicPayloads();
  radio.setRetries(retry_delay, retries);

  radio.openWritingPipe(TX_pipe);
  radio.openReadingPipe(1, RX_pipe);

  radio.startListening();
  radio.printDetails();
  
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

      radio.stopListening();

      radio.write(Buffer, len );
      Serial.println(F("Sent response."));

      radio.startListening();
    }
  
  
}

