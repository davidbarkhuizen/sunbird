String data="Hello From Arduino!";

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
  Serial.begin(9600);
}

int received = 0;

int delayMS = 0;

void loop() {
  if (delayMS > 0) {
    digitalWrite(LED_BUILTIN, LOW);
    delay(delayMS);
  }

  digitalWrite(LED_BUILTIN, HIGH);

  if (Serial.available() > 0) {

    delayMS = Serial.read();

    Serial.print("delay updated to: ");
    Serial.print(delayMS);
    Serial.println();
  }
}
