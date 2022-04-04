///*
//  Complete project details: https://randomnerdtutorials.com/arduino-poor-mans-oscilloscope/
//*/
//
//#define ANALOG_IN 0
//
//void setup() {
//    Serial.begin(9600);
//    //Serial.begin(115200);
//}
//void loop() {
//    int val = analogRead(ANALOG_IN);
//    Serial.write( 0xff );
//    Serial.write( (val >> 8) & 0xff );
//    Serial.write( val & 0xff );
//}



#include "MCP3008.h"
 
//define pin connections
#define CLOCK_PIN 14
#define MISO_PIN 12
#define MOSI_PIN 13
#define CS_PIN 15

 
MCP3008 adc(CLOCK_PIN, MOSI_PIN, MISO_PIN, CS_PIN);
 
void setup() 
{
 // open serial port
  Serial.begin(9600); 
}
 
void loop() 
{
 
  int val = adc.readADC(0); // read Channel 0 from MCP3008 ADC (pin 1)
  int val2 = adc.readADC(1); // read Channel 1 from MCP3008 ADC (pin 2)

  Serial.write( 0xff );
  Serial.write( (val >> 8) & 0xff );
  Serial.write( val & 0xff );
  Serial.write( (val2 >> 8) & 0xff );
  Serial.write( val2 & 0xff );
}
