// sungate: serial -> IR gateway for the Syma S107G.
//
// Reads SSSP packets (see sssp.h) from the host and transmits the latest
// command as IR every 180 ms, after Kerry D Wong's protocol analysis.
//
// The IR command is sent from loop(), not from a timer interrupt, so the
// serial receive interrupt keeps running during the 24-36 ms it takes to
// send one: incoming bytes queue in the 64-byte serial buffer instead of
// being lost, and the command is only ever read and written in loop(), so
// it can't be sent half-updated.

#include "sssp.h"

const long SERIAL_BAUD_RATE = 9600;

// comment this out to see the demodulated waveform
// it is useful for debugging purpose.
#define MODULATED 1

const int IR_PIN = 3;
const unsigned long COMMAND_INTERVAL_US = 180000UL;
const int HEADER_DURATION = 2000;
const int HIGH_DURATION = 380;
const int ZERO_LOW_DURATION = 220;
const int ONE_LOW_DURATION = 600;

// Neutral values as flown (control.py) and as decoded by Wong.
const uint8_t YAW_NEUTRAL = 60;
const uint8_t PITCH_NEUTRAL = 63;
const uint8_t TRIM_DEFAULT = 52;

// No valid packet for this long and the failsafe ramps throttle down,
// THROTTLE_RAMP_STEP per command (every 180 ms): from a hover throttle
// of about 95 to 0 in about 3.5 s. Checked on the bench 2026-11-18
// (from throttle 80; see README, Bench results).
const sssp::Failsafe FAILSAFE = {1000, 5, YAW_NEUTRAL, PITCH_NEUTRAL};

sssp::Decoder decoder;
uint8_t received[sssp::DATA_LENGTH] = {YAW_NEUTRAL, PITCH_NEUTRAL, 0, TRIM_DEFAULT};
uint8_t transmitted[sssp::DATA_LENGTH] = {YAW_NEUTRAL, PITCH_NEUTRAL, 0, TRIM_DEFAULT};
bool everReceived = false;
unsigned long lastPacketMs = 0;
unsigned long lastSendUs = 0;

void carrierOn() {
#ifndef MODULATED
  digitalWrite(IR_PIN, HIGH);
#else
  TCCR2A |= _BV(COM2B1);
#endif
}

void carrierOff() {
#ifndef MODULATED
  digitalWrite(IR_PIN, LOW);
#else
  TCCR2A &= ~_BV(COM2B1);
#endif
}

void sendHeader() {
  carrierOn();
  delayMicroseconds(HEADER_DURATION);
  carrierOff();
  delayMicroseconds(HEADER_DURATION);
  carrierOn();
  delayMicroseconds(HIGH_DURATION);
  carrierOff();
}

void sendBit(bool one) {
  delayMicroseconds(one ? ONE_LOW_DURATION : ZERO_LOW_DURATION);
  carrierOn();
  delayMicroseconds(HIGH_DURATION);
  carrierOff();
}

void sendByte(uint8_t value) {
  for (int i = 7; i >= 0; i--) sendBit((value >> i) & 1);
}

void sendCommand(const uint8_t* command) {
  sendHeader();
  for (uint8_t i = 0; i < sssp::DATA_LENGTH; i++) sendByte(command[i]);
}

void setup() {
  // configure the IR pin for output
  pinMode(IR_PIN, OUTPUT);
  digitalWrite(IR_PIN, LOW);

  // configure the carrier PWM on timer 2: duty 0.5, f = 38 kHz
  // (16 MHz / (2 * 210) = 38.1 kHz, phase correct, OCR2A as top)
  byte v = 8000 / 38;
  TCCR2A = _BV(WGM20);
  TCCR2B = _BV(WGM22) | _BV(CS20);
  OCR2A = v;
  OCR2B = v / 2;

  Serial.begin(SERIAL_BAUD_RATE);
  lastSendUs = micros();
}

void loop() {
  // decode whatever has arrived; echo each valid packet so the host can
  // confirm receipt
  while (Serial.available() > 0) {
    if (decoder.feed((uint8_t)Serial.read())) {
      for (uint8_t i = 0; i < sssp::DATA_LENGTH; i++) received[i] = decoder.data()[i];
      everReceived = true;
      lastPacketMs = millis();

      uint8_t packet[sssp::PACKET_LENGTH];
      sssp::encode(received, packet);
      Serial.write(packet, sssp::PACKET_LENGTH);
    }
  }

  unsigned long nowUs = micros();
  if (nowUs - lastSendUs >= COMMAND_INTERVAL_US) {
    lastSendUs = nowUs;
    unsigned long sinceMs = everReceived ? millis() - lastPacketMs : FAILSAFE.timeout_ms;
    sssp::next_transmit(received, sinceMs, FAILSAFE, transmitted);
    sendCommand(transmitted);
  }
}
