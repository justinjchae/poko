"""Ring stack (2026-10-13, supersedes ring_stack_v1/v2): flush plain disc, printed keeper ring, printed tongue springs, hub bore in the printed plate.

Builds in the ACTIVE Fusion design (run it in a new design). Frame = enclosure_v2_inset.py: Z=0 is datum A (back face of the front plate),
+Z toward the user, ring axis at the origin (real axis (0, -38.25); AS5600 on the carrier board in the free chin area). All mm.

Custom machined parts: cover (plain through hole R13.8, nothing else new) and the disc (plain cylinder R13.65 + central boss + magnet pocket,
front face flush with the cover at +1.0, 0.15 radial reveal). Everything else is printed or commodity:
  Keeper       printed ring R13.65..14.8, glued on the disc OD behind the cover (it is the retention: foam pushes it against A);
               PTFE tape ring on its front face (rubs the cover back, r ~14, low drag)
  Plate        printed (PLA/PETG), 1.15 thick + hub R4.6 with the journal bore R3.05 reamed to size (no bushing part; optional sleeve later);
               ears at R17.8 take 3x M1.6x2.5 from below into bosses on the cover (angles as enclosure_v2_inset rp_angles; screw heads modelled as
               counterbore, use csk/pan to suit); pilot Ø1.4 into the cover boss, 0.5 mm skin left on the front
  Tongue x3    printed cantilever spring cut into the plate (U slit, thinned from below to tongue_t), pad Ø4 on its tip printed 0.5 high (FREE shape),
               PTFE film tape dot 0.13 on the pad; the disc squeezes it 0.07 at rest (= the preload, shows as an expected overlap), tune k with
               tongue_t / root_r / tongue_w and reprint, trim height with tape layers. Replaces the foam dots (no purchased spring)
  Rib          printed rib R13.4..14.0 with a PTFE tape ring; 0.05 under the keeper = press travel / hard stop
Press = disc pushes the tongues 0.05 mm and lands on the taped rib; detection by AS5600 AGC/MAGNITUDE (magnet to chip gap shrinks 0.05 from 1.000).
"""
import adsk.core, adsk.fusion, math

K = dict(
    front_t=1.0, hole_r=13.8, front_od=22.0,
    disc_r=13.65, disc_top=1.0, disc_bot=-0.55,
    boss_r=3.0, mag_d=4.0, mag_t=2.0, pocket_clr=0.05, glue_top=0.2, mag_bot=-1.855,
    keeper_r=(13.65, 14.8), keeper_z=(-0.55, -0.13), tape_t=0.13, keeper_tape_r=(13.9, 14.8),
    bore_r=3.05, hub_r=4.6, hub_top=-0.70, plate_bot=-2.26, plate_r=16.0,
    foot_r=2.0, foot_rc=10.5, foot_angles=(0.0, 120.0, 240.0),
    pad_free=0.5, pre_sq=0.07,                       # printed pad height above the plate (free), squeeze at rest = tongue preload deflection
    tongue_w=4.0, slit=0.6, root_r=5.6, tongue_t=0.6, E=2000.0,   # printed cantilever tongue: width, slit width, root radius, thickness (bottom relief), modulus MPa
    rib_r=(13.4, 14.0), rib_gap=0.05,
    post_r=17.8, post_angles=(45.0, 135.0, 250.0), boss_rr=1.8, ear_w=4.6, ear_r=2.3,
    screw_hole=0.9, screw_head_r=1.5, screw_head_h=0.9, cbore_r=1.6, screw_r=0.8, screw_len=2.5, pilot_r=0.7, pilot_top=0.5,
    pcb_top=-4.605, pcb_t=1.2, pcb_w=30.0, chip=(4.9, 3.9, 1.75),
    budget_floor=-2.405, section=True, overlaps=True,   # flags: run geometry first, then the slow checks (Fusion stalled with all in one call)
)


def cm(v):
    return v / 10.0


def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    comp = design.rootComponent
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    VI = adsk.core.ValueInput.createByReal
    P3 = lambda x, y: adsk.core.Point3D.create(cm(x), cm(y), 0)

    def sketch_at(z):
        if abs(z) < 1e-9:
            return comp.sketches.add(comp.xYConstructionPlane)
        inp = comp.constructionPlanes.createInput()
        inp.setByOffset(comp.xYConstructionPlane, VI(cm(z)))
        cp = comp.constructionPlanes.add(inp)
        cp.isLightBulbOn = False
        return comp.sketches.add(cp)

    def extrude(sk, z0, z1, op, loops=None, bodies=None):
        profs = adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count):
            p = sk.profiles.item(i)
            if loops is None or p.profileLoops.count == loops:
                profs.add(p)
        inp = comp.features.extrudeFeatures.createInput(profs, op)
        inp.setDistanceExtent(False, VI(cm(z1 - z0)))
        if op != NEW:
            inp.participantBodies = bodies
        return comp.features.extrudeFeatures.add(inp)

    def annulus(name, z0, z1, r0, r1, op=NEW, bodies=None, c=(0.0, 0.0)):
        sk = sketch_at(z0)
        sk.sketchCurves.sketchCircles.addByCenterRadius(P3(*c), cm(r1))
        if r0 > 0:
            sk.sketchCurves.sketchCircles.addByCenterRadius(P3(*c), cm(r0))
        f = extrude(sk, z0, z1, op, loops=2 if r0 > 0 else 1, bodies=bodies)
        if op == NEW:
            f.bodies.item(0).name = name
            return f.bodies.item(0)

    def box(name, z0, z1, w, d):
        sk = sketch_at(z0)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(P3(-w / 2, -d / 2), P3(w / 2, d / 2))
        b = extrude(sk, z0, z1, NEW).bodies.item(0)
        b.name = name
        return b

    def ear(z0, z1, a_deg, body):
        """radial strip (R14..post_r, width ear_w) with a round end, joined to a body"""
        a = math.radians(a_deg)
        ux, uy, vx, vy = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
        hw = K['ear_w'] / 2
        pts = [(14.0 * ux + s * hw * vx, 14.0 * uy + s * hw * vy) for s in (-1, 1)] + \
              [(K['post_r'] * ux + s * hw * vx, K['post_r'] * uy + s * hw * vy) for s in (1, -1)]
        sk = sketch_at(z0)
        for i in range(4):
            sk.sketchCurves.sketchLines.addByTwoPoints(P3(*pts[i]), P3(*pts[(i + 1) % 4]))
        sk.sketchCurves.sketchCircles.addByCenterRadius(P3(K['post_r'] * ux, K['post_r'] * uy), cm(K['ear_r']))
        extrude(sk, z0, z1, JOIN, bodies=[body])

    def rot_pts(a_deg, x0, x1, y0, y1):
        a = math.radians(a_deg)
        ux, uy, vx, vy = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
        return [(x * ux + y * vx, x * uy + y * vy) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]

    def poly_cut(z0, z1, polys, body):
        sk = sketch_at(z0)
        for pts in polys:
            for i in range(4):
                sk.sketchCurves.sketchLines.addByTwoPoints(P3(*pts[i]), P3(*pts[(i + 1) % 4]))
        extrude(sk, z0, z1, CUT, bodies=[body])

    while comp.bRepBodies.count:
        comp.bRepBodies.item(0).deleteMe()
    sa = design.analyses.sectionAnalyses
    while sa.count:
        sa.item(0).deleteMe()

    top = K['front_t']
    zu = K['disc_bot']
    foam_top = zu - K['tape_t']
    plate_top = foam_top - (K['pad_free'] - K['pre_sq'])
    rib_bare = zu - K['rib_gap'] - K['tape_t']

    cover = annulus('Cover', 0.0, top, K['hole_r'], K['front_od'])
    disc = annulus('Disc', K['disc_bot'], K['disc_top'], 0, K['disc_r'])
    annulus('Disc', K['mag_bot'], K['disc_bot'], 0, K['boss_r'], JOIN, [disc])
    mr = K['mag_d'] / 2
    annulus('Disc', K['mag_bot'], K['glue_top'], 0, mr + K['pocket_clr'], CUT, [disc])
    annulus('Magnet', K['mag_bot'], K['mag_bot'] + K['mag_t'], 0, mr)
    annulus('Keeper', K['keeper_z'][0], K['keeper_z'][1], K['keeper_r'][0], K['keeper_r'][1])
    annulus('KeeperPTFE', K['keeper_z'][1], 0.0, K['keeper_tape_r'][0], K['keeper_tape_r'][1])

    plate = annulus('Plate', K['plate_bot'], plate_top, 0, K['plate_r'])
    annulus('Plate', plate_top, K['hub_top'], 0, K['hub_r'], JOIN, [plate])
    annulus('Plate', plate_top, rib_bare, K['rib_r'][0], K['rib_r'][1], JOIN, [plate])
    for a in K['post_angles']:
        ear(K['plate_bot'], plate_top, a, plate)
    annulus('RibTape', rib_bare, rib_bare + K['tape_t'], K['rib_r'][0], K['rib_r'][1])
    hw, sl = K['tongue_w'] / 2, K['slit']
    x_end = K['foot_rc'] + K['foot_r']
    for a in K['foot_angles']:
        poly_cut(K['plate_bot'], plate_top, [rot_pts(a, K['root_r'], x_end + sl, hw, hw + sl),
                                             rot_pts(a, K['root_r'], x_end + sl, -hw - sl, -hw),
                                             rot_pts(a, x_end, x_end + sl, -hw - sl, hw + sl)], plate)
        poly_cut(K['plate_bot'], K['plate_bot'] + (plate_top - K['plate_bot'] - K['tongue_t']), [rot_pts(a, K['root_r'], x_end, -hw, hw)], plate)
    for i, a in enumerate(K['foot_angles']):
        c = (K['foot_rc'] * math.cos(math.radians(a)), K['foot_rc'] * math.sin(math.radians(a)))
        annulus('Plate', plate_top, plate_top + K['pad_free'], 0, K['foot_r'], JOIN, [plate], c=c)
        annulus('TonguePTFE%d' % (i + 1), plate_top + K['pad_free'], plate_top + K['pad_free'] + K['tape_t'], 0, K['foot_r'], NEW, c=c)

    # posts on the cover, pilot holes; screw holes + counterbores in the plate; screws
    for i, a in enumerate(K['post_angles']):
        c = (K['post_r'] * math.cos(math.radians(a)), K['post_r'] * math.sin(math.radians(a)))
        annulus('Cover', plate_top, 0.0, 0, K['boss_rr'], JOIN, [cover], c=c)
        annulus('Cover', plate_top, K['pilot_top'], 0, K['pilot_r'], CUT, [cover], c=c)
        annulus('Plate', K['plate_bot'], plate_top, 0, K['screw_hole'], CUT, [plate], c=c)
        annulus('Plate', K['plate_bot'], K['plate_bot'] + K['screw_head_h'], 0, K['cbore_r'], CUT, [plate], c=c)
        sc = annulus('Screw%d' % (i + 1), K['plate_bot'], K['plate_bot'] + K['screw_head_h'], 0, K['screw_head_r'], NEW, c=c)
        annulus('Screw%d' % (i + 1), K['plate_bot'] + K['screw_head_h'], K['plate_bot'] + K['screw_len'], 0, K['screw_r'], JOIN, [sc], c=c)
    # journal bore through plate and hub (reamed), cut last so it also clears the ears
    annulus('Plate', K['plate_bot'], K['hub_top'], 0, K['bore_r'], CUT, [plate])

    box('CarrierPCB', K['pcb_top'] - K['pcb_t'], K['pcb_top'], K['pcb_w'], K['pcb_w'])
    box('AS5600_chip', K['pcb_top'], K['pcb_top'] + K['chip'][2], K['chip'][0], K['chip'][1])

    if K['section']:
        sa.add(sa.createInput(comp.xZConstructionPlane, 0.0))

    chip_top = K['pcb_top'] + K['chip'][2]
    print('chip top %.3f, magnet bottom %.3f -> gap %.3f' % (chip_top, K['mag_bot'], K['mag_bot'] - chip_top))
    print('lowest ring-group part %.3f vs budget floor %.3f -> spare %.3f; plate %.3f..%.3f (%.2f thick)' % (
        K['plate_bot'], K['budget_floor'], K['plate_bot'] - K['budget_floor'], K['plate_bot'], plate_top, plate_top - K['plate_bot']))
    print('disc face %.2f vs cover face %.2f (flush), reveal %.2f; skin over magnet %.2f; keeper overhang past the hole %.2f' % (
        K['disc_top'], top, K['hole_r'] - K['disc_r'], K['disc_top'] - K['glue_top'], K['keeper_r'][1] - K['hole_r']))
    L = K['foot_rc'] - K['root_r']
    I = K['tongue_w'] * K['tongue_t'] ** 3 / 12.0
    k = 3 * K['E'] * I / L ** 3
    f0, fs = 3 * k * K['pre_sq'], 3 * k * (K['pre_sq'] + K['rib_gap'])
    sig = 6 * (fs / 3) * L / (K['tongue_w'] * K['tongue_t'] ** 2)
    print('tongue: L %.1f w %.1f t %.2f -> k %.2f N/mm each (E %.0f MPa, estimate); preload %.2f N total, force at the stop %.2f N, tongue stress at the stop %.1f MPa' % (
        L, K['tongue_w'], K['tongue_t'], k, K['E'], f0, fs, sig))
    print('rib gap %.3f; journal engagement %.2f (boss tip %.3f to hub top %.3f); bore clearance %.3f; slit end %.2f vs rib start %.2f' % (
        K['rib_gap'], K['hub_top'] - K['mag_bot'], K['mag_bot'], K['hub_top'], K['bore_r'] - K['boss_r'], x_end + sl, K['rib_r'][0]))
    print('screws M1.6x%.1f: engagement above the plate top %.2f (post %.2f + cover %.2f), pilot skin %.2f' % (
        K['screw_len'], K['plate_bot'] + K['screw_len'] - plate_top, -plate_top, K['pilot_top'], top - K['pilot_top']))
    if K['overlaps']:
        tbm = adsk.fusion.TemporaryBRepManager.get()
        bs = [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
        for i in range(len(bs)):
            for j in range(i + 1, len(bs)):
                a = tbm.copy(bs[i])
                b = tbm.copy(bs[j])
                tbm.booleanOperation(a, b, adsk.fusion.BooleanTypes.IntersectionBooleanType)
                if a.volume > 1e-9:
                    print('OVERLAP %s / %s: %.4f mm3' % (bs[i].name, bs[j].name, a.volume * 1000))
    print('bodies:', ', '.join(b.name for b in comp.bRepBodies))
