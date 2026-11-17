# Sunbird

## Acknowledgements

### Kerry D Wong

This project draws heavily on work done by [Kerry D Wong](http://www.kerrywong.com/about/) - who reverse engineered the IR communications protocol used by the Syma S107G, built a reference control circuit that implements that protocol, and then [made her research publicly available](http://www.kerrywong.com/2012/08/27/reverse-engineering-the-syma-s107g-ir-protocol/).

## Goals

* achieve basic remote control of drone functions  
  * reverse engineer the IR communication protocol
    * source a USB IR transducer with a workable interface  
  * develop a basic control module  
* achieve blind control of basic flight components  
  * hover  
  * rotate  
  * linear translate / forwards-backwards  
* achieve basic blind flight control  
  * take off and land  
  * migrate  
* build position monitoring system for feedback
  * options
    * optical camera
      * location & orientation recognition
      * determination of spatial (physical environment) & control range constraints
  * sample space dimensions
    * absolute grid position  
    * relative orientation  
5. ML using feedback

## OEM Drone Specification

Syma S107G IR controlled helicopter, produced by [Syma Toys](http://www.symatoys.com/).

specification|value
-------------|-----
OEM|Syma
Model|107G Phantom
Battery|3.7 V, 150 mAh Li-poly
Charging Time|40 mins
Flying Time|5-6 mins
Length|220 mm
Width|38 mm
Height|98 mm
Main Rotor|190 mm
Tail Rotor|30 mm
OEM link|http://www.symatoys.com/goodshow/syma-s107g-phantom.html

This model is [available from amazon.com](https://www.amazon.com/s?k=Syma+S107G) from a number of retailers for a price in the range of 20 - 25 USD, as of 2020/12/17.

## Execution

### Basic Remote Control of Drone Functions

#### Reverse Engineering & Analysis of Infra Red Communications

[Kerry D Wong](http://www.kerrywong.com/about/) - who reverse engineered the IR communications protocol used by the Syma S107G, built a reference control circuit that implements that protocol, and then [made her research publicly available](http://www.kerrywong.com/2012/08/27/reverse-engineering-the-syma-s107g-ir-protocol/):

The transmitter works on one of two channels, A or B, with a 38 kHz or 57 kHz carrier (50% duty cycle). Every command repeats continuously; Wong measured an interval of 184 ms from the stock remote, and the reference sketch sends one every 180 ms.

Each command is 34 pulses: a two-pulse header, then 4 bytes of data, most significant bit first. Every pulse is the same width; a bit's value is set by the length of the low before it.

Timing (from Wong's measurements and reference sketch):

parameter|38 kHz (channel A)|57 kHz (channel B)
---------|-----|-----
header high|2 ms|2 ms
header low|2 ms|2 ms
pulse width (high)|380 us|380 us
low before a 0|220 us|220 us
low before a 1|600 us|660 us
command interval|180 ms|160 ms

Wong's article prints the header low as "2 us"; the sketch uses 2000 us, so it is 2 ms. Wong's published sketch also pairs a 57 kHz carrier with the 38 kHz bit timings; `sungate` uses 38 kHz throughout.

The 4 data bytes, with the values Wong decoded from the stock remote:

byte|control|stock remote values|neutral
----|-------|-------------------|-------
1|yaw (rotate left/right)|8 (full right) .. 106 (full left)|60
2|pitch (forward/back)|1 (full forward) .. 126 (full back)|63
3|throttle (main rotor speed)|139 (~0%) .. 253 (100%)|-
4|trim (yaw calibration knob)|52 as captured; raises when turned right|52

Open question: the stock remote's throttle byte always had its top bit set (139..253), while `control.py` hovers with throttle 80..100 (top bit clear). The top bit may encode the channel. Capturing the stock remote on both channels with `tools/decode_capture.py` would settle it.

The signed ranges in Wong's sketch (-64..63, -128..127) are its potentiometer conversions, which the sketch adds to the neutrals; they are not values on the wire.

Links
* [kerry-d-wong](http://www.kerrywong.com/2012/08/27/reverse-engineering-the-syma-s107g-ir-protocol/)

#### Development of an Arduino-based IR Control Gateway Module

IR on the RPi
* https://projects.raspberrypi.org/en/projects/infrared-bird-box/6  
* https://www.raspberrypi.org/forums/viewtopic.php?t=117580  
* https://raspberrypi.stackexchange.com/questions/4308/how-to-attach-a-ir-led-to-a-gpio-port  
* https://www.hackster.io/austin-stanton/creating-a-raspberry-pi-universal-remote-with-lirc-2fd581#toc-step-2--circuit-1  

Driving a Hi-Power Current From the Arduino With a MOSFET NPN Transistor
* https://bildr.org/2012/03/rfp30n06le-arduino/
* https://www.instructables.com/Arduino-Tutorial-Handling-High-Power-Devices/
* https://www.raspberrypi.org/forums/viewtopic.php?t=180944
* https://itp.nyu.edu/physcomp/labs/motors-and-transistors/using-a-transistor-to-control-high-current-loads-with-an-arduino/

## References

### Topic Links

ESP32
* [multi-core operation](https://www.youtube.com/watch?v=k_D_Qu0cgu8)