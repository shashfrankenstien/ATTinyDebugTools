
#ifndef ATTinyFuseReset_h
#define ATTinyFuseReset_h

// AVR High-voltage Serial Fuse Reprogrammer with 12 Volt Charge Pump
// Adapted from code and design by Paul Willoughby 03/20/2010
//   http://www.rickety.us/2010/03/arduino-avr-high-voltage-serial-programmer/
//
// Fuse Calc:
//   http://www.engbedded.com/fusecalc/

#define  SCI     9     // Target Clock Input
#define  SDO     13    // Target Data Output
#define  SII     12    // Target Instruction Input
#define  SDI     11    // Target Data Input
#define  VCC     10    // Target VCC

#define  HFUSE  0x747C
#define  LFUSE  0x646C
#define  EFUSE  0x666E

// Define ATTiny series signatures
#define  ATTINY13   0x9007  // L: 0x6A, H: 0xFF             8 pin
#define  ATTINY24   0x910B  // L: 0x62, H: 0xDF, E: 0xFF   14 pin
#define  ATTINY25   0x9108  // L: 0x62, H: 0xDF, E: 0xFF    8 pin
#define  ATTINY44   0x9207  // L: 0x62, H: 0xDF, E: 0xFFF  14 pin
#define  ATTINY45   0x9206  // L: 0x62, H: 0xDF, E: 0xFF    8 pin
#define  ATTINY84   0x930C  // L: 0x62, H: 0xDF, E: 0xFFF  14 pin
#define  ATTINY85   0x930B  // L: 0x62, H: 0xDF, E: 0xFF    8 pin


// void readFuses();
// unsigned int readSignature();

// void setup();
// void resetFuses();


class PumpFuseResetter {
    public:
    PumpFuseResetter();
    ~PumpFuseResetter();

    char reset();
};



#endif // ATTinyFuseReset_h
