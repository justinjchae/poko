# JLC / LCSC cost notes (2026-10-09)

Planning numbers for the first board order. Nothing here is a quote. The JLC instant quote (BOM +
Gerbers) is the only authoritative number, so redo this when a schematic exists.

Sources: Hack Club guide https://highway.hackclub.com/guides/JLC-cost-optimizing, JLC pages
(US tariff FAQ updated 2026-09-09, tariff news 2026-03-17, assembly price page, part pages),
the guide's economic-parts CSV https://lrks.github.io/jlcpcb-economic-parts/economic-parts.csv
(library `base` = Basic, `expand` = Preferred Extended; that mapping is inferred).

## Tariffs (US, DDP)
- The guide's "60%" is the May 2025 rate. JLC's page updated 2026-03-17 lists **US DDP advance rates:
  PCB 35%, SMT 35%, stencil 90%** (3D printing 40-70%, CNC aluminum 6061/7075 **90%**, CNC plastics 40%).
- JLC's stated overall stack is about 35% to 92.5%. Rates in the 35-90% band are NOT refunded or adjusted
  against the real customs bill. Changes of +/-10% or less are not adjusted either.
- Not stated: whether the base includes shipping (forums say goods only; assumed here) and whether the SMT
  rate covers the parts inside the PCBA order (assumed yes).
- The pages disagree in places (one section mentions 175%), so treat the checkout tariff line as the truth.
- Enclosure: a JLC CNC aluminum order would be at 90%. A US shop avoids that.

## Fee structure (JLC "PCB Assembly Cost" help page, last updated 2026-09-09, read 2026-10-10)
This replaces the older table (the "$3 extended" and "$1.50 basic, unconfirmed" figures were wrong or stale).
| Item | Economic | Standard |
|---|---|---|
| Setup | $8.18 | $25.56 (one side), $51.12 (two) |
| Stencil | $1.53 | $8.21 (one side) |
| Component loading | **$3.07 per unique Extended part, Basic free** | **$1.53 per unique part, Basic AND Extended** (every line, passives included) |
| SMT joints | $0.0016/joint | $0.0016/joint |
| X-ray (LGA, module) | $1.64/pc for 1-10 pcs, $0.82/pc for 11-50 | same |
| Confirm parts placement | $0.45 | $0.45 |
| Packing | free | $0.50 + $0.00003 x PCB cm2 |
| Fixture (Standard, rigid) | not listed | $16.42 for 1-29 pcs (unclear whether it applies to a one-sided order; ask in the quote) |
| Stencil / fixture storage | not listed | $4.93 each (probably only if you ask for storage) |
| Handling fee | if both tiers are possible, Economic must save at least $14.93 or the shortfall is charged | |
Consequence: **under Standard, swapping an Extended part for a Basic one saves nothing** (every unique part costs $1.53 either way), so the 12 pF-cap, TP4054 and LMV321 swaps
save only part price there. They matter only under Economic, where Extended parts cost $3.07 each.
Economic limits (JLC capabilities page): 2-50 pieces per order, single-sided placement, 2/4/6 layers, 0.8-1.6 mm, standard stackup, minimum package 0402.

## PCB size and layers (from the guide)
- Cheap tier: 2-layer under 100x100 mm, or 4-8 layer under 50x50 mm. A 60x90 outline is only in the cheap tier at 2 layers.
- All components on the front means the back can be a solid ground plane, which suits 2 layers.
  Check the Raytac MDBT50Q hardware guide for layer and ground-clearance advice (not read yet).
- Thickness: JLC offers 0.8/1.0/1.2/1.6/2.0 on 4-layer (not 0.6). No surcharge found for 0.8-1.2 (2024 post,
  unconfirmed; JLC publishes no price table). Tolerance +/-10% at 1.0 mm and up, +/-0.1 mm below 1.0.

## Part classes (JLC part pages and the CSV)
| Part | LCSC | Class | PCBA type | Note |
|---|---|---|---|---|
| Raytac MDBT50Q-P1MV2 | C5119772 | Extended | Economic + Standard | X-ray required, 0 stock (global sourcing) |
| HDGC 0.5K-HX-16PWB | C2919496 | Extended | Economic + Standard | |
| MCP73831T-2ACI/OT | C424093 | Extended | Economic + Standard | |
| AO3400A | C20917 | Basic | Economic + Standard | |
| TLV9001IDBVR | C398363 | Extended | Economic + Standard | |
| USBLC6-2SC6 | C7519 | Extended | Economic + Standard | |
| Epson Q13FC13500003 | C99010 | Extended | Economic + Standard | |
| 12 pF C0G | C107034 | Extended | | replace with Basic C38523 (0603) or C1547 (0402): PASS 2026-10-10 (value stays 12 pF) |
| Epson Q13FC13500004 | C32346 | Basic | Economic + Standard | 12.5 pF: REJECTED, outside Raytac's CL max 9 pF |
| TP4054-42-SOT25R | C32574 | Preferred Extended | Economic + Standard | 39,877 in stock, $0.10 @100: PASS with corrections |
| LMV321IDBVR | C7972 | Preferred Extended | Economic + Standard | REJECTED on offset, see LOCK.md |
| 18 pF C0G (reference) | C1647 / C1549 | Basic | Economic + Standard | only needed with a 12.5 pF crystal, which is rejected |
| W25Q128JVSIQ | C97521 | Basic | Economic + Standard | only Basic 16 MB flash |
| LSM6DS3TR-C | C967633 | Extended | **Standard Only** | whole LSM6DS family is Standard Only |
| MSM261DDB020 | C27636198 | Extended | Economic + Standard | |
| DRV2605L | C527464 | Extended | Economic + Standard | |
| TYPE-C-31-M-12 | C165948 | Extended | Economic + Standard | |
| ITR8307/TR8 | C67922 | Extended | Economic + Standard | SMD-4P |
| AS5600-ASOT | C499458 | Extended | Economic + Standard | |
| TS-1187A-B-A-B | C318884 | Basic | Economic + Standard | SMD, 1.5 mm tall |
| TS-1088-AR02016 | C720477 | Basic | Economic + Standard | SMD, 2 mm tall |
| SKRPACE010 | C139797 | Extended | Economic + Standard | 2.5 mm tall, drop in favor of TS-1187A |
| 5.1k 0603 | C23186 | Basic | | |
| LIS3DHTR | C15134 | Extended | **Standard Only** | corrected 2026-10-10 from the live JLC page (this table said Economic + Standard); 61 in stock; swap rejected, see LOCK.md |

Rejected: C2906290 (CB1.6 sink-mount USB-C) is Extended, difficulty High, Standard Only.

## Savings ideas
| Change | Saves | Risk |
|---|---|---|
| IMU: LSM6DS3TR-C -> LIS3DHTR | **nothing: LIS3DHTR is Standard Only too (2026-10-10)** | rejected; every usable accelerometer on JLC is Standard Only, see LOCK.md IMU row |
| Crystal C99010 -> C32346 (Basic, Epson Q13FC13500004, $0.17) | $3 + part | **rejected 2026-10-10**: CL 12.5 pF vs Raytac's max 9 pF; no Basic crystal at 9 pF or below exists |
| 12 pF caps -> Basic C38523 / C1547 | $3 | none, PASS 2026-10-10 |
| MCP73831 -> TP4054 C32574 (preferred, $0.10 @100) | about $3 fee + about $0.37 per board | PASS 2026-10-10: PROG 5.1 kohm gives about 186 mA, STAT is open-drain (also fixes the 5 V STAT problem of the MCP73831) |
| TLV9001 -> LMV321 C7972 (preferred, $0.097 vs $0.077) | $3 fee only | **rejected 2026-10-10**: offset up to 7 mV on a 96 mV reference, +/-3.2 mA, dead zone at low brightness |
| Raytac: compare JLC global-sourcing quote vs TME ($6.50 @100) + shipping to China | unknown | consignment may not be Economic-compatible (JLC docs silent) |

Not worth chasing: bare nRF52840 ($4.20, needs RF design + FCC), Ebyte E73-2G4M08S1C (C356849, about $5.5-7.6,
no JLC listing, cert unclear), cheaper flash (no cheaper Basic 16 MB part).

## Estimate, 10 boards, 2-layer, one side, shipped to the US
Assumed: PCB $5-10 for 10 pcs (guess), about 300 joints/board, parts at qty-100 LOCK.md prices +20%,
Raytac $8-9 via global sourcing, shipping $20-40 (guess), X-ray $0-16.

| Scenario | Pre-tariff | Tariff | Shipping | Total |
|---|---|---|---|---|
| Baseline (Standard, 11-12 extended parts), 60% tariff (old guide rate) | $210-335 | $125-200 | $20-40 | $355-580 |
| Baseline, 2026 rates (PCB 35%, SMT 35%, stencil 90%) | $210-335 | $78-122 | $20-40 | $308-497 (mid about $400) |
| Optimized (Economic, IMU/crystal/caps/charger/op-amp swapped, 8 extended) | $184-275 | $65-97 | $20-40 | $269-412 (mid about $340, about $34/board) |

Assembling only 2 boards and fabbing 10: about half the 10-assembled cost (fixed fees stay, parts drop to about $50).
Excluded: displays (7 ordered, $66), LRAs ($31), cells, magnets, enclosure, JST connectors (hand-soldered),
SWD probe, anything bought from TME or other non-JLC sources.

## Re-run 2026-10-10 after the swap checks and the JLC Raytac quote
What changed: the IMU stays a Standard Only part, so assembly is **Standard**, not Economic (+$17 setup, +$7.2 stencil before tariff); the TLV9001 and the 9 pF crystal stay Extended (+$6);
only the 12 pF caps and the TP4054 charger save fees. The Raytac quote is $15.69 each (10) / $15.50 (100) instead of the assumed $8-9 (+about $50 on 7 modules).
JLC part pages (2026-10-10): Economic PCBA also needs 2-50 pieces, single-sided placement, 2/4/6 layers, 0.8-1.6 mm board, standard stackup, single boards or mouse-bite panels, minimum package 0402.

| 7 boards assembled, 10 fabbed | Pre-tariff | Tariff | Shipping | Total |
|---|---|---|---|---|
| Standard, 10 Extended lines, Raytac at the old $8.50 (if TME or a cheaper source works) | $169-234 | $63-86 | $20-40 | **about $253-361** |
| Standard, 10 Extended lines, Raytac at the JLC quote $15.69 | $220-285 | $81-104 | $20-40 | **about $321-429** (mid about $375, about $46-61 per board) |

Same assumptions as the tables below (planning numbers, not quotes). At 100 units the Raytac quote costs about $1,550 against about $650-713 at TME, a gap of about $840.
Extended lines now: Raytac, HDGC connector, TLV9001, USBLC6, crystal, LSM6DS3TR-C, mic, DRV2605L, TYPE-C, ring sensor (AS5600 or the ITR8307 pair); TP4054 is Preferred and the caps are Basic.

## First batch plan: 7 boards assembled (Justin, 2026-10-09)
(Superseded by the re-run above: the Economic-with-swaps row assumed the IMU swap, which was rejected.)
Same assumptions as above (fab 10 bare, assemble 7; parts $105-154 baseline, $97-146 with the swaps; X-ray $0-11).

| Scenario | Pre-tariff | Tariff | Shipping | Total | Per assembled board |
|---|---|---|---|---|---|
| Economic + swaps (IMU to LIS3DHTR, Basic crystal/caps, TP4054, LMV321) | $139-204 | $49-72 | $20-40 | **$208-316** (mid about $262) | $30-45 |
| Baseline (Standard because of the LSM6DS IMU) | $180-263 | $68-97 | $20-40 | $268-400 (mid about $335) | $38-57 |

The swaps save about $60-85 on this batch, almost all from leaving Standard assembly. The fixed fees are spread over 7 boards instead of 10,
so the per-board number is a bit higher than the 10-board case.

## DIY assembly vs JLC (hand-placed, hotplate or oven) - not recommended for the first batch
Justin has no reflow oven or hot air station, so equipment would be bought.

Avoided JLC assembly fees (10 boards): about $38-54 optimized Economic ($49-74 with tariff), $72-106 Standard ($91-140 with tariff).
Parts cost is roughly a wash: US distributors cost more than LCSC; whether LCSC-to-US parts carry a tariff was not verified.

| DIY extra cost | Estimate |
|---|---|
| Stencil, 0.1 mm laser-cut (US shop, or JLC about $9 + 90% tariff) | $10-25 |
| Paste, flux, consumables | $25-40 |
| Several vendors (about 25 unique parts): shipping, MOQ overhead | $20-40 |
| One-time: hotplate or T-962-style oven $60-300, hot air $60-120, loupe or microscope $50-150 | $170-600 |

Net first run: about -$85 to +$70 before equipment, plus an estimated 10-20 hours (1-2 h per board, about 100-150 placements).
Pays off only after several runs; not viable at 100 units.

Risks, greatest first:
1. 0.5 mm pitch: TYPE-C-31-M-12 (16 pins + THT legs), HDGC display connector, DRV2605L (VSSOP-10). Paste printing and bridging; needs a stencil jig.
2. Hidden joints: Raytac module (JLC page says X-ray required), LGA IMU, LGA mic. Cannot inspect, hard to rework; IMU and mic are MSL 3 (storage, bake).
3. Bottom-port mic: paste or flux in the sound port.
4. 1.0-1.2 mm board on a hotplate: warp, uneven heating, tombstoning on 0402/0603; lead-free profile peaks near 245 C.
5. Yield with no AOI or X-ray; each failed board is lost parts and time.
Hybrid that makes sense: JLC assembles (Economic), Justin hand-solders the JST and LRA tail as planned. Practice hotplate reflow on a scrap board first if DIY is wanted later.

## Open items
- Run a JLC quote with a real BOM and Gerbers; check the checkout tariff line and whether it covers parts.
- Confirm whether consigned parts (Raytac, DRV2605L) are allowed on Economic.
- Swaps checked 2026-10-10: caps and charger pass, IMU, crystal and op-amp rejected (LOCK.md, "Swap checklist"). Justin to confirm each.
- Ask JLC why the Raytac quote is 2x its own list price ($7.73 at qty 10).
- Decide: 2-layer vs 4-layer.
- First batch: 7 boards assembled.
- Confirm the extended-fee amount ($3 vs $1.50). (The Epson -004 load capacitance is settled: 12.5 pF, rejected.)
