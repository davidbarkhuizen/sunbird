int delayMS;
int availableBytes;
char receivedCommand[3];

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
  else {
    Serial.write(8);
    delay(1000);
  }

  availableBytes = Serial.available();
  if (availableBytes >= 3) {
    Serial.readBytes(receivedCommand, 3);
    delayMS = (int)receivedCommand[0];
    Serial.write(delayMS);
  }
}
