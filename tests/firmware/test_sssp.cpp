// Host tests for the firmware's SSSP decoder and failsafe (sssp.h).
// Built and run by tests/test_firmware.py.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <vector>

#include "../../sungate/arduino/sungate/sssp.h"

static int failures = 0;

#define CHECK(cond)                                                  \
  do {                                                               \
    if (!(cond)) {                                                   \
      std::printf("%s:%d: CHECK failed: %s\n", __FILE__, __LINE__, #cond); \
      failures++;                                                    \
    }                                                                \
  } while (0)

static std::vector<uint8_t> packet(uint8_t a, uint8_t b, uint8_t c, uint8_t d) {
  uint8_t data[4] = {a, b, c, d};
  uint8_t out[sssp::PACKET_LENGTH];
  sssp::encode(data, out);
  return std::vector<uint8_t>(out, out + sssp::PACKET_LENGTH);
}

// Feeds bytes; returns the decoded packets.
static std::vector<std::vector<uint8_t>> feed(sssp::Decoder& decoder,
                                              const std::vector<uint8_t>& bytes) {
  std::vector<std::vector<uint8_t>> out;
  for (uint8_t b : bytes) {
    if (decoder.feed(b)) out.emplace_back(decoder.data(), decoder.data() + 4);
  }
  return out;
}

static void test_encode_matches_host_format() {
  // Same bytes as the gateway's encode(): [17, 171, 4, data..., sum % 256]
  auto p = packet(60, 63, 95, 52);
  const uint8_t expected[] = {17, 171, 4, 60, 63, 95, 52, (60 + 63 + 95 + 52) % 256};
  CHECK(p.size() == sizeof(expected));
  CHECK(std::memcmp(p.data(), expected, sizeof(expected)) == 0);
}

static void test_decodes_one_packet() {
  sssp::Decoder d;
  auto got = feed(d, packet(60, 63, 95, 52));
  CHECK(got.size() == 1);
  CHECK(got[0] == std::vector<uint8_t>({60, 63, 95, 52}));
  CHECK(d.accepted() == 1);
  CHECK(d.rejected() == 0);
}

static void test_resyncs_after_junk_and_lost_bytes() {
  sssp::Decoder d;
  std::vector<uint8_t> bytes = {0, 255, 17, 17, 3, 171};  // junk, header fragments
  auto first = packet(1, 2, 3, 4);
  first.erase(first.begin() + 4);  // a lost data byte: this packet must be dropped
  bytes.insert(bytes.end(), first.begin(), first.end());
  auto second = packet(60, 63, 0, 52);
  bytes.insert(bytes.end(), second.begin(), second.end());
  auto got = feed(d, bytes);
  // The damaged packet swallows the next packet's header into its
  // checksum slot at worst; the stream must still recover by the third.
  auto third = packet(60, 63, 90, 52);
  auto more = feed(d, third);
  CHECK(!more.empty());
  CHECK(more.back() == std::vector<uint8_t>({60, 63, 90, 52}));
  for (auto& g : got) CHECK(g != std::vector<uint8_t>({1, 2, 3, 4}));
}

static void test_rejects_bad_checksum() {
  sssp::Decoder d;
  auto p = packet(60, 63, 95, 52);
  p.back() ^= 1;
  CHECK(feed(d, p).empty());
  CHECK(d.rejected() == 1);
}

static void test_header_byte_inside_data() {
  // Data bytes equal to H1/H2 must not confuse the decoder.
  sssp::Decoder d;
  auto got = feed(d, packet(17, 171, 17, 171));
  CHECK(got.size() == 1);
  CHECK(got[0] == std::vector<uint8_t>({17, 171, 17, 171}));
}

static void test_long_junk_never_overflows() {
  // The old decoder appended to a 64-byte buffer until a packet was
  // found; a long run of junk overflowed it. The streaming decoder holds
  // no buffer to overflow; check it still decodes after 10k junk bytes.
  sssp::Decoder d;
  std::vector<uint8_t> junk;
  std::srand(1);
  for (int i = 0; i < 10000; i++) junk.push_back((uint8_t)(std::rand() & 0xff));
  feed(d, junk);
  auto got = feed(d, packet(60, 63, 95, 52));
  CHECK(!got.empty());
  CHECK(got.back() == std::vector<uint8_t>({60, 63, 95, 52}));
}

static void test_failsafe() {
  const sssp::Failsafe fs = {1000, 5, 60, 63};
  uint8_t received[4] = {80, 20, 95, 50};
  uint8_t tx[4] = {0, 0, 0, 0};

  sssp::next_transmit(received, 999, fs, tx);  // fresh: pass through
  CHECK(std::memcmp(tx, received, 4) == 0);

  sssp::next_transmit(received, 1000, fs, tx);  // stale: neutral, ramp down
  CHECK(tx[sssp::YAW] == 60);
  CHECK(tx[sssp::PITCH] == 63);
  CHECK(tx[sssp::THROTTLE] == 90);
  CHECK(tx[sssp::TRIM] == 50);

  int steps = 0;
  while (tx[sssp::THROTTLE] > 0 && steps < 100) {
    sssp::next_transmit(received, 5000, fs, tx);
    steps++;
  }
  CHECK(tx[sssp::THROTTLE] == 0);
  CHECK(steps == 18);  // 90 / 5
  sssp::next_transmit(received, 5000, fs, tx);  // stays at 0, no wrap
  CHECK(tx[sssp::THROTTLE] == 0);

  uint8_t odd[4] = {60, 63, 3, 52};  // step larger than what's left
  sssp::next_transmit(odd, 0, fs, tx);
  sssp::next_transmit(odd, 2000, fs, tx);
  CHECK(tx[sssp::THROTTLE] == 0);
}

int main() {
  test_encode_matches_host_format();
  test_decodes_one_packet();
  test_resyncs_after_junk_and_lost_bytes();
  test_rejects_bad_checksum();
  test_header_byte_inside_data();
  test_long_junk_never_overflows();
  test_failsafe();
  if (failures) {
    std::printf("%d check(s) failed\n", failures);
    return 1;
  }
  std::printf("all firmware checks passed\n");
  return 0;
}
