# Haptics

Status 2026-10-08: 10 test motors ordered on Alibaba (Xinhailong L090835, $1.50 each, $31.06 all-in incl. import charges and tax, paid 14:04, payment processing at time of writing, delivery estimate Oct 19 - Nov 09). The order remarks carry the full part number L090835H-008678999-8160. Supplier questions message not yet sent. Nothing locked.

## Motor under test

Xinhailong L090835H-008678999-8160 (spec LL-3-J-30510 rev A.1, 2024-07-18; the spec says "Lnlon's part").

- X-axis LRA, 9 x 8 x 3.5 mm, 170 +/-10 Hz, 8 +/-1 ohm, 145 mA max.
- Rated 0.9 V RMS AC sine (the listing says 1.5 V; use the datasheet value for the DRV2605L rated-voltage register).
- Vibration 0.7 +/-0.15 G RMS on a 100 g fixture (page 4); the outline drawing says 0.82 G. Unresolved.
- Noise 50 dB(A) max at 10 cm. Rise and fall 50 ms max. Life 1M cycles.
- Contacts: flat FPC tail, two gold pads, hand-soldered to board pads. Tail 3.9 mm wide, sticks out 2.75 mm. Read exact pad sizes off page 7 at full zoom.
- Keep away from strong magnets (page 11, no limit given). Use within 6 months of manufacture (lot code format ML1 + YYMMDD).
- Side force limit 20 N / 10 N: bond it, do not clamp it.

## Open questions for the supplier

Vibration 0.7 vs 0.82 G; safe magnet field or distance; who makes it (Xinhailong or Lnlon); lot date; X axis direction and which face the tail pads are on; optional 12 x 6 x 2.8 mm 220 Hz sample.

## Quiet mounting requirements (phone-like buzz, no desk rattle)

1. Stiff adhesive mount (VHB or equivalent) to a rigid part. No loose fit in the pocket.
2. Nothing else loose in the stack: battery, ring, gear, display flex. Secure or foam-pad them.
3. Soft feet (rubber or silicone) so the case does not drum on the desk.
4. Short shaped pulses (20-40 ms) with DRV2605L active braking; avoid long buzzes.
5. Drive at resonance (auto-calibration), amplitude only as high as the feel needs.
6. Check the enclosure for a resonance near 170 Hz.

## Bench checks when the samples arrive

1. Inspect: marking, lot date, tail pads, which face the pads are on, X axis direction. Compare to page 7.
2. Drive with the DRV2605L (LRA mode, rated voltage from the datasheet), run auto-calibration, check the measured resonance.
3. Feel and noise: mount in the V1B enclosure the intended way, test on a desk against Justin's hobby ERM. Log IMU acceleration for each motor in the same pocket.
4. Magnet test: hold a MagSafe puck against the case and near the AS5600 magnet position; compare vibration before and after.
5. Rattle test: the ring and wheel are the likely noisemakers.

Fallbacks: 12 x 6 x 2.8 mm 220 Hz X-axis model, or the hobby ERM (DRV2605L drives either; board uses a generic 2-pad footprint).
