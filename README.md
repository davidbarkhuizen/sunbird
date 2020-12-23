# Sunbird

## Acknowledgements

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
OEM link|http://www.symatoys.com/goodshow/syma-s107g-phantom.html

This model is [available from amazon.com](https://www.amazon.com/s?k=Syma+S107G) from a number of retailers for a price in the range of 20 - 25 USD, as of 2020/12/17.

## Execution

### Basic Remote Control of Drone Functions

#### Reverse Engineering & Analysis of Infra Red Communications

Links
* https://gist.github.com/rxseger/b6ff37961f7fc80f421b5d30eb7147e1
* http://www.kerrywong.com/2012/08/27/reverse-engineering-the-syma-s107g-ir-protocol/

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