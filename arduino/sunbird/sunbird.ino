int delayMS;
int availableBytes;
char receivedCommand[3];

char power;
short leftRight;
short fwdRev; 

void setup() {
  delayMS = 0;
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
}

void loop() {

  if (delayMS > 0) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(delayMS);
    digitalWrite(LED_BUILTIN, LOW);
    delay(delayMS);
  }

  availableBytes = Serial.available();
  if (availableBytes >= 3) {
    Serial.readBytes(receivedCommand, 3);

    power = receivedCommand[0];
    leftRight = (short)receivedCommand[1];
    fwdRev = (short)receivedCommand[2];    
    
    delayMS = power;
    Serial.println(power);
    Serial.println(leftRight);
    Serial.println(fwdRev);
  }
}
