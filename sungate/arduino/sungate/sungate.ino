#include <TimerOne.h>
 
int availableBytes;
char receivedCommand[3];

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
const byte ROTATION_STATIONARY = 60;
const byte CAL_BYTE = 52; 
 
int Throttle, LeftRight, FwdBack;

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

void sendBytes(byte B[4]) {
  byte b;
  for (int i = 0; i < 4; i++)
  {
    sendByte(B[i]);
  }
}

void sendCommand(int throttle, int leftRight, int forwardBackward)
{
  sendHeader();

  byte b[4];
  b[0] = (byte)(ROTATION_STATIONARY + leftRight);
  b[1] = (byte)(63 + forwardBackward);
  b[2] = (byte)throttle;
  b[4] = CAL_BYTE;

  sendBytes(b);
}

void timerISR()
{
  sendCommand(Throttle, LeftRight, FwdBack);
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

byte writeToSerial[4];

void loop()
{  
  availableBytes = Serial.available();
  if (availableBytes >= 3) {
    Serial.readBytes(receivedCommand, 3);

    Throttle = receivedCommand[0]; // 0 to 255
    LeftRight = (int)((short)receivedCommand[1]); // -64 to 63
    FwdBack = (int)((short)receivedCommand[2]); // -128 to 127

    writeToSerial[0] = (byte)(ROTATION_STATIONARY + LeftRight);
    writeToSerial[1] = (byte)(63 + FwdBack);
    writeToSerial[2] = (byte)Throttle;
    writeToSerial[4] = CAL_BYTE;
    Serial.write(writeToSerial, 4);
    Serial.print("");
  }
}