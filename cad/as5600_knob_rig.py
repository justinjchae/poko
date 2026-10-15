"""AS5600 knob test rig: is the AS5600 field strength (AGC/MAGNITUDE) a usable 'select' press, and does the on-axis knob fit the
enclosure stack? Builds RIG_* components in the active Fusion design (run it in a new, empty design).

Frame: same datum as enclosure_v2_inset.py. Z = 0 is datum A (back face of the front plate); +Z toward the user. The rig plate is
2.0 thick (front face +2.0) instead of 1.0 for stiffness; nothing below A changes. Knob axis at the origin. All mm.

Stack (nominal, rest):
  plate 0..+2 with a 0.3 thrust rib (R14.8-15.3) on its back face, knob front R14.15 in an R14.4 hole, knob flange R19.5
  -0.3..-1.4 (up-stop: flange top against that rib), underside flat,
  magnet Ø4x2 in a pocket on the axis, bottom face at mag_bot (-1.4), AS5600 board centred under it.
  Board top = base_top + spacer stack + 1.6; chip top = board top + 1.8 (Seeed/generic breakout model). Rest gap = 2.405 - stack.
Press: the knob flange sits on a carrier ring (thin rib) carried by 3 PLA flexure arms, preloaded upward (frame on post ledges,
shims raise it = more preload). The carrier bottom lands on 3 stop pads; washers on the pads set the travel.
RIG_PrintSet_spring is the printed (flat, free) spring, off to the side; RIG_Spring_assembled is a display-only copy in the rest
pose (carrier pushed down by the preload, arms drawn as a stepped S-curve) and is what the interference check uses.

Rev B (2026-10-12, after the first rig turned badly with one finger): the press load now goes through a small-radius thrust ring (RIG_Spider,
ring R5.5-7.5 under the flange, 3 bars glued into notches in the carrier's standoff rib) so the friction torque arm is ~6 mm instead of 17;
the rib itself is cut down 0.15 and only catches a tilt; the finger dimple is replaced by 24 radial pill ridges (0.4 high) on the knob face.
Turning needs finger_radius * mu_skin > thrust_radius * mu_PLA; rev A had 9.5 * ~0.6 vs 17 * ~0.4, which is why one finger could not turn it.
Prints (PLA, no supports): plate face down (back-face rib up), knob flange-down (magnet pocket opens on the bed), spring flat (as modelled), base flat on its bottom, the two rails standing on their edge (pegs up), spacers/washers flat.
Hardware: 4x M3x8 countersunk (plate to posts), magnet Ø4x2 (glue or press), AS5600 breakout with headers pointing DOWN.
"""
import adsk.core, adsk.fusion, math

AS5600_ID = 'urn:adsk.wipprod:dm.lineage:td3I6-p2Qy2UHJECxqpHuQ'   # AS5600 Magnetic Encoder (Device project)

R = dict(
    sq=60.0, post_xy=25.0, post_d=8.0, post_up_d=5.0, pilot_d=2.9, pilot_depth=7.0,
    plate_t=2.0, hole_r=14.4, csk_hole=3.4, csk_d=6.4,
    knob_r=14.15, flange_r=19.5, flange_top=-0.3, flange_bot=-1.4,      # flange underside flat and flush with the magnet
    plate_rib_r=(14.8, 15.3), plate_rib_h=0.3,
    pill_n=24, pill_w=1.25, pill_l=4.0, pill_h=0.4, pill_r=(9.5, 13.5),   # rev B: radial pill ridges on the knob face instead of a dimple
    # rev B thrust spider: ring at small radius carries the press load, 3 bars sit in notches in the carrier's standoff rib;
    # the rib itself is cut down by rib_relief so it only catches the knob when it tilts (hard press on the rim)
    spider_ring_r=(5.5, 7.5), spider_bar_w=4.0, spider_bar_t=0.8, spider_up=2.2, spider_bar_r1=17.6, spider_a0=75.0,
    spider_lift=0.4, foot_l=1.4,                 # spider raised 0.4 above the notch floor (3 glued feet) so it clears the breakout's 1.0 tall capacitors up to a 1.6 stack
    notch_clr=0.4, rib_relief=0.15, spider_print_xy=(-75.0, -62.0),
    mag_d=4.0, mag_t=2.0, mag_bot=-1.4, pocket_clr=0.05,
    board=23.0, board_t=1.6, chip_h=1.8, pin_d=3.1, pin_xy=8.0, pin_h=3.8,
    base_top=-7.205, base_t=3.0, foot_h=15.0, rail_w=5.0, peg_d=3.0, peg_h=2.0, peg_y=20.0,
    stack_nom=1.0, spacers=[0.2, 0.4, 0.8, 1.6], spacers_in_place=[0.2, 0.8],
    # spring: carrier ring + 3 curved arms + frame, printed flat (arms 0.8 thick, frame 2.0)
    car_r=(16.6, 19.5), car_t=0.8, rib_r=(16.8, 17.4), standoff_h=4.0,
    arm_r=(20.0, 22.5), arm_t=0.8, arm_sweep=67.0, stub=6.0, frame_r=23.0, frame_t=2.0,
    preload=1.5,                    # carrier lift in the free state = flexure deflection at rest (mm), before preload shims
    ledge_clr=0.4, shim_od=8.0, shim_id=5.4, shims=[0.4, 0.8],
    pad_d=4.0, pad_r=18.15, travel_open=0.5, washers=[0.2, 0.4],
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
        if root.occurrences.item(i).component.name.startswith(('RIG_', 'AS5600')):
            root.occurrences.item(i).deleteMe()

    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    VI = adsk.core.ValueInput.createByReal
    report = []

    def new_comp(name):
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = 'RIG_' + name
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

    def sector(sk, r0, r1, a0, a1):
        L = sk.sketchCurves.sketchLines.addByTwoPoints
        A = sk.sketchCurves.sketchArcs.addByCenterStartSweep
        p = lambda r, a: pt(r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
        A(pt(0, 0), p(r1, a0), math.radians(a1 - a0))
        A(pt(0, 0), p(r0, a0), math.radians(a1 - a0))
        L(p(r0, a0), p(r1, a0))
        L(p(r0, a1), p(r1, a1))

    def rot_rect(sk, c, a_deg, r0, r1, w):
        """Rectangle w wide along the radial direction a_deg, from radius r0 to r1, about centre c."""
        a = math.radians(a_deg)
        u, v = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
        P = lambda r, t: (c[0] + r * u[0] + t * v[0], c[1] + r * u[1] + t * v[1])
        q = [P(r0, -w / 2), P(r1, -w / 2), P(r1, w / 2), P(r0, w / 2)]
        for i in range(4):
            sk.sketchCurves.sketchLines.addByTwoPoints(pt(*q[i]), pt(*q[(i + 1) % 4]))

    def done(comp):
        for b in comp.bRepBodies:
            q = b.boundingBox
            report.append('%-14s %-12s vol %8.1f mm3  X %6.2f..%6.2f  Y %6.2f..%6.2f  Z %6.2f..%6.2f' % (
                comp.name[4:], b.name, b.volume * 1000, q.minPoint.x * 10, q.maxPoint.x * 10, q.minPoint.y * 10,
                q.maxPoint.y * 10, q.minPoint.z * 10, q.maxPoint.z * 10))

    h = R['sq'] / 2
    posts = [(sx * R['post_xy'], sy * R['post_xy']) for sx in (-1, 1) for sy in (-1, 1)]
    z_car_rest = R['flange_bot'] - R['standoff_h']                  # carrier bottom at rest (knob up on the plate)
    z_ledge = z_car_rest + R['preload']                             # frame bottom = carrier bottom in the free state
    z_pad = z_car_rest - R['travel_open']
    board_top = R['base_top'] + R['stack_nom'] + R['board_t']
    chip_top = board_top + R['chip_h']

    # ---------------- plate ----------------
    pl = new_comp('Plate')
    rect(pl, 0, R['plate_t'], -h, -h, h, h, NEW)
    pl.bRepBodies.item(0).name = 'Plate'
    discs(pl, R['plate_t'], 0, [(0, 0)], 2 * R['hole_r'], CUT)
    annulus(pl, 0, -R['plate_rib_h'], R['plate_rib_r'][0], R['plate_rib_r'][1], JOIN)
    sk = sketch_at(pl, R['plate_t'])
    pts = adsk.core.ObjectCollection.create()
    for p in posts:
        pts.add(sk.sketchPoints.add(pt(*p)))
    hi = pl.features.holeFeatures.createCountersinkInput(VI(cm(R['csk_hole'])), VI(cm(R['csk_d'])), VI(math.radians(90)))
    hi.setPositionBySketchPoints(pts)
    hi.setDistanceExtent(VI(cm(R['plate_t'])))
    pl.features.holeFeatures.add(hi)
    done(pl)

    # ---------------- knob (magnet pocket from below, on the axis) ----------------
    kn = new_comp('Knob')
    discs(kn, R['plate_t'], R['flange_top'], [(0, 0)], 2 * R['knob_r'], NEW).bodies.item(0).name = 'Knob'
    discs(kn, R['flange_top'], R['flange_bot'], [(0, 0)], 2 * R['flange_r'], JOIN)
    discs(kn, R['mag_bot'], R['mag_bot'] + R['mag_t'], [(0, 0)], R['mag_d'] + 2 * R['pocket_clr'], CUT)
    # radial pill ridges on the front face: a fingertip pushes against their edges instead of relying on friction
    sk = sketch_at(kn, R['plate_t'])
    rc = (R['pill_r'][0] + R['pill_r'][1]) / 2
    hl = (R['pill_l'] - R['pill_w']) / 2                      # half length of the straight part
    for k in range(R['pill_n']):
        a = 2 * math.pi * k / R['pill_n']
        u, v = (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))
        P = lambda s, t: (rc * u[0] + s * u[0] + t * v[0], rc * u[1] + s * u[1] + t * v[1])
        c4 = [P(-hl, -R['pill_w'] / 2), P(hl, -R['pill_w'] / 2), P(hl, R['pill_w'] / 2), P(-hl, R['pill_w'] / 2)]
        for i in range(4):
            sk.sketchCurves.sketchLines.addByTwoPoints(pt(*c4[i]), pt(*c4[(i + 1) % 4]))
        circle(sk, P(-hl, 0), R['pill_w'] / 2)
        circle(sk, P(hl, 0), R['pill_w'] / 2)
    extrude(kn, sk, R['plate_t'], R['plate_t'] + R['pill_h'], JOIN)
    discs(kn, R['mag_bot'] + R['mag_t'], R['mag_bot'], [(0, 0)], R['mag_d'], NEW).bodies.item(0).name = 'Magnet4x2'
    done(kn)

    # ---------------- spring: carrier ring + 3 curved flexure arms + frame ----------------
    # Spring_print = the printed (flat, free) shape, off to the side. Spring_assembled = display-only copy in the rest pose:
    # frame on the ledges, carrier + rib pushed down by the preload, arms drawn as a stepped S-curve (guided beam).
    def build_spring(comp, zf, drop, n_seg):
        zc = zf - drop                                                                    # carrier plane
        annulus(comp, zc, zc + R['car_t'], R['car_r'][0], R['car_r'][1], NEW).bodies.item(0).name = 'Spring'
        for k in range(3):
            a0 = 90.0 + 120.0 * k
            a1 = a0 + R['arm_sweep']
            sk_ = sketch_at(comp, zc)
            sector(sk_, R['car_r'][1] - 0.5, R['arm_r'][0] + 0.5, a0, a0 + R['stub'])     # stub to the carrier
            extrude(comp, sk_, zc, zc + R['arm_t'], JOIN)
            for i in range(n_seg):                                                        # arm, carrier end (s=0) to frame end (s=1)
                s = (i + 0.5) / n_seg
                z_ = zf - drop * (1.0 - (3 * s * s - 2 * s * s * s))
                sk_ = sketch_at(comp, z_)
                sector(sk_, R['arm_r'][0], R['arm_r'][1], a0 + (a1 - a0) * i / n_seg, a0 + (a1 - a0) * (i + 1) / n_seg + 0.01)
                extrude(comp, sk_, z_, z_ + R['arm_t'], JOIN)
            sk_ = sketch_at(comp, zf)
            sector(sk_, R['arm_r'][1] - 0.5, R['frame_r'] + 0.5, a1 - R['stub'], a1)      # stub to the frame
            extrude(comp, sk_, zf, zf + R['arm_t'], JOIN)
        sk_ = sketch_at(comp, zf)
        sk_.sketchCurves.sketchLines.addTwoPointRectangle(pt(-h, -h), pt(h, h))
        circle(sk_, (0, 0), R['frame_r'])
        extrude(comp, sk_, zf, zf + R['frame_t'], JOIN, loops=2)
        discs(comp, zf, zf + R['frame_t'], posts, R['post_up_d'] + 0.4, CUT)
        rib_top = zc + R['standoff_h'] - R['rib_relief']
        annulus(comp, zc + R['car_t'], rib_top, R['rib_r'][0], R['rib_r'][1], JOIN)   # standoff rib: tilt stop only, clear of the flange at rest
        for k in range(3):                                                             # notches for the spider bars
            sk_ = sketch_at(comp, zc + R['spider_up'])
            rot_rect(sk_, (0.0, 0.0), R['spider_a0'] + 120.0 * k, R['rib_r'][0] - 0.5, R['rib_r'][1] + 0.5,
                     R['spider_bar_w'] + R['notch_clr'])
            extrude(comp, sk_, zc + R['spider_up'], rib_top, CUT)
        done(comp)

    build_spring(new_comp('Spring_assembled'), z_ledge, R['preload'], 1 if R['preload'] == 0 else 12)
    sp_print = new_comp('PrintSet_spring')
    build_spring(sp_print, z_ledge, 0.0, 1)
    tr = adsk.core.Matrix3D.create()
    tr.translation = adsk.core.Vector3D.create(cm(-(R['sq'] + 15.0)), 0, cm(-z_ledge + (R['base_top'] - R['base_t'])))
    for o in root.occurrences:
        if o.component == sp_print:
            o.transform = tr
    if design.snapshots.hasPendingSnapshot:
        design.snapshots.add()

    # ---------------- thrust spider: ring at small radius under the flange + 3 bars into the rib notches (glued) ----------------
    def build_spider(comp, zb, c):
        ring_h = R['flange_bot'] - (z_car_rest + R['spider_up'] + R['spider_lift'])   # ring top lands on the flange underside
        annulus(comp, zb, zb + ring_h, R['spider_ring_r'][0], R['spider_ring_r'][1], NEW, c=c).bodies.item(0).name = 'Spider'
        for k in range(3):
            sk_ = sketch_at(comp, zb)
            rot_rect(sk_, c, R['spider_a0'] + 120.0 * k, R['spider_ring_r'][0] + 1.0, R['spider_bar_r1'], R['spider_bar_w'])
            extrude(comp, sk_, zb, zb + R['spider_bar_t'], JOIN)
        done(comp)

    sp_asm = new_comp('Spider')
    build_spider(sp_asm, z_car_rest + R['spider_up'] + R['spider_lift'], (0.0, 0.0))
    for k in range(3):                                                               # feet: bar end down to the notch floor (glued)
        sk_ = sketch_at(sp_asm, z_car_rest + R['spider_up'])
        rot_rect(sk_, (0.0, 0.0), R['spider_a0'] + 120.0 * k, R['spider_bar_r1'] - R['foot_l'], R['spider_bar_r1'], R['spider_bar_w'])
        extrude(sp_asm, sk_, z_car_rest + R['spider_up'], z_car_rest + R['spider_up'] + R['spider_lift'], JOIN)
    build_spider(new_comp('PrintSet_spider'), R['base_top'] - R['base_t'], R['spider_print_xy'])
    feet = new_comp('PrintSet_feet')                                                 # 3 loose feet, flat
    for k in range(3):
        rect(feet, R['base_top'] - R['base_t'], R['base_top'] - R['base_t'] + R['spider_lift'], -60.0 + k * 6.0, -60.0,
             -60.0 + k * 6.0 + R['spider_bar_w'], -60.0 + R['foot_l'], NEW)

    # ---------------- base: plate, posts with ledges, feet, board pins, header slots, stop pads ----------------
    bs = new_comp('Base')
    bt, bb = R['base_top'], R['base_top'] - R['base_t']
    rect(bs, bt, bb, -h, -h, h, h, NEW)
    bs.bRepBodies.item(0).name = 'Base'
    discs(bs, bt, z_ledge, posts, R['post_d'], JOIN)
    discs(bs, z_ledge, 0, posts, R['post_up_d'], JOIN)
    discs(bs, 0, -R['pilot_depth'], posts, R['pilot_d'], CUT)
    peg_xy = [(sx * (h - R['rail_w'] / 2), sy * R['peg_y']) for sx in (-1, 1) for sy in (-1, 1)]
    discs(bs, bb, bb + R['peg_h'] + 0.2, peg_xy, R['peg_d'] + 0.3, CUT)                     # peg holes for the separate rails
    discs(bs, bt, bt + R['pin_h'], [(R['pin_xy'], R['pin_xy']), (-R['pin_xy'], -R['pin_xy'])], R['pin_d'], JOIN)
    for x0, y0, x1, y1 in R['header_slots']:
        rect(bs, bt, bb, x0, y0, x1, y1, CUT)
    pads = [(R['pad_r'] * math.cos(math.radians(a)), R['pad_r'] * math.sin(math.radians(a))) for a in (30.0, 150.0, 270.0)]
    discs(bs, bt, z_pad, pads, R['pad_d'], JOIN)
    done(bs)
    for sx in (-1, 1):                                       # two separate side rails (wires exit front/back), pegs into the base
        rl = new_comp('Rail_%s' % ('L' if sx < 0 else 'R'))
        rect(rl, bb, bb - R['foot_h'], sx * h, -h, sx * (h - R['rail_w']), h, NEW)
        rl.bRepBodies.item(0).name = 'Rail'
        discs(rl, bb, bb + R['peg_h'], [p_ for p_ in peg_xy if p_[0] * sx > 0], R['peg_d'], JOIN)
        done(rl)

    # ---------------- spacers (under the board), preload shims (on the ledges), travel washers (on the pads) ----------------
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
    loose = new_comp('PrintSet_loose')                       # off to the side, all flat on z = bb
    xo = h + 20.0
    for i, t in enumerate(R['spacers']):                      # spare spacers: own component each so the header slots / pin holes cut only them
        sp = new_comp('PrintSet_spacer_%.1f' % t)
        spacer(sp, bb, t)
        sp.bRepBodies.item(0).name = 'Spacer'
        tr_ = adsk.core.Matrix3D.create()
        tr_.translation = adsk.core.Vector3D.create(cm(xo), cm(-h + 14.0 + i * 27.0), 0)
        for o in root.occurrences:
            if o.component == sp:
                o.transform = tr_
    for i, t in enumerate(R['shims']):
        for j in range(4):
            c0 = (xo + 22.0 + j * 10.0, -h + 6.0 + i * 12.0)
            annulus(loose, bb, bb + t, R['shim_id'] / 2, R['shim_od'] / 2, NEW, c=c0)
    for i, t in enumerate(R['washers']):
        for j in range(3):
            discs(loose, bb, bb + t, [(xo + 22.0 + j * 10.0, -h + 34.0 + i * 10.0)], R['pad_d'], NEW)
    report.append('PrintSet_loose: spacers %s, preload shims %s (x4 each), travel washers %s (x3 each)' % (
        R['spacers'], R['shims'], R['washers']))

    # ---------------- AS5600 breakout (referenced model), centred, chip up ----------------
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
        if o.component.name.startswith('RIG_PrintSet'):
            continue
        for b in o.bRepBodies:
            if b.isLightBulbOn:
                bodies.append((o.component.name.replace('RIG_', '') + '/' + b.name, b))
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
    report.append('interference (> 0.005 mm3): %d (assembled pose; the printed spring is off to the side)' % len(hits))
    report.extend(hits)
    print('\n'.join(report))
    print('z: plate 0..%.1f, knob flange bottom %.2f, magnet %.2f..%.2f, carrier rest bottom %.2f, ledge %.2f (preload %.1f), '
          'pads %.2f (travel %.1f open), base top %.3f' % (R['plate_t'], R['flange_bot'], R['mag_bot'], R['mag_bot'] + R['mag_t'],
                                                         z_car_rest, z_ledge, R['preload'], z_pad, R['travel_open'], bt))
    print('nominal stack %.1f: board top %.3f, chip top %.3f, rest gap %.3f (enclosure chip top -2.855)' % (
        R['stack_nom'], board_top, chip_top, R['mag_bot'] - chip_top))
    print('rest gap by spacer stack: ' + ', '.join('%.1f->%.2f' % (s / 5.0, R['mag_bot'] - (R['base_top'] + s / 5.0 + R['board_t'] + R['chip_h']))
                                                   for s in range(0, 12)))
    app.activeViewport.fit()
