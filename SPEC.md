# Personal Assistant Device — Concept & Requirements Spec

**Status:** v0.1 draft — living document, updated as decisions get made.
**Working name:** TBD (referred to as "the device" below)

## 1. Concept

A pocketable, credit-card-footprint "second device" that acts as a fast, tactile capture
tool and a small set of purpose-built apps — not a phone replacement, not a general
computer. Core idea borrowed from Pebble Index/Pebble watch + Rabbit R1: press a button,
speak or interact, get something useful done, put it back in your pocket. Extensible via
an app model similar to Pebble's (write an app, push it to the device), rather than being
a fixed single-purpose gadget.

## 2. Core use cases (v1 target)

1. **Voice capture / reminders** — pull it out, press-and-hold to record a short voice
   note or reminder, put it away. Syncs to phone when in range.
2. **Pomodoro timer** — standalone timer app with haptic buzz on interval changes, usable
   sitting on a desk without a phone nearby. Must support long work sessions with the
   time remaining **visible continuously** for the whole session (not just a brief
   on-touch glance) — this is the worst case for battery/display power and should drive
   that budget rather than the average case.
3. **Gym workout logger** — clip/stick it to a machine (magnetically) and log sets/reps/
   weight via the encoder + button. Works fully offline during a workout; syncs to phone
   afterward.
4. **General-purpose app platform** — the above are the launch apps, but the device should
   support installing/writing additional small apps later (Pebble-style).

## 3. Physical form factor

- **Footprint:** roughly credit-card length/width (~85 × 55 mm). Thickness will *not* be
  credit-card-thin (0.76 mm is unrealistic with a battery + round display + electronics) —
  target is closer to a MagSafe battery pack, ~8–12 mm, which matches the reference product
  the user cited.
- **Display window:** round, 1.5–2" diameter, centered.
- **Mounting:** embedded magnet ring + steel plate (MagSafe-style) so it can stick to the
  back of a phone or to magnetic/steel gym equipment. Magnet ring placement needs to be
  decided before PCB layout since it dictates an antenna keepout zone for BLE.
- **Enclosure:** Phase 1 — 3D printed or off-the-shelf project enclosure for prototyping.
  Phase 2 (later) — machined metal enclosure once the internal layout is stable.

## 4. Physical inputs — [DECIDED, v1]

Minimal, tactile-only input — **no touchscreen**.

- **One rotary encoder** for scroll/navigate, with an integrated detent click-feel
  (mechanical encoder, e.g. EC11-style, possibly upgraded to a nicer sealed encoder for
  a more premium feel). Many of these also have a built-in push-switch on the shaft,
  which can double as a "select" action.
- **One separate push button**, on a hot-swappable mechanical keyboard switch socket
  (e.g. Kailh) so the tactile feel can be tuned/changed later. Low-profile switches
  (Kailh Choc or similar) recommended to keep enclosure thin.
- **Haptic feedback**: LRA (linear resonant actuator) motor + haptic driver IC
  (e.g. TI DRV2605L) rather than a cheap ERM motor — LRA gives crisper, more "premium"
  feedback for scroll ticks and confirmations, closer to the iPod clickwheel feel the
  user is after.
- **Stretch goal / v2 exploration:** replace the mechanical encoder with a capacitive
  touch ring (true iPod clickwheel-style continuous touch surface) + haptic feedback in
  place of mechanical clicks. Deferred because it needs a custom capacitive sensing ring
  + gesture-decoding firmware — meaningfully higher cost/complexity/risk than an
  off-the-shelf mechanical encoder. Revisit after v1 is working.

## 5. Display — [DECIDED: round color TFT, GC9A01]

Requirements: mostly static text + simple icons, occasional light animation, no fast
graphics needed — **plus** the pomodoro use case needs the countdown visible
continuously for the length of a work session (up to hours across a workday), which
makes "display on" a much larger fraction of total time than originally assumed. Three
options were weighed:

- **Sharp/LXD Memory LCD** (what Pebble actually used): ultra low power, always-on
  capable, fast enough refresh (not to be confused with e-paper). Best possible battery
  life for an always-on display. Downsides: round variants are hard to source, thinner
  Arduino/library ecosystem, more niche driver work (VCOM toggling).
- **Round OLED:** self-emissive, would have been the best power fit for an always-on
  countdown. **Rejected after real sourcing research**, not on technical merit — see the
  sourcing note below.
- **Round color TFT (GC9A01)** (chosen): best library support, matches existing tooling
  most closely. Backlight is the dominant power draw and stays on for hours at a time on
  heavy pomodoro days, which is a real battery-life cost — but its cost and availability
  are known and verified *today*, at low/no MOQ, which won over the OLED power advantage.

**Decision reversal — why OLED was dropped:** OLED was the original pick for battery-life
reasons, but real sourcing research (see Section 14/15) found that round AMOLED panels
are not sold with transparent pricing — genuine panel distributors (hemlcd.com,
lcdscreenmfg.com, etc.) quote on request only, and the one concrete MOQ found was **1,000
pieces**. The user's realistic first-run quantity is **at most ~100 units**, which doesn't
reach that MOQ and leaves the real per-unit cost unknown without a drawn-out RFQ process.
Round TFT (GC9A01), by contrast, has fully transparent pricing at any quantity (confirmed
$14.99 at 1–9 units direct from Waveshare, with volume discounts, and it's such a
commodity part in the smartwatch-clone supply chain that it's realistically much cheaper
still at 100+ units from other channels) — see Section 14. Given the choice between an
unknown, MOQ-gated cost (AMOLED) and a known, low-MOQ-friendly one (TFT), the user chose
to de-risk on the display and accept a shorter/adjustable battery-life target instead
(see Section 9's revised numbers). AMOLED remains documented here as a valid option to
revisit if/when production volume ever justifies engaging a panel distributor directly.

**Sourcing strategy [DECIDED]:** prefer parts already commoditized by the smartwatch
market wherever the requirements allow it — round display + driver, haptic motor,
wearable-oriented PMIC — since that volume keeps unit cost down and known, keeps parts
easy to re-source if one goes out of stock, and means better real-world documentation/
community precedent (PineTime, smartwatch-clone teardowns, etc.). Combine with an
**auto-dim behavior**: full brightness right after an encoder/button touch, dim to a
low-but-still-readable backlight level after a few seconds of no interaction while a
session/countdown is actively displayed, back to full brightness on next touch. This is
a firmware-level lever independent of the panel choice and should be implemented
regardless — it's the main lever available for a TFT, since (unlike OLED) the backlight
lights the whole panel uniformly regardless of content, so there's no "dark background
saves power" trick available here.

**Power budget note:** see Section 9 for the revised estimate — TFT backlight-on-for-
hours during pomodoro sessions is a bigger battery hit than the OLED estimate was, and
the week-long target has been explicitly relaxed as part of this decision.

**Cost note (checked against real pricing):** round AMOLED would have cost meaningfully
more than round TFT even if the MOQ/RFQ issue weren't a blocker — a bare 1.39" AMOLED
panel runs ~$60 at hobbyist single-unit quantity (DisplayModule.com) vs. TFT's confirmed
$14.99 (Waveshare, 1–9 units) — so this decision also directly reduces BOM cost risk, not
just sourcing-timeline risk.

## 6. Compute & connectivity — [RECOMMENDED, pending final confirmation]

**Sync model (decided):** store-and-forward, Garmin-watch style — the device is fully
functional standalone (records voice notes, logs workouts, runs the pomodoro timer)
without a phone nearby, and opportunistically syncs over Bluetooth LE whenever the phone
companion app comes into range. No requirement for the device to have its own internet
connection.

Given that, the device does **not** need standalone WiFi — it needs a low-power BLE MCU
with enough local storage to buffer data between syncs.

**Recommended MCU: Nordic nRF52840** (over continuing with ESP32-S3):
- Purpose-built for exactly this workload (BLE peripheral + long battery life); it's what
  most fitness wearables and Pebble's later hardware are built around.
- Native USB (no separate USB-serial chip needed) — fits the USB-C charge + flash
  requirement directly.
- Well-supported in Arduino via the Adafruit_nRF52_Arduino core, so the jump from
  ESP32-S3/Arduino isn't a total ecosystem change.
- **PineTime** (open-source nRF52832 smartwatch project) is a very useful reference
  design — same "small BLE wearable, several days of battery, hand-solderable" goals,
  fully open hardware/firmware to study.
- Tradeoff: less raw compute than ESP32-S3, and BLE-only ecosystem is a bit smaller than
  ESP32's — but it's the right tool for "week-long battery + BLE sync" specifically.

If, after building v1, standalone WiFi turns out to matter more than expected, an
ESP32-S3 revision is still possible — but starting on nRF52840 is the better bet given
the sync model you described.

## 7. Storage

Local flash needed to buffer workout logs, pomodoro history, and voice-memo audio between
syncs. Plan: external SPI NOR flash (e.g. 8–32 MB, cheap, SOIC-8, hand-solderable) rather
than relying on the MCU's internal flash alone. Voice notes likely stored as compressed
audio (e.g. ADPCM) rather than raw PCM to control storage/sync size; heavier processing
(transcription, etc.) deferred to the phone app after sync rather than done on-device.

## 8. Power

- **Target [REVISED]:** originally ~1 week; relaxed by the user in favor of the round-TFT
  cost/sourcing decision (Section 5). Realistic framing is now **~1 week on light-use
  days, ~3–5 days on heavy-pomodoro-use weeks** with a 400–500 mAh cell — see Section 9.
- **Battery:** flat LiPo pouch cell sized to the enclosure footprint — exact mAh TBD once
  enclosure thickness and power budget are firmed up (rough starting estimate: 300–500 mAh).
- **Charging/data:** USB-C for charging and wired dev flashing.
- **App delivery to end device:** BLE OTA for day-to-day app installs (once firmware is
  stable), similar to how the Pebble phone app pushes watchfaces/apps. USB-C flashing
  stays available for development/debugging.
- **Sleep strategy:** MCU deep sleep by default, instant wake on encoder/button interrupt;
  display dimmed (not off) during an active pomodoro/workout session per Section 5, fully
  off otherwise. This is the main lever for hitting the week-long target and needs to be
  validated empirically once hardware exists.

## 9. Power budget estimate (rough, pre-hardware)

**Caveat up front:** these are back-of-envelope numbers from typical datasheet figures
for this class of component (generic nRF52840 sleep/BLE currents, typical small GC9A01
TFT backlight currents). We haven't measured the exact module yet, so treat this as "is
the target roughly plausible" not a guarantee — it needs to be re-checked against the
real datasheet and validated with an actual USB power meter once the breadboard
prototype exists.

Assuming a **400 mAh** cell (middle of the earlier 300–500 mAh estimate) and a 7-day
target, the *average* allowance is ~57 mAh/day (~2.4 mA continuous).

Rough draw per day-type (**revised for TFT**, replacing the earlier OLED-based estimate):

| Scenario | Rough basis | Est. energy |
|---|---|---|
| Idle baseline (screen off, BLE slow-advertise, MCU deep sleep) | ~20–30 µA average × ~16 h/day | ~0.3–0.5 mAh |
| Heavy pomodoro day (6–8 h dimmed GC9A01 backlight, always-on) | ~12–18 mA average (dimmed backlight + light MCU activity) × 8 h | ~95–145 mAh |
| Gym session (~1 h, similar dimmed display + encoder interaction) | ~15 mA average × 1 h | ~15 mAh |
| Voice memos + BLE sync bursts | short bursts, low duty cycle | ~0.5 mAh/day |

**Why this is worse than the OLED estimate was:** a TFT backlight lights the whole panel
uniformly regardless of content — there's no "dark background costs ~nothing" trick like
self-emissive OLED gets for a mostly-black countdown display. Dimming still helps
(backlight current drops roughly with PWM duty cycle), but there's a floor below which
the display isn't readable, so the achievable minimum average current is higher than the
OLED case.

**Takeaway:** a single heavy-pomodoro day (~110–160 mAh) is now roughly **2–2.8× over**
the 57 mAh/day average the 7-day target assumes. Across a work week with several such
days, a 400 mAh cell realistically points to **~3–5 days** of real-world battery life on
heavy-use weeks, or more like a week on lighter weeks (occasional voice memos, no long
pomodoro sessions). **This has been explicitly accepted as a trade-off** (Section 5) in
exchange for de-risking display sourcing/cost — not something to silently fix later.
Options that remain open if it's worse than acceptable in practice:

1. **Bigger battery** (~600–800 mAh) if enclosure thickness allows — trades off against
   the "MagSafe battery pack" size/weight reference.
2. **Dim further / accept a dimmer minimum brightness** during passive display than
   originally planned, re-testing readability once real hardware exists.
3. **Live with more frequent charging on heavy-use weeks** — normal for many wearables,
   and USB-C charging is quick/low-friction by design.

Revisit with real numbers once the breadboard prototype allows actual current
measurement of the specific GC9A01 module purchased.

## 10. App / firmware model — [DECIDED: framework + v1 scope, 2026-09-26]

Pebble-inspired: apps are small, purpose-built, and can be developed/installed
independently of the base firmware.

**Firmware framework: Nordic's nRF Connect SDK (Zephyr RTOS), not Arduino.** Arduino
and CircuitPython are breadboard bring-up/validation tools only (Section 13) — neither
is the production path. Real nRF52-based commercial wearables (including the PineTime
reference design in Section 6) are built on Zephyr, not Arduino: it gives proper RTOS
power-state management (load-bearing given the tight power budget in Section 9) and a
built-in BLE DFU/OTA bootloader, which this section's own OTA requirement below needs
and Arduino has no real equivalent for. Confirmed before committing: USB-C flashing
still works the same way under Zephyr as on the current bring-up rig — Zephyr has
official `xiao_ble/nrf52840/sense` board support, flashed via `west flash` over the same
factory UF2 bootloader/double-tap-reset flow already in use, no new hardware needed.
Zephyr also already has a validated display driver for the GC9A01 panel
(`galaxycore,gc9x01x`-compatible, via a MIPI-DBI devicetree node), confirmed via
Zephyr's own docs — a head start for whenever firmware work starts on this framework.

- v1: apps live in firmware, written against Zephyr, flashed via USB-C during
  development (same physical flow as today — see Section 8).
- Later: explore a proper app-package format + BLE push mechanism (companion phone app or
  simple web tool) once the on-device app runtime is designed, mirroring CloudPebble /
  the Pebble phone app model. This is a significant chunk of work on its own and should
  be scoped separately once v1 hardware is proven.

**v1 app scope: a few in-house apps only** (pomodoro, workout logger, voice memo) —
deliberately narrow to avoid scope creep. A further idea — letting end users write or
prompt-generate their own app on a website and push it to the device — is explicitly
parked as a future direction, not a v1 requirement (see Section 11). Costs nothing to
defer: the SPI NOR flash already in the BOM (Section 7/15) has far more headroom than a
handful of in-house apps need. The one cheap thing worth doing now while writing the
Zephyr firmware is keeping a clean boundary between "OS" code (input handling, display
driver, storage) and "app" code (pomodoro/workout/voice-memo logic) rather than one
monolithic blob, so that door stays open without committing to it now.

## 11. Open questions / TBDs

- Exact battery mAh and cell dimensions (depends on final enclosure thickness).
- Final round display size/part number (1.28" vs 1.4" vs something closer to 2").
- Magnet ring size/placement and its antenna keepout impact on PCB layout.
- Whether the phone companion app is iOS, Android, or both (affects BLE stack work, not
  device hardware).
- Assembly approach: hand-solder vs. JLCPCB/PCBWay PCBA assembly service vs. stencil +
  home reflow — leaning toward fab-assembly for the finer-pitch parts (nRF52840 QFN,
  encoder chip if any) given cost-consciousness and no reflow oven on hand; final call
  once BOM and unit-cost estimate exist.
- Click-ring sensing mechanism: gear/friction-coupled AS5600, multi-pole magnetic ring +
  quadrature Hall sensors, or capacitive touch ring — see Section 13's encoder design
  note. Decide once the physical ring/enclosure design is underway.
- USB-C role on the final board: wire the data lines to the MCU and keep a bootloader
  active (lets anyone reflash over cable, like the current dev board does), or make it
  charge-only (data lines not connected — all field updates go through BLE DFU only,
  matching most consumer wearables, e.g. Fitbit/Garmin). Cheap to defer; doesn't affect
  breadboard prototyping either way.
- User-generated app store: let end users write or prompt-generate their own app on a
  website and push it to the device, instead of only the in-house v1 app set (Section
  10). Real appeal, but the hard part isn't storage (already have headroom) — it's
  safely running untrusted code on a memory-tight MCU. Pebble's own answer (CloudPebble
  compiling against a vetted SDK into signed binaries server-side, never running
  arbitrary code on-device) is the precedent to study closely if this gets revisited.

## 12. Next steps

1. ~~Draft a rough BOM / component shortlist~~ — see Section 15 (and Section 14 for the
   verified prototyping shopping list).
2. ~~Sanity-check power budget against the week-long target~~ — see Section 9 (rough
   estimate done; needs re-checking once a real display part is chosen, and validating
   with real hardware measurement).
3. Source/order the prototyping rig (Section 13) and validate firmware/UX end to end.
4. Move into KiCad schematic once the BOM and prototype are validated.

## 13. Prototyping plan (before custom PCB)

**Status as of 2026-09-26:** displays arrived. Encoder (step 3) and haptic (step 4)
are wired and validated working end to end on the breadboard, including velocity-scaled
haptic intensity (see the encoder design note below for a live finding from this).
Display (step 2) has not been wired/tested yet — next up. Validation so far has used
disposable Arduino/CircuitPython bring-up scripts, not the Zephyr framework decided on
in Section 10 — that scaffolding hasn't started yet.

Validate subsystems on breadboard-friendly modules before any custom PCB layout:

1. **MCU/firmware bring-up:** use a cheap, widely-documented nRF52840 dev board — Seeed
   XIAO nRF52840 (Sense variant has an onboard mic + IMU, useful for the voice-capture
   flow) or Adafruit Feather nRF52840 — rather than the Raytac module directly. Firmware
   written against the nRF52840 silicon is portable to the Raytac module later; a generic
   dev board is cheaper/easier for this stage.
2. **Display:** use a **bare round GC9A01 TFT module** (panel + driver IC, no onboard
   MCU, 4-wire SPI) driven from the nRF52840 dev board — confirmed real and cheap: $14.99
   at 1–9 units direct from Waveshare (their 1.28" round LCD module), with likely cheaper
   options at 100+ units given how commoditized this exact driver+panel combo is in the
   smartwatch-clone supply chain. Switched from round AMOLED after real sourcing research
   found AMOLED panels are RFQ-only with MOQs around 1,000 units — see Section 5's
   decision-reversal note and Section 14 for the verified link. Same caution applies as
   before: some vendors sell MCU-combo boards under similar names (e.g. Waveshare's
   ESP32-based dev boards) — confirm "no onboard MCU" on the specific product page.
3. **Encoder (click-ring around the display):** see the dedicated note below — this is
   not a drop-in EC11-style part swap, the ring geometry needs its own design decision.
4. **Haptic driver, mic:** wire directly to the dev board on a breadboard/perfboard.
5. Get the full firmware/UX loop working end to end on this rig (pomodoro, workout
   logging, voice capture, BLE sync, USB HID) before finalizing the BOM further.
6. **RF validation:** once firmware is solid, get Raytac's eval board **MDBT50Q-DB-40**
   (confirmed available via DigiKey, contains the MDBT50Q-1MV2 module) to confirm
   real-world antenna/RF performance of the specific certified module before committing
   it to the custom PCB layout.
7. Only after 1–6 are validated: move into KiCad schematic integrating the actual chosen
   modules/parts.

### Encoder design note: click-ring around the display changes the sensing approach

A standard magnetic angle sensor like the **AS5600** (the "magnetic encoder" option we'd
discussed generically) is an **on-axis** sensor — it expects a small diametric magnet
mounted directly on a shaft, centered right above the sensor die. That works fine for a
small knob, but it does **not** directly work for a ring that goes around the outer edge
of a 1.4"+ display, because the magnet would then be sitting off to the side at the
ring's radius, not centered on the sensor. This needs one of three real approaches,
which is a mechanical decision as much as an electrical one:

1. **Gear/friction-coupled AS5600 (simplest electrically):** keep the cheap, well-
   documented AS5600 breakout, but mechanically couple the visible outer ring to a small
   hidden on-axis magnet+shaft (behind/beside the display) via a small idler gear or
   friction wheel. Electronics stay simple and well-supported; the ring/gear coupling is
   an enclosure-design problem to solve with the mechanical design (3D-printable in
   prototype).
2. **Multi-pole magnetic ring + quadrature Hall sensors (matches real rotating-bezel
   products):** embed a multi-pole magnetized ring (common for BLDC motor encoders) into
   the rotating bezel itself, read it with 2 Hall-effect sensors near the ring's edge
   spaced for quadrature (A/B) output — the same principle as how Samsung Galaxy Watch's
   rotating bezel works. No gearing needed, but it's a less plug-and-play component set
   and needs quadrature decoding firmware (well-trodden pattern, just more parts to spec).
3. **Reconsider the capacitive touch ring:** previously deferred as the "harder" v2
   option, but a capacitive ring is *inherently* ring-shaped with zero moving parts (no
   bearing, no magnet, no gear) — arguably the most direct hardware match for "ring
   around the display." Dedicated capacitive touch-wheel controller ICs exist
   specifically for this pattern (e.g. Cypress/Infineon CapSense parts with slider/rotary
   pad support), which makes this less exotic than it first sounded.

**Recommendation:** don't block early firmware bring-up on this — prototype rotation
sensing/haptic-detent logic now with a plain shaft-mounted AS5600 breakout (temporary,
not the final mechanical form), and make the actual ring-mechanism call (option 1, 2, or
3 above) when we get to enclosure design, once the tactile feel can be evaluated
hands-on. Added as an open question in Section 11.

**Live data point (2026-09-26):** Justin physically removed the mechanical detent from
his breadboard EC11 and drove the "click" entirely from the ERM haptic motor instead —
an early, low-cost stand-in for the "no mechanical detent" property options 2 and 3
above both share. Findings so far: a plain EC11 used this way is capped at its native
electrical resolution (a fixed number of quadrature steps per revolution — this specific
part's exact count wasn't measured), which reads as noticeably coarser/steppier than a
true continuous angle sensor (AS5600, or a capacitive ring) would feel; and getting the
haptic "click" itself to feel right required PWM-based, velocity-scaled intensity
(soft on slow turns, firmer on fast ones) rather than a fixed-strength buzz — worth
carrying that same velocity-scaling idea forward regardless of which final ring
mechanism gets chosen.

## 14. Prototyping shopping list — verified (v1)

Checked against reputable retailers (Adafruit, DigiKey, dedicated display distributors)
as of this conversation. This is the breadboard-prototyping list (dev boards/breakouts),
distinct from the production BOM in Section 15 (which will use bare chips/modules).

### 14a. Bare-minimum order to start prototyping — priced

**Updated: the user already owns several of these parts**, which meaningfully shrinks the
actual purchase needed. Substitutions using on-hand parts are electrically/functionally
equivalent for firmware bring-up purposes — see notes per row.

| Item | Status | Part / substitute | Link | Price |
|---|---|---|---|---|
| MCU dev board | **Already owned** | Seeed XIAO nRF52840 Sense | [Seeed Studio](https://www.seeedstudio.com/Seeed-Studio-XIAO-nRF52840-Sense-Pre-Soldered-p-6330.html) (for reference) | $0 |
| Display | **Buy** | Hosyond 1.28" Round TFT Module, 3-pack (GC9A01, bare, 4-wire SPI, likely non-touch — confirm before ordering) | Amazon (Hosyond storefront) | **$17.99 for 3** |
| Display fallback | *(if dimming matters enough to switch later)* | Waveshare 1.28" Round LCD Module — **confirmed to have a genuine separate BL pin** (independent PWM control, not tied to VCC), 8-pin header | [Waveshare](https://www.waveshare.com/1.28inch-lcd-module.htm) | $14.99 |
| Push button | **Already owned** | Any standard momentary push button — electrically identical to a Kailh Choc switch (both are simple SPST momentary contacts); debounce/press logic carries over unchanged. Swap in Kailh Choc switches on the real PCB for the final low-profile/swappable feel. | — | $0 |
| Encoder | **Already owned** | User's existing rotary knob (pot or clicky rotary encoder — confirm which, firmware approach differs slightly) substitutes for the AS5600 as a temporary rotation-sensing stand-in — this was always meant to be a placeholder for firmware logic validation, not the final ring mechanism, so no reason to buy the AS5600 until actually prototyping the click-ring mechanism itself at the enclosure stage. | — | $0 |
| Haptic driver | **Deferred** | Adafruit DRV2605L (STEMMA QT), #2305 — not needed for basic on/off haptic validation, see minimal circuit note below. Worth getting later for crisp click waveforms / LRA resonance tracking once refining tactile feel. | [Adafruit](https://www.adafruit.com/product/2305) | $0 for now |
| Haptic motor drive | **Already owned + ~$1 in passives** | User's existing standard ERM motor, driven via a minimal transistor/MOSFET + flyback-diode circuit instead of a driver chip — see note below. GPIOs can't safely drive a motor directly (current exceeds GPIO rating; inductive kickback risks damage without a flyback diode). | — | ~$0–1 (if a basic transistor/diode isn't already on hand) |
| **Total (new purchases)** | | | | **$17.99** |

**Minimal ERM on/off circuit (no DRV2605L):** Motor+ → 3.3V; Motor− → drain of a small
N-channel MOSFET (2N7000/AO3400) or collector of an NPN transistor (2N2222/2N3904);
MOSFET source / transistor emitter → GND; gate (or base, via ~1kΩ resistor) → any spare
GPIO; flyback diode (1N4148) across the motor terminals, cathode to motor+, to absorb
the inductive spike on switch-off — don't skip this part. Firmware is a plain
`digitalWrite` on/off, or PWM the same GPIO for basic intensity control without needing
the driver chip at all. DRV2605L remains worth adding later for crisp click waveforms
and (especially) LRA resonance tracking once evaluating final tactile feel — not
required to validate that the haptic-trigger firmware logic works end to end.

Deferred until later (not needed for this bring-up): AS5600 + diametric magnet (until
prototyping the actual click-ring mechanism), Kailh Choc switch + hot-swap socket (until
the real PCB), SPI flash, BQ25120AEVM, Raytac eval board — see Section 14b.

Not included above: breadboard, jumper wires, USB-C cable if not already on hand.

**Known display limitation (per supplier schematic + user reviews) if buying the Hosyond
board:** it hardwires the backlight (LEDA through a 2Ω resistor to the always-on 3.3V
rail, LEDK straight to GND) — no PWM dimming pin is broken out. A fix exists (cut the
LEDK-to-GND trace, insert a low-side N-channel MOSFET gated by a spare GPIO) but the user
has opted to skip that for now and just validate firmware/UX without real dimming,
switching to the Waveshare module (confirmed genuine BL pin, no mod needed) later if
dimming turns out to matter enough.

### 14b. Deferred — not needed for bare-minimum prototyping

| Item | Part | Source | Notes |
|---|---|---|---|
| Storage | **Adafruit SPI Flash Breakout, W25Q128 (16MB)**, product #5643 | [Adafruit](https://www.adafruit.com/product/5643), also SparkFun's bare W25Q128JV breakout | Confirmed real and current at both retailers. Not needed until testing the storage/buffering flow specifically — the XIAO's internal flash is enough for early firmware work. |
| Power/charging | **TI BQ25120AEVM** official evaluation board | [DigiKey](https://www.digikey.com/en/products/detail/texas-instruments/BQ25120AEVM/8105811) | Confirmed in stock at DigiKey. Not needed yet — the Seeed XIAO already has its own basic LiPo charging circuit onboard for early firmware work; this EVM is for validating the actual PMIC chip before finalizing the custom PCB. |
| RF validation (later stage) | **Raytac MDBT50Q-DB-40** eval board | [DigiKey](https://www.digikey.com/en/products/detail/raytac/MDBT50Q-DB-40/13677598) | Confirmed real SKU and in stock. Not needed until Section 13 step 6, once firmware is solid. |

## 15. Draft BOM / component shortlist (v0.1)

Rough shortlist to price out and validate footprints/availability against. Quantities
and part numbers are starting points for BOM costing, not final selections — swap for
equivalents as needed during sourcing (this is exactly the kind of swap the user has done
before on past projects).

| Subsystem | Candidate part | Notes |
|---|---|---|
| MCU | **Raytac MDBT50Q-1MV2** (nRF52840 module) | Certified module (chip + crystal + matching + antenna network + FCC/CE pre-cert) rather than bare QFN — much easier to hand-solder (castellated pads, larger pitch) and removes RF layout risk for v1. Move to bare nRF52840-QIAA later if cost optimization at volume matters. Well precedented in maker projects. |
| Display | **Bare round GC9A01 TFT module**, 1.28", 240×240, 4-wire SPI, non-touch, no onboard MCU | Confirmed real and cheap directly from Waveshare ($14.99 at 1–9 units); this exact driver+panel combo is heavily commoditized in the smartwatch-clone supply chain so expect meaningfully cheaper pricing at 100+ units from other channels (see Section 14). Chosen over round AMOLED specifically because its pricing/MOQ is transparent today rather than RFQ-gated — see Section 5. |
| Encoder ring | **TBD — see the encoder design note in Section 13.** Candidates: (1) AS5600 on-axis sensor + gear/friction-coupled ring, (2) multi-pole magnetic ring + quadrature Hall sensors, (3) capacitive touch ring/wheel controller. | Decision depends on enclosure/mechanical design, not just electrical — deferred until we design the physical ring mechanism. Not a simple part swap from the original EC11 plan. |
| Microphone | **PDM MEMS microphone** (e.g. the same family as the XIAO Sense's onboard mic, MSM261D3526H1CPM or equivalent) | **Added — was missing from this BOM.** The nRF52840 on the Raytac module has no built-in mic; that was only ever a feature of Seeed's XIAO Sense dev board used for prototyping. Needed for voice capture, one of the three core use cases. Talks to the nRF52840 over its native PDM peripheral — same interface style as the prototype, no firmware architecture change, just a real component to place. |
| Push button | **Kailh Choc low-profile mechanical switch + hot-swap socket** | Matches the "changeable feel" requirement; low-profile keeps enclosure thin. Confirmed widely available. |
| Haptic driver | **TI DRV2605L** + **Vybronics VC0720B or Precision Microdrives coin LRA motor** | DRV2605L confirmed real/current (Adafruit #2305 and others). LRA motor sourced separately via DigiKey or Precision Microdrives — commoditized via the wearable/haptics market. |
| Storage | **Winbond W25Q128** (16MB SPI NOR flash, SOIC-8) | Extremely common, cheap, easy to hand-solder pitch. Buffers workout logs/pomodoro history/voice-memo audio between BLE syncs. Confirmed real (Adafruit #5643, SparkFun bare breakout). |
| Power / charging | **TI BQ25120A** (wearable-focused PMIC: charger + load switches + LDOs + ship mode + button monitor) | Purpose-built for exactly this device category (fitness trackers/wearables use it). Confirmed real via TI's official BQ25120AEVM (DigiKey) for prototyping. More complex to design with than a bare linear charger — fallback is **MCP73831** (simple linear charger, very common in maker LiPo/USB-C projects) + separate small LDO if BQ25120A proves too involved for v1. |
| Connector | **USB-C receptacle** (basic power+data, no need for full 24-pin) | Charging + native USB (HID/CDC) via the nRF52840's built-in USB controller — no separate USB-serial chip needed. |
| Magnets | **N52 segmented magnet ring assembly**, ~54mm OD × 46mm ID, ~1.15–2.5mm thick, with alignment magnet | Confirmed real, commodity product — sold as "MagSafe magnetic sticker rings" for phone cases (AliExpress, Etsy, eBay, [totalElement](https://totalelement.com/products/54-x-46-x-2-5mm-magsafe-neodymium-rare-earth-magnet-phone-attachment-ring-assembly-with-alignment-magnet-5-pack)). Genuinely segmented (e.g. 36 individual magnets), matching Apple's real array more closely than a single continuous ring would. 46mm ID comfortably clears the 32.5mm round display. Confirm whether the specific product includes a steel backing plate (concentrates flux outward for max holding force) — add a thin steel washer behind it if not. Placement to be finalized before PCB layout for antenna keepout. |
| Battery | Flat LiPo pouch cell, capacity TBD (~300–500 mAh starting estimate, may need to grow to 600–800 mAh — see Section 9) | Exact size depends on final enclosure thickness and re-checking the power budget once a real display part is chosen. |
