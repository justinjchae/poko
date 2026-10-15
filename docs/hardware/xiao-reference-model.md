# XIAO nRF52840 Sense reference model

**Result: built from Seeed's official STEP** (not hand-built). Reoriented to the frame below, checked against Seeed's own mechanical DXF, coloured, and exported.

- Fusion: component `XIAO_nRF52840_Sense_ref`, in the Fusion document **XIAO_nRF52840_Sense_ref** (Device project, Device folder), saved 2026-10-10.
- STEP export: `cad/XIAO_nRF52840_Sense_ref.step` (80 solids, 2.6 MB, Seeed's solids unchanged, only moved).
- The V1B enclosure file and every existing document were not touched.
- Rev 2 (2026-10-10): rotated 180 degrees about Z at Justin's request so the USB-C points toward -Y. All numbers below are for this orientation.

## Frame (all numbers below are in it)

- **Z = 0 is the PCB underside**, +Z up through the PCB top.
- The PCB occupies X 0 to 17.78 and Y 0 to 20.955 (origin at the PCB corner on the **USB-C end**). **The USB-C points toward -Y** and overhangs to Y = -1.527. The antenna end is Y = 20.955.
- It is the earlier frame turned 180 degrees about the vertical line through the board centre (X 8.89, Y 10.4775), so the board stays in the positive quadrant. Converting old numbers: X_new = 17.78 - X_old, Y_new = 20.955 - Y_old.
- Colours: PCB green, USB-C steel, RF shield orange, mic yellow, reset button red, antenna purple.

## Sources

| Tag | What | Link |
|---|---|---|
| STEP | Seeed's 3D model of the board, `XIAO-nRF52840 v15.step`, dated 2023-06-02 | https://files.seeedstudio.com/wiki/XIAO-BLE/seeed-studio-xiao-nrf52840-3d-model.zip (linked from https://wiki.seeedstudio.com/XIAO_BLE/) |
| DXF | Seeed's mechanical drawing, `Seeed XIAO nRF52840 v1.0 Dimensioning.dxf` (dimension entities read directly) | https://files.seeedstudio.com/wiki/XIAO-BLE/Bottom-pad-positioning.zip |
| KiCad | Seeed's v1.1 PCB (rev 2026-01-05), used for part placement and which side each part is on | https://files.seeedstudio.com/wiki/XIAO-BLE/Seeed-Studio-XIAO-nRF52840V1.1-KiCad-Project-260105.zip |

Cross-check of the STEP against the DXF: length 20.955 (exact), width 17.78 (exact), pad pitch 2.54 (exact), row spacing 15.24 (exact), corner radius 1.905 vs DXF R1.9063. Retail listings say 21 x 17.5 mm; Seeed's own drawing and STEP say 17.78, so the listings are rounded.

"Read back" means measured in Fusion after the move, from body bounding boxes (they match the DXF to the micron, so they are exact, not padded). "Est." means not read from a Seeed number.

## Board and heights

| Item | Value (mm) | Source | Flag |
|---|---|---|---|
| Outline | 17.78 (X) x 20.955 (Y) | DXF, read back | |
| Corner radius | 1.905, all four | STEP cylinder faces; DXF R1.9063 | |
| PCB thickness | **1.25** | STEP only (read back Z 0 to 1.25) | **Not in any Seeed spec I found. Measure Justin's board with calipers.** The KiCad file's 1.6 mm stackup is a default template, not used. |
| USB-C shell | X 4.428 to 13.368 (8.94 wide), Y -1.527 to 5.773 (7.30 long), Z 0.26 to 4.46 | STEP, read back | See notes: highest-uncertainty height |
| USB-C top above PCB top | 3.21 (Z 4.46) | read back | |
| USB-C top above PCB underside | **4.46** | read back | |
| USB-C overhang past PCB edge | 1.527 (Y 0 to -1.527) | read back | |
| USB-C centre vs board centre | X 8.898 vs 8.89 | read back | |
| USB-C solder tabs | Y 5.37 to 6.37, 0.3 tall on the PCB top | read back | |
| RF shield | X 2.59 to 15.19 (12.6), Y 6.935 to 17.535 (10.6), top Z 3.25 = **2.00 above PCB top** | STEP, read back | STEP shield bottom is at Z 0.55, 0.7 below the PCB top (a modelling shortcut; the real can sits on the PCB) |
| Reset button | X 13.81 to 15.41, Y 0.33 to 3.42, top Z 1.98 = 0.73 above PCB top | STEP, read back | Part is an Alps SKTAAAE010 per the STEP |
| Mic (PDM, MSM261D3526H1CPM) | X 2.55 to 6.05, Y 18.08 to 20.73, top Z 2.19 = 0.94 above PCB top | STEP, read back | **Top side**, see notes |
| Antenna (ANT1, chip, AN3216) | X 9.10 to 12.30, Y 19.08 to 20.68, top Z 1.75 = 0.50 above PCB top | STEP, read back | |
| Charge LED | X 2.55 to 3.82, Y 0.31 to 0.95, 0.30 tall | STEP, read back | |
| User RGB LED | X 2.69 to 3.69, Y 2.29 to 3.29, 0.30 tall | STEP, read back | |
| Passives (0201/0402 etc.) | top Z <= 1.65 (<= 0.40 above PCB top) | STEP, read back | |
| IMU LSM6DS3TR-C | centre about X 13.46, Y 8.89, inside the shield footprint | KiCad U3 position mapped into the STEP frame (mic, antenna and reset button agree to within 0.03 mm) | **Est.** Not in the STEP. Height not measured here (a 2.5 x 3.0 LGA, under 1 mm in the datasheet as I remember it). Does not set Z because the shield covers it. |
| QSPI flash | footprint U7 at about X 13.71, Y 15.50, inside the shield footprint | KiCad | **Est.** Not in the STEP. The footprint is marked DNP in Seeed's v1.1 KiCad file, so whether the Sense populates it is unconfirmed. |

Parts over 1 mm above the PCB top: only the USB-C (3.21) and the shield (2.00). Everything else on top is 0.94 mm or less.

## Underside and pads

The underside is flat. In Seeed's KiCad file every IC, mic, IMU, LED, button and the USB-C are on the top (F.Cu); the bottom (B.Cu) has test and battery pads only. The STEP models the pad copper 0.01 mm thick, flush with the board.

| Item | Position / size (mm) | Source | Flag |
|---|---|---|---|
| Battery pads (2) | 2.11 (X) x 1.095 (Y) each, centres X 13.339, Y 8.257 and 10.162 | STEP, read back | Which is BAT+ and GND comes from KiCad (BAT0 at Y 10.16, GND0 at Y 8.26), **est.** mapping |
| NFC pads (2) | 1.09 (X) x 2.11 (Y) each, centres X 3.179 and 5.082, Y 19.687 | STEP, read back | |
| SWD test pads (4, round) | dia 1.524, X 7.619 and 10.159, Y 1.902 and 4.442 (2.54 grid) | STEP faces | KiCad draws these at dia 1.143 (TP-D45MIL); I used the STEP value, so size is **est.** |
| Underside keep-out | none needed for components; keep clear of the 8 pad areas above | derived | Anything that touches the underside can short or press on pads |

## Castellations and header holes

| Item | Value (mm) | Source |
|---|---|---|
| Count and rows | 7 per long edge, 14 total, edge centres at X = 0 and X = 17.78 | STEP |
| Pitch | 2.54, first at Y = 2.922, then 5.462, 8.002, 10.542, 13.082, 15.622, 18.162 | STEP, DXF (2.54) |
| Castellation half-hole | dia 0.634, at the board edge | STEP |
| Through-hole behind each | dia 0.75 at X = 1.27 and 16.51 (15.24 apart), top copper ring dia 1.53 | STEP, DXF (15.24) |
| Pad outline | the DXF has unlabelled 2.032 x 1.016 dimensions that probably describe it | DXF | **Est.** interpretation, not used |

Headers are not in this model. The V1B enclosure keeps its own `XIAO headers 2x7 (ref)` for Justin's soldered headers.

## Antenna end

The antenna is a ceramic chip (ANT1, AN3216) at the Y = 20.955 end, X 9.10 to 12.30, so it sits right of the board centre. Seeed's files give **no keep-out dimension**; I did not invent one. For stack work: nothing metal over or beside that end is the safe assumption until the PM picks a number (Nordic's and the antenna vendor's layout guidance would be the source).

## Overall bounding box (read back from Fusion)

| Case | X | Y | Z |
|---|---|---|---|
| Whole model | 17.78 (0 to 17.78) | 22.482 (-1.527 to 20.955) | 4.46 |
| Without the USB-C (PCB and shield limit it) | 17.78 | 20.955 | 3.25 |
| Without the shield and USB-C | 17.78 | 20.955 | 2.19 (mic) |
| With vs without the pads | identical, pad copper is inside the PCB envelope | | |

## Conflicts with the plan

1. **A model of this STEP already existed.** The Device project has a document "XIAO-nRF52840 v15" (the same Seeed file, imported earlier, Y-up, centred), and Enclosure V1B references it. This new file is the same geometry moved to the Z-up corner frame above, with colours and the numbers measured.
2. **The original underside assumption is wrong for this board.** The mic, IMU and flash are not on the underside. They are on the top; the underside is a flat face with pads. That is good for stacking (nothing to clear below), bad if anything on top was assumed free.
3. **The total height is 4.46 mm** (underside to USB-C top), with the USB-C shell sitting 0.26 mm above the underside. The STEP's USB-C and PCB overlap in Z (the shell is 0.26 to 4.46, the PCB is 0 to 1.25) and the STEP PCB has no cutout for it, so the connector looks mid-mounted but the CAD does not show how. Neither the PCB thickness nor the USB-C height is stated anywhere in the Seeed files I read. If the carrier plan assumes a thinner board, check it against this number, and have Justin calliper his board (thickness, and USB-C top to underside) before the stack is trusted.
4. The 3D file is titled "XIAO-nRF52840 v15" and dated 2023; the KiCad project is rev 2026-01-05. Mic, antenna and reset-button positions agree between them to about 0.03 mm, so the layout is the same. The 3D file has the Sense mic, so it is the Sense board, but it does not carry the IMU or flash.

## Open items

- Calliper check on a real board: PCB thickness, USB-C top height above the underside, USB-C overhang.
- Antenna keep-out number (none published in the files above).
