// Super simple serial protocol (SSSP) and the transmit failsafe.
//
// Plain C++ with no Arduino dependency, so the same code runs in the
// sketch and in the host tests (tests/firmware/test_sssp.cpp).
//
// Packet: H1, H2, DATA_LENGTH, 4 data bytes, checksum (sum of the data
// bytes mod 256). Data bytes are the IR command in wire order:
// yaw (leftright), pitch (fwdback), throttle, trim (calib).

#pragma once

#include <stdint.h>

namespace sssp {

const uint8_t H1 = 17;
const uint8_t H2 = 171;
const uint8_t DATA_LENGTH = 4;
const uint8_t PACKET_LENGTH = 3 + DATA_LENGTH + 1;

const uint8_t YAW = 0;
const uint8_t PITCH = 1;
const uint8_t THROTTLE = 2;
const uint8_t TRIM = 3;

inline uint8_t checksum(const uint8_t* data) {
  uint8_t sum = 0;
  for (uint8_t i = 0; i < DATA_LENGTH; i++) sum += data[i];
  return sum;
}

// Writes a full packet for data into out (PACKET_LENGTH bytes).
inline void encode(const uint8_t* data, uint8_t* out) {
  out[0] = H1;
  out[1] = H2;
  out[2] = DATA_LENGTH;
  for (uint8_t i = 0; i < DATA_LENGTH; i++) out[3 + i] = data[i];
  out[3 + DATA_LENGTH] = checksum(data);
}

// Streaming decoder: one byte at a time, constant memory, so junk on
// the line can never overflow a buffer. After a bad length or checksum
// it waits for the next header; the host resends often, so a dropped
// packet is replaced within one keepalive period.
class Decoder {
 public:
  // Returns true when b completes a valid packet; its data is in data().
  bool feed(uint8_t b) {
    switch (state_) {
      case WAIT_H1:
        if (b == H1) state_ = WAIT_H2;
        return false;
      case WAIT_H2:
        if (b == H2) state_ = WAIT_LENGTH;
        else if (b != H1) state_ = WAIT_H1;
        return false;
      case WAIT_LENGTH:
        if (b == DATA_LENGTH) {
          state_ = WAIT_DATA;
          count_ = 0;
        } else {
          rejected_++;
          state_ = (b == H1) ? WAIT_H2 : WAIT_H1;
        }
        return false;
      case WAIT_DATA:
        buffer_[count_++] = b;
        if (count_ == DATA_LENGTH) state_ = WAIT_CHECKSUM;
        return false;
      case WAIT_CHECKSUM:
        if (b == checksum(buffer_)) {
          for (uint8_t i = 0; i < DATA_LENGTH; i++) data_[i] = buffer_[i];
          accepted_++;
          state_ = WAIT_H1;
          return true;
        }
        rejected_++;
        state_ = (b == H1) ? WAIT_H2 : WAIT_H1;
        return false;
    }
    state_ = WAIT_H1;
    return false;
  }

  const uint8_t* data() const { return data_; }
  uint16_t accepted() const { return accepted_; }
  uint16_t rejected() const { return rejected_; }

 private:
  enum State { WAIT_H1, WAIT_H2, WAIT_LENGTH, WAIT_DATA, WAIT_CHECKSUM };
  State state_ = WAIT_H1;
  uint8_t buffer_[DATA_LENGTH] = {0};
  uint8_t data_[DATA_LENGTH] = {0};
  uint8_t count_ = 0;
  uint16_t accepted_ = 0;
  uint16_t rejected_ = 0;
};

struct Failsafe {
  uint32_t timeout_ms;      // silence before the failsafe takes over
  uint8_t throttle_step;    // throttle drop per transmitted command
  uint8_t yaw_neutral;
  uint8_t pitch_neutral;
};

// Chooses the next command to transmit. transmitted holds the previous
// transmitted command on entry and the next one on exit.
//
// While packets arrive (since_ms < timeout_ms) the last received command
// is sent as is. After timeout_ms of silence, yaw and pitch go to neutral,
// trim is kept, and throttle falls by throttle_step per command until 0,
// so a lost host brings the helicopter down instead of holding its last
// throttle until the battery runs out.
inline void next_transmit(const uint8_t* received, uint32_t since_ms,
                          const Failsafe& failsafe, uint8_t* transmitted) {
  if (since_ms < failsafe.timeout_ms) {
    for (uint8_t i = 0; i < DATA_LENGTH; i++) transmitted[i] = received[i];
    return;
  }
  transmitted[YAW] = failsafe.yaw_neutral;
  transmitted[PITCH] = failsafe.pitch_neutral;
  uint8_t throttle = transmitted[THROTTLE];
  transmitted[THROTTLE] =
      throttle > failsafe.throttle_step ? throttle - failsafe.throttle_step : 0;
}

}  // namespace sssp
