// AS5600 knob test rig logger (XIAO ESP32-S3). Streams CSV at ~100 Hz over USB serial:
//   t_ms,raw_angle,agc,magnitude,status
// raw_angle 0..4095 (12-bit), agc 0..255 (0..128 at 3.3 V), magnitude 12-bit CORDIC, status bits MD(5) ML(4) MH(3).
// Send a character over serial to drop a marker line "#mark <char>" into the log (label test phases).
// Wiring: AS5600 VCC->3V3, GND->GND, SDA->D4, SCL->D5, DIR->GND.
#include <Wire.h>

static const uint8_t AS5600 = 0x36;
static const uint32_t PERIOD_US = 10000;   // 100 Hz

static bool readRegs(uint8_t reg, uint8_t *buf, uint8_t n) {
  Wire.beginTransmission(AS5600);
  Wire.write(reg);
  if (Wire.endTransmission(false) != 0) return false;
  if (Wire.requestFrom(AS5600, n) != n) return false;
  for (uint8_t i = 0; i < n; i++) buf[i] = Wire.read();
  return true;
}

void setup() {
  Serial.begin(115200);
  Wire.begin();            // XIAO ESP32-S3: SDA = D4, SCL = D5
  Wire.setClock(400000);
  delay(500);
  Serial.println("#as5600_rig start");
  Serial.println("t_ms,raw_angle,agc,magnitude,status");
}

void loop() {
  static uint32_t next = micros();
  while (Serial.available()) {
    char c = Serial.read();
    if (c > ' ') Serial.printf("#mark %c\n", c);
  }
  uint32_t now = micros();
  if ((int32_t)(now - next) < 0) return;
  next += PERIOD_US;
  if ((int32_t)(now - next) > 0) next = now + PERIOD_US;   // fell behind (USB stall): resync, don't burst

  uint8_t st, ang[2], agc, mag[2];
  if (!readRegs(0x0B, &st, 1) || !readRegs(0x0C, ang, 2) || !readRegs(0x1A, &agc, 1) || !readRegs(0x1B, mag, 2)) {
    Serial.println("#i2c_error");
    delay(200);
    return;
  }
  Serial.printf("%lu,%u,%u,%u,%u\n", (unsigned long)millis(), ((ang[0] & 0x0F) << 8) | ang[1], agc,
                ((mag[0] & 0x0F) << 8) | mag[1], st & 0x38);
}
