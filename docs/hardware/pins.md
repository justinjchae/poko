# Pin and peripheral budget: XIAO → Raytac MDBT50Q-P1MV2

**Written:** 2026-10-05 for the schematic work. Taken from
`firmware/app/boards/xiao_ble_nrf52840_sense.overlay`, `as5600.overlay` and the Zephyr XIAO board files at `d5af456`, and
from the Raytac MDBT50Q-1MV2/P1MV2 spec (pin assignment §2.5–2.6, reference circuits §8).

## Update 2026-10-08 (supersedes the text below where they disagree)

The 2026-10-07 power decisions replaced the BQ25120A with the MCP73831 and set a 3.0 V rail. Concretely:
- **I2C:** there is no I2C charger, so the IMU stays at **0x6A** (SA0 low); point 2 below no longer applies. Bus: IMU 0x6A, DRV2605L 0x5A (3.3k pull-ups).
- **Charger pins:** only STAT on **P1.06**. P1.07 (/CD) and the BQ25120A MR idea are dropped.
- **Rail:** UICR.REGOUT0 = **3.0 V** (not 3.3 V). Display, flash and IMU all run at 3.0 V.
- **Backlight:** the PWM on P0.25 drives the reference of a discrete constant-current sink (AO3400A + TLV9001); the op-amp supply is a GPIO, **BL_EN**, which needs a pin (not yet assigned; take it from the low-frequency spares, e.g. P1.04).
- **Display TE** (P1.02) is worth routing; the Shineworld panel has the pin.
- Ring sensing, select button pin (P1.10) and the haptic IN/TRIG pin are unchanged and still open.

## Read this first: four things that change the schematic

1. **21 of the module's 48 GPIOs are "standard drive, low frequency I/O only" (≤ 10 kHz).** Raytac §2.6 is explicit:
   "SPI, I2C, UART, PWM are NOT low frequency I/O". These pins sit near the radio. They are:
   P0.02, P0.03, P0.09, P0.10, P0.28–P0.31, P1.01–P1.07, P1.10–P1.15.
   **On the XIAO, the display's SPI clock and data (P1.13, P1.15), the backlight PWM (P1.12) and the haptic PWM (P0.02)
   all sit on these pins.** They work on the bench, but they must move on our board. The table below does that.
2. **I2C address clash: the BQ25120A charger is fixed at 0x6A, and so is the LSM6DS3TR-C with SA0 low.** Tie the
   IMU's SDO/SA0 pin **high**, so the IMU is at **0x6B**. The DRV2605L is at 0x5A. All three can then share one bus.
   The firmware change is a one-line `reg` edit.
3. **Fit the 32.768 kHz crystal on P0.00/P0.01** (Raytac's X2 + C12/C13). The firmware runs on the crystal today
   (`CLOCK_CONTROL_NRF_K32SRC_XTAL=y`), and BLE stays connected all day, so a crystal saves power over the RC oscillator.
   The 32 MHz crystal and the REG1 DC/DC inductor are already inside the module.
4. **P0.18 stays as reset** (`gpio-as-nreset`; reset must be reachable from outside). Raytac lists P0.18 as a
   "recommended QSPI CSN" pin, so ignore that suggestion and use the nRF52840 DK's QSPI pins instead (below).

## What the firmware uses today (XIAO) and where it goes

"Instance" = the nRF52840 peripheral the firmware binds to. Peripherals that share an ID can't both be on:
SPIM0/TWIM0 share one, SPIM1/TWIM1 share one, and SPIM2 and SPIM3 each stand alone. QSPI, PDM, PWM0–3 and SAADC are
separate. Any signal can go on any pin (the nRF52840 routes pins freely), **except** the analog inputs (fixed AIN pins),
USB, SWD, the 32 kHz crystal and reset.

| Function | Signal | XIAO pin | XIAO nRF pin | Instance | Needs | Proposed pin | Notes |
|---|---|---|---|---|---|---|---|
| Display (GC9A01) | SCK | D8 | P1.13 ⚠ | **SPIM3** (32 MHz, DMA) | full speed | **P0.13** | SPIM3 is the only 32 MHz SPI; a full redraw is several times faster than on SPIM2 |
| | MOSI | D10 | P1.15 ⚠ | SPIM3 | full speed | **P0.14** | write-only, no MISO |
| | CS | D1 | P0.03 ⚠ | GPIO (SPIM3 cs-gpios) | full speed | **P0.15** | |
| | DC | D2 | P0.28 ⚠ | GPIO | full speed | **P0.16** | toggles on every command/data switch |
| | RST | D3 | P0.29 | GPIO | any | P1.01 | slow, so low-frequency is fine |
| | TE (new, if the FPC has it) | — | — | GPIO in | any | P1.02 | optional; 60 Hz tear signal |
| Backlight | PWM to a MOSFET gate | D7 | P1.12 ⚠ | **PWM1** ch1 | full speed (PWM) | **P0.25** | **must have** (LOCK.md). Unwired on the Hosyond |
| External flash | SCK | (on-board) | P0.21 | **QSPI** | full speed | **P0.19** | nRF52840 DK pins (proven at 32 MHz, H0H1 drive) |
| | CSN | | P0.25 | QSPI | full speed | **P0.17** | |
| | IO0–IO3 | | P0.20, P0.24, P0.22, P0.23 | QSPI | full speed | **P0.20–P0.23** | in order IO0..IO3 |
| | | | | | | | Only one QSPI. A QSPI AMOLED (LOCK.md "future run") would conflict, so it would need SPIM3 instead |
| Microphone (PDM) | CLK | (on-board) | P1.00 | **PDM0** | full speed (~1.3 MHz) | **P0.06** | |
| | DIN | | P0.16 | PDM0 | full speed | **P0.08** | |
| | Power enable | | P1.10 (high drive) | GPIO | high drive | **P1.08** | the XIAO powers the mic from a GPIO; keeps the mic at 0 µA off. Or power it from 3V3 and drop the pin |
| IMU (LSM6DS3TR-C) | SDA / SCL | (on-board) | P0.07 / P0.27 | **TWIM0** (400 kHz) | full speed | **P0.26 / P0.27** | shared bus: IMU 0x6B, DRV2605L 0x5A, BQ25120A 0x6A |
| | INT1 | | P0.11 | GPIO in | any | **P0.11** | not used yet (polling, 009), but routing it is free (LOCK.md) |
| | Power enable | | P1.08 | GPIO | — | **drop** | the XIAO gates the IMU; ours can power it from 3V3. 009: polling costs < 0.1 mA |
| Haptic (today) | ERM PWM | D0 | P0.02 ⚠ | PWM1 ch0 | — | **goes away** | replaced by the DRV2605L |
| Ring (today) | EC11 A / B | D4 / D5 | P0.04 / P0.05 | GPIO (gpio-qdec) | — | **goes away** | replaced by the optical ring (below) |
| Ring (AS5600 variant) | SDA / SCL | D4 / D5 | P0.04 / P0.05 | TWIM1 | — | — | only if the AS5600 wins; it would join the shared TWIM0 bus at 0x36 |
| Select button | switch to GND | D6 | P1.11 | GPIO in, pull-up | any | P1.10 | wakes from sleep (GPIO sense works on every pin) |
| Battery sense | divider tap | (on-board) | P0.31 / AIN7 | **SAADC** ch7 | AIN pin | **P0.31 / AIN7** | analog is fine on a low-frequency pin |
| | divider enable | | P0.14 | GPIO out | any | P1.05 | switches the divider off so it doesn't drain the cell |
| Charger status | STAT / CHG | (on-board) | P0.17 | GPIO in, pull-up | any | see charger below | |
| USB | D+ / D− / VBUS | USB-C | dedicated | USBD | dedicated | module pins 35 / 34 / 32 | stays wired (015 recovery path). "On USB power" is read from VBUS internally, so no GPIO is needed |
| SWD | SWDIO / SWDCLK | pads under the XIAO | dedicated | — | dedicated | module pins 51 / 53 | to a Tag-Connect or pads, with reset, 3V3, GND |
| Reset | nRESET | button | P0.18 | — | fixed | **P0.18** | reachable from outside |
| SWO (trace, optional) | SWO | — | P1.00 | — | fixed | P1.00 | on a TC2030-CTX footprint it's the 6th pin. Free because QSPI doesn't use P1.00 here |
| 32 kHz crystal | XL1 / XL2 | (on-board) | P0.00 / P0.01 | LFXO | fixed | **P0.00 / P0.01** | fit it (point 3) |
| XIAO RGB LED | | | P0.26, P0.30, P0.06 | — | — | **drop** | the firmware doesn't use it |

⚠ = a low-frequency-only pin on the module that carries a fast signal today. It has to move.

## New parts with no pin yet

| Function | Signal | Instance | Proposed pin | Notes |
|---|---|---|---|---|
| **DRV2605L** (LRA driver) | SDA / SCL | TWIM0 (shared) | P0.26 / P0.27 | 0x5A |
| | EN | GPIO out | P1.03 | low = 1 µA shutdown |
| | IN/TRIG | GPIO / PWM | **P0.12** | optional, but cheap. An external trigger fires a detent click without an I2C write, which may help detent latency. It's on a full-speed pin so PWM input mode stays possible. With only edge triggers it could move to a low-frequency pin |
| **Optical ring** (2× ITR8307) | sensor A | GPIO **or** AIN | **P0.04 / AIN2** | these are the only two pins that are both analog **and** full speed, so either design works (see below) |
| | sensor B | GPIO **or** AIN | **P0.05 / AIN3** | |
| | IR emitter enable | GPIO (QDEC LED) | **P1.09** | through a transistor. Each emitter wants more current than a GPIO gives |
| **Battery sense** | divider tap + enable | SAADC + GPIO | P0.31/AIN7 + P1.05 | as on the XIAO (above) |
| **Charger, BQ25120A** | SDA / SCL | TWIM0 (shared) | P0.26 / P0.27 | 0x6A, so the IMU moves to 0x6B (point 2) |
| | /INT | GPIO in | P1.06 | charge and fault events |
| | /CD | GPIO out | P1.07 | chip disable / high-impedance mode |
| | MR (manual reset / ship-mode wake) | — | to the select button? | an open design question, not a pin: the BQ25120A can wake from ship mode on a button press |
| Charger, MCP73831 fallback | STAT | GPIO in | P1.06 | same pin, if the fallback is chosen |
| **Backlight PWM** | gate drive | PWM1 ch1 | P0.25 | (above) |

**Optical ring, GPIO vs ADC.** The nRF52840 has a hardware **QDEC** peripheral with its own LED-enable output. It pulses
the emitters only while it samples, so the ring costs almost nothing when idle. That's the reason to put emitter enable
on its own GPIO. If the reflective signal is too weak for a clean digital edge, the same two pins can be read on the
SAADC instead. Putting each sensor on an AIN pin that is also full speed keeps both options open until the bench test
decides.

## Spare pins (to break out: Justin's rule)

After everything above:
- **Full speed, free:** P0.07, P0.24 (+ P1.00 if SWO isn't used). **Break out P0.07 and P0.24.**
- **Analog-capable, low frequency:** P0.02/AIN0, P0.03/AIN1, P0.28/AIN4, P0.29/AIN5, P0.30/AIN6. **Break out
  P0.02/AIN0 and P0.03/AIN1.**
- **Low frequency only:** P0.09, P0.10 (NFC pins; need `nfct-pins-as-gpios`), P1.04, P1.11–P1.15.
- Pads: 3V3, GND, reset (P0.18).

Budget: 48 GPIOs = 27 full speed + 21 low frequency. This plan uses 21 full-speed pins (counting P0.00/P0.01 for the
crystal and P0.18 for reset, it's 24 of 27) and 7 low-frequency ones (8 with TE), which leaves 13 low-frequency pins spare. **Full speed is the tight resource.**
Only P0.07, P0.24 and P1.00 are left, so any new fast signal (a second SPI, a QSPI display) means taking one back. The
IN/TRIG pin (P0.12) is the first to give up.

## Power-architecture notes that touch the module

- The module takes a LiPo straight on **VDDH** (Raytac §8.1/8.2, "highest input ≥ 3.6 V"), using REG0 to make VDD. That
  could replace a separate LDO, depending on the charger choice. Then the firmware has to set **UICR.REGOUT0 to 3.3 V**,
  because it defaults to 1.8 V, which the display and flash won't run on. Easy in firmware, but it must be planned.
  Raytac §8.3 (VDD direct, no REG0) is for a regulated supply under 3.6 V.
- The REG0 DC/DC needs the external 10 µH inductor (L4, 0603, ≥ 80 mA) and the 32 kHz crystal parts. Remove the NFC
  parts (NFC1/C19/C21) since we don't use NFC.

## Firmware changes this implies (later, not now)

A new board definition (devicetree + pinctrl) with the pins above, IMU `reg = <0x6b>`, the W25Q128JV in place of the
XIAO's P25Q16H (that chip is 2 MB, and the memo store already sizes itself from devicetree), DRV2605L and BQ25120A
nodes, QDEC for the ring, and REGOUT0 = 3.3 V if VDDH is used. The ERM, EC11 and XIAO-gating pins are deleted. None of
this blocks the schematic.

Sources: [Raytac MDBT50Q-1MV2/P1MV2 spec (Seeed mirror)](https://files.seeedstudio.com/products/113990582/res/MDBT50Q-1MV2_datasheet.pdf) ·
[TI BQ25120A datasheet](https://www.ti.com/lit/ds/symlink/bq25120a.pdf) (7-bit address 0x6A) ·
[Nordic DevZone on low-frequency pins](https://devzone.nordicsemi.com/f/nordic-q-a/69155/low-frequency-i-o-signal-usage) ·
nRF52840 DK QSPI pins from `zephyr/boards/nordic/nrf52840dk/nrf52840dk_nrf52840-pinctrl.dtsi`.
