#include "ChargePump.h"
/*
    * Dickson Charge Pump Driver
    */

// Variables used by Charge pump
volatile char phase = 0;
volatile char onOff = 0;
volatile char _v12_mode = 0;
volatile char pwrOn = 0;

void _pump () {
    if (onOff & _v12_mode) {
        DDRD = P1 | P2 | PWR | GND;
        int volts = analogRead(A0);
        if (volts < REF) {
            if (phase) {
                PORTD = P1 | PWR;
            } else {
                PORTD = P2 | PWR;
            }
            phase ^= 1;
        } else {
          pwrOn = 1;
        }
    } else if (onOff) {
        DDRD = PWR | GND;
        PORTD = PWR;
    } else {
        pwrOn = 0;
        DDRD = GND;
        PORTD = GND;        
    }
}


ChargePump::ChargePump(char v12_mode)
{
    _v12_mode = v12_mode;
    turn_off();
    analogReference(DEFAULT);
    Timer1.initialize(500);
    Timer1.attachInterrupt(_pump);
}

ChargePump::~ChargePump()
{
    turn_off();
    delay(10);
    Timer1.detachInterrupt();
}

void ChargePump::turn_on()
{
    onOff = 1;
    while (pwrOn == 0);
}

void ChargePump::turn_off()
{
    onOff = 0;
    while (pwrOn == 1);
}
