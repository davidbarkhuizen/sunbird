void setup() {
  pinMode(LED_BUILTIN, OUTPUT);
}

void longOn() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(1000);
}

void shortOn() {
  digitalWrite(LED_BUILTIN, HIGH);
  delay(100);
}

void longOff() {
  digitalWrite(LED_BUILTIN, LOW);
  delay(1000);
}

void shortOff() {
  digitalWrite(LED_BUILTIN, LOW);
  delay(100);
}


void loop() {
  longOn();
  shortOff();
  longOn();
  shortOff();
  longOn();
  shortOff();

  longOff();
}
