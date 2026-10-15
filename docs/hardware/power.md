# Power measurements

Measured 2026-10-01 on the breadboard-era prototype in Enclosure V1B: XIAO nRF52840 Sense, Hosyond
1.28" GC9A01 module, EC11, ERM, LiPo. Firmware: `./build.sh ec11 power` (the Power Test app).
A multimeter in series with the battery's + lead, USB unplugged, phone (iPhone) connected unless
noted. One reading per state, steady states on a normal meter.

**All numbers are upper bounds.** The XIAO's charger, regulator and LED circuitry, and the display
module's own LDO (U3), add draw a production board won't have.

## Battery current per state (mA)

| State | Link fast (15 ms, latency 0) | Link lazy (30 ms, latency 30) |
|---|---|---|
| Deep idle (screen off, IMU off) | 37.48 | 37.36 |
| IMU polling 5 Hz | 37.38 | 37.94 (noise) |
| IMU polling 12.5 Hz | 37.52 | 37.45 |
| IMU polling 25 Hz | 37.52 | 37.46 |
| Screen on, static | 42.61 | 42.56 |
| Screen on, animating | 43.08 | 43.12 |
| Recording (mic + flash writes) | 44.00 | 43.90 |
| Phone sync (transfer) | 42.58 | 42.58 |
| Haptics (screen off, a click every 0.5 s) | 30–50, unreadable | ~51 at the peaks |

Deep idle with the phone's Bluetooth **off** (advertising only): 37.48 mA.

**Backlight:** 275 mV across R6 on the display module. R6 is marked 8R2 and measures 9 Ω out of
circuit, including the leads. So the backlight is 275 / 8.2 = **33.5 mA**. It's hardwired on (no
BLK pin), so it's included in every reading above, "screen off" ones too.

## What the numbers say

| Component | Draw | Notes |
|---|---|---|
| Backlight, full | 33.5 mA | ~90% of idle, ~79% of screen-on. The biggest lever by far. |
| Everything else, asleep | ~4.0 mA | 37.5 - 33.5. Should be well under 1 mA in production (below). |
| Panel + drawing, screen on | +5.1 mA | DISPON vs DISPOFF, plus LVGL/SPI. |
| Animation | +0.5 mA | over a static screen |
| Recording | +1.4 mA | mic + flash, over screen on |
| IMU polling, any rate to 25 Hz | < 0.1 mA | Below what the meter resolves at a 37 mA baseline. |
| Bluetooth, fast vs lazy vs off | < 0.2 mA | Same. Lazy (30 ms x 31) was accepted by the phone. |
| Haptics | ~+14 mA while buzzing | ERM pulses of 60 ms. A few clicks a minute average out to ~0. |

The 4.0 mA non-backlight sleep floor is mostly fixable in firmware and in the PCB:
- The GC9A01 only gets DISPOFF today. SLPIN (sleep in) cuts its own draw to near zero.
- The QSPI flash can go into deep power-down between uses.
- The XIAO's and the display module's regulators and charge circuit go away on the custom PCB.
A production sleep floor of **~0.5 mA** is a conservative target (nRF52840 System ON idle with a lazy
connection is ~10-50 uA). It's still unmeasured, though: re-measure once the display sleeps properly.

## Battery life estimates

Assumptions: 90% of rated capacity usable. The screen-on draw is the measured 42.6 mA (full
brightness). Recording time is negligible.

Day profiles:
- **Light:** 20 min of screen on (checking, a few memos), asleep the rest.
- **Pomodoro:** 4 h of screen on (the countdown is always visible during sessions), asleep the rest.
- **Gym:** 1 h of screen on for rest timers plus 20 min of other use, asleep the rest.
- **Pomodoro, dimmed:** as Pomodoro, but 3.5 of the 4 h are the idle glance with the backlight at
  50% (needs the backlight MOSFET: 16.8 + 9.1 mA).

| Day | mAh/day, today's sleep (4.0 mA) | mAh/day, production sleep (0.5 mA) |
|---|---|---|
| Light | 109 | 26 |
| Pomodoro | 250 | 180 |
| Pomodoro, dimmed | 192 | 122 |
| Gym | 147 | 68 |

Days per charge, **production sleep (0.5 mA)**:

| Day | 300 mAh | 500 mAh | 700 mAh |
|---|---|---|---|
| Light | 10.4 | 17.3 | 24.2 |
| Pomodoro | 1.5 | 2.5 | 3.5 |
| Pomodoro, dimmed | 2.2 | 3.7 | 5.2 |
| Gym | 4.0 | 6.6 | 9.3 |

Days per charge, **today's sleep (4.0 mA)**, for comparison:

| Day | 300 mAh | 500 mAh | 700 mAh |
|---|---|---|---|
| Light | 2.5 | 4.1 | 5.8 |
| Pomodoro | 1.1 | 1.8 | 2.5 |
| Gym | 1.8 | 3.1 | 4.3 |

## Takeaways for the hardware lock

1. **Backlight control is required, not optional.** At full brightness the backlight is ~79% of
   screen-on draw, and a 300 mAh cell lasts ~1.5 pomodoro days. A PWM-dimmed idle glance buys
   ~45% more.
2. **The sleep floor must come down** (display SLPIN, flash deep power-down, no dev-board overhead).
   At 4 mA, even a light day drains a 500 mAh cell in ~4 days. At 0.5 mA it lasts ~17 days.
3. **IMU polling is free at this resolution.** Pickup-to-wake doesn't need the interrupt pin for
   power reasons (latency decides that).
4. **The Bluetooth interval doesn't matter for battery yet.** Lazy-when-idle is still worth doing once
   the floor is under 1 mA, where 0.1-0.2 mA would show. Re-measure then.
5. Sized for a heavy pomodoro user, ~500 mAh gives 2.5-3.7 days. 300 mAh is about a day and a half.
