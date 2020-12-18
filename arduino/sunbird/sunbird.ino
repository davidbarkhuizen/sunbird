#include <TimerOne.h>

int availableBytes;
char receivedCommand[3];

char power;
short leftRight;
short fwdBack; 

const int IR_PIN = 3;
const unsigned long DURATION = 180000l;
const int HEADER_DURATION = 2000;
const int HIGH_DURATION = 380;
const int ZERO_LOW_DURATION = 220;
const int ONE_LOW_DURATION = 600;
const byte ROTATION_STATIONARY = 60;
const byte CAL_BYTE = 52;

void sendHeader()
{
  digitalWrite(IR_PIN, HIGH);
  delayMicroseconds(HEADER_DURATION);

  digitalWrite(IR_PIN, LOW);
  delayMicroseconds(HEADER_DURATION);
  
  digitalWrite(IR_PIN, HIGH);
  delayMicroseconds(HIGH_DURATION);
  
  digitalWrite(IR_PIN, LOW);
}
 
void sendZero()
{
  delayMicroseconds(ZERO_LOW_DURATION);
  digitalWrite(IR_PIN, HIGH);
  delayMicroseconds(HIGH_DURATION);
  digitalWrite(IR_PIN, LOW);
}
 
void sendOne()
{
  delayMicroseconds(ONE_LOW_DURATION);
  digitalWrite(IR_PIN, HIGH);
  delayMicroseconds(HIGH_DURATION);
  digitalWrite(IR_PIN, LOW);  
}
 
void sendCommand(int throttle, int leftRight, int forwardBackward)
{
  byte b;
 
  sendHeader();
   
  for (int i = 7; i >=0; i--)
  {
    b = ((ROTATION_STATIONARY + leftRight) & (1 << i)) >> i;    
    if (b > 0) sendOne(); else sendZero();
  }
   
  for (int i = 7; i >=0; i--)
  {
    b = ((63 + forwardBackward) & (1 << i)) >> i;    
    if (b > 0) sendOne(); else sendZero();
  } 
   
  for (int i = 7; i >=0; i--)
  {
    b = (throttle & (1 << i)) >> i;    
    if (b > 0) sendOne(); else sendZero();
  }
   
  for (int i = 7; i >=0; i--)
  {
    b = (CAL_BYTE & (1 << i)) >> i;    
    if (b > 0) sendOne(); else sendZero();
  } 
}

void setup() {

  pinMode(IR_PIN, OUTPUT);
  digitalWrite(IR_PIN, LOW);
 
  //setup interrupt interval: 180ms  
  Timer1.initialize(DURATION);
  Timer1.attachInterrupt(timerISR);
   
  //setup PWM: f = [38 | 57] Khz PWM=0.5  
  byte v = 8000 / 57;
  TCCR2A = _BV(WGM20);
  TCCR2B = _BV(WGM22) | _BV(CS20); 
  OCR2A = v;
  OCR2B = v / 2;
  
//  Serial.begin(9600);
}

void loop() {

//  availableBytes = Serial.available();
//  if (availableBytes >= 3) {
//    Serial.readBytes(receivedCommand, 3);
//
//    power = receivedCommand[0];
//    leftRight = (short)receivedCommand[1];
//    fwdBack = (short)receivedCommand[2];    
//  }
}

  void timerISR() {
  sendCommand(150, 0, 0);
  // sendCommand((int)power, (int)leftRight, (int)fwdBack);
}
