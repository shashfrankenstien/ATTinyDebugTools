#include "ChargePump.h"
#include "ATTinyFuseReset.h"



byte shiftOut (byte val1, byte val2) {
  int inBits = 0;
  //Wait until SDO goes high
  while (!digitalRead(SDO))
    ;
  unsigned int dout = (unsigned int) val1 << 2;
  unsigned int iout = (unsigned int) val2 << 2;
  for (int ii = 10; ii >= 0; ii--)  {
    digitalWrite(SDI, !!(dout & (1 << ii)));
    digitalWrite(SII, !!(iout & (1 << ii)));
    inBits <<= 1;
    inBits |= digitalRead(SDO);
    digitalWrite(SCI, HIGH);
    digitalWrite(SCI, LOW);
  }
  return inBits >> 2;
}

void writeFuse (unsigned int fuse, byte val) {
  shiftOut(0x40, 0x4C);
  shiftOut( val, 0x2C);
  shiftOut(0x00, (byte) (fuse >> 8));
  shiftOut(0x00, (byte) fuse);
}

void readFuses () {
  byte val;
        shiftOut(0x04, 0x4C);  // LFuse
        shiftOut(0x00, 0x68);
  val = shiftOut(0x00, 0x6C);
  Serial.print("LFuse: ");
  Serial.print(val, HEX);
        shiftOut(0x04, 0x4C);  // HFuse
        shiftOut(0x00, 0x7A);
  val = shiftOut(0x00, 0x7E);
  Serial.print(", HFuse: ");
  Serial.print(val, HEX);
        shiftOut(0x04, 0x4C);  // EFuse
        shiftOut(0x00, 0x6A);
  val = shiftOut(0x00, 0x6E);
  Serial.print(", EFuse: ");
  Serial.println(val, HEX);
}

unsigned int readSignature () {
  unsigned int sig = 0;
  byte val;
  for (int ii = 1; ii < 3; ii++) {
          shiftOut(0x08, 0x4C);
          shiftOut(  ii, 0x0C);
          shiftOut(0x00, 0x68);
    val = shiftOut(0x00, 0x6C);
    sig = (sig << 8) + val;
  }
  return sig;
}




PumpFuseResetter::PumpFuseResetter()
{
  pinMode(VCC, OUTPUT);
  pinMode(SDI, OUTPUT);
  pinMode(SII, OUTPUT);
  pinMode(SCI, OUTPUT);
  pinMode(SDO, OUTPUT);     // Configured as input when in programming mode
}

PumpFuseResetter::~PumpFuseResetter()
{
  pinMode(VCC, INPUT);
  pinMode(SDI, INPUT);
  pinMode(SII, INPUT);
  pinMode(SCI, INPUT);
  pinMode(SDO, INPUT);
}

// void setup() {
//   pinMode(VCC, OUTPUT);
//   pinMode(SDI, OUTPUT);
//   pinMode(SII, OUTPUT);
//   pinMode(SCI, OUTPUT);
//   pinMode(SDO, OUTPUT);     // Configured as input when in programming mode
//   Serial.begin(57600);
//   // Setup timer interrupt for  charge pump
//   analogReference(DEFAULT);
//   // Timer1.initialize(500);
//   // Timer1.attachInterrupt(ticker);
// }

char PumpFuseResetter::reset()
{
  ChargePump pump = ChargePump(1);

  pinMode(SDO, OUTPUT);     // Set SDO to output
  digitalWrite(SDI, LOW);
  digitalWrite(SII, LOW);
  digitalWrite(SDO, LOW);
  pump.turn_off();                // 12v Off
  digitalWrite(VCC, HIGH);  // Vcc On
  delayMicroseconds(20);
  pump.turn_on();                // 12v On
  delayMicroseconds(10);
  pinMode(SDO, INPUT);      // Set SDO to input
  delayMicroseconds(300);
  unsigned int sig = readSignature();
  Serial.print("Signature is: ");
  Serial.println(sig, HEX);
  if (sig == 0xFFFF)
    return 1;
  readFuses();
  if (sig == ATTINY13) {
    writeFuse(LFUSE, 0x6A);
    writeFuse(HFUSE, 0xFF);
  } else if (sig == ATTINY24 || sig == ATTINY44 || sig == ATTINY84 ||
              sig == ATTINY25 || sig == ATTINY45 || sig == ATTINY85) {
    writeFuse(LFUSE, 0x62);
    writeFuse(HFUSE, 0xDF);
    writeFuse(EFUSE, 0xFF);
  }
  readFuses();
  digitalWrite(SCI, LOW);
  digitalWrite(VCC, LOW);    // Vcc Off
  pump.turn_off();                // 12v Off
  return 0;
}
