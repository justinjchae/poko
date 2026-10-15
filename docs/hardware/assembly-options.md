# First-batch assembly options: line items (2026-10-10)

Planning numbers, not quotes. The only authoritative figure is a JLC instant quote with the real BOM and Gerbers. There is no schematic yet,
so passive counts are assumed (39 passives per board, 26 unique parts, about 250 solder joints, 61 of them on the Raytac).
Fees come from JLC's help page (updated 2026-09-09), part prices and stock from the JLC parts API on 2026-10-10 (qty 1-9 tier),
the Raytac JLC price from Justin's quote ($15.69 each at 10). Excluded from every column: displays, LRAs, cells, JST connectors, magnets, enclosure, SWD probe.

Assumptions that are guesses: bare PCB $8 for 10 pieces (60 x 90 mm, 2 layer), JLC shipping $30, US tariff 35% on PCB, parts and assembly and 90% on the stencil
(from `jlc-cost.md`), X-ray on the Raytac, IMU and mic (21 pieces for 7 boards, $0.82 each), no Standard fixture fee ($16.42 possible).
Whether the 35% applies to parts inside the PCBA order is not verified. Duty on the Raytac bought from Digi-Key (made in Taiwan) is not included.

## Raytac MDBT50Q-P1MV2 prices, live 2026-10-10
| Source | Price | Stock | Notes |
|---|---|---|---|
| JLC pre-order (quote) | $15.69 each at 10, $15.50 at 100 | none (8 business days) | 2.0x JLC's own list price of $7.73 |
| Digi-Key (Marketplace, ships from Raytac) | $6.00 each (only the qty 1 price is shown) | 39 | **$25.00 flat shipping per order**, ships in about 14 days, non-returnable |
| TME US | no price | 0 | the 10-01 note of 1,239 in stock is gone |
| Mouser | unknown | unknown | page blocked my browser check; Adafruit sells the 1MV2 breakout, not the module |
| LCSC | about $7.33 at 10+ | 0 | |

## Parts at 7 boards (JLC prices)
| Part | Code | Per board | Qty bought | Unit | Cost |
|---|---|---|---|---|---|
| Raytac MDBT50Q-P1MV2 (JLC quote) | C5119772 | 1 | 7 | 15.6892 | 109.82 |
| W25Q128JVSIQ flash | C97521 | 1 | 7 | 2.5571 | 17.90 |
| LSM6DS3TR-C IMU | C967633 | 1 | 7 | 1.5180 | 10.63 |
| MSM261DDB020 mic | C27636198 | 1 | 7 | 0.6499 | 4.55 |
| DRV2605L | C527464 | 1 | 7 | 1.4252 | 9.98 |
| AS5600-ASOT | C499458 | 1 | 7 | 1.2232 | 8.56 |
| TYPE-C-31-M-12 | C165948 | 1 | 7 | 0.1860 | 1.30 |
| HDGC 16-pin connector | C2919496 | 1 | 7 | 0.2162 | 1.51 |
| Epson 32.768k -003 | C99010 | 1 | 7 | 0.2030 | 1.42 |
| USBLC6-2SC6 | C7519 | 1 | 7 | 0.1770 | 1.24 |
| TP4054 | C32574 | 1 | 7 | 0.1315 | 0.92 |
| TLV9001 | C398363 | 1 | 7 | 0.0981 | 0.69 |
| AO3400A | C20917 | 1 | 7 | 0.0890 | 0.62 |
| TS-1187A tact switch | C318884 | 1 | 7 | 0.0206 | 0.14 |
| 12 caps/resistors/inductor lines (12 pF, 10 uH, 100 nF, 1 uF, 4.7 uF, 10 uF, 5.1k, 3.3k, 27R, 2.2R, 100k, 10k), minimum 20 each | Basic | 39 total | 20-70 each | 0.0015-0.0305 | 3.73 |
| **Total** | | | | | **173.02** (63.19 without the Raytac) |

## Option matrix (USD)
A = JLC assembles everything (Standard). B = JLC assembles everything except the Raytac, which you buy from Digi-Key and hot-air solder.
C = bare boards, you place everything. "3" or "7" is how many boards get assembled; 10 bare boards are fabbed in every case.

| Line | A7 | A3 | B7 | B3 | C7 |
|---|---|---|---|---|---|
| Bare PCB, 10 pcs | 8.00 | 8.00 | 8.00 | 8.00 | 8.00 |
| JLC parts excluding Raytac | 63.19 | 28.85 | 63.19 | 28.85 | (LCSC) 63.19 |
| Raytac (A: JLC quote; B and C: 7 or 3 x $6.00 + $25 shipping) | 109.82 | 47.07 | 67.00 | 43.00 | 67.00 |
| Setup | 25.56 | 25.56 | 25.56 | 25.56 | 0 |
| Stencil | 8.21 | 8.21 | 8.21 | 8.21 | 18.00 (US shop, guess) |
| Component loading (26 or 25 lines x $1.53) | 39.78 | 39.78 | 38.25 | 38.25 | 0 |
| X-ray | 17.22 | 14.76 | 11.48 | 9.84 | 0 |
| SMT joints | 2.77 | 1.19 | 2.08 | 0.89 | 0 |
| Confirm placement + packing | 0.95 | 0.95 | 0.95 | 0.95 | 0 |
| Tariff (35%; 90% on the JLC stencil) | 100.94 | 65.54 | 59.72 | 46.71 | 2.80 to 24.90 |
| Shipping | 30.00 | 30.00 | 30.00 | 30.00 | 40.00 (PCB 20 + LCSC parts 20) |
| Paste and flux | 0 | 0 | 0 | 0 | 32.00 |
| **Total** | **406** | **270** | **314** | **240** | **about 231-253** |
| Per assembled board | 58 | 90 | 45 | 80 | 33-36 |
| One-time tools | 0 | 0 | 90-200 (hot air $60-120, paste, loupe) | 90-200 | 170-600 (oven or hotplate, hot air, microscope) |
| Your time | 0 | 0 | 2-4 h | 1-2 h | 10-20 h |

For comparison, the same 7 boards under Economic assembly (only possible with an Economic-eligible IMU, which does not exist in practice): about $357.

## XIAO + carrier board option (added 2026-10-10)
X = a carrier PCB with a XIAO nRF52840 Sense hand-soldered to it (in a notch or on top). The XIAO supplies the MCU, antenna, IMU, mic, charger, regulator, 32 kHz crystal, USB-C and 2 MB flash,
so the JLC order shrinks to 13 unique lines: DRV2605L, AS5600, TLV9001, AO3400A, the HDGC connector, the tact switch and 7 passive values (about 20 passives per board, about 88 joints).
Every one of those is Economic-eligible, so assembly drops to **Economic** ($8.18 setup, $1.53 stencil, $3.07 for each of the 4 Extended lines, no X-ray).
XIAO Sense price: Seeed $15.90 each, $13.90 at 10+ (store page, 2026-10-10; Seeed ships from a China warehouse). Shipping assumed $10. The 16 MB flash is left off (Justin, 2026-10-10).

| Line | A7 | A3 | B7 | B3 | C7 | X7 | X3 |
|---|---|---|---|---|---|---|---|
| Bare PCB, 10 pcs | 8.00 | 8.00 | 8.00 | 8.00 | 8.00 | 8.00 | 8.00 |
| JLC parts excluding the MCU | 63.19 | 28.85 | 63.19 | 28.85 | 63.19 (LCSC) | 23.29 | 10.89 |
| MCU (Raytac JLC quote / Digi-Key $6 + $25 / XIAO $15.90 each + $10) | 109.82 | 47.07 | 67.00 | 43.00 | 67.00 | 121.30 | 57.70 |
| JLC fees (setup, stencil, loading, X-ray, joints, misc) | 94.49 | 90.45 | 86.53 | 83.70 | 18 (stencil) | 23.43 | 22.86 |
| Tariff (35%; 90% on the JLC stencil) | 100.94 | 65.54 | 59.72 | 46.71 | 3-25 | 19.99 | 15.46 |
| Shipping | 30.00 | 30.00 | 30.00 | 30.00 | 40.00 | 30.00 | 30.00 |
| Paste and flux | 0 | 0 | 0 | 0 | 32.00 | 0 | 0 |
| **Total** | **406** | **270** | **314** | **240** | **231-253** | **226** | **145** |
| Per assembled board | 58 | 90 | 45 | 80 | 33-36 | 32 | 48 |
| One-time tools | 0 | 0 | 90-200 | 90-200 | 170-600 | 0 (an iron) | 0 (an iron) |

Savings: X7 against A7 saves about $180, against B7 about $88; X3 against A3 saves about $125, against B3 about $95.
Not in the X columns: the carrier PCB design work, a possible 35% tariff on the XIAO if it ships from China (about +$39 for 7), the 16 MB flash (about +$20 if added later), hand-soldering the XIAO and battery wires.

## Alternatives to the Raytac that JLC has in stock (2026-10-10)
| Part | JLC stock | Price at 1-9 | What it is | Problem |
|---|---|---|---|---|
| Ebyte E73-2G4M08S1C (C356849) | 1,471 | $7.65 (qty 10: $7.49) | nRF52840 module, 1 MB / 256 KB, ceramic antenna, 13 x 18 mm, 43 castellated 1.27 mm pads (hand-solderable with an iron), USB, SWD, 32 kHz crystal pins | pin table (Chinese datasheet) breaks out only about 28 usable GPIOs; the QSPI pins P0.19, P0.21, P0.23 and P0.11 are missing, so the flash would move to plain SPI; bigger than the Raytac; radio certification not verified |
| Ebyte E73-2G4M08S1CX (C2764963) | 1,458 | $6.34 | same with a u.FL connector | no on-board antenna |
| RF-star RF-BM-ND05I (C5441194) | 38 | $7.00 | nRF52840, u.FL | no on-board antenna, 38 in stock |
| nRF52840-QIAA-R bare chip (C190794) | 47,859 | $5.93 (qty 100: $4.17) | the chip itself | needs our own RF design, crystals, matching and a full FCC program |
| RF-BM-ND04 (C5441197) | 171 | $5.33 | looks like nRF52840, is nRF52832 | wrong chip |
