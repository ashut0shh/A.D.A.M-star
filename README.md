# A.D.A.M-star
a test for alziemer's and dementia using praxia



1.download the arduino ide
2.upload arduino isp's code from examples->arduinoisp
3.make the pinout as shown in the pinout file
4.burn bootloader (if you upload any new code to uno i.e. not attiny then run isp again)
5.run the test codes to make sure the individual components are working properly
6.run the final code 
7.locate avrdude in your arduino folder
8.to obtain eeprom data run the following below identify the file and open it
9.avrdude -C /path/to/avrdude.conf -v -p attiny85 -c stk500v1 -P /dev/ttyUSB0 -b 19200 -U eeprom:r:backup_eeprom.hex:i
