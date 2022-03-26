#ifndef ChargePump_h
#define ChargePump_h


#include <TimerOne.h>

/*
    * Dickson Charge Pump Driver
    */

// Define Direct I/O pins for Charge Pump
#define P1  (1<<2)  // Pin D2
#define P2  (1<<3)  // Pin D3
#define PWR (1<<4)  // Pin D4
#define GND (1<<5)  // Pin D5
#define REF 420     // 12v ADC reference


class ChargePump
{
  public:
  ChargePump(char v12_mode);
  ~ChargePump();
  void turn_on();
  void turn_off();
};

#endif // ChargePump_h
