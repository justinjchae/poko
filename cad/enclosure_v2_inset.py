"""Enclosure v2, inset back plate, rough first pass. Builds EV2_* components in the active Fusion design.

Frame: Z is the thickness axis. A (datum) = XY plane at Z=0 = back face of the 1.0 mm front plate (the face the display
sits against). Front surface Z=+1.0, back face Z=-7.0 (8.0 total). Floorplan x, y are the same as in floorplan_v2.py
(origin = display centre, +Y toward the half-circle end, USB-C toward -Y).

Reads P and solve() from floorplan_v2.py, so the XIAO position, ring OD and ring depth stay driven from there.
Nominal dimensions only; clearances below are design choices, marked ASSUMED.
Rerun is safe: it deletes every EV2_* occurrence first.

Display recess: the front plate keeps a lip_t (0.5) lip in front of the glass; the glass pocket is cut from behind, so the
display datum is the pocket floor at Z = 1.0 - lip_t, not A itself.
Retainer bosses are equally spaced on a circle concentric with the display (same distance from the glass rim); carrier
bosses sit on a curve 4.5 mm inside the cavity wall. Webs are boss-wide (tangent), R1.0 where they meet a wall or the rim.
TODO / notes: cell swell (+0.3 mm toward the front) is not modelled (0.45 mm clearance under the retainer and ring floor, so it
should fit); the tire is nominally squeezed 0.2 mm into the ring; HDGC connector, tact switch, mic port position and button cap
are estimates; cell sits in a carrier window and 5 mm from the XIAO antenna end (metal-near-antenna risk).
FINALIZE: radius every remaining sharp corner (all parts, not only the CNC internal verticals) once the design is frozen.
"""
import adsk.core, adsk.fusion, math

FP = '/Users/justin/code/device/cad/floorplan_v2.py'
DISPLAY_ID = 'urn:adsk.wipprod:dm.lineage:mwBPvT5vTyWRxVTSZovvLA'     # Display LH128R-IF138H (Device project)
XIAO_ID = 'urn:adsk.wipprod:dm.lineage:GwbC92wTQW6rrWqnG2m0Vg'        # XIAO_nRF52840_Sense_ref (Device project)

E = dict(
    wall_rim=1.5,            # outline to the back-plate pocket
    wall_cav=2.5,            # outline to the cavity (rim wall + 1.0 ledge)
    plate_clr=0.1,           # back plate to pocket wall, per side ASSUMED
    pcb_t=1.2, xiao_pcb_t=1.25,
    pcb_clr=0.3,             # carrier edge to cavity wall ASSUMED
    xiao_gap=0.1,            # carrier arm to XIAO edge (castellation solder) ASSUMED
    ant_clear=3.0,           # carrier-free zone beyond the XIAO antenna end ASSUMED (no published keep-out)
    port_clr=0.4,            # USB-C opening over the receptacle, total ASSUMED
    rim_in=17.9, rim_out=19.4, rim_notch=15.4,       # glass locating rim (glass r 17.8 + 0.1), FPC notch width
    glass_t=1.55, gasket_t=0.4, retainer_t=1.0,      # gasket nominal compressed
    gasket_r=(16.5, 17.7),
    ret_r=(16.5, 19.4), ear_d=6.0, arm_w=3.0, ret_notch=16.0,
    ret_pilot_d=1.35, ret_clear_d=1.8, ret_pilot_depth=1.8,
    lip_t=0.5, pocket_d=35.8,   # front lip left over the glass (glass front sits this far below the front surface); pocket = glass + 0.2
    ret_web_len=1.5, ret_angles=[45.0, 135.0, 225.0, 315.0],   # retainer bosses: equal spacing, same distance from the glass rim
    boss_d=4.5, neck_d=3.0, pilot_d=1.35, pilot_depth=3.5,
    bp_d=3.5, bp_edge=4.0, bp_top_angles=[30.0, 150.0], bp_bot_angles=[0.0, 180.0],   # back-plate bosses (V1B-style symmetry), centres bp_edge from the outline
    # 12, 2 and 10 o'clock on the top arc (3/9 o'clock would hit the 50 mm cell); chin: 6 o'clock, both sides where the right flat
    # meets the R30 (y -30, mirrored on the left), plus the bottom-left corner. The chin ones stop on the PCB (neck through it)
    web_over=0.5, cnc_r=1.0,   # web run into the wall/rim, min internal vertical radius (CNC); web width = boss diameter (tangent)
    cav_corner_r=3.0,        # bottom-left cavity corner radius (matches the R3 outside corner)
    port_r=1.25,             # USB-C receptacle external corner radius (opening = this + half the clearance)

    csk_d=3.4, plate_hole_d=1.8,
    # --- remaining components (rough; sizes marked est. are not from a datasheet)
    cell_w=50.0, cell_l=34.0, cell_t=3.0, cell_cx=0.0, cell_cy=-6.3, cell_z_top=-2.9,   # 303450 lying on its side, no PCB under it; SWELL (+0.3) NOT MODELLED, revisit
    pcb_ycut=-23.7,          # carrier PCB ends here (0.6 below the cell edge); it is a chin board now
    chip_l=4.9, chip_w=3.9, chip_h=1.75,                                                              # AS5600 SOIC-8
    # roller: no axle (it would sit on the magnet axis). Rigid ring hub, Ø4x2 diametric disc magnet glued in its through-hole
    # (top flush), TPU tire band on the hub. Front plate face above, ring-plate tab below, collar on the tab around the hub bottom
    tire_r=4.5, tire_z=(-0.1, -0.9), tire_squeeze=0.2,                                               # tire runs on the ring's wide back part
    hub_r=2.8, hub_z=(-0.1, -1.9),
    mag_d=4.0, mag_t=2.0, mag_z_top=-0.1, pocket_clr=0.05,
    tab_r=(2.1, 3.6), tab_w=4.0,                                                                     # tab ring under the hub wall, centre open
    collar_r=(2.9, 3.6), collar_top=-1.0,                                                            # 0.1 radial clearance
    plate_t=0.4, thrust_gap=0.1, plate_od=15.6, rp_r=17.8, rp_angles=[45.0, 135.0, 250.0], rp_ear_d=4.6,   # ring retaining plate
    hub_clr=0.2, hub_wall=0.8, hub_top=0.3,                                                          # fixed inner hub on the plate locates the ring bore (FDM clearance), hidden
    rib_r=[9.5, 14.5], rib_w=0.6, rib_h=0.3,                                                         # two raised thrust ribs on the plate (washer version later)
    arm_blk=(-25.0, -51.25), blk_r=1.5, notch_r=1.0,                                                 # left-arm end block (inner x, top y), its outer corner radius; notch radius
    sw_l=4.0, sw_w=3.0, sw_h=1.5, stem_d=4.0, stem_gap=0.2,                                          # select switch est.
    fpc_conn=(0.0, -27.0), fpc_conn_w=3.0, fpc_conn_l=11.3, fpc_conn_h=1.0,                          # HDGC 16P, size est.
    lra=(19.5, -28.5), lra_w=8.0, lra_l=9.0, lra_h=3.5, tail_w=3.9, tail_out=2.75, tail_t=0.3,        # Xinhailong L090835H, pads down
    mic_tube_d=3.0, mic_hole_d=1.0, mic_foam=0.3,                                                    # mic port, hole centred on the mic body (est.)
    # ring (no sleeve): front part in a plain front-plate hole, wider back part behind A (forward stop on A, roller track),
    # bore rides on the hidden hub, inner lip at the front holds the button cap (0.15 hairline between ring and cap)
    ring_bore_r=8.7, ring_bore_clr=0.3, flange_over=1.0, ring_top_play=0.1, ring_lip_r=7.15, ring_lip_bot=0.4,
    cap_r=7.0, cap_t=1.5, cap_flange_r=7.55, cap_flange_z=(0.4, -0.6),                                # flange sits under the ring lip
    key_flat=7.0, key_clr=0.15, key_half=3.25,                         # anti-rotation: two flats in the hub bore (at x = +-7.0), matching flats on the cap flange
)


def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    ns = {}
    exec(compile(open(FP).read(), 'floorplan_v2.py', 'exec'), ns)
    P, cm, pt = ns['P'], ns['cm'], ns['pt']
    draw_outline, circle, line, arc = ns['draw_outline'], ns['circle'], ns['line'], ns['arc']
    S = ns['solve'](P)
    g = S['g']

    for i in range(root.occurrences.count - 1, -1, -1):
        nm = root.occurrences.item(i).component.name
        if nm.startswith('EV2_') or nm.startswith('XIAO_nRF52840') or nm.startswith('Display LH128R'):
            root.occurrences.item(i).deleteMe()
    for i in range(root.constructionPlanes.count - 1, -1, -1):
        pass

    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    CUT = adsk.fusion.FeatureOperations.CutFeatureOperation
    VI = adsk.core.ValueInput.createByReal

    zf, zb = S['z_front'], S['z_back']
    z_ledge = zb + P['back_plate']
    z_top = zf
    z_pcb = S['z_pcb_top']
    c, rr = S['c'], S['rr']
    orad = S['orad']
    glass_front_z = zf - E['lip_t']                          # glass front face (display datum is this pocket floor)
    glass_back_z = glass_front_z - E['glass_t']
    depth = S['depth']                                       # ring assembly budget from the front surface (ring + plate)
    z_plate_bot = z_top - depth
    z_plate_top = z_plate_bot + E['plate_t']
    z_rib_top = z_plate_top + E['rib_h']
    z_ring_bot = z_rib_top + E['thrust_gap']                 # ring rides on the rib, the plate stays where the shield allows

    def new_comp(name):
        occ = root.occurrences.addNewComponent(adsk.core.Matrix3D.create())
        occ.component.name = 'EV2_' + name
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
        if op != NEW:                                       # never touch bodies of other components
            inp.participantBodies = [comp.bRepBodies.item(i) for i in range(comp.bRepBodies.count)]
        return comp.features.extrudeFeatures.add(inp)

    def discs(comp, z0, z1, pts, d, op):
        sk = sketch_at(comp, z0)
        for p in pts:
            circle(sk, p, d / 2)
        return extrude(comp, sk, z0, z1, op)

    def annulus(comp, z0, z1, ctr, r_in, r_out, op):
        sk = sketch_at(comp, z0)
        circle(sk, ctr, r_out)
        circle(sk, ctr, r_in)
        return extrude(comp, sk, z0, z1, op, loops=2)

    def rect(comp, z0, z1, x0, y0, x1, y1, op):
        sk = sketch_at(comp, z0)
        sk.sketchCurves.sketchLines.addTwoPointRectangle(pt(x0, y0), pt(x1, y1))
        return extrude(comp, sk, z0, z1, op)

    Rcav = g['Rb'] - E['wall_cav']

    def arc_boss(org, ang, d):
        """Boss on an arc wall, centre bp_edge in from the outline, tangent web out into the wall. Returns centre, web, joints."""
        a = math.radians(ang)
        u, h_ = (math.cos(a), math.sin(a)), d / 2
        v = (-u[1], u[0])
        r = g['Rb'] - E['bp_edge']
        p = (org[0] + r * u[0], org[1] + r * u[1])
        L_ = Rcav - r + E['web_over']
        q = [(p[0] + s_ * h_ * v[0] + t * u[0], p[1] + s_ * h_ * v[1] + t * u[1]) for s_, t in ((-1, 0), (1, 0), (1, L_), (-1, L_))]
        aw = math.sqrt(Rcav ** 2 - h_ ** 2)
        return p, q, [(org[0] + aw * u[0] + s_ * h_ * v[0], org[1] + aw * u[1] + s_ * h_ * v[1]) for s_ in (-1, 1)]

    bp_top = [arc_boss((0.0, 0.0), a_, E['bp_d']) for a_ in E['bp_top_angles']]
    bp_bot = [arc_boss((0.0, g['cBR'][1]), a_, E['bp_d']) for a_ in E['bp_bot_angles']]
    bp_bl = (g['xl'] + E['bp_edge'], g['bot'] + E['bp_edge'])        # inside the left-arm end block
    bp_neck = [b_[0] for b_ in bp_bot] + [bp_bl]                                       # these two pass through the carrier PCB
    bp_all = [b_[0] for b_ in bp_top] + bp_neck
    report = []

    def done(comp, label):
        for b in comp.bRepBodies:
            bb = b.boundingBox
            report.append('%-18s %-16s vol %8.2f mm3  X %7.2f..%7.2f  Y %7.2f..%7.2f  Z %6.2f..%6.2f' % (
                label, b.name, b.volume * 1000, bb.minPoint.x * 10, bb.maxPoint.x * 10, bb.minPoint.y * 10,
                bb.maxPoint.y * 10, bb.minPoint.z * 10, bb.maxPoint.z * 10))

    # ---------------- front shell (one piece: plate, walls, ledge, bosses, display rim) ----------------
    sh = new_comp('FrontShell')
    sk = sketch_at(sh, zf)
    draw_outline(sk, g, 0)
    extrude(sh, sk, zf, zb, NEW)
    sh.bRepBodies.item(0).name = 'FrontShell'
    sk = sketch_at(sh, 0)
    draw_outline(sk, g, E['wall_cav'], rmin=E['cav_corner_r'])
    extrude(sh, sk, 0, z_ledge, CUT)                       # cavity, below the ledge
    sk = sketch_at(sh, z_ledge)
    draw_outline(sk, g, E['wall_rim'])
    extrude(sh, sk, z_ledge, zb, CUT)                      # back-plate pocket
    sk = sketch_at(sh, zf)
    circle(sk, (0, 0), orad)
    extrude(sh, sk, zf, 0, CUT)                            # display window (datasheet: active + 0.6)
    sk = sketch_at(sh, 0)
    circle(sk, (0, 0), E['pocket_d'] / 2)
    extrude(sh, sk, 0, glass_front_z, CUT)                 # glass pocket from behind, leaves a lip_t front lip
    rect(sh, 0, glass_front_z, -E['rim_notch'] / 2, 14.0, E['rim_notch'] / 2, 22.0, CUT)   # tab relief in the pocket
    r_hole = rr + E['ring_bore_clr']
    sk = sketch_at(sh, zf)
    circle(sk, c, r_hole)
    extrude(sh, sk, zf, 0, CUT)                            # plain ring hole (no sleeve)
    # display locating rim around the glass, notched for the FPC tab
    annulus(sh, 0, glass_back_z, (0, 0), E['rim_in'], E['rim_out'], JOIN)
    hn = E['rim_notch'] / 2
    rect(sh, 0, glass_back_z, -hn, 14.0, hn, 22.0, CUT)
    # bosses. Carrier bosses: on a curve 4.5 mm inside the cavity wall, web (as wide as the boss, tangent) to the wall.
    # Retainer bosses: equally spaced, all the same distance outside the glass rim, web to the rim, so the clamp is even.
    z_ret_top = glass_back_z - E['gasket_t']                # retainer front face = boss top
    hw = E['boss_d'] / 2                                    # half web width = boss radius
    rb_c = E['rim_out'] + E['ret_web_len'] + hw             # retainer boss centre radius from the display centre
    ret_b = [((rb_c * math.cos(math.radians(a_)), rb_c * math.sin(math.radians(a_))),
              (-math.cos(math.radians(a_)), -math.sin(math.radians(a_)))) for a_ in E['ret_angles']]
    ear_pts = [b_[0] for b_ in ret_b]

    def web_poly(sk, c0, d, length):
        v = (-d[1], d[0])
        q = [(c0[0] + s_ * hw * v[0] + t * d[0], c0[1] + s_ * hw * v[1] + t * d[1])
             for s_, t in ((-1, 0), (1, 0), (1, length), (-1, length))]
        for i in range(4):
            line(sk, q[i], q[(i + 1) % 4])

    def boss_with_webs(group, z_boss, z_web, length):
        discs(sh, 0, z_boss, [g_[0] for g_ in group], E['boss_d'], JOIN)
        sk_ = sketch_at(sh, 0)
        for c0, d in group:
            web_poly(sk_, c0, d, length)
        extrude(sh, sk_, 0, z_web, JOIN)

    boss_with_webs(ret_b, z_ret_top, glass_back_z, E['ret_web_len'] + hw + E['web_over'])
    # back-plate bosses: top two run the full depth to the ledge, bottom-right stops on the PCB (neck through it)
    jpts = []
    for (p_, q_, j_), z_end in [(b_, z_ledge) for b_ in bp_top] + [(b_, z_pcb) for b_ in bp_bot]:
        discs(sh, 0, z_end, [p_], E['bp_d'], JOIN)
        sk_ = sketch_at(sh, 0)
        for i in range(4):
            line(sk_, q_[i], q_[(i + 1) % 4])
        extrude(sh, sk_, 0, z_end, JOIN)
        jpts += j_
    # left-arm end block: the bottom-left cavity corner is solid down to the arm's front face (also the bottom-left boss);
    # outer corner rounded, internal corners filleted below
    x_wall = g['xl'] + E['wall_cav']
    bx, by = E['arm_blk']
    br_ = E['blk_r']
    sk_ = sketch_at(sh, 0)
    sk_.sketchCurves.sketchLines.addTwoPointRectangle(pt(g['xl'] + 1.0, g['bot'] + 1.0), pt(bx, by - br_))
    sk_.sketchCurves.sketchLines.addTwoPointRectangle(pt(g['xl'] + 1.0, by - br_), pt(bx - br_, by))
    circle(sk_, (bx - br_, by - br_), br_)
    extrude(sh, sk_, 0, z_pcb, JOIN)
    ccx, ccy = g['xl'] + E['wall_cav'] + E['cav_corner_r'], g['bot'] + E['wall_cav'] + E['cav_corner_r']
    y_meet = ccy - math.sqrt(max(E['cav_corner_r'] ** 2 - (bx - ccx) ** 2, 0)) if bx < ccx else g['bot'] + E['wall_cav']
    jpts += [(x_wall, by), (bx, y_meet)]
    # CNC: round the internal vertical corners where each web meets the wall or the rim
    for c0, d in ret_b:
        u = (-d[0], -d[1])
        v = (-u[1], u[0])
        ar_ = math.sqrt(E['rim_out'] ** 2 - hw ** 2)
        for s_ in (-1, 1):
            jpts.append((ar_ * u[0] + s_ * hw * v[0], ar_ * u[1] + s_ * hw * v[1]))
    edges = adsk.core.ObjectCollection.create()
    for e_ in sh.bRepBodies.item(0).edges:
        gg = e_.geometry
        if gg.curveType != adsk.core.Curve3DTypes.Line3DCurveType:
            continue
        sp_, ep_ = gg.startPoint, gg.endPoint
        if abs(sp_.x - ep_.x) > 1e-6 or abs(sp_.y - ep_.y) > 1e-6:
            continue                                         # not parallel to Z
        mx, my = sp_.x * 10, sp_.y * 10
        if any(math.hypot(mx - jx, my - jy) < 0.15 for jx, jy in jpts):
            edges.add(e_)
    report.append('web fillet edges selected: %d of %d expected' % (edges.count, len(jpts)))
    fi = sh.features.filletFeatures.createInput()
    fi.addConstantRadiusEdgeSet(edges, VI(cm(E['cnc_r'])), True)
    sh.features.filletFeatures.add(fi)
    discs(sh, z_ret_top, z_ret_top + E['ret_pilot_depth'], ear_pts, E['ret_pilot_d'], CUT)
    # back-plate bosses: necks through the PCB (bottom two), M1.6 pilots from the back (all four)
    discs(sh, z_pcb, z_ledge, bp_neck, E['neck_d'], JOIN)
    discs(sh, z_ledge, z_ledge + E['pilot_depth'], bp_all, E['pilot_d'], CUT)
    # mic: short tube from the front plate down to the XIAO mic (foam gasket between), 1.0 mm port through the plate
    mic_c = (S['ox'] + 4.3, S['y0'] + 19.405)
    z_tube = z_pcb + 0.94 + E['mic_foam']                    # mic top is 0.94 above the XIAO top face
    discs(sh, 0, z_tube, [mic_c], E['mic_tube_d'], JOIN)
    discs(sh, zf, z_tube, [mic_c], E['mic_hole_d'], CUT)
    # ring retaining plate bosses (3, outside the ring back part), tapped from below
    rp_c = [(c[0] + E['rp_r'] * math.cos(math.radians(a_)), c[1] + E['rp_r'] * math.sin(math.radians(a_))) for a_ in E['rp_angles']]
    discs(sh, 0, z_plate_top, rp_c, E['boss_d'], JOIN)
    discs(sh, z_plate_top, z_plate_top + E['ret_pilot_depth'], rp_c, E['ret_pilot_d'], CUT)
    rc = (c[0] + rr + E['flange_over'] + E['tire_r'] - E['tire_squeeze'], c[1])  # roller centre, tire pressed on the ring's back part
    # USB-C opening through the bottom wall, stadium centred on Z = port centre
    pw, ph = P['usb_w'] + E['port_clr'], 3.21 + E['port_clr']
    pr = E['port_r'] + E['port_clr'] / 2
    y_pl = g['bot'] - 1.0
    pin = sh.constructionPlanes.createInput()
    pin.setByOffset(sh.xZConstructionPlane, VI(cm(0)))
    xz0 = sh.constructionPlanes.add(pin)
    n0 = xz0.geometry.normal
    off = y_pl if n0.y > 0 else -y_pl
    pin = sh.constructionPlanes.createInput()
    pin.setByOffset(sh.xZConstructionPlane, VI(cm(off)))
    plane = sh.constructionPlanes.add(pin)
    plane.isLightBulbOn = False
    xz0.isLightBulbOn = False
    sk = sh.sketches.add(plane)
    zc, pcx = S['z_port'], S['pcx']
    ha, hb = pw / 2, ph / 2
    sp = lambda x, z: sk.modelToSketchSpace(adsk.core.Point3D.create(cm(x), cm(y_pl), cm(z)))
    L = sk.sketchCurves.sketchLines.addByTwoPoints
    A = sk.sketchCurves.sketchArcs.addByThreePoints
    k = pr * (1 - math.sqrt(0.5))
    L(sp(pcx - ha + pr, zc + hb), sp(pcx + ha - pr, zc + hb))
    L(sp(pcx + ha, zc + hb - pr), sp(pcx + ha, zc - hb + pr))
    L(sp(pcx + ha - pr, zc - hb), sp(pcx - ha + pr, zc - hb))
    L(sp(pcx - ha, zc - hb + pr), sp(pcx - ha, zc + hb - pr))
    A(sp(pcx + ha - pr, zc + hb), sp(pcx + ha - k, zc + hb - k), sp(pcx + ha, zc + hb - pr))
    A(sp(pcx + ha, zc - hb + pr), sp(pcx + ha - k, zc - hb + k), sp(pcx + ha - pr, zc - hb))
    A(sp(pcx - ha + pr, zc - hb), sp(pcx - ha + k, zc - hb + k), sp(pcx - ha, zc - hb + pr))
    A(sp(pcx - ha, zc + hb - pr), sp(pcx - ha + k, zc + hb - k), sp(pcx - ha + pr, zc + hb))
    profs = adsk.core.ObjectCollection.create()
    profs.add(sk.profiles.item(0))
    inp = sh.features.extrudeFeatures.createInput(profs, CUT)
    inp.participantBodies = [sh.bRepBodies.item(0)]
    nrm = sk.xDirection.crossProduct(sk.yDirection)
    sgn = 1 if nrm.y > 0 else -1
    inp.setDistanceExtent(False, VI(cm(sgn * (1.0 + 3.0))))
    sh.features.extrudeFeatures.add(inp)
    done(sh, 'FrontShell')

    # ---------------- back plate (inset, on the ledge) ----------------
    bp = new_comp('BackPlate')
    sk = sketch_at(bp, z_ledge)
    draw_outline(sk, g, E['wall_rim'] + E['plate_clr'])
    extrude(bp, sk, z_ledge, zb, NEW)
    bp.bRepBodies.item(0).name = 'BackPlate'
    # countersunk M1.6 holes at the four back-plate bosses (head 3.4 x 90 deg from the back face)
    sk = sketch_at(bp, zb)
    pts = adsk.core.ObjectCollection.create()
    for p in bp_all:
        pts.add(sk.sketchPoints.add(pt(*p)))
    hi = bp.features.holeFeatures.createCountersinkInput(VI(cm(E['plate_hole_d'])), VI(cm(E['csk_d'])), VI(math.radians(90)))
    hi.setPositionBySketchPoints(pts)
    hi.setDistanceExtent(VI(cm(P['back_plate'])))
    hi.isDefaultDirection = False
    bp.features.holeFeatures.add(hi)
    done(bp, 'BackPlate')

    # ---------------- carrier PCB mock (1.2 mm plate, XIAO notch open at the bottom edge) ----------------
    pcb = new_comp('CarrierPCB_mock')
    notch = (S['pcx'] - P['xiao_w'] / 2 - E['xiao_gap'], S['pcx'] + P['xiao_w'] / 2 + E['xiao_gap'],
             S['y0'] + P['xiao_l'] + E['ant_clear'])
    sk = sketch_at(pcb, z_pcb)
    draw_outline(sk, g, E['wall_cav'] + E['pcb_clr'], notch=notch, rmin=E['cav_corner_r'], ycut=E['pcb_ycut'], notch_r=E['notch_r'])
    extrude(pcb, sk, z_pcb, z_pcb - E['pcb_t'], NEW)
    pcb.bRepBodies.item(0).name = 'CarrierPCB'
    discs(pcb, z_pcb, z_pcb - E['pcb_t'], bp_neck, E['neck_d'] + 0.2, CUT)
    done(pcb, 'CarrierPCB')

    # ---------------- display gasket + retainer ----------------
    gk = new_comp('DisplayGasket')
    annulus(gk, glass_back_z, z_ret_top, (0, 0), E['gasket_r'][0], E['gasket_r'][1], NEW)
    gk.bRepBodies.item(0).name = 'Gasket'
    done(gk, 'Gasket')
    rt = new_comp('DisplayRetainer')
    z_ret_bot = z_ret_top - E['retainer_t']
    annulus(rt, z_ret_top, z_ret_bot, (0, 0), E['ret_r'][0], E['ret_r'][1], NEW)
    rt.bRepBodies.item(0).name = 'Retainer'
    sk = sketch_at(rt, z_ret_top)                           # arms from the annulus out to the ears
    for ex, ey in ear_pts:
        r2 = math.hypot(ex, ey)
        u = (ex / r2, ey / r2)
        v = (-u[1], u[0])
        r1, hw_ = E['ret_r'][1] - 0.5, E['arm_w'] / 2
        q = [(r1 * u[0] + s_ * hw_ * v[0], r1 * u[1] + s_ * hw_ * v[1]) for s_ in (-1, 1)] + \
            [(r2 * u[0] + s_ * hw_ * v[0], r2 * u[1] + s_ * hw_ * v[1]) for s_ in (1, -1)]
        for i in range(4):
            line(sk, q[i], q[(i + 1) % 4])
    extrude(rt, sk, z_ret_top, z_ret_bot, JOIN)
    discs(rt, z_ret_top, z_ret_bot, ear_pts, E['ear_d'], JOIN)
    discs(rt, z_ret_top, z_ret_bot, ear_pts, E['ret_clear_d'], CUT)
    rect(rt, z_ret_top, z_ret_bot, -hn, E['ret_notch'], hn, 22.0, CUT)
    done(rt, 'Retainer')

    # ---------------- ring, retaining plate, button cap (no sleeve) ----------------
    # axial stack (Z): front plate back face A > 0.1 play > ring back part > 0.1 > ribs on the plate (3 screws into bosses from A).
    # Radially the ring rides on the hidden hub; the front-plate hole is only a clearance.
    ring = new_comp('Ring')
    r_back = rr + E['flange_over']
    z_back_top = -E['ring_top_play']
    annulus(ring, z_top, z_back_top, c, E['ring_bore_r'], rr, NEW)                                 # front part, in the hole
    ring.bRepBodies.item(0).name = 'Ring'
    annulus(ring, z_back_top, z_ring_bot, c, E['ring_bore_r'], r_back, JOIN)                       # back part: stop on A, roller track
    annulus(ring, z_top, E['ring_lip_bot'], c, E['ring_lip_r'], E['ring_bore_r'] + 0.2, JOIN)      # inner lip over the cap flange
    done(ring, 'Ring')
    # plate: fixed inner hub (stops 0.1 under the ring lip), two raised thrust ribs, an open-centred tab under the roller hub
    # and a collar around the hub bottom
    hub_out = E['ring_bore_r'] - E['hub_clr']
    hub_in = hub_out - E['hub_wall']
    u0 = P['xiao_usb_over']
    usb_ko = (S['ox'] + 4.428 - 0.2, S['y0'] - u0 - 0.2, S['ox'] + 13.368 + 0.2, S['y0'] + P['xiao_usb_len'] - u0 + 0.2)
    rp = new_comp('RingPlate')
    annulus(rp, z_plate_top, z_plate_bot, c, hub_in, E['plate_od'], NEW)
    rp.bRepBodies.item(0).name = 'RingPlate'
    annulus(rp, z_plate_top, E['hub_top'], c, hub_in, hub_out, JOIN)                               # inner hub (hidden)
    for sx in (-1, 1):                                                                             # anti-rotation flats in the bore
        xa, xb = c[0] + sx * E['key_flat'], c[0] + sx * (hub_in + 0.05)
        rect(rp, z_plate_top, E['hub_top'], min(xa, xb), c[1] - E['key_half'], max(xa, xb), c[1] + E['key_half'], JOIN)
    for r_ in E['rib_r']:
        annulus(rp, z_plate_top, z_rib_top, c, r_ - E['rib_w'] / 2, r_ + E['rib_w'] / 2, JOIN)     # thrust ribs
    rect(rp, z_plate_top, z_plate_bot, c[0] + E['plate_od'] - 0.5, rc[1] - E['tab_w'] / 2, rc[0] - E['tab_r'][0], rc[1] + E['tab_w'] / 2, JOIN)
    annulus(rp, z_plate_top, z_plate_bot, rc, E['tab_r'][0], E['tab_r'][1], JOIN)                  # roller retaining tab
    discs(rp, z_plate_top, z_plate_bot, [rc], 2 * E['tab_r'][0], CUT)                              # open centre under the magnet
    rect(rp, z_plate_top, z_plate_bot, *usb_ko, CUT)
    sk = sketch_at(rp, z_plate_top)
    for ex, ey in rp_c:
        dx, dy = ex - c[0], ey - c[1]
        r2 = math.hypot(dx, dy)
        u = (dx / r2, dy / r2)
        v = (-u[1], u[0])
        r1, hw_ = E['plate_od'] - 0.4, 1.5
        q = [(c[0] + r1 * u[0] + s_ * hw_ * v[0], c[1] + r1 * u[1] + s_ * hw_ * v[1]) for s_ in (-1, 1)] + \
            [(c[0] + r2 * u[0] + s_ * hw_ * v[0], c[1] + r2 * u[1] + s_ * hw_ * v[1]) for s_ in (1, -1)]
        for i in range(4):
            line(sk, q[i], q[(i + 1) % 4])
    extrude(rp, sk, z_plate_top, z_plate_bot, JOIN)
    discs(rp, z_plate_top, z_plate_bot, rp_c, E['rp_ear_d'], JOIN)
    discs(rp, z_plate_top, z_plate_bot, rp_c, E['ret_clear_d'], CUT)
    col = annulus(rp, z_plate_top, E['collar_top'], rc, E['collar_r'][0], E['collar_r'][1], NEW).bodies.item(0)
    tools = adsk.core.ObjectCollection.create()
    tools.add(col)
    rp.features.combineFeatures.add(rp.features.combineFeatures.createInput(rp.bRepBodies.itemByName('RingPlate'), tools))
    done(rp, 'RingPlate')
    cap = new_comp('ButtonCap')
    sk = sketch_at(cap, z_top)
    circle(sk, c, E['cap_r'])
    extrude(cap, sk, z_top, z_top - E['cap_t'], NEW)
    cap.bRepBodies.item(0).name = 'ButtonCap'
    discs(cap, E['cap_flange_z'][0], E['cap_flange_z'][1], [c], 2 * E['cap_flange_r'], JOIN)        # flange under the ring lip
    for sx in (-1, 1):                                                                             # flats that key into the hub
        xa, xb = c[0] + sx * (E['key_flat'] - E['key_clr']), c[0] + sx * (E['cap_flange_r'] + 0.5)
        rect(cap, E['cap_flange_z'][0], E['cap_flange_z'][1], min(xa, xb), c[1] - 4.5, max(xa, xb), c[1] + 4.5, CUT)
    z_sw_top = z_pcb + E['sw_h']
    sk = sketch_at(cap, z_top - E['cap_t'])
    circle(sk, c, E['stem_d'] / 2)
    extrude(cap, sk, z_top - E['cap_t'], z_sw_top + E['stem_gap'], JOIN)                # stem down to the switch 
    done(cap, 'ButtonCap')

    # ---------------- cell, sensor, roller, switch, FPC connector, LRA ----------------
    cell = new_comp('Cell')
    z_cb = E['cell_z_top'] - E['cell_t']
    rect(cell, E['cell_z_top'], z_cb, E['cell_cx'] - E['cell_w'] / 2, E['cell_cy'] - E['cell_l'] / 2,
         E['cell_cx'] + E['cell_w'] / 2, E['cell_cy'] + E['cell_l'] / 2, NEW)
    cell.bRepBodies.item(0).name = 'Cell303450'
    done(cell, 'Cell')
    z_chip_top = z_pcb + E['chip_h']
    chip = new_comp('AS5600')
    rect(chip, z_pcb, z_chip_top, rc[0] - E['chip_l'] / 2, rc[1] - E['chip_w'] / 2, rc[0] + E['chip_l'] / 2, rc[1] + E['chip_w'] / 2, NEW)
    chip.bRepBodies.item(0).name = 'AS5600'
    done(chip, 'AS5600')
    # roller: rigid ring hub, magnet glued in its through-hole (top flush), TPU tire band on the hub
    z_mag_bot = E['mag_z_top'] - E['mag_t']
    rol = new_comp('Roller')
    annulus(rol, E['hub_z'][0], E['hub_z'][1], rc, E['mag_d'] / 2 + E['pocket_clr'], E['hub_r'], NEW).bodies.item(0).name = 'Hub'
    annulus(rol, E['tire_z'][0], E['tire_z'][1], rc, E['hub_r'], E['tire_r'], NEW).bodies.item(0).name = 'TireTPU'
    discs(rol, E['mag_z_top'], z_mag_bot, [rc], E['mag_d'], NEW).bodies.item(0).name = 'Magnet4x2'
    done(rol, 'Roller')
    swc = new_comp('SelectSwitch')
    rect(swc, z_pcb, z_sw_top, c[0] - E['sw_l'] / 2, c[1] - E['sw_w'] / 2, c[0] + E['sw_l'] / 2, c[1] + E['sw_w'] / 2, NEW)
    swc.bRepBodies.item(0).name = 'Switch'
    done(swc, 'Switch')
    fc = new_comp('FPCConnector')
    fx, fy = E['fpc_conn']
    rect(fc, z_pcb, z_pcb + E['fpc_conn_h'], fx - E['fpc_conn_l'] / 2, fy - E['fpc_conn_w'] / 2, fx + E['fpc_conn_l'] / 2, fy + E['fpc_conn_w'] / 2, NEW)
    fc.bRepBodies.item(0).name = 'HDGC16P'
    done(fc, 'FPCConnector')
    lr = new_comp('LRA')
    lx, ly = E['lra']
    rect(lr, z_pcb, z_pcb + E['lra_h'], lx - E['lra_w'] / 2, ly - E['lra_l'] / 2, lx + E['lra_w'] / 2, ly + E['lra_l'] / 2, NEW)
    lr.bRepBodies.item(0).name = 'LRA'
    tx0 = lx - E['lra_w'] / 2 + 0.8
    rect(lr, z_pcb, z_pcb + E['tail_t'], tx0, ly - E['lra_l'] / 2 - E['tail_out'], tx0 + E['tail_w'], ly - E['lra_l'] / 2 + 0.2, JOIN)
    done(lr, 'LRA')

    # ---------------- inserted models: display (Shineworld) and XIAO ----------------
    m = adsk.core.Matrix3D.create()
    m.setToRotation(math.pi / 2, adsk.core.Vector3D.create(0, 0, 1), adsk.core.Point3D.create(0, 0, 0))   # FPC toward +Y
    m.translation = adsk.core.Vector3D.create(0, 0, cm(glass_front_z - E['glass_t']))                   # front face on the pocket floor
    occ = root.occurrences.addByInsert(app.data.findFileById(DISPLAY_ID), m, False)
    occ.component.name = 'EV2_Display'
    for b in occ.component.bRepBodies:
        if b.name in ('fpc', 'fpc_stiffener') or b.name.startswith('pad_'):
            b.isLightBulbOn = False
    m = adsk.core.Matrix3D.create()                         # must be a referenced insert: a copy ignores the transform
    m.translation = adsk.core.Vector3D.create(cm(S['ox']), cm(S['y0']), cm(z_pcb - E['xiao_pcb_t']))
    occ = root.occurrences.addByInsert(app.data.findFileById(XIAO_ID), m, True)

    # appearances (library copies), by component
    lib = app.materialLibraries.itemByName('Fusion Appearance Library')
    look = {'EV2_FrontShell': 'Aluminum - Anodized Rough (Grey)', 'EV2_BackPlate': 'Aluminum - Anodized Glossy (Grey)',
            'EV2_CarrierPCB_mock': 'Plastic - Matte (Green)', 'EV2_DisplayGasket': 'Plastic - Matte (Yellow)',
            'EV2_DisplayRetainer': 'Plastic - Matte (Black)', 'EV2_Ring': 'Aluminum - Satin',
            'EV2_RingPlate': 'Plastic - Matte (White)', 'EV2_ButtonCap': 'Plastic - Glossy (Black)',
            'EV2_Cell': 'Plastic - Matte (Blue)', 'EV2_AS5600': 'Plastic - Matte (Black)', 'EV2_Roller': 'Plastic - Matte (White)',
            'EV2_SelectSwitch': 'Plastic - Matte (Black)', 'EV2_FPCConnector': 'Plastic - Matte (White)', 'EV2_LRA': 'Aluminum - Satin'}
    for o in root.occurrences:
        nm = o.component.name
        if nm in look:
            ap = design.appearances.itemByName(look[nm]) or design.appearances.addByCopy(lib.appearances.itemByName(look[nm]), look[nm])
            for b in o.component.bRepBodies:
                b.appearance = ap
    for o in root.occurrences:
        if o.component.name == 'EV2_Roller':
            tp = design.appearances.itemByName('Rubber - Soft') or design.appearances.addByCopy(lib.appearances.itemByName('Rubber - Soft'), 'Rubber - Soft')
            o.component.bRepBodies.itemByName('TireTPU').appearance = tp
            mg = design.appearances.itemByName('Steel - Satin') or design.appearances.addByCopy(lib.appearances.itemByName('Steel - Satin'), 'Steel - Satin')
            o.component.bRepBodies.itemByName('Magnet4x2').appearance = mg
    for i in range(root.sketches.count):
        root.sketches.item(i).isLightBulbOn = False
    for o in root.occurrences:
        for i in range(o.component.sketches.count):
            o.component.sketches.item(i).isLightBulbOn = False
    # pairwise interference with the Boolean kernel (design.analyzeInterference silently misses pairs on large selections)
    tbm = adsk.fusion.TemporaryBRepManager.get()
    mine = [(o.component.name[4:] + '/' + b.name, b) for o in root.occurrences if o.component.name.startswith('EV2_') for b in o.bRepBodies
            if b.isLightBulbOn and not (b.name.startswith('pad_') or b.name in ('fpc', 'fpc_stiffener', 'panel_LCM', 'active_area_D32.4', 'Adhesive_tape', 'Mounting holes'))
            and o.component.name != 'EV2_Display']
    mine += [('Display/panel_LCM', b) for o in root.occurrences if o.component.name == 'EV2_Display' for b in o.bRepBodies if b.name == 'panel_LCM']
    others = []
    for o in root.allOccurrences:
        n = o.fullPathName
        if n.startswith('XIAO') and o.component.bRepBodies.count:
            for b in o.bRepBodies:
                if b.isLightBulbOn and not (b.name.startswith('pad_') or b.name in ('fpc', 'fpc_stiffener')):
                    others.append((n.split('+')[0] + '+' + n.split('+')[-1] + '/' + b.name, b))

    def near(a_, b_):
        p, q = a_.boundingBox, b_.boundingBox
        return not (p.maxPoint.x < q.minPoint.x or q.maxPoint.x < p.minPoint.x or p.maxPoint.y < q.minPoint.y or
                    q.maxPoint.y < p.minPoint.y or p.maxPoint.z < q.minPoint.z or q.maxPoint.z < p.minPoint.z)

    def overlap(a_, b_):
        x_, y_ = tbm.copy(a_), tbm.copy(b_)
        tbm.booleanOperation(x_, y_, adsk.fusion.BooleanTypes.IntersectionBooleanType)
        return x_.volume * 1000 if x_.isValid else 0.0

    hits = []
    for i in range(len(mine)):
        for j in range(i + 1, len(mine)):
            if near(mine[i][1], mine[j][1]):
                v_ = overlap(mine[i][1], mine[j][1])
                if v_ > 0.005:
                    hits.append('%s <> %s  %.3f mm3' % (mine[i][0], mine[j][0], v_))
        for nm, ob in others:
            if near(mine[i][1], ob):
                v_ = overlap(mine[i][1], ob)
                if v_ > 0.005:
                    hits.append('%s <> %s  %.3f mm3' % (mine[i][0], nm, v_))
    report.append('interference between parts (> 0.005 mm3): %d' % len(hits))
    report.extend(hits)
    print('\n'.join(report))
    print('z levels: front %.3f A 0 ledge %.3f back %.3f | port centre %.3f | PCB front %.3f | ring bottom %.3f, plate %.3f..%.3f'
          % (zf, z_ledge, zb, S['z_port'], z_pcb, z_ring_bot, z_plate_top, z_plate_bot))
    print('ring OD %.1f (back part R%.2f), height %.3f, front hole R %.2f, ring bore R %.2f on hub R %.2f..%.2f, lip R %.2f, cap R %.2f' % (
        2 * rr, r_back, z_top - z_ring_bot, r_hole, E['ring_bore_r'], hub_in, hub_out, E['ring_lip_r'], E['cap_r']))
    print('back-plate screws at ' + ', '.join('(%.2f, %.2f)' % p_ for p_ in bp_all) + '; plate bosses at ' + ', '.join('(%.2f, %.2f)' % p_ for p_ in rp_c))
    print('roller at (%.2f, %.2f): magnet %.2f..%.2f, AS5600 top %.3f, air gap %.3f; tire %.2f..%.2f vs ring back part top %.3f; hub bottom to plate %.3f' % (
        rc[0], rc[1], E['mag_z_top'], z_mag_bot, z_chip_top, z_mag_bot - z_chip_top, E['tire_z'][0], E['tire_z'][1], z_back_top,
        E['hub_z'][1] - z_plate_top))
    app.activeViewport.fit()
