# Ring design notes (2026-10-09)

Decisions from the ring discussion. Nothing here is modeled or tested yet.

## Layout (decided)
- Option 2: the ring sits in the chin below the round display, and a separate select button sits in the center of the ring.
- The ring only rotates. The button is a separate part, so the ring needs no axial travel or spring return.
- Option 1 (ring around the display, button in the chin) stays as the fallback if the chin layout fails.

## Sensing (decided: relative only)
- The EC11 was incremental (quadrature), so nothing in the firmware needs absolute ring angle.
- AS5600 reads a magnet on a small drive roller or pulley, off the ring's axis. The ring is larger than the roller, so the magnet turns faster than the ring (inherent speed-up).
- Pick the ratio for belt/roller grip and packaging, not resolution. Suggested 3:1 to 5:1. Small pulleys grip less, so keep the small one as large as fits.
- Firmware:
  - Unwrap the angle at 360. Each poll must see less than 180 deg of sensor rotation, so max ring speed is about 180 deg / (ratio x poll period). Example: 4:1 at 200 Hz tracks about 6 ring rev/s.
  - Set the AS5600 to the fast filter.
  - Add a small dead-band or hysteresis against rest jitter.
  - Detents are virtual: the LRA ticks off a running accumulator. Slip does not matter for that.
- Slip only loses counts on hard flicks. Magnet misalignment nonlinearity shrinks with the ratio.

## Drive (leading idea)
- Friction drive: an O-ring or round belt over grooved pulleys, or a rubber-tired roller pressed against the ring's edge with a light spring.
- Belt tension puts a constant radial load on the pulley bearings, so keep the stretch low (about 5 to 10 percent) and use a V-groove for grip at low tension.
- Standard O-rings take compression set. For the 100-unit run consider spliced or welded urethane round belt, or EPDM/FKM O-rings.
- Direct friction roller on the ring edge is the simpler alternative (no belt, no second pulley).

## Ring support (open: prototype first)
1. Printed or POM sliding race (bushing). Cheapest, fastest to try. Use POM or PTFE against a smooth surface, 0.1 to 0.2 mm radial clearance, a lip for axial retention, light grease. Expect some stick-slip.
2. Thin-section bearing, e.g. 20x27x4 (67xx series). The ring bonds or presses onto the outer race and the 20 mm hole clears the button. Best feel, costs more. Prices and MOQ NOT verified.
3. Three rollers at 120 deg on the ring's outer edge, one of them the sprung drive roller. Forgiving of tolerances, more parts.
- Plan: test option 1 on the next print. If the slow-spin feel is bad even with lube, step up to option 2.

## Select button
- Firm tact switch, roughly 160 to 250 gf with short travel, to avoid accidental presses while spinning the ring.
- Firmware: ignore ring motion for a short window after a press starts, since pressing the center nudges the ring.
- Reuse the LRA click on press.

## Alternative noted, not chosen
- Capacitive touch ring (Apple Siri Remote style): no moving parts and no backlash, but no real motion or resistance. Worth comparing only if the mechanical ring fails. Touch IC choice not researched.

## Open items
- Ring OD (current V1B thumb wheel is 33 mm), roller size, final ratio.
- Whether the friction drive is a belt or a direct roller.
- Where the AS5600 PCB sits relative to the ring (off-axis, thin stack).
- Relates to the open "ring sensing" and "select button" items in the hardware lock tracker.

