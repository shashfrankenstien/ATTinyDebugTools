# ATTiny85 Debug Tools

Arduino ISP, debugwire and charge pump based HVP for ATTiny85

-----

### This project is mostly based on code and circuits from [Wayne's Tinkering Page](https://sites.google.com/site/wayneholder/)

- [debugwire2](https://sites.google.com/site/wayneholder/debugwire2)
- [attiny-fuse-reset](https://sites.google.com/site/wayneholder/attiny-fuse-reset)
- [attiny-fuse-reset-with-12-volt-charge-pump](https://sites.google.com/site/wayneholder/attiny-fuse-reset-with-12-volt-charge-pump)


```
 Commands:
  F - Identify Device & Print Fuses
  + - Enable debugWire DWEN Fuse
  - - Disable debugWire DWEN Fuse
  8 - Enable CKDIV8 (divide clock by 8)
  1 - Disable CKDIV8
  B - Engage Debugger
  < - Save Current Fuses
  > - Restore Saved Fuses
 High Voltage Programmer:
  R - Restore Saved Fuses (HVP)
  X - Hard Reset Fuses (HVP)
 Dev Commands:
  C - Send 4 Byte ISP Command
  P - Vcc On
  O - Vcc Off
```


### Also included, serial oscilloscope

- [arduino poor man's oscilloscope](https://randomnerdtutorials.com/arduino-poor-mans-oscilloscope/)
