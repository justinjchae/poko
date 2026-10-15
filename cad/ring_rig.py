"""Ring test rig (2026-10-13): the flush-disc / flange / printed-tongue ring stack (ring_stack.py) on the AS5600 rig base. Builds RIG2_* components in
the ACTIVE Fusion design (run it in a new, empty design). Same datum as enclosure_v2_inset.py: Z=0 is datum A (back face of the cover), +Z toward
the user, ring axis at the origin. All mm. Rig base/spacers/rails/board holder are the as5600_knob_rig.py ones.

Difference from the product stack: the rig cover is PLA 2.5 thick (stiff, no aluminium), so the printed disc is 3.05 thick (face flush at +2.5) and has an
integral 45 deg flare behind the cover (front section R13.65 flaring to R14.4 at the underside, no shelf: prints face down with no support; the flare touches the plain cover hole's back edge = the retention). Rig only: a Ø2 hole from the front face down to the magnet pocket to poke the magnet out.
The plate is registered to the cover by two pins on the cover (round hole at 0 deg, slot toward it at 120 deg; the third screw boss only clamps), so the hub sits at the same place
on every rebuild. Hole sizes are nominal: printed holes usually come out small, so check the fit and change peg_clr. The disc stands R['ext'] above the cover face with a 45 deg front chamfer and vertical knurl grooves on the edge (thumb grip; prints face down with no support).
Everything below A is as in ring_stack.py (plate -2.26..-1.11, magnet bottom -1.855, chip gap set by spacers).

Assembly (cover face down on the bench so the disc face and the cover face are flush on the table):
 1. Magnet (Ø4x2) into the boss pocket (glue, or a snug fit: the front hole lets you poke it out). 2. Grease (or a thin film) on the flare where it touches the cover hole edge, tape ring on the plate rib, a tape dot on each pad. 3. Disc into the cover hole from the back (face on the bench).
 4. The plate bore is Ø6.4 on purpose (loose: the flare centres the disc); just deburr it, no reaming. 5. Plate onto the cover pins (round hole on the 0 deg pin, slot on the 120 deg pin), then onto the bosses, 3x M3x4 (button/pan head, self-tapping) from below.
 6. Cover + base with 4x M3x8 countersunk into the base posts (breakout headers pointing down). 7. Choose the spacer stack for the magnet-to-chip gap (table below).
Print (PLA/PETG; PETG or nylon for the plates): cover face down; disc face down (boss up; the flare is a continuous 45 deg slope, no support needed);
plate bottom down (tongues are the first layers on the bed, the rest is cut away from the top, pads are pillars: no overhangs; three variants tongue_t 0.32 / 0.44 / 0.56
= softest / soft / default (PLA is about 1.75x stiffer than the PETG the notes assume)); base flat; rails on edge (pegs up); spacers flat.
Hardware: 3x M3x4 (button/pan head), 4x M3x8 csk, Ø4x2 diametric magnet, thin low-friction tape or grease (see the summary), AS5600 breakout with headers DOWN.
"""
import adsk.core, adsk.fusion, math

AS5600_ID = 'urn:adsk.wipprod:dm.lineage:td3I6-p2Qy2UHJECxqpHuQ'   # AS5600 Magnetic Encoder (Device project)

R = dict(
    sq=60.0, post_xy=25.0, post_d=8.0, pilot_d=2.9, pilot_depth=7.0, csk_hole=3.4, csk_d=6.4,
    cover_t=2.48, hole_r=13.8,                       # printed at 0.12 mm layers, first layer 0.2: heights = 0.2 + 0.12 n
    disc_r=13.65, disc_top=4.84, disc_bot=-0.60, flange_r=14.4, flange_z=(-0.60, -0.12), flange_tape_r=(13.9, 14.4), pen_hole_d=2.0, boss_r=3.0, mag_d=4.0, mag_t=2.0, pocket_clr=-0.025, glue_top=0.12, mag_bot=-1.92,
    tape_t=0.12,                     # tape / shim thickness (PTFE film 0.13; stack the substitute to about this; the disc is dimensioned for 0.12)
    bore_r=3.20, hub_r=4.6, plate_r=16.0,   # loose journal (0.2 radial): the 45 deg flare centres the disc on the cover hole, the bore must not fight it
    plate_h=1.16, hub_h=1.52, rib_h=1.40, pad_top_h=1.64,   # plate heights above its bottom (on the bed), each 0.2 + 0.12 n; the rib is left ~0.17 low: close the gap with tape layers
    foot_r=2.0, foot_rc=10.5, foot_angles=(0.0, 120.0, 240.0), pre_sq=0.07,
    tongue_w=4.0, slit=0.6, root_r=5.6, tongue_t=0.56, tongue_variants=(0.32, 0.44), E=2000.0,
    rib_r=(13.4, 14.0),
    post_r=17.8, post_angles=(60.0, 180.0, 300.0), boss_rr=3.0, ear_w=6.4, ear_r=3.2,   # equally spaced, midway between the tongues
    peg_angles=(0.0, 120.0), peg_r=1.5, peg_clr=0.05, peg_in=0.8, slot_extra=0.5,   # locating pins on the cover: round hole at the first, slot (toward the first) at the second
    ext=2.36, chamfer=0.6, knurl_n=48, knurl_r=0.5, knurl_off=0.1, knurl_z0=0.3,   # disc stands ext above the cover face (disc_top = cover_t + ext; 2.36 = 0.2 + 18 x 0.12); 45 deg front chamfer; vertical round knurl grooves (r, centre knurl_off outside the edge) from knurl_z0 above the cover face to the top
    screw_hole=1.7, pilot_r=1.25, pilot_top=2.04,         # M3x4 button/pan head, self-tapping into the printed boss; head sits under the plate. Screw tip lands at about 1.73, so 1.8 bottomed out (0.07) and bulged the front; 2.04 leaves 0.3 of tip room and a 0.44 front skin (cover is printed face down: 0.2 + 2 x 0.12)
    base_top=-7.205, base_t=3.0, foot_h=15.0, rail_w=5.0, peg_d=3.0, peg_h=2.0, peg_y=20.0,
    board=23.0, board_t=1.6, chip_h=1.8, pin_d=3.1, pin_xy=8.0, pin_h=3.8,
    stack_nom=1.0, spacers=[0.2, 0.4, 0.8, 1.6], spacers_in_place=[0.2, 0.8],
    header_slots=[(-8.4, -3.5, -5.4, 4.1), (4.8, -4.4, 7.8, 5.8)],   # x0, y0, x1, y1 around the two header rows (board-centred)
)


def cm(v):
    return v / 10.0


def pt(x, y, z=0.0):
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))


def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    for i in range(root.occurrences.count - 1, -1, -1):
        if root.occurrences.item(i).component.name.startswith(('RIG2_', 'AS5600')):
            root.occurrences.item(i).deleteMe()

    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    VI = adsk.core.ValueInput.createByReal
    report = []

    def new_comp(name):
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = 'RIG2_' + name
        return occ.component

    def sketch_at(comp, z):
        if abs(z) < 1e-9:
            return comp.sketches.add(comp.xYConstructionPlane)
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(comp.xYConstructionPlane, VI(cm(z)))
        cp = comp.constructionPlanes.add(inp)
        cp.isLightBulbOn = False
        return comp.sketches.add(cp)

    def extrude(comp, sk, z0, z1, op, loops=None):
        profs = adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count):
            p = sk.profiles.item(i)
            if loops is None or p.profileLoops.count == loops:
                profs.add(p)
        inp = comp.features.extrudeFeatures.createInput(profs, op)
        inp.setDistanceExtent(False, VI(cm(z1 - z0)))
        if op != NEW:
            inp.participantBodies = [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
        return comp.features.extrudeFeatures.add(inp)

    def circle(sk, c, r):
        sk.sketchCurves.sketchCircles.addByCenterRadius(pt(*c), cm(r))

    def discs(comp, z0, z1, pts, d, op):
        sk = sketch_at(comp, z0)
        for p in pts:
            circle(sk, p, d / 2)
        return extrude(comp, sk, z0, z1, op)

    def annulus(comp, z0, z1, r0, r1, op, c=(0.0, 0.0)):
        sk = sketch_at(comp, z0)
        circle(sk, c, r1)
        circle(sk, c, r0)
        return extrude(comp, sk, z0, z1, op, loops=2)

    def rect(comp, z0, z1, x0, y0, x1, y1, op):
        sk = sketch_at(comp, z0)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(pt(x0, y0), pt(x1, y1))
        return extrude(comp, sk, z0, z1, op)

    def rot_pts(a_deg, x0, x1, y0, y1):
        a = math.radians(a_deg)
        ux, uy, vx, vy = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
        return [(x * ux + y * vx, x * uy + y * vy) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]

    def poly(comp, z0, z1, polys, op):
        sk = sketch_at(comp, z0)
        for pts in polys:
            for i in range(4):
                sk.sketchCurves.sketchLines.addByTwoPoints(pt(*pts[i]), pt(*pts[(i + 1) % 4]))
        return extrude(comp, sk, z0, z1, op)

    def done(comp):
        for b in comp.bRepBodies:
            q = b.boundingBox
            report.append('%-18s %-12s vol %8.1f mm3  X %6.2f..%6.2f  Y %6.2f..%6.2f  Z %6.2f..%6.2f' % (
                comp.name[5:], b.name, b.volume * 1000, q.minPoint.x * 10, q.maxPoint.x * 10, q.minPoint.y * 10,
                q.maxPoint.y * 10, q.minPoint.z * 10, q.maxPoint.z * 10))

    h = R['sq'] / 2
    posts = [(sx * R['post_xy'], sy * R['post_xy']) for sx in (-1, 1) for sy in (-1, 1)]
    zu = R['disc_bot']
    plate_bot = zu - (R['pad_top_h'] + R['tape_t'] - R['pre_sq'])      # pad top + tape dot squeezed pre_sq by the disc underside
    plate_top = plate_bot + R['plate_h']
    hub_top = plate_bot + R['hub_h']
    rib_bare = plate_bot + R['rib_h']
    pad_free = R['pad_top_h'] - R['plate_h']
    rib_gap = zu - (rib_bare + R['tape_t'])                              # to the disc underside with ONE tape layer on the rib
    board_top = R['base_top'] + R['stack_nom'] + R['board_t']
    chip_top = board_top + R['chip_h']
    pcs = [(R['post_r'] * math.cos(math.radians(a)), R['post_r'] * math.sin(math.radians(a))) for a in R['post_angles']]
    pegs = [(R['post_r'] * math.cos(math.radians(a)), R['post_r'] * math.sin(math.radians(a))) for a in R['peg_angles']]

    # ---------------- cover (rig: 2.0 thick, hole, 3 bosses with pilots, 4 corner countersinks) ----------------
    cv = new_comp('Cover')
    rect(cv, 0, R['cover_t'], -h, -h, h, h, NEW)
    cv.bRepBodies.item(0).name = 'Cover'
    discs(cv, 0, R['cover_t'], [(0, 0)], 2 * R['hole_r'], CUT)
    discs(cv, plate_top, 0, pcs, 2 * R['boss_rr'], JOIN)
    discs(cv, plate_top, R['pilot_top'], pcs, 2 * R['pilot_r'], CUT)
    discs(cv, plate_top - R['peg_in'], 0, pegs, 2 * R['peg_r'], JOIN)                                     # locating pins (round + slot) for the plate
    sk = sketch_at(cv, R['cover_t'])
    pts = adsk.core.ObjectCollection.create()
    for p in posts:
        pts.add(sk.sketchPoints.add(pt(*p)))
    hi = cv.features.holeFeatures.createCountersinkInput(VI(cm(R['csk_hole'])), VI(cm(R['csk_d'])), VI(math.radians(90)))
    hi.setPositionBySketchPoints(pts)
    hi.setDistanceExtent(VI(cm(R['cover_t'])))
    cv.features.holeFeatures.add(hi)
    done(cv)

    # ---------------- disc: plain cylinder, boss, magnet pocket from the boss tip ----------------
    dc = new_comp('Disc')
    # body of revolution: front section R disc_r, then ONE 45 deg flare to the flange radius behind the cover (no shelf, prints face down without support).
    # The flare passes through (R hole_r, Z 0): it touches the cover hole's back edge there (line contact = the axial retention), plain cover hole.
    zf = R['hole_r'] - R['disc_r']                                    # flare starts here (45 deg: radius grows 1 per 1 of Z)
    r_fl = R['hole_r'] + (0.0 - R['disc_bot'])                        # flare radius at the underside
    sk = dc.sketches.add(dc.xZConstructionPlane)
    sp = lambda r, z: sk.modelToSketchSpace(adsk.core.Point3D.create(cm(r), 0, cm(z)))
    prof = [(0, R['disc_top']), (R['disc_r'] - R['chamfer'], R['disc_top']), (R['disc_r'], R['disc_top'] - R['chamfer']), (R['disc_r'], zf), (r_fl, R['disc_bot']), (0, R['disc_bot'])]
    for i in range(len(prof)):
        a_, b_ = prof[i], prof[(i + 1) % len(prof)]
        sk.sketchCurves.sketchLines.addByTwoPoints(sp(*a_), sp(*b_))
    ri = dc.features.revolveFeatures.createInput(sk.profiles.item(0), dc.zConstructionAxis, NEW)
    ri.setAngleExtent(False, adsk.core.ValueInput.createByString('360 deg'))
    dc.features.revolveFeatures.add(ri).bodies.item(0).name = 'Disc'
    discs(dc, R['mag_bot'], R['flange_z'][0], [(0, 0)], 2 * R['boss_r'], JOIN)
    discs(dc, R['mag_bot'], R['glue_top'], [(0, 0)], R['mag_d'] + 2 * R['pocket_clr'], CUT)
    discs(dc, R['glue_top'], R['disc_top'], [(0, 0)], R['pen_hole_d'], CUT)                         # rig only: poke the magnet out from the front
    # knurl: vertical round grooves around the edge of the part that stands above the cover (not in the hole, the sliding section stays smooth); they also notch the chamfer
    kc = [((R['disc_r'] + R['knurl_off']) * math.cos(2 * math.pi * k / R['knurl_n']), (R['disc_r'] + R['knurl_off']) * math.sin(2 * math.pi * k / R['knurl_n']))
          for k in range(R['knurl_n'])]
    discs(dc, R['cover_t'] + R['knurl_z0'], R['disc_top'] + 0.1, kc, 2 * R['knurl_r'], CUT)
    report.append('disc stands %.2f above the cover face, chamfer %.2f, %d knurl grooves r %.2f (depth %.2f)' % (
        R['ext'], R['chamfer'], R['knurl_n'], R['knurl_r'], R['knurl_r'] - R['knurl_off']))
    done(dc)
    mg = new_comp('Magnet')
    discs(mg, R['mag_bot'], R['mag_bot'] + R['mag_t'], [(0, 0)], R['mag_d'], NEW)
    mg.bRepBodies.item(0).name = 'Magnet4x2'
    done(mg)

    # ---------------- keeper + tapes ----------------
    tp = new_comp('Tape')
    annulus(tp, rib_bare, rib_bare + R['tape_t'], R['rib_r'][0], R['rib_r'][1], NEW).bodies.item(0).name = 'RibTape'
    for i, a in enumerate(R['foot_angles']):
        c = (R['foot_rc'] * math.cos(math.radians(a)), R['foot_rc'] * math.sin(math.radians(a)))
        z0 = plate_top + pad_free
        sk = sketch_at(tp, z0)
        circle(sk, c, R['foot_r'])
        extrude(tp, sk, z0, z0 + R['tape_t'], NEW).bodies.item(0).name = 'DotTape%d' % (i + 1)
    done(tp)

    # ---------------- plate (printed, three tongue thicknesses) ----------------
    def build_plate(comp, tt):
        discs(comp, plate_bot, plate_top, [(0, 0)], 2 * R['plate_r'], NEW)
        comp.bRepBodies.item(0).name = 'Plate_t%.2f' % tt
        discs(comp, plate_top, hub_top, [(0, 0)], 2 * R['hub_r'], JOIN)
        annulus(comp, plate_top, rib_bare, R['rib_r'][0], R['rib_r'][1], JOIN)
        for a in tuple(R['post_angles']) + tuple(R['peg_angles']):
            ux, uy, vx, vy = math.cos(math.radians(a)), math.sin(math.radians(a)), -math.sin(math.radians(a)), math.cos(math.radians(a))
            sk = sketch_at(comp, plate_bot)
            q = rot_pts(a, 14.0, R['post_r'], -R['ear_w'] / 2, R['ear_w'] / 2)
            for i in range(4):
                sk.sketchCurves.sketchLines.addByTwoPoints(pt(*q[i]), pt(*q[(i + 1) % 4]))
            circle(sk, (R['post_r'] * ux, R['post_r'] * uy), R['ear_r'])
            extrude(comp, sk, plate_bot, plate_top, JOIN)
        hw, sl = R['tongue_w'] / 2, R['slit']
        x_end = R['foot_rc'] + R['foot_r']
        for a in R['foot_angles']:
            poly(comp, plate_bot, plate_top, [rot_pts(a, R['root_r'], x_end + sl, hw, hw + sl),
                                                   rot_pts(a, R['root_r'], x_end + sl, -hw - sl, -hw),
                                                   rot_pts(a, x_end, x_end + sl, -hw - sl, hw + sl)], CUT)
            # tongue = the first tt mm on the bed; the plate above it is cut away from the TOP (no bridging), the pad is a pillar from the tongue tip
            poly(comp, plate_bot + tt, plate_top, [rot_pts(a, R['root_r'], x_end, -hw, hw)], CUT)
        for a in R['foot_angles']:
            c = (R['foot_rc'] * math.cos(math.radians(a)), R['foot_rc'] * math.sin(math.radians(a)))
            discs(comp, plate_bot + tt, plate_top + pad_free, [c], 2 * R['foot_r'], JOIN)
        discs(comp, plate_bot, plate_top, pcs, 2 * R['screw_hole'], CUT)
        rh = R['peg_r'] + R['peg_clr']
        discs(comp, plate_bot, plate_top, [pegs[0]], 2 * rh, CUT)                                   # round hole at the first pin
        dx, dy = pegs[0][0] - pegs[1][0], pegs[0][1] - pegs[1][1]                                        # slot at the second pin, long axis toward the first
        dl = math.hypot(dx, dy)
        ux, uy, vx, vy = dx / dl, dy / dl, -dy / dl, dx / dl
        e = R['slot_extra'] / 2
        c1 = pegs[1]
        sk = sketch_at(comp, plate_bot)
        q = [(c1[0] - e * ux + sgn * rh * vx, c1[1] - e * uy + sgn * rh * vy) for sgn in (-1, 1)] + \
            [(c1[0] + e * ux + sgn * rh * vx, c1[1] + e * uy + sgn * rh * vy) for sgn in (1, -1)]
        for i in range(4):
            sk.sketchCurves.sketchLines.addByTwoPoints(pt(*q[i]), pt(*q[(i + 1) % 4]))
        circle(sk, (c1[0] - e * ux, c1[1] - e * uy), rh)
        circle(sk, (c1[0] + e * ux, c1[1] + e * uy), rh)
        extrude(comp, sk, plate_bot, plate_top, CUT)
        discs(comp, plate_bot, hub_top, [(0, 0)], 2 * R['bore_r'], CUT)
        done(comp)

    build_plate(new_comp('Plate'), R['tongue_t'])
    for i, tt in enumerate(R['tongue_variants']):
        pc = new_comp('PrintSet_plate_t%.2f' % tt)
        build_plate(pc, tt)
        tr = adsk.core.Matrix3D.create()
        tr.translation = adsk.core.Vector3D.create(cm(h + 30.0 + i * 46.0), cm(30.0), cm(R['base_top'] - R['base_t'] - plate_bot))
        for o in root.occurrences:
            if o.component == pc:
                o.transform = tr
    report.append('plate (0.12 mm layers, first 0.2): bottom Z %.3f, slab %.2f, hub %.2f, rib %.2f, pad top %.2f above the bed; rib gap to the disc with one tape layer %.2f (add %.0f more %.2f layers for ~0.05)' % (
        plate_bot, R['plate_h'], R['hub_h'], R['rib_h'], R['pad_top_h'], rib_gap, round((rib_gap - 0.05) / R['tape_t']), R['tape_t']))
    L = R['foot_rc'] - R['root_r']
    for tt in [R['tongue_t']] + list(R['tongue_variants']):
        k = 3 * R['E'] * R['tongue_w'] * tt ** 3 / 12.0 / L ** 3
        report.append('tongue t %.2f: k %.2f N/mm each, preload %.2f N, force at the stop %.2f N total (E %.0f MPa estimate)' % (
            tt, k, 3 * k * R['pre_sq'], 3 * k * (R['pre_sq'] + rib_gap), R['E']))

    # ---------------- base: plate, posts, board pins, header slots, rails ----------------
    bs = new_comp('Base')
    bt, bb = R['base_top'], R['base_top'] - R['base_t']
    rect(bs, bt, bb, -h, -h, h, h, NEW)
    bs.bRepBodies.item(0).name = 'Base'
    discs(bs, bt, 0, posts, R['post_d'], JOIN)
    discs(bs, 0, -R['pilot_depth'], posts, R['pilot_d'], CUT)
    peg_xy = [(sx * (h - R['rail_w'] / 2), sy * R['peg_y']) for sx in (-1, 1) for sy in (-1, 1)]
    discs(bs, bb, bb + R['peg_h'] + 0.2, peg_xy, R['peg_d'] + 0.3, CUT)
    discs(bs, bt, bt + R['pin_h'], [(R['pin_xy'], R['pin_xy']), (-R['pin_xy'], -R['pin_xy'])], R['pin_d'], JOIN)
    for x0, y0, x1, y1 in R['header_slots']:
        rect(bs, bt, bb, x0, y0, x1, y1, CUT)
    done(bs)
    for sx in (-1, 1):
        rl = new_comp('Rail_%s' % ('L' if sx < 0 else 'R'))
        rect(rl, bb, bb - R['foot_h'], sx * h, -h, sx * (h - R['rail_w']), h, NEW)
        rl.bRepBodies.item(0).name = 'Rail'
        discs(rl, bb, bb + R['peg_h'], [p_ for p_ in peg_xy if p_[0] * sx > 0], R['peg_d'], JOIN)
        done(rl)

    # ---------------- spacers under the board ----------------
    def spacer(comp, z0, t):
        b = R['board'] / 2
        rect(comp, z0, z0 + t, -b, -b, b, b, NEW)
        hp = [(sx * R['pin_xy'], sy * R['pin_xy']) for sx in (-1, 1) for sy in (-1, 1)]
        discs(comp, z0, z0 + t, hp, 3.5, CUT)
        for x0, y0, x1, y1 in R['header_slots']:
            rect(comp, z0, z0 + t, x0, y0, x1, y1, CUT)

    z_ = bt
    for t in R['spacers_in_place']:
        c_ = new_comp('Spacer_%.1f' % t)
        spacer(c_, z_, t)
        c_.bRepBodies.item(0).name = 'Spacer'
        done(c_)
        z_ += t
    xo = h + 20.0
    for i, t in enumerate(R['spacers']):
        sp = new_comp('PrintSet_spacer_%.1f' % t)
        spacer(sp, bb, t)
        sp.bRepBodies.item(0).name = 'Spacer'
        tr_ = adsk.core.Matrix3D.create()
        tr_.translation = adsk.core.Vector3D.create(cm(xo), cm(-h + 14.0 + i * 27.0), 0)
        for o in root.occurrences:
            if o.component == sp:
                o.transform = tr_

    # ---------------- AS5600 breakout (referenced model), chip up ----------------
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(cm(-R['board'] / 2), cm(-R['board'] / 2), cm(board_top))
    occ = root.occurrences.addByInsert(app.data.findFileById(AS5600_ID), m, True)
    for b in occ.bRepBodies:
        if b.name == 'Magnet_ref':
            b.isLightBulbOn = False

    # ---------------- checks ----------------
    tbm = adsk.fusion.TemporaryBRepManager.get()
    bodies = []
    for o in root.occurrences:
        if o.component.name.startswith('RIG2_PrintSet'):
            continue
        for b in o.bRepBodies:
            if b.isLightBulbOn:
                bodies.append((o.component.name.replace('RIG2_', '') + '/' + b.name, b))
    hits = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            p, q = bodies[i][1].boundingBox, bodies[j][1].boundingBox
            if p.maxPoint.x < q.minPoint.x or q.maxPoint.x < p.minPoint.x or p.maxPoint.y < q.minPoint.y or \
               q.maxPoint.y < p.minPoint.y or p.maxPoint.z < q.minPoint.z or q.maxPoint.z < p.minPoint.z:
                continue
            x_, y_ = tbm.copy(bodies[i][1]), tbm.copy(bodies[j][1])
            tbm.booleanOperation(x_, y_, adsk.fusion.BooleanTypes.IntersectionBooleanType)
            v = x_.volume * 1000 if x_.isValid else 0.0
            if v > 0.005:
                hits.append('%s <> %s  %.3f mm3' % (bodies[i][0], bodies[j][0], v))
    report.append('interference (> 0.005 mm3): %d (expected: 3 tape dots on the disc = pad preload squeeze)' % len(hits))
    report.extend(hits)
    print('\n'.join(report))
    print('nominal stack %.1f: board top %.3f, chip top %.3f, rest gap %.3f (enclosure chip top -2.855, gap 1.000)' % (
        R['stack_nom'], board_top, chip_top, R['mag_bot'] - chip_top))
    print('rest gap by spacer stack: ' + ', '.join('%.1f->%.2f' % (s / 5.0, R['mag_bot'] - (R['base_top'] + s / 5.0 + R['board_t'] + R['chip_h']))
                                                   for s in range(0, 12)))
    print('plate bottom %.2f vs chip top at the smallest gap tried (stack 1.4): %.2f' % (
        plate_bot, R['base_top'] + 1.4 + R['board_t'] + R['chip_h']))
    app.activeViewport.fit()
