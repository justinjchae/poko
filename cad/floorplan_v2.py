"""v2 enclosure 2D floorplan (front view). Rebuilds the FP_* sketches in the active Fusion design.

Frame: origin = display centre, X right, Y toward the half-circle (top) end, Z toward the viewer (front),
all mm (Fusion API wants cm, converted in cm()). Outline matches Enclosure V1B: R30 on the two top
corners and the bottom-right corner, R3 on the bottom-left corner, 60 x 90.

Edit the P dict and rerun. Nothing here is a Fusion user parameter, so editing a sketch by
hand will be overwritten by the next run. enclosure_v2_inset.py imports geom/solve/draw helpers from here.

Sources: display numbers from cad/display_LH128R-IF138H.py (Shineworld spec V1.0, page 6). The spec (note 9) proposes
a window 0.6 mm wider than the active area, so the front-plate opening is active_d + 0.6.
ESTIMATED (not dimensioned on the drawing): tab trapezoid, FPC head length 5.5.
ASSUMED (Justin to confirm): ring_rim, ring_gap, ring_part_gap, ring_part_clr, usb_hc, xiao_tip_inset.
DRIVING inputs: outline, display position, XIAO position (xiao_cx, xiao_tip_inset).
DRIVEN outputs: ring OD (largest circle that clears the outline, glass and every part the ring may not cover)
and ring depth (stack height to the tallest XIAO part the ring does cover, minus clearance).
"""
import adsk.core, adsk.fusion, math

P = dict(
    body_w=60.0, body_h=90.0, corner_big=30.0, corner_small=3.0,
    disp_top=30.0,                      # display centre to the top edge
    glass_d=35.6, active_d=32.4,
    window_extra=0.6,                   # front-plate opening = active_d + this (datasheet note 9)
    fpc_dir=1,                          # +1 = FPC leaves toward the top (+Y), -1 = toward the chin (-Y)
    tab_root_y=15.0, tab_root_half=7.5, tab_edge_half=6.4, tab_edge_y=19.94,
    head_half=5.0, head_len=5.5,                                              # head length ESTIMATED
    ring_rim=2.5,                       # ring OD to outline (housing wall) ASSUMED
    ring_gap=2.0,                       # ring OD to glass / FPC head ASSUMED
    ring_cx=0.0,
    ring_cy=None,                       # None = centred between the opening edge and the bottom edge
    usb_w=8.94,                         # XIAO USB-C shell width; the opening is not sized yet
    xiao_w=17.78, xiao_l=20.955, xiao_usb_over=1.527,   # Seeed STEP/DXF (xiao-reference-model.md); USB-C overhang past the PCB
    xiao_usb_len=7.30,                  # USB-C shell length from its tip
    xiao_cx=None,                       # XIAO centre X; None = middle of the bottom flat. The port follows it
    xiao_tip_inset=1.0,                 # USB-C tip to the outline, ASSUMED (about one wall)
    ring_covers=('shield', 'antenna', 'mic', 'reset'),   # parts the ring may sit over (USB-C is not one)
    ring_part_gap=2.0,                  # ring OD to a part it may not cover (housing wall), ASSUMED
    ring_part_clr=0.2,                  # ring underside to the tallest part it covers, ASSUMED
    front_t=1.0, stack_T=8.0, back_plate=1.0,   # front plate; total thickness; back plate (inset)
    usb_hc=1.605,                       # USB-C centreline above the PCB top (tolerance-stack.md), unchecked
    back_fillet=2.5,
)


def cm(v):
    return v / 10.0


def pt(x, y, z=0.0):
    return adsk.core.Point3D.create(cm(x), cm(y), cm(z))


def geom(P):
    w, h, Rb, Rs, top = P['body_w'], P['body_h'], P['corner_big'], P['corner_small'], P['disp_top']
    bot = top - h
    xl, xr = -w / 2, w / 2
    return dict(w=w, h=h, Rb=Rb, Rs=Rs, top=top, bot=bot, xl=xl, xr=xr,
                cTL=(xl + Rb, top - Rb), cTR=(xr - Rb, top - Rb), cBR=(xr - Rb, bot + Rb), cBL=(xl + Rs, bot + Rs))


# ---- sketch drawing helpers (all take a sketch; mm in, cm out) ----
def line(sk, a, b, constr=False):
    if math.hypot(a[0] - b[0], a[1] - b[1]) < 1e-6:
        return
    l = sk.sketchCurves.sketchLines.addByTwoPoints(pt(*a), pt(*b))
    l.isConstruction = constr


def arc(sk, c, r, a0, a1, constr=False):
    if r <= 1e-6:
        return
    am = math.radians((a0 + a1) / 2)
    p = lambda a: (c[0] + r * math.cos(math.radians(a)), c[1] + r * math.sin(math.radians(a)))
    e = sk.sketchCurves.sketchArcs.addByThreePoints(pt(*p(a0)), pt(c[0] + r * math.cos(am), c[1] + r * math.sin(am)), pt(*p(a1)))
    e.isConstruction = constr


def circle(sk, c, r, constr=False):
    e = sk.sketchCurves.sketchCircles.addByCenterRadius(pt(*c), cm(r))
    e.isConstruction = constr
    return e


def draw_outline(sk, g, inset, constr=False, notch=None, rmin=0.0, ycut=None, notch_r=0.0):
    """Outline offset inward by `inset`. notch = (x0, x1, ytop) carves a rectangle out of the bottom edge.
    rmin = smallest bottom-left corner radius (the offset of the small corner would otherwise go below it).
    notch_r rounds the two top corners of the notch (the board's inside corners, where stress concentrates)."""
    rb = g['Rb'] - inset
    rs = max(g['Rs'] - inset, rmin)
    cTL, cTR, cBR = g['cTL'], g['cTR'], g['cBR']
    top, bot, xl, xr = g['top'], g['bot'], g['xl'], g['xr']
    cBL = (xl + inset + rs, bot + inset + rs)
    if ycut is not None:
        line(sk, (xl + inset, ycut), (xr - inset, ycut), constr)               # flat cut instead of the half circle
        line(sk, (xr - inset, ycut), (xr - inset, cBR[1]), constr)
    elif abs(cTL[0] - cTR[0]) < 1e-6:
        arc(sk, cTL, rb, 0, 180, constr)          # the top is one half circle
        line(sk, (xr - inset, cTR[1]), (xr - inset, cBR[1]), constr)
    else:
        arc(sk, cTL, rb, 90, 180, constr)
        arc(sk, cTR, rb, 0, 90, constr)
        line(sk, (cTL[0], top - inset), (cTR[0], top - inset), constr)
        line(sk, (xr - inset, cTR[1]), (xr - inset, cBR[1]), constr)
    arc(sk, cBR, rb, -90, 0, constr)
    yb = bot + inset
    if notch is None:
        line(sk, (cBR[0], yb), (cBL[0], yb), constr)
    else:
        n0, n1, nt = notch
        line(sk, (cBR[0], yb), (n1, yb), constr)
        r = notch_r
        line(sk, (n1, yb), (n1, nt - r), constr)
        arc(sk, (n1 - r, nt - r), r, 0, 90, constr)
        line(sk, (n1 - r, nt), (n0 + r, nt), constr)
        arc(sk, (n0 + r, nt - r), r, 90, 180, constr)
        line(sk, (n0, nt - r), (n0, yb), constr)
        line(sk, (n0, yb), (cBL[0], yb), constr)
    arc(sk, cBL, rs, 180, 270, constr)
    line(sk, (xl + inset, cBL[1]), (xl + inset, ycut if ycut is not None else cTL[1]), constr)


def text(sk, s, x, y, ht=1.2, width=40.0, rows=1):
    inp = sk.sketchTexts.createInput2(s, cm(ht))
    inp.setAsMultiLine(pt(x, y), pt(x + width, y - ht * 1.5 * rows),
                       adsk.core.HorizontalAlignments.LeftHorizontalAlignment,
                       adsk.core.VerticalAlignments.TopVerticalAlignment, 0)
    sk.sketchTexts.add(inp)


# ---- pure geometry ----
def seg_d(q, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0 if L2 < 1e-12 else max(0, min(1, ((q[0] - a[0]) * dx + (q[1] - a[1]) * dy) / L2))
    return math.hypot(q[0] - (a[0] + t * dx), q[1] - (a[1] + t * dy))


def arc_d(q, c_, r, a0, a1):
    ang = math.degrees(math.atan2(q[1] - c_[1], q[0] - c_[0]))
    if (ang - a0) % 360 <= (a1 - a0) % 360:
        return abs(r - math.hypot(q[0] - c_[0], q[1] - c_[1]))
    ends = [(c_[0] + r * math.cos(math.radians(a)), c_[1] + r * math.sin(math.radians(a))) for a in (a0, a1)]
    return min(math.hypot(q[0] - e[0], q[1] - e[1]) for e in ends)


def solve(P):
    """Driven numbers: XIAO placement, ring centre / OD / depth, stack Z levels. Everything in mm."""
    g = geom(P)
    S = dict(g=g)
    top, bot, xl, xr = g['top'], g['bot'], g['xl'], g['xr']
    cTL, cTR, cBR, cBL, Rb, Rs = g['cTL'], g['cTR'], g['cBR'], g['cBL'], g['Rb'], g['Rs']
    gr, ar = P['glass_d'] / 2, P['active_d'] / 2
    orad = (P['active_d'] + P['window_extra']) / 2
    S.update(gr=gr, ar=ar, orad=orad)

    pcx = P['xiao_cx'] if P['xiao_cx'] is not None else (cBL[0] + cBR[0]) / 2
    xw, xl_, ov = P['xiao_w'], P['xiao_l'], P['xiao_usb_over']
    y_tip = bot + P['xiao_tip_inset']
    y0 = y_tip + ov
    ox = pcx - xw / 2
    parts = [('USB-C', 4.428, 13.368, -ov, P['xiao_usb_len'] - ov, 3.21),   # shell Y -1.527..5.773 in the XIAO frame
             ('shield', 2.59, 15.19, 6.935, 17.535, 2.00), ('mic', 2.55, 6.05, 18.08, 20.73, 0.94),
             ('reset', 13.81, 15.41, 0.33, 3.42, 0.73), ('antenna', 9.10, 12.30, 19.08, 20.68, 0.50)]
    S.update(pcx=pcx, y_tip=y_tip, y0=y0, ox=ox, parts=parts)

    def rect_dist(c_, r):
        x0_, x1_, ya, yb = ox + r[1], ox + r[2], y0 + r[3], y0 + r[4]
        return math.hypot(c_[0] - min(max(c_[0], x0_), x1_), c_[1] - min(max(c_[1], ya), yb))

    def d_outline(q):
        return min(arc_d(q, cTL, Rb, 90, 180), arc_d(q, cTR, Rb, 0, 90), seg_d(q, (cTL[0], top), (cTR[0], top)),
                   seg_d(q, (xr, cTR[1]), (xr, cBR[1])), arc_d(q, cBR, Rb, -90, 0),
                   seg_d(q, (cBR[0], bot), (cBL[0], bot)), arc_d(q, cBL, Rs, 180, 270),
                   seg_d(q, (xl, cBL[1]), (xl, cTL[1])))

    cy = P['ring_cy'] if P['ring_cy'] is not None else (bot - orad) / 2
    c = (P['ring_cx'], cy)
    limits = {'outline': d_outline(c) - P['ring_rim'], 'glass': math.hypot(*c) - gr - P['ring_gap']}
    for r in parts:
        if r[0] not in P['ring_covers']:
            limits[r[0]] = rect_dist(c, r) - P['ring_part_gap']
    bind = min(limits, key=limits.get)
    rr = math.floor(limits[bind] * 2 * 10) / 20.0      # radius for an OD rounded down to 0.1
    covered = [r for r in parts if r[0] in P['ring_covers'] and rect_dist(c, r) < rr]
    # Z levels (A = back face of the front plate at Z=0, front surface at +front_t, back face at front_t - stack_T)
    z_front = P['front_t']
    z_back = P['front_t'] - P['stack_T']
    z_port = (z_front + z_back) / 2
    z_pcb_top = z_port - P['usb_hc']
    pcb_top_from_front = z_front - z_pcb_top
    depth = pcb_top_from_front - max(r[5] for r in covered) - P['ring_part_clr'] if covered else None
    dname = max(covered, key=lambda r: r[5])[0] if covered else 'nothing'
    S.update(c=c, cy=cy, rr=rr, od=2 * rr, bind=bind, limits=limits, covered=covered, depth=depth, dname=dname,
             z_front=z_front, z_back=z_back, z_port=z_port, z_pcb_top=z_pcb_top, pcb_top_from_front=pcb_top_from_front,
             rect_dist=rect_dist, d_outline=d_outline)
    return S


def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    for i in range(root.sketches.count - 1, -1, -1):
        if root.sketches.item(i).name.startswith('FP_'):
            root.sketches.item(i).deleteMe()

    S = solve(P)
    g = S['g']
    w, h, Rb, Rs, top, bot, xl, xr = g['w'], g['h'], g['Rb'], g['Rs'], g['top'], g['bot'], g['xl'], g['xr']
    gr, ar, orad = S['gr'], S['ar'], S['orad']
    pcx, y0, ox, parts, c, rr, od = S['pcx'], S['y0'], S['ox'], S['parts'], S['c'], S['rr'], S['od']
    cy, bind, depth, dname = S['cy'], S['bind'], S['depth'], S['dname']
    hw = P['usb_w'] / 2
    xw, xl_ = P['xiao_w'], P['xiao_l']

    def new_sketch(name):
        sk = root.sketches.add(root.xYConstructionPlane)
        sk.name = name
        return sk

    # 1. outline and back flat
    sk = new_sketch('FP_01_Outline')
    draw_outline(sk, g, 0, False)
    draw_outline(sk, g, P['back_fillet'], True)

    # 2. display, FPC exit and keep-outs
    sk = new_sketch('FP_02_Display')
    circle(sk, (0, 0), gr)
    circle(sk, (0, 0), ar)
    circle(sk, (0, 0), orad)
    circle(sk, (0, 0), gr + P['ring_gap'], True)
    sg = P['fpc_dir']
    ty = P['tab_edge_y']
    head_end = sg * (ty + P['head_len'])
    poly = [(-P['tab_root_half'], sg * P['tab_root_y']), (-P['tab_edge_half'], sg * ty), (-P['head_half'], sg * ty),
            (-P['head_half'], head_end), (P['head_half'], head_end), (P['head_half'], sg * ty),
            (P['tab_edge_half'], sg * ty), (P['tab_root_half'], sg * P['tab_root_y'])]
    for i in range(len(poly) - 1):
        line(sk, poly[i], poly[i + 1])
    line(sk, poly[-1], poly[0])
    limit_y = head_end - P['ring_gap'] if sg < 0 else -(gr + P['ring_gap'])
    line(sk, (-12, limit_y), (12, limit_y), True)
    text(sk, 'Display glass D%.1f' % P['glass_d'], -7, 6.0, 1.2, 16)
    text(sk, 'active D%.1f, opening D%.1f' % (P['active_d'], 2 * orad), -9, 3.0, 1.2, 20)
    text(sk, 'FPC tab + head (head est.)', 8.5, sg * 19.0 + (1.0 if sg > 0 else 0), 1.0, 22)
    text(sk, 'ring top limit %.2f' % limit_y, 12.5, limit_y + 0.6, 1.0, 22)
    text(sk, 'glass + gap', -24.0, 16.0, 1.0, 14)

    # 3. ring: centred between the opening edge and the bottom edge, OD and depth DRIVEN
    sk = new_sketch('FP_03_Ring')
    gap_top = -orad - (cy + rr)
    gap_bot = (cy - rr) - bot
    print('ring OD %.1f limited by %s; limits %s' % (od, bind, {k: round(2 * v, 2) for k, v in S['limits'].items()}))
    print('ring depth %s (XIAO top %.3f from front, covers %s, tallest %s)' % (
        'free' if depth is None else '%.2f' % depth, S['pcb_top_from_front'], [r[0] for r in S['covered']], dname))
    line(sk, (c[0], -orad), (c[0], cy + rr), True)
    line(sk, (c[0], cy - rr), (c[0], bot), True)
    text(sk, 'gap %.1f' % gap_top, c[0] + 1.0, (-orad + cy + rr) / 2 + 0.6, 1.2, 10)
    text(sk, 'gap %.1f' % gap_bot, c[0] + 1.0, (cy - rr + bot) / 2 + 0.6, 1.2, 10)
    circle(sk, c, rr)
    line(sk, (c[0] - 2, c[1]), (c[0] + 2, c[1]), True)
    line(sk, (c[0], c[1] - 2), (c[0], c[1] + 2), True)
    if abs(P['ring_rim'] - P['back_fillet']) > 1e-6:
        draw_outline(sk, g, P['ring_rim'], True)
    text(sk, 'ring OD %.1f' % od, c[0] - 5, c[1] + 1.2, 1.4, 14)
    text(sk, 'driven by %s' % bind, c[0] - 5, c[1] - 1.0, 1.0, 14)

    # 4. USB-C port on the flat and notes
    sk = new_sketch('FP_04_Port_Notes')
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt(pcx - hw, bot), pt(pcx + hw, bot + 1.2))
    text(sk, 'USB-C port, centred on the XIAO x=%.1f (shell %.2f)' % (pcx, P['usb_w']), xl, bot - 1.5, 1.0, 40)
    text(sk, 'FLOORPLAN V2 front view, mm. %.0f x %.0f, R%.0f x3, R%.0f BL (as V1B)' % (w, h, Rb, Rs),
         xr + 4, top, 1.4, 70)
    hits = [(r[0], r[5]) for r in parts if S['rect_dist'](c, r) < rr]
    notes = ['INPUTS: XIAO centre x %.1f, USB-C tip %.1f inside the bottom edge; display at origin' % (pcx, P['xiao_tip_inset']),
             'DRIVEN: ring OD %.1f (limited by %s), %.1f to opening edge and %.1f to bottom edge' % (od, bind, gap_top, gap_bot),
             'DRIVEN: ring depth %s' % ('free' if depth is None else '%.2f from the front face (tallest covered part: %s, +%.2f clr)' % (depth, dname, P['ring_part_clr'])),
             'ring may not cover: ' + ', '.join(r[0] for r in parts if r[0] not in P['ring_covers']) + ' (gap %.1f)' % P['ring_part_gap'],
             'limits: rim %.1f to outline, gap %.1f to glass; FPC exits %s, head %.1f (est.)' % (P['ring_rim'], P['ring_gap'], 'top' if sg > 0 else 'bottom', P['head_len']),
             'XIAO top face is %.3f from the front (USB-C centreline %.3f above it)' % (S['pcb_top_from_front'], P['usb_hc']),
             'above its top face: USB-C 3.21, shield 2.00, mic 0.94, reset 0.73, antenna 0.50',
             'inside the ring circle: ' + (', '.join('%s +%.2f' % h_ for h_ in hits) if hits else 'none'),
             'dashed inner outline = back flat (R%.1f back fillet) and ring rim limit' % P['back_fillet'],
             'cell, sensor/roller not drawn']
    for i, s_ in enumerate(notes):
        text(sk, s_, xr + 4, top - 4.5 - i * 2.6, 1.2, 70)

    # 5. XIAO nRF52840 Sense outline: USB-C toward the bottom, centred on the port
    sk = new_sketch('FP_05_XIAO')
    sk.sketchCurves.sketchLines.addTwoPointRectangle(pt(ox, y0), pt(ox + xw, y0 + xl_))
    for r in parts:
        sk.sketchCurves.sketchLines.addTwoPointRectangle(pt(ox + r[1], y0 + r[3]), pt(ox + r[2], y0 + r[4]))
        if r[0] in ('shield', 'USB-C'):
            text(sk, '%s +%.2f' % (r[0], r[5]), ox + r[1] + 1.0, y0 + r[4] - 1.0, 1.0, 10)
    text(sk, 'XIAO %.2f x %.3f' % (xw, xl_), ox, y0 + xl_ + 3.0, 1.0, 30)
    text(sk, 'antenna end: keep metal off', ox, y0 + xl_ + 1.2, 1.0, 30)

    app.activeViewport.fit()
