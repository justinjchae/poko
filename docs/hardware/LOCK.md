# Hardware lock tracker

**Goal:** lock the BOM so PCB design (and, with it, the enclosure) can start. A part is **locked**
when it's (1) validated on the bench where that matters, (2) sourceable at ~100 units, and (3) fits
the thickness and layout targets.

SPEC.md keeps the reasoning; this file tracks status.

**Status:** `OPEN` = no decision yet · `CANDIDATE` = leading part, validation or sourcing pending ·
`LOCKED` = done.
**Prices:** LCSC USD per unit at qty 100 (or the nearest price break), **live snapshot 2026-10-01**.
Stock moves daily, so re-check before ordering. JLC basic/extended status not checked yet.

## Decisions since 2026-10-05 (these supersede the rows below)
Synced 2026-10-08 from the decisions of 10-05 to 10-07.

| Item | Decision | Status |
|---|---|---|
| MCU | Raytac MDBT50Q-P1MV2, JLC pre-order C5119772 (Extended, 0 stock, Economic + Standard); consign from TME as fallback. **JLC quote 2026-10-10: $15.69 each for 10 ($156.89), $15.50 each for 100 ($1,549.55), lead time 8 business days, valid 370 h (about 15 days).** That is 2.0x JLC's own list price for the same part ($7.73 at qty 10 on the part page) and 2.2x TME ($6.50-7.13 @100). Ask JLC why; at 100 units the gap is about $840, so volume wants TME or another source, the first 7-10 boards can absorb it (about +$50 over the old $8.50 assumption) | LOCKED (part), price high, ask JLC |
| Display | Shineworld LH128R-IF138H, 4-wire SPI GC9A01, 16-pin 0.5 mm, 1.55 mm bare panel; connector HDGC 0.5K-HX-16PWB C2919496. Samples ordered 2026-10-07. Oric dropped | LOCKED, samples pending |
| Rail | One 3.0 V system rail from the Raytac REG0 on VDDH (REGOUT0 = 3.0 V; was 3.3 V in pins.md) | LOCKED |
| Charger | **TP4054-42-SOT25R C32574 (checked 2026-10-10, see "Swap checklist" #4; replaces MCP73831T C424093, was LOCKED).** PROG resistor: use **5.1 kohm (already on the BOM as the CC resistor) = about 186 mA, 0.37C of a 500 mAh cell** (TP4054 formula, NOT 1000/R above 150 mA). STAT/CHRG on P1.06 needs a pull-up (internal ~13k or an external 10k). BQ25120A rejected (0 stock). No I2C charger, so the IMU stays at 0x6A (SA0 low), DRV2605L 0x5A | PASS with corrections, Justin to confirm |
| Battery level | ADC divider on P0.31/AIN7 + P1.05, plus charger STAT | LOCKED |
| Backlight | Discrete constant-current sink: AO3400A C20917 + TLV9001 C398363 + 2.2 ohm sense, reference from PWM via 100k/3.3k/1uF, op-amp supplied from GPIO BL_EN, cap about 44 mA. Calculated, not simulated; bench-check gate oscillation. **Added 2026-10-10 (swap check #5):** 100k gate pull-down so the gate cannot float while BL_EN is low (the op-amp is unpowered then); a small series resistor in the gate line (start at 100 ohm, tune on the bench) for the about 630 pF Ciss of the AO3400A; firmware drives the PWM low before dropping BL_EN (the 100k reference resistor would otherwise feed the unpowered op-amp input) | LOCKED (bench pending) |
| Battery connection | **CHANGED 2026-10-10 (Justin): Batch 1 solders the cell's wire leads directly to PCB pads, no connector.** Use large or through-hole pads, strain relief (adhesive or Kapton) a few mm before the pads, a slack loop, and secure the cell with VHB/foam so it cannot swing on its leads. Solder the leads, not the cell tabs; one lead at a time, tape the other, keep the cell's protection circuit, check polarity yourself. Beta users do not replace cells; service by re-soldering. **Revisit rule:** if a joint or pad fails from drops in beta, add a connector for production; drop-test one of Justin's own units first. Why: the 4.8 mm JST did not fit (front face is on the XIAO in-line stack: PCB front face 4.605 mm from datum A, 4.405 mm free height after 0.2 clearance, so the connector was about 0.4 mm too tall and needed a 0.4+ mm front-plate pocket; also this entry said "on the back", which cannot work since only about 0.2 mm exists behind the PCB, tolerance-stack.md puts it on the front). The connector height tolerance was never found (4.8 mm is from the JST catalog p.22). Superseded plan below kept for the production revisit. Previously: JST PH 2.0 side-entry TH S2B-PH-K-S C173752 (wave-soldered, not JLC-reflowable), hand-soldered on the back, 4.8 mm tall (does not fit the 8 mm stack columns; pocket OPEN). Plug on the cell (decided 2026-10-08, not direct solder). SMD alternative S2B-PH-SM4-TB C295747 (5.5 mm, 7.9 x 8.6 mm) rejected: taller, and back-side JLC placement forces Standard PCBA. Buy the through-hole connectors myself (commodity). Cell must have built-in protection; confirm in writing. **Height decision deferred (Justin 2026-10-08):** plan on the PH right-angle TH part; the 1D stackup (cavity 4.7-4.9 mm from 10-01 estimates, PCB 1.6 + connector 4.8 = 6.4 mm) says it may not fit, so at layout populate the board, export the 3D model, design the enclosure around it, and revisit if too tall (lower 1.0/1.25 mm side-entry connector, back-wall pocket, or thicker stack). **Justin will NOT order the cells or the boards until the 3D height check is done; no connectors ordered until then.** Place it at a board edge on the back, opening facing outward, with a keep-out for a possible pocket. Ask the cell supplier which lead connectors they offer and whether changing costs anything. No reverse-polarity guard (Justin 2026-10-08: trusts the cell polarity; Schottky ruled out for its drop on the backlight headroom, P-FET declined) | Batch 1: DIRECT SOLDER (decided 2026-10-10). Production connector: revisit after beta drop results. The old height gate for cell and board orders no longer applies to a connector, but the other stack checks remain |
| USB-C | TYPE-C-31-M-12 C165948, 5.1k CC (C23186), tie both D+ and both D-, 27 ohm series per Raytac reference. Height about 3.2 mm per a third-party library entry, NOT confirmed from the datasheet | CANDIDATE |
| USB ESD | ST USBLC6-2SC6 C7519 (Extended; no Basic array found; UMW C2687116 and TECH PUBLIC C2827654 are Extended second sources). Place at the connector, on the connector side of the 27 ohm series resistors | LOCKED 2026-10-08 |
| Crystal | **Epson Q13FC13500003 9 pF C99010 (Extended, 19,874 in stock) + two 12 pF C0G caps, use the Basic C38523 (0603) or C1547 (0402) instead of Extended C107034.** Raytac's own spec sheet (design-guide package 230606, "Recommended 32.768KHZ Crystal Spec"): CL max 9 pF, ESR under 80 kohm, C0 under 2 pF, drive under 1.0 uW; "CL = 9 pF means 12 pF external caps". The -004 (C32346, 12.5 pF) is OUT of that spec. No Basic 32.768 kHz crystal with CL 9 pF or less exists on JLC (checked 70+ listings) | LOCKED 2026-10-10 |
| IMU | **LSM6DS3TR-C C967633 stays (checked 2026-10-10: the LIS3DHTR swap REJECTED).** JLC's live part page lists LIS3DHTR C15134 as **Standard Only**, not "Economic and Standard" as the 2026-10-09 note said, so it does not unlock Economic assembly; it also has only 61 in stock and ST forum staff say it may be near end of life. Every accelerometer from ST, TDK, Bosch, QST and Silan that I checked is Standard Only (LIS2DH12, LIS2DW12, BMA253/400, LSM6DS*, ICM-42670, QMA6100P, SC7A20, STK8321, KXTJ3, BMI270). The Economic-eligible ones are unusable: MMA8451Q/8452Q (NXP end of life, no Zephyr driver), MSKSEMI LIS2DW12TR-MS and BMA253-MS (clones, no datasheet found), MPU-6050/6000 ($10-16 each), MXC4005XC (WLP-6, no driver). LSM6DS3TR-C: Standard Only, MSL 3, 25,335 in stock, $1.05 @100, the same part as the XIAO (firmware already works: `imu_lsm6dsl.c`, I2C 0x6A with SA0 low, INT1 to P0.11, gyro available later). Cost of staying: Standard PCBA instead of Economic, about +$24 per order before tariff (setup $25 vs $8, stencil about $8.7 vs $1.50). If Justin still wants LIS3DHTR for other reasons, the research is in the checklist below (address 0x18/0x19, ODR steps 10/25/50 Hz, Zephyr `st,lis3dh`) | REVERT to LSM6DS3TR-C recommended, Justin to confirm |
| Swaps approved 2026-10-09 | **Checked 2026-10-10 (details in "Swap checklist"):** (1) IMU LIS3DHTR **FAIL** (Standard Only, 61 in stock); (2) crystal C32346 **FAIL** (12.5 pF breaks Raytac's CL max 9 pF spec); (3) 12 pF caps **PASS** as a stand-alone swap, 12 pF stays 12 pF, use Basic C38523 (0603) or C1547 (0402) with the -003 crystal; (4) charger TP4054 **PASS with corrections** (identical SOT-23-5 pinout, different PROG formula, open-drain STAT, and it removes a real STAT overvoltage problem of the MCP73831); (5) op-amp LMV321 **FAIL on value** (works electrically, but offset is up to 7 mV on a 96 mV reference for a saving of only the $3 Extended fee). Net savings left: about $3 (caps) + $3 plus part cost (charger). Economic assembly is NOT reachable while the IMU is a Standard Only part | CHECKED, needs Justin's yes on each |
| I2C pull-ups | 3.3k | LOCKED |
| Haptics | DRV2605L C527464 (**JLC stock 12,489 on 2026-10-10 via the JLC parts API, was 58 in the 10-08 notes, so no consigning needed; recheck before ordering**), generic 2-pad footprint. Motor under test: Xinhailong L090835H-008678999-8160 X-axis LRA, 10 ordered 2026-10-08 (order #317053639501020632), see haptics.md | CANDIDATE |
| Ring sensing | OPEN (shared pins P0.04/P0.05/P1.09) | OPEN |
| Select button | OPEN (candidates TS-1187A-B-A-B C318884, TS-1088-AR02016 C720477, SKRPACE010 C139797) | OPEN |
| Flash / programming | W25Q128JV 16 MB; Tag-Connect TC2030 no-legs footprint (SWDIO, SWDCLK, reset, 3V3, GND, SWO on P1.00). Justin owns no SWD probe; the probe choice is deferred (any probe works through the footprint), but one must be on hand before the first boards arrive | footprint LOCKED, probe deferred. **TODO at layout: add a fallback row of five plain 1.27 or 2.54 mm pads (SWDIO, SWDCLK, reset, 3V3, GND) beside the Tag-Connect footprint as insurance (pin header or pogo clip if the TC2030 footprint turns out wrong).** Order the probe about when the boards go to fab |
| Batch 1 carrier: battery path | **Added 2026-10-10 (Justin).** The XIAO's BAT pads are on its UNDERSIDE (2.11 x 1.1 mm each, about 3.4 mm in from the right edge, beside the 1.5 mm SWD test pads; polarity from Seeed's KiCad, BAT0 at Y 10.16 and GND0 at Y 8.26 in the xiao-reference-model frame, NOT measured: meter a real board first). Cell wires solder to those pads with the board open, run flat under Kapton out of the XIAO footprint, through a slot in the carrier about 3 mm beyond the XIAO's castellated edge, and up to the cell on the front. The carrier also gets VBAT/GND pads on the front with a second short wire pair, because the backlight sink needs battery headroom (the XIAO 3V3 pad is a regulated output). Joints plus 30 AWG wire use about 0.4-0.6 mm of back gap: fits the overlay plate (0.695), not the inset (0.195); a 0.3 mm recess in the back plate under the XIAO is the cheap fix. Keep solder clear of the SWD test pads | DECIDED, geometry in the floorplan |
| Batch 1 carrier: XIAO pins | **Added 2026-10-10.** D1/D2/D3/D8/D10 display SPI, D4/D5 I2C (AS5600 0x36, DRV2605L 0x5A; the IMU is on the XIAO's internal bus), D6 select, D7 backlight PWM, **D0 = BL_EN** (op-amp supply gate; not a jumper candidate, tying it high costs 80-170 uA in sleep), **D9 spare**. **DRV2605L EN tied to 3V3, no GPIO:** datasheet SLOS854D shows shutdown (EN low) 4 uA typ / 7 max vs standby (EN high, STANDBY bit set) 4.1 uA typ / 7 max, so a GPIO saves nothing. Firmware must set the STANDBY bit after every buzz (STANDBY clear = 0.5 mA, the whole sleep budget); wait 250 us after power-up before I2C. **Display TE** routes to D9 through an OPEN 2-pad solder jumper (bridge to enable); skipped for batch 1 (tearing only matters in fast animation). Optional 3-pad "cut to change" jumper on DRV EN (3V3 by default, bridge to D9 for GPIO control); both share D9. Solder jumpers go on the front face only. **AS5600** sits on the I2C bus with a DNP 4-pad row (3V3, GND, SDA, SCL) so a remote sensor board can replace it if the roller geometry changes. Pin count is from the current firmware overlay, not yet checked against Seeed's pinout | DECIDED |
| Batch 1 carrier: floorplan inputs | **2026-10-10 (Justin):** half-circle end is the TOP edge, USB-C points at the BOTTOM edge, display centered in the half circle on the upper part of the face, ring OD TBD (V1B thumb wheel was 33 mm; 54.1 mm MagSafe ring needs outline >= 59.1 overlay), cell 303450 (3 x 34 x 50 mm), back plate overlay as default. Open: caliper the real XIAO, ring OD | IN PROGRESS (CAD session) |

## Swap checklist (approved 2026-10-09, CHECKED 2026-10-10)
Method: datasheets (Raytac design-guide package 230606, TI LMV321 SLOS263Y, Microchip MCP73831 DS20001984H, TP4054 datasheet (Chinese only),
ST LIS3DH rev 1 mirror), JLC part pages and the JLC parts API (library type, Preferred flag, stock, assembly type read from the live page), and the
Zephyr tree in `~/ncs` (NCS v3.4.1). Datasheet PDFs and scripts were kept outside the repo.

1. **IMU LIS3DHTR (C15134) for LSM6DS3TR-C: FAIL, revert.**
   - The premise was wrong: JLC lists C15134 as **Standard Only** (and X-ray, MSL 3). Stock is 61. Every ST/TDK/Bosch/QST/Silan accelerometer checked is Standard Only too,
     and the Economic-eligible ones are unusable (see the IMU row). So the swap cannot get the project to Economic assembly.
   - Technical findings, in case LIS3DH is wanted later: Vdd 1.71-3.6 V, Vdd_IO 1.71 V to Vdd+0.1 V; I2C address 0x18 (SA0 low) or 0x19; CS must be tied high for I2C; RES to GND;
     ADC1-3 may float; INT1 to P0.11 as before; WHO_AM_I 0x33; power-down 0.5 uA, 50 Hz normal mode 11 uA; 100 nF at the supply pin.
     ODR steps are 1/10/25/50/100/200/400 Hz, **no 12.5 Hz**, so `apply_odr()` in `imu_lsm6dsl.c` (12/26/52) and the 12 Hz poll default would change, and `PICKUP_DWELL_MS` (80, "two samples at 12.5 Hz") needs a recheck.
     Zephyr has `st,lis3dh` on the `lis2dh` driver (WHO_AM_I checked, runtime ODR, ODR 0 = power-down); `Kconfig` `DT_HAS_ST_LSM6DSL_ENABLED` and the `LSM6DSL_*` lines in `prj.conf` would change; the simulator has only the lsm6dsl backend.
   - Part risk: ST community staff say LIS3DH is not guaranteed past two to three years; the LIS2DH12TR successor is also Standard Only.
2. **Crystal C32346 (Q13FC13500004) for C99010 (-003): FAIL.**
   - The -004 is **CL = 12.5 pF** (Epson FC-135 12.5 pF, +/-20 ppm, ESR 70 kohm max, SMD3215-2P). Raytac's spec sheet for the external 32.768 kHz crystal (in the Footprint & Design Guide package, annotated) says
     **CL max 9 pF, ESR under 80 kohm, C0 under 2 pF, drive level under 1.0 uW**, "use CL = 7 pF: 9 pF caps; use CL = 9 pF: 12 pF caps". The -003 (9 pF, C0 1.2 pF typ, 70 kohm, 0.5 uW max) matches it exactly.
   - A 12.5 pF crystal would also need about 17-19 pF caps (C = 2 x (CL - Cstray), Cstray about 3-4 pF; the Raytac pairing of a 9 pF crystal with 12 pF caps implies about 3 pF), so the 12 pF caps would be wrong for it.
   - The nRF52840 chip itself accepts up to 12.5 pF (Nordic forum), but the module guidance is stricter, and the module's own internal trace likely adds stray capacitance. Not worth the risk for a $3 fee.
   - No Basic 32.768 kHz crystal with CL 9 pF or less exists on JLC (about 70 listings checked); the only Basic one is the 12.5 pF C32346. So the crystal stays Extended ($3 per order). Alternatives with the same class: 7 pF C48615 (Epson Q13FC13500002) with 9 pF caps.
3. **12 pF C0G caps, Basic C38523 (0603) or C1547 (0402), for Extended C107034: PASS.**
   - Value unchanged (the -003 crystal stays), 12 pF, 50 V, C0G, +/-5%, MSL 1, Economic and Standard, 563k / 1.83M in stock. Saves the $3.07 Extended fee under Economic only; under Standard every unique part costs $1.53 either way (JLC fee page, 2026-09-09).
   - Choose the size at layout. 0402 is smaller and keeps the crystal loop short; 0603 is easier to hand-rework. Economic minimum package is 0402.
   - Layout rules from the Epson sheet: no copper pattern under or near the crystal, shortest possible traces, 150 um solder paste.
4. **Charger TP4054 (C32574) for MCP73831T (C424093): PASS with corrections.**
   - **Pinout is identical**, the earlier note saying it differs was wrong: SOT-23-5 pin 1 CHRG/STAT, 2 GND/VSS, 3 BAT/VBAT, 4 VCC/VDD, 5 PROG on both. Same footprint; only the symbol names change.
   - **PROG formula differs above 150 mA.** TP4054: R = 1000/I for I up to 0.15 A, and R = 1000 x (1.2/I - 4/3) above (example in the datasheet: 400 mA is 1.66 kohm). MCP73831: R = 1000/I. At 5.1 kohm (an existing BOM value) the TP4054 gives about 186 mA (0.37C of 500 mAh); the MCP73831 would give about 196 mA. Pick 5.1 kohm. The cell's rated charge current must be at least that (typical 303450 cells: 0.5C = 250 mA).
   - **STAT/CHRG behaves differently, and the old part had a problem.** MCP73831 STAT is tri-state and drives HIGH to about VDD (USB 5 V minus 0.4 V) in Charge Complete. That would put about 4.6 V on a GPIO powered from 3.0 V (nRF52840 absolute maximum VDD + 0.3 V), so the MCP73831 as locked needed a clamp or divider that nobody had drawn. TP4054 CHRG is open-drain: strong pull-down (about 10 mA) while charging, **weak pull-down (about 20 uA, 8-35 uA) when charge is done and USB is present**, high impedance when USB is absent. Firmware: P1.06 with a pull-up; with the nRF internal pull-up (about 13 kohm) the done state reads 2.5-2.7 V worst case to typical (needs 2.1 V), with an external 10 kohm to 3.0 V it reads 2.65-2.8 V. **Do not use a pull-up above about 20 kohm.** The three states are told apart with VBUS detect (already read from the USB peripheral): VBUS present and low = charging, VBUS present and high = done, no VBUS = on battery.
   - Input 4.0-9 V (abs max 10 V) against 3.75-6 V (abs max 7 V) for the MCP73831: better for USB hot-plug. Needs a 1 uF or more on VCC.
   - Output: stable with the battery connected and no capacitor; with no cell attached a capacitor at BAT is recommended (the MCP73831 requires 4.7 uF). Keep a 4.7 uF at the BAT node, bench-check once with no cell and USB plugged in (the system then runs from the charger at up to 4.2 V, within VDDH range).
   - Battery drain with USB unplugged: TP4054 sleep mode 1-2 uA max (datasheet), MCP73831 0.15 uA typ. Both are negligible against the 0.5 mA sleep floor.
   - Termination at C/10 (about 19 mA at 186 mA) and recharge at 4.05 V; same as before. **System load shares the BAT node**, so with the screen on (45 mA) while plugged in, the charger never terminates and holds the cell at 4.2 V. This is true of the MCP73831 as well; not a swap issue, but worth a thought for cell life.
   - Thermal regulation starts at about 100 C die temperature and C/10 termination is disabled in trickle and thermal-limit mode. Dissipation at 186 mA from 5 V is up to about 0.37 W at a 3.0 V cell; fine on the bench, check in the closed enclosure.
   - TP4054 is a clone of the LTC4054 from Nanjing Top Power; the datasheet is Chinese only. JLC: Preferred Extended, 39,877 in stock, $0.10 @100 (MCP73831 $0.48, Extended). Under Standard the fee is the same for both; the gain is part price and the STAT fix.
5. **Op-amp LMV321 (C7972) for TLV9001 (C398363) in the backlight sink: FAIL on value.**
   - What passes: supply 2.7-5.5 V against the 3.0 V GPIO supply (0.3 V margin, so the 3.0 V rail must never sag below 2.7 V while the backlight is on); input common-mode range 0 to 1.7 V minimum includes the 0-96 mV sense voltage; output low swing up to 180 mV keeps the AO3400A off (gate threshold 0.65 V minimum); supply current 80 typ / 170 uA max, fine for a GPIO; Preferred Extended, so no $3 loading fee.
   - What fails: **input offset up to 7 mV (1.7 mV typ)** against 1.6 mV max for the TLV9001. The reference is 96 mV at full PWM (3.0 V x 3.3k/103.3k), so the sink current error is up to +/-3.2 mA (+/-7.3%) at full brightness (nominal 43.6 mA), +/-3.2 mA on about 10.9 mA at 25% duty (+/-29%), and at 10% duty the nominal 4.4 mA could be anywhere from 1.2 to 7.6 mA; units with negative offset have a dead zone up to about 7% duty. TLV9001 worst case is +/-0.7 mA. Input bias up to 250 nA adds up to 0.8 mV over the 3.2 kohm reference network.
   - The saving exists only under Economic ($3.07 Extended fee); under Standard it is zero, and the LMV321 costs $0.097 against $0.077. TI marks the LMV321 as superseded by the LMV321A for new designs, and the A parts are Extended, so no fee saving there.
   - Stability with the AO3400A gate (Ciss about 630 pF) is unproven for either part (LMV321 is characterized at 200 pF load, 60 degrees phase margin); the existing bench check applies to both, plus the gate pull-down, series gate resistor and PWM-before-BL_EN sequencing added to the Backlight row.
   - Recommendation: keep TLV9001.
6. **Re-run of `jlc-cost.md`: done 2026-10-10** (see that file). With the IMU staying Standard Only, Economic assembly is not reachable; the remaining savings are the 12 pF caps and the charger.

## Targets (agreed 2026-10-01)
- MagSafe-style accessory, 60 × 90 mm outline (fits the 54 mm magnet ring).
- **Thickness: under 9 mm, ideally 8 mm.** Layout B: PCB under the display, battery under the chin,
  side by side, never stacked. With 1.5 mm walls and a 1.6 mm PCB, layout B comes to ≈ 8.7 mm
  nominal. The ways to reach ~8 mm are listed in "Thickness" below.
- Every prototype breaks out the spare GPIOs + 3V3/GND and makes reset reachable from outside.

## Order of operations
1. Targets (above) ✔
2. BOM candidates with sourcing data (this file) ← **now**
3. Bench-test only the risky items: ring sensing, LRA feel, power draw, MagSafe hold, **edge-on hold on a squat rack strut**
4. Lock the BOM and block diagram
5. Mechanical layout: board outline, keep-outs (display, battery, magnet ring, antenna window, ring
   sensor), height zones
6. Schematic → PCB layout
7. First boards (5–10, assembled by JLC) → the enclosure around them
8. Certification plan, quotes for 100, preorder

## On-board parts (assembled by JLC, sourced from LCSC)

| Subsystem | Leading candidate | LCSC # | Stock | $ @100 | Still needs | Status |
|---|---|---|---|---|---|---|
| **MCU + radio** | Raytac MDBT50Q-P1MV2 (PCB antenna) or -1MV2 (chip antenna): same datasheet, so check that one footprint fits both | LCSC: 0 stock. **Buy from TME** (authorized) | P1MV2: TME 1,239 · 1MV2: TME 1,298 | **6.50** (P1MV2) / 7.13 (1MV2) | JLC global sourcing or consign; confirm footprint/keep-out match | CANDIDATE |
| ↳ rejected | XIAO nRF52840 Sense as a solder-down module (FCC ID Z4T-XIAONRF52840) | DigiKey 1,181 · Mouser 514 | | 15.90 flat | ~$6/unit more than discrete parts, about 1.5–3 mm thicker (USB-C on top), its 2 MB flash still needs the 16 MB chip, and the mic/USB/antenna layout is fixed | — |
| ↳ insurance | nRF54L15 modules: Fanstel BM15C/BM15M, u-blox NORA-B201, Murata | DigiKey 4,179 (BM15C) · Mouser 2,258 (NORA) | | ~5–6 | plentiful. **Verify: probably no native USB** (flashing + memo-over-USB depend on it) | — |
| ↳ alternative | nRF52840-QIAA-R bare chip | C190794 | 48,511 | 4.20 | needs our own RF design + full FCC testing | — |
| **Charger / power** | TI BQ25120A (wearable PMIC) | C2866577 | **3** | 2.32 | sourcing; DSBGA-25 needs JLC assembly | OPEN |
| ↳ fallback | MCP73831T-2ACI/OT linear charger + an LDO (TBD) | C424093 | 9,358 | 0.49 | pick the LDO, plus battery protection | — |
| **Storage** | Winbond W25Q128JVSIQ, 16 MB (≈ 33 memo-min) | C97521 | 2,601 | 1.78 | 008: memo-minutes per day → is 16 MB enough? | CANDIDATE |
| **IMU** | ST LSM6DS3TR-C (same as XIAO) | C967633 | 25,000 | 1.06 | polling costs <0.1 mA (009), so INT1 isn't needed for power; 004 latency decides. Routing INT1 to a spare GPIO costs nothing, so do it. **Missing from SPEC §15** | CANDIDATE |
| **Microphone** | MEMSensing MSM261DDB020 (bottom-port PDM) | C27636198 | 6,121 | 0.41 | port design (lesson from the VHB pad); the XIAO's MSM261D3526H1CPM isn't listed on LCSC | CANDIDATE |
| ↳ alternative | TDK MMICT390200012 (bottom-port PDM) | C3171752 | 7,891 | 0.99 | — | — |
| **Haptic driver** | TI DRV2605L | C527464 | 684 | 0.86 | feel test with an LRA (Adafruit #2305 breakout) | CANDIDATE |
| **Ring sensing** | 2× Everlight ITR8307 reflective optical | C67922 | 5,580 | 0.19 @50 | bench test (mouse salvage first); flat, so it fits under the face at 8 mm | OPEN |
| ↳ alternative | ams AS5600-ASOT + gear (V1 style) | C499458 | 39,747 | 0.86 | needs about 1–2 mm more height, plus the magnet interference check. (The -ASOM variant, C79815, has only 4 in stock) | — |
| **Select button** | thin dome or low-profile tact switch, just under the bezel (over the PCB, not the battery) | TBD | | | pick a part | OPEN |
| **USB-C** | TYPE-C-31-M-12 receptacle | C165948 | 437,405 | 0.15 @50 | height check against the 8 mm stack | CANDIDATE |
| **Display backlight** | MOSFET + PWM from the MCU, **plus a lower full-brightness current** than the Hosyond's 33.5 mA | TBD (generic) | | | **Must have.** The backlight is ~80–90% of all current (009). Pick a full-brightness current on the bench | LOCKED (requirement) |
| **Debug / expansion** | SWD pads + spare GPIO + 3V3/GND pads + reachable reset | generic | | | Justin's rule | LOCKED (requirement) |

## Off-board parts (separate suppliers: the overseas sourcing practice)

| Part | Leading candidate | Still needs | Status |
|---|---|---|---|
| Display | bare 1.28" GC9A01 round TFT, 1.5 mm thick, FPC to a connector | supplier, price at 100, MOQ, backlight pins. **Future run: AMOLED** (Justin, 2026-10-01). **Alibaba check 2026-10-01: 1.43" 466×466 CO5300 QSPI AMOLEDs are ~$7.5–9 at MOQ 1–100** (Oric ORC-Z014311C $8.96, sample $3.78; Startek KD014VGOSN001 with touch $7.99 @100; TDO TA014WVC08CT $7.56). Same 35.6 × 38.1 × 1.56 mm outline as the GC9A01, with a 36.35 mm active area. A bare GC9A01 TFT is ~$2.8–3.8, so AMOLED adds ~+$4–5/unit. Open questions: supply rails, Zephyr driver, 466² rendering speed on the nRF52840. Re-check MOQ/pricing then: earlier quotes were RFQ-only with a 1,000 MOQ. It changes power (dark UI ≈ near-zero backlight cost) and interface (many round AMOLEDs use QSPI, and the nRF52840 has one QSPI port, so check for a conflict with flash) | CANDIDATE (first run) |
| Battery | 303450 LiPo, 3.0 × 34 × 50 mm, **500 mAh (chosen for now, 2026-10-01)** | ⚠️ **Redecide before ordering:** re-check against any new apps, hardware changes or use cases since then, and re-run the 009 estimates with the production sleep floor and backlight current. Basis: 009 says 500 mAh ≈ 2.5 Pomodoro days at full brightness, ~3.7 with a 50% idle glance, ~5+ at ~25%. Still needs: supplier, shipping rules (UN38.3) | CANDIDATE |
| LRA | 8 mm coin LRA, about 2.5 mm thick (e.g. Vybronics VG0825001U or equivalent) | feel test with the DRV2605L; supplier at 100 | CANDIDATE |
| MagSafe magnets | N52 ring 54 × 46 mm with alignment magnet (+ steel shim) | hold strength on Justin's phone; placement (centered on display vs body) | OPEN |
| Left-edge magnet | bar magnet (about 30–40 × 3–4 × 2 mm, N52) in the left long edge, thin wall at the face. **Use case (Justin, 2026-10-01): stick the left edge ONLY to a vertical steel squat-rack strut, device sticks out like a flag, screen facing the lifter, to read rest times from a few steps back.** Mostly a shear load (sliding down), not peeling | hold test on a real rack strut (powder coat, sweat, chalk, J-hook holes); weight of the device; edge friction (silicone strip?); keep it away from the antenna window | OPEN |
| Kickstand (considering) | hinged flap with a constant-torque friction hinge, opens 180°, works in portrait and landscape, magnet on the flap to prop on a phone or a laptop-lid sticker. Parked for later: Justin is considering it, no decision | hinge size and price at 100 (verify MOQ); thickness (<9 mm); don't cover the back magnet ring; portrait vs landscape needs hinges on two edges or a rotating disc | OPEN |
| Ring | FDM-printed toothed inner ring; visible bezel CNC aluminum or cast | follows from ring sensing | OPEN |
| Enclosure | CNC aluminum frame + **non-metal back** (Bluetooth window), or resin cast | material choice; antenna placement | OPEN |

## Top risks (as of 2026-10-01)
1. ~~nRF52840 modules out of stock~~ **Resolved 2026-10-01:** they're out of stock at LCSC, but TME (authorized)
   has ~1,200+ of each Raytac variant at $6.50–7.13 @100. The chip itself is plentiful (48k at LCSC). Plenty of nRF54L15
   modules exist as a fallback. Stay on the nRF52840.
2. **BQ25120A has only 3 in stock.** The MCP73831 fallback is simple and plentiful, but needs a
   separate regulator, and possibly battery protection.
3. **Bluetooth vs aluminum + magnets.** The antenna needs a non-metal window, away from the magnet
   ring. Decide before the mechanical layout (step 5).
4. **Thickness vs ring sensing.** At 8 mm, only reflective optical clearly fits under the face.

## Thickness (layout B, from 2026-10-01 analysis)
Display column: 1.5 wall + 1.5 display + 0.2 foam + 1.6 PCB + 1.4 parts/magnets + 1.5 wall = **7.7**.
Battery column: 1.5 + 0.2 + 3.0 cell + 0.3 swell + 1.4 magnets + 1.5 = **7.9**. Plus a 1.0 mm bezel ≈
**8.7**, and tolerances add about +0.3 (worst case +0.5).
Ways to reach ~8 mm:
1. A 0.8 mm front ledge at the display (−0.7)
2. Bezel 0.5 mm proud with a knurled edge (−0.5)
3. A 1.0 / 0.8 mm 4-layer PCB (−0.6 to −0.8)
4. Magnets pocketed into the back wall (−1.0 where they overlap)
5. 1.0 mm CNC walls (−0.5 each)

## Bench tests

| Test | Settles | Who | Status |
|---|---|---|---|
| 009 power measurement | battery size, and therefore thickness | firmware + Justin | **Done** (cbe00e4, `docs/hardware/power.md`). Backlight 33.5 mA dominates; rest ≈ 9.1 mA with the screen on, ≈ 4.0 mA asleep on the XIAO |
| 004 pickup to wake | IMU + interrupt pin | firmware | queued |
| 008 memo storage | flash size | firmware | queued |
| Optical ring (salvaged mouse encoder, printed toothed ring) | ring sensing | Justin + firmware | waiting on the mouse teardown |
| LRA + DRV2605L feel | haptics | needs parts ordered | not started |
| MagSafe hold + magnet interference | magnets; AS5600 viability | Justin | not started |
| Capacitive pad through 1–1.5 mm plastic, wet fingers (TTP223-type board he owns) | whether capacitive select stays an option | Justin | optional |

## Power findings (009, 2026-10-01)
- Upper bounds, measured on the XIAO: deep idle 37.5 mA, screen on 42.6 mA, recording ~44 mA. Of that,
  **33.5 mA is backlight** (275 mV across R6, which is 8.2 Ω, not the 2 Ω in SPEC §14a).
- IMU polling at 5–25 Hz costs <0.1 mA. BLE fast vs lazy link: no difference while the floor is 4 mA.
  Re-measure once the floor drops.
- **Battery strategy:** keep the 3.0 mm / 500 mAh cell (it protects the 8–9 mm target) and win battery
  life with backlight control:
  - a dim idle glance (~25%) on the PWM backlight
  - a lower full-brightness current in production
  - a sleep floor under 1 mA (display SLPIN, flash deep power-down, no dev-board parts)
  The estimates assume a 0.5 mA production floor, which still needs to be measured.

## Measurement caveats (009)
- **Hosyond backlight is hardwired on**, so "screen off" still burns backlight current, and deep idle
  will read high. Production has backlight control. Measure the backlight separately (the voltage
  across its 2 Ω series resistor ÷ 2 Ω) and subtract it.
- **BLE stays connected at a 15 ms interval with latency 0 all day.** That's probably a big drain,
  and it's a firmware choice, not hardware. Production should use a lazy interval (or slave latency)
  when idle. Size the battery on the lazy-interval numbers.
- The XIAO's own parts (charger, LED, regulator) add draw. Treat the readings as upper bounds.

## OTA and the board (hardware-affecting decisions; revisit before the PCB goes out)
The OTA plan. Only these touch the hardware, so these are what must be settled before manufacturing; hosting, the app store and
auto-install can change later.
| Item | Decision / question | Status |
|---|---|---|
| USB data lines | Wired to the MCU on the first batch, as a wired recovery path (Justin, 2026-10-02) | DECIDED |
| Second image slot | Internal flash (1 MB) or the 16 MB external chip? The external chip also holds memos | DECIDED 2026-10-05 (ota-checks.md, 381da4b): external 16 MB chip. Image is 547 KiB signed, internal slots would max 472 KiB each. Layout: internal MCUboot 64 KiB + app 928 KiB + settings 32 KiB; external OTA slot 928 KiB + memos (about 31 memo-min) |
| Programming access | Pads or a Tag-Connect footprint to load the first image at assembly; reset reachable from outside | RECOMMENDED 2026-10-05: Tag-Connect TC2030 no-legs, Cortex pinout (SWO on P1.00), 5 pogo pads as fallback; reset reachable. Justin to say which SWD probe he owns |
| Signing key | Generated once, kept offline and backed up; a lost key means shipped units can't be safely updated | RECOMMENDED 2026-10-05: ECDSA P-256, private key offline under ~/.device-keys, backed up twice, never in the repo; no key rotation for 100 units. Still before units ship |
| Bootloader | MCUboot (NCS) on production; the dev board's UF2 bootloader doesn't carry over | CONFIRMED 2026-10-05: MCUboot (64 KiB partition) works on a bare Raytac; USB serial recovery needs no extra hardware (hold select while pressing reset) |

## Decisions log
- 2026-10-01: EC11 out (too thick). Hall bezel with a magnet array out (no custom parts, no gluing
  magnets). LRA is the only haptic (no keyboard switch). Detents come from the LRA, not mechanical
  parts. Layout B (side by side).
- 2026-10-02: OTA: USB data lines stay wired (recovery path). Staged update, installed on the next charge. Firmware file hosted later. **Revisit OTA before the PCB is sent for manufacturing.**
