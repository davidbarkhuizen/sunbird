#include <TimerOne.h>
 
byte availableBytes;
byte serialInBuffer[64];

byte commandBuffer[64];
byte commandBufferEndIndex = 0;
byte command[4];

const int SERIAL_BAUD_RATE = 9600;

// ------------------------------

//comment this out to see the demodulated waveform
//it is useful for debugging purpose.
#define MODULATED 1 
 
const int IR_PIN = 3;
const unsigned long DURATION = 180000l;
const int HEADER_DURATION = 2000;
const int HIGH_DURATION = 380;
const int ZERO_LOW_DURATION = 220;
const int ONE_LOW_DURATION = 600;
 
void sendHeader()
{
  #ifndef MODULATED
    digitalWrite(IR_PIN, HIGH);
  #else
    TCCR2A |= _BV(COM2B1);
  #endif
   
  delayMicroseconds(HEADER_DURATION);
   
  #ifndef MODULATED
    digitalWrite(IR_PIN, LOW);
  #else
    TCCR2A &= ~_BV(COM2B1);
  #endif
   
  delayMicroseconds(HEADER_DURATION);
   
  #ifndef MODULATED
    digitalWrite(IR_PIN, HIGH);
  #else
    TCCR2A |= _BV(COM2B1);
  #endif
   
  delayMicroseconds(HIGH_DURATION);
   
  #ifndef MODULATED
    digitalWrite(IR_PIN, LOW);
  #else
    TCCR2A &= ~_BV(COM2B1);
  #endif
}
 
void sendZero()
{
  delayMicroseconds(ZERO_LOW_DURATION);
 
  #ifndef MODULATED
    digitalWrite(IR_PIN, HIGH);
  #else  
    TCCR2A |= _BV(COM2B1);
  #endif
   
  delayMicroseconds(HIGH_DURATION);
   
  #ifndef MODULATED
    digitalWrite(IR_PIN, LOW);
  #else
    TCCR2A &= ~_BV(COM2B1);
  #endif
}
 
void sendOne()
{
  delayMicroseconds(ONE_LOW_DURATION);
   
  #ifndef MODULATED
    digitalWrite(IR_PIN, HIGH);
  #else
    TCCR2A |= _BV(COM2B1);
  #endif
   
  delayMicroseconds(HIGH_DURATION);
   
  #ifndef MODULATED
    digitalWrite(IR_PIN, LOW);  
  #else
    TCCR2A &= ~_BV(COM2B1);
  #endif
}
 
void sendByte(byte B) {
  byte b;
  for (int i = 7; i >=0; i--)
  {
    b = (B & (1 << i)) >> i;    
    if (b > 0) sendOne(); else sendZero();
  }
}

void timerISR()
{
  sendHeader();

  for (int i = 0; i < 4; i++)
  {
    sendByte(command[i]);
  }
}
 
void setup()
{
  pinMode(IR_PIN, OUTPUT);
  digitalWrite(IR_PIN, LOW);
 
  //setup interrupt interval: 180ms  
  Timer1.initialize(DURATION);
  Timer1.attachInterrupt(timerISR);
   
  //setup PWM: f=38 || 57 Khz PWM=0.5  
  byte v = 8000 / 38;
  TCCR2A = _BV(WGM20);
  TCCR2B = _BV(WGM22) | _BV(CS20); 
  OCR2A = v;
  OCR2B = v / 2;

  // ----------------------------

  Serial.begin(SERIAL_BAUD_RATE);
}

bool busy = false;

void loop()
{  
  if (busy) {
    return;
  } else {
    busy = true;
  }

  // if there is at least a byte to read
  //
  availableBytes = Serial.available();
  if (availableBytes > 0) {

    // read as much as we can fit
    
    int countToRead = availableBytes;
    // int maxAllowedToRead = sizeof(commandBuffer) - commandBufferEndIndex;
    // if (countToRead > maxAllowedToRead) {
    //   countToRead = maxAllowedToRead;
    // }
    
    Serial.print("read ");
    Serial.print(countToRead);
    Serial.print(" bytes. ");

    byte countRead = Serial.readBytes(serialInBuffer, countToRead);
    for (int i = 0; i < countRead; i++)
    {
      commandBuffer[commandBufferEndIndex + i] = serialInBuffer[i];
    }

    commandBufferEndIndex = commandBufferEndIndex + countRead;
    
    if (commandBufferEndIndex < 8) {
      busy = false;
      return;
    }

    byte L = 4;
    byte H1 = 17;
    byte H2 = 171;

    for (size_t i = 0; i <= commandBufferEndIndex - (L + 4); i++)
    {
      bool headerOK = (commandBuffer[0 + i] == H1) && (commandBuffer[1 + i] == H2);
      if (!headerOK) {
        continue;
      }

      bool expectedLength = (commandBuffer[2 + i] == L);
      if (!expectedLength) {
        continue;
      }

      byte d1 = commandBuffer[3 + i];
      byte d2 = commandBuffer[4 + i];
      byte d3 = commandBuffer[5 + i];
      byte d4 = commandBuffer[6 + i];

      byte T = commandBuffer[7 + i];

      bool checksumOK = (d1 + d2 + d3 + d4) % 256 == T;
      if (!checksumOK) {
        continue;
      }

      // extract command

      command[0] = d1;
      command[1] = d2;
      command[2] = d3;
      command[3] = d4;

      Serial.print("GOOD!");
      Serial.write(command, 4);
      Serial.print("done.");

      // shift contents right of command left, dropping command and preceding bytes

      byte remainderCount = commandBufferEndIndex - (i + 8);
      for (size_t j = 0; j < remainderCount; j++) {
        commandBuffer[j] = commandBuffer[i + 8 + j];
      }

      commandBufferEndIndex = remainderCount;

      break;
    }    
  }

  busy = false;
}
