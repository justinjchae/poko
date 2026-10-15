# Tolerance stack and datums (2026-10-09)

First-pass Z stack for the enclosure. **Sourced** numbers come from datasheets (marked S). Everything else is
an assumption (marked A) and should be replaced by a measurement from a real print or board.
Related: `ring-design.md`, `LOCK.md`, CAD scripts in `cad/` (display, LRA).

## Layout (Justin's current sketch)
- Front plate (CNC aluminum, 1.0 mm), display against its back face. Back plate sits inside the walls, 1.0 mm.
- Total thickness T = 8.0 mm (1.0 + 6.0 of wall from A + 1.0). A = back face of the front plate.
- All components on the front (display-facing) face of a 1.2 mm PCB. USB-C is top-mounted on that face and centered at T/2.
  The PCB front face is therefore 4.63 mm from A, about 3 mm behind the display back face.
- Back of the PCB is bare (clipped THT leads only), with a small gap to the back plate.

## Datum scheme
- Datum A: back face of the front plate (Z). Datums B/C: two pilot pins in the front shell (XY, rotation).
- Display: against A, XY from a pocket rim. PCB: pilot pins in its holes, seated on standoffs from A, located by
  the same shell, not through the display. Ring and select button locate off the shell; only the button-to-switch gap
  crosses into the PCB chain. USB-C opening is cut entirely in the front plate (no parting line through it).
- Seat the PCB on the face the receptacle is dimensioned from, so PCB thickness drops out of the port chain.

## Verified component heights (above the board surface)
| Part | Height | Below the surface | Source |
|---|---|---|---|
| USB-C TYPE-C-31-M-12 (C165948) | **3.26 mm** body, datum = seating plane (S) | 4 plated-slot shell legs 1.01 mm (S); 2 locating holes dia 0.6 | Hroparts drawing |
| USB-C opening centerline | about **1.67 mm** above the seating plane (scale reading off the drawing, +/-0.04; not dimensioned) | | same |
| JST S2B-PH-K-S (C173752) | **4.8 mm** (S) | leads 3.4 mm (S) | JST PH catalog p.22 |

- Legs are 1.01 mm: contained in a 1.2 mm board, flush in 1.0, 0.21 mm proud in 0.8.
- JST leads: 2.2 mm stick out of a 1.2 mm board (2.6 mm for 0.8). Clip before soldering to about 0.5 mm proud.
- A distributor lists the USB-C at 3.21 mm; the drawing governs.

## Formulas
- Back gap: `gap = T/2 - back_plate - Hc - t_pcb`, where Hc = opening centerline height (1.63 if half of 3.26, about 1.67 measured).
  It does not depend on the front plate thickness.
- Port center from A: `T/2 - front_plate`; PCB seat height `h = T/2 - front_plate + Hc` (4.63 for T=8, front 1.0, Hc 1.63).
- Cavity for the tallest front-face part: `D >= tallest + front clearance (0.2) + t_pcb + gap`, with `D = T - front - back`.
- Centering requires `T = 2 (gap + back_plate + Hc + t_pcb)`.

## Justin's sketch numbers (nominal)
8.00 total, walls 1.00, PCB 1.20, USB-C 3.26 centered: gap = 0.170 mm from the displayed dimensions (sketch shows 0.187;
one dimension is probably rounded). With Hc = 1.67 the gap is 0.13.

## Allowances needed behind the PCB (A = assumed)
| Piece | Printed | CNC / production |
|---|---|---|
| Back-side features (clipped THT leads, fillets) | 0.1 (0.5 if long leads / THT on the main board) | 0.1 |
| Board warp | 0.3 first print, 0.2 design (typical 0.1-0.3% of 85 mm; IPC ceiling 0.75% about 0.64 mm; JLC publishes no limit) | 0.1-0.2 |
| Tolerance RSS of D, h, PCB thickness | 0.28 (D +/-0.2, h +/-0.1, PCB +/-0.16) | about 0.14 (D, h +/-0.05, PCB +/-0.12 at 1.2 mm) |
| Margin | 0.1 (0.05 with soft contact) | 0.05-0.1 |
| **Total** | **about 0.7 (no THT) to 1.1** | **about 0.5-0.7** |

Realistic reductions: keep THT off the main PCB back, calibrate the printer and compensate in CAD (same-part features are
correlated), balance copper to reduce warp, allow soft contact.

## Reaching about 0.7 mm at 8 mm (levers, from the gap formula)
| Change | Gap |
|---|---|
| Sketch as drawn (1.2 PCB, 1.0 back plate) | 0.17 |
| PCB 1.0 | 0.37 |
| PCB 0.8 | 0.57 |
| Back plate 0.8 | +0.2 |
| T +1 mm | +0.5 |
| PCB 0.8 and back plate 0.8 (needs a 0.8 front plate too for the 4.8 mm JST) | 0.77 |

Candidate: T about 8.1-8.2 mm, 0.8 mm PCB and plates, gives gap about 0.8 and centered USB-C. The 4.8 mm JST on the front
then has only about 0.1 mm of front clearance, so allow a small pocket in the front plate or round T up a little.
Without centering the tallest front part sets the cavity: JST 4.8 needs T about 8.9 (1.0 plates, 1.2 PCB); USB-C alone about 7.4;
centered USB-C about 9.06 (1.0 plates, 1.2 PCB).

## Consequences of this layout
- Display retention: the thin foam gap is gone (about 3.08 mm between the display back and the PCB). Needs a retainer ring
  or thicker foam. The space under the disc can hold parts up to about 2.8 mm (Raytac module and others still unchecked).
- Front free height beside the display is about 4.4 mm (h - 0.2); the 4.8 mm JST body is about 0.4 mm too tall without a pocket,
  or use a lower connector (1.0/1.25 mm pitch).
- Bluetooth: aluminum blocks the antenna; use a plastic window or plastic back over the Raytac antenna.
- Aluminum is about 35x stiffer than PETG, so printed-style leaf springs do not carry over. Use elastomer or foam pads.

## PCB hold-down (decided to try)
- Friction pilot pins (0.03-0.05 mm interference) keep the PCB in place with the back plate off. Start with 2.0 mm pin in 2.1 mm hole
  and test, JLC hole tolerance not checked. Spring tabs or pads in the back plate clamp the PCB onto the standoffs, each opposite a standoff,
  with one pair close to the USB-C (cable side loads).
- Rejected for now: hooks through the PCB (cost 0.6-0.8 mm locally and printed upright hooks bend across layer lines, about 3-4% strain
  over 3.35 mm); screws from the back (heads 1.1-1.6 mm, M1.6/M2). Hooks make sense once molded.
- Thread depth into a 1.75 mm printed standoff is short (about 2.6 mm if the hole runs into the wall, leave 0.6 mm skin).

## Rejected USB-C options
- Mid-mount / sink-board 16P parts at JLC (C2906290 CB1.6, C2906289 CB0.8, C2835313, C963367): Extended, difficulty High, Standard-only
  assembly; centerline offset not in any datasheet found; no CB1.0 or CB1.2 variant. Dropped in favor of the top-mount TYPE-C-31-M-12.

## Update 2026-10-10: XIAO in-line, direct-solder battery, back-plate options
Numbers assume: T = 8.00, plates 1.0, PCB 1.2 (XIAO assumed 1.2; its STEP says 1.25, unverified), USB-C centerline
**1.605 mm above the PCB top face** (Justin measured 3.21 mm connector height; the XIAO STEP shell is 4.20 mm tall and
overlaps the PCB, which is probably a modeling artifact, so the opening centre still needs a check). The XIAO sits in a
notch of the main PCB with its top face flush to the main PCB top. Reference model: `xiao-reference-model.md`.

- The gap is set by the **thickest board**, which is the XIAO, so thinning the main PCB alone does not help.
- Battery: cell leads soldered directly to pads on the **front** face (see `LOCK.md`). No JST, so the 4.8 mm connector
  and its front-plate pocket are gone. Do not put the solder joints on the back: only about 0.2 mm exists there.

### Back gap (PCB back face to back-plate inner face)
`gap = (T - p)/2 - Hc - t` for the overlay plate with the port centered on the body band; `gap = T/2 - p - Hc - t` for inset.
| Case | Gap |
|---|---|
| Inset plate, port centered on the full 8.0 edge, PCB 1.2 | **0.195** (0.145 with a 1.25 XIAO) |
| Same, PCB 1.6 | -0.205 (collision) |
| Overlay plate (p = 1.0), port centered on the body band, 3.5 mm from the front | **0.695** |
| Overlay, p = 1.2 / 1.5 | 0.595 / 0.445 (plate costs 0.5 mm of gap per mm) |
| Inset, port 0.3 mm off-center toward the front | +0.3 |
| T +0.4 mm | +0.2 |
| 0.3 mm recess in the back plate under the XIAO only | +0.3 local |
Need (table above): about 0.5-0.7 CNC, 0.7-1.1 printed. A plate thinner than 1.0 is rejected: countersunk M1.6 heads are
about 1 mm tall and a 0.8 mm plate is hard to hold flat and machine.

### Overlay vs inset (back plate)
| | Overlay | Inset with rim |
|---|---|---|
| Port centering | Centered on the visible body band, needs a deliberate seam (reveal, V-groove, contrasting finish) | Centered on the full 8.0 edge |
| Gap | ~0.695 | ~0.195 |
| Back stop | Wall end face (simplest datum) | Ledge in the rim |
| Plate | Carries the back fillet, thin and hard for a shop | Flat, easy |
| Edge protection | Plate edge exposed | Walls protect it |
| Min outline width (54.1 ring) | 59.1 | about 60.1 (60.6 with margin) |

### Back fillet (R 2.5 on an 8 mm edge, flat strip 3 mm)
- Front edge: fine (one piece, no seam).
- Inset: needs wall >= R + 0.5, but only over the plate's height. Keep 1.5 mm walls above and widen a rim ~1.0 mm tall to
  about 3.0 mm. Fillet offset from the outline at height z above the back plane: `R - sqrt(R^2 - (R - z)^2)`; at z = 1.0 it is 0.5 mm.
- Overlay: the plate carries the fillet and the seam lands on the curve about 1 mm above the back plane; no knife edge.
- With R 2.5 the back flat is outline minus 5.0 mm each way. Ring minimum width = ring OD + 2R (59.0 / 59.1 / 61.0 for
  54.0 / 54.1 / 56 mm rings). Current outline 60 x 90 covers a 54.1 mm ring with 0.45 mm per side (overlay).

### Magnet ring (not yet in the stack)
- Ring (54 x 46, about 1.5 mm, steel shim optional) plus 0.4-0.6 mm floor toward the phone is about 2.0-2.1 mm of plate,
  against 1.0 now. That adds roughly +0.6 to +1.0 mm of T unless a thinner ring works. Pocket depth = ring + 0.15.
- Hold force falls steeply with distance and depends on the other side (phone MagSafe array, case, steel grade and
  thickness, coating). Measure with shims of 0.3-2.0 mm on the real phone and a painted strut.

### Whole-body CNC
- Two setups (front features first, then hollow from the back). 1.0 mm front floor over about 60 x 90 mm needs shop
  fixturing; 1.2 mm is acceptable (front plate thickness does not enter the back gap). Inside corners R >= about 1.0.
- Aluminium front and walls enclose the antenna: plan a plastic window or edge cut-out and a range test. Plastic back plate likely.

## Open items / to measure
0. Caliper a real XIAO: PCB thickness, USB-C top above the underside, overhang. Check the opening centre in Fusion (1.605 vs STEP).
1. Print a coupon (one standoff, one back-plate stop) to measure the real h and D correlation.
2. Measure board warp on the first boards (feeler gauge on a flat plate).
3. Confirm the USB-C centerline offset (1.67 mm) on the part.
4. JLC 0.8 / 1.0 / 1.2 mm 4-layer or 2-layer price: run the instant quote.
5. Raytac module and other tall-part heights, display retention scheme, front pocket for the JST, battery connector choice.
