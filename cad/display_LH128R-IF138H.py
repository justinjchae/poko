"""Shineworld LH128R-IF138H 1.28in round TFT (GC9A01, 16-pin 0.5 mm FPC), unfolded.

Source: Shineworld spec V1.0 2026-03-27, page 6 (drawing sheet is labelled IF130H,
the module cover and the order say IF138H). All dimensions mm, Fusion API wants cm.

Frame: origin = active-area centre, X toward the FPC, Z up from the back of the glass to
the front (viewing) face. Front view of the drawing is looking down -Z.

Read straight off the drawing: 35.60 LCM dia, 35.2 LCD, 34.32 POL, 32.40 active area,
37.74 LCM length (includes the bonding tab), 1.55 thick, FPC 58.80 from the glass edge,
FPC head 10.0 wide, neck 5.0, tip 8.5, tip stiffener 4.0 long, FPC+PI 0.30 total, pads P0.5
x 16 (7.50 span), 0.30 wide.
ESTIMATED from scaling the drawing (not dimensioned): bonding-tab shape, FPC head length 5.5,
neck length, taper length, FPC body thickness 0.10, pad length 3.0 and pad thickness.
UNKNOWN: which end is pin 1, glass layer split (LCD vs backlight), FPC fold (not modelled).
"""
import adsk.core, adsk.fusion, math

P = dict(
    D_LCM=35.60, D_ACTIVE=32.40, T_PANEL=1.55, T_ACTIVE=0.05,
    L_LCM=37.74,                       # from the -X glass edge to the +X bonding edge
    TAB_HALF_ROOT=7.5, TAB_HALF_EDGE=6.4, TAB_ROOT_X=15.0,   # estimated trapezoid
    FPC_LEN=58.80,                     # glass bonding edge to FPC tip
    HEAD_W=10.00, HEAD_L=5.5, NECK_W=5.00, NECK_END=47.0, TAPER_L=5.3, TIP_W=8.50,
    T_FPC=0.10, T_FPC_TOTAL=0.30, STIFF_L=4.00,
    PINS=16, PITCH=0.50, PAD_W=0.30, PAD_L=3.00, PAD_T=0.02,
    NAME='Display_LH128R-IF138H',
)


def paint(design):
    """Appearances: copies of Fusion library entries, tinted where an rgb is given."""
    app = adsk.core.Application.get()
    lib = app.materialLibraries.itemByName('Fusion Appearance Library')

    def apply(body, base, name, rgb=None):
        ap = design.appearances.itemByName(name)
        if not ap:
            ap = design.appearances.addByCopy(lib.appearances.itemByName(base), name)
            if rgb:
                prop = adsk.core.ColorProperty.cast(ap.appearanceProperties.itemById('opaque_albedo'))
                prop.value = adsk.core.Color.create(rgb[0], rgb[1], rgb[2], 255)
        body.appearance = ap

    for b in design.rootComponent.bRepBodies:
        if b.name == 'panel_LCM':
            apply(b, 'Plastic - Matte (Black)', 'disp_glass_black', (27, 29, 33))
        elif b.name.startswith('active_area'):
            apply(b, 'Paint - Enamel Glossy (Black)', 'disp_active_navy', (8, 14, 28))
        elif b.name == 'fpc':
            apply(b, 'Plastic - Glossy (Yellow)', 'fpc_amber', (217, 138, 28))
        elif b.name == 'fpc_stiffener':
            apply(b, 'Plastic - Glossy (Yellow)', 'fpc_stiffener_brown', (140, 90, 20))
        elif b.name.startswith('pad_'):
            apply(b, 'Gold - Polished', 'pad_gold')


def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if design.rootComponent.bRepBodies.count or design.rootComponent.sketches.count:
        app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    cm = lambda v: v / 10.0

    def sketch_at(z):
        if z == 0:
            return root.sketches.add(root.xYConstructionPlane)
        pl = root.constructionPlanes.createInput()
        pl.setByOffset(root.xYConstructionPlane, adsk.core.ValueInput.createByReal(cm(z)))
        return root.sketches.add(root.constructionPlanes.add(pl))

    def poly(sk, pts):
        lines = sk.sketchCurves.sketchLines
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            lines.addByTwoPoints(adsk.core.Point3D.create(cm(a[0]), cm(a[1]), 0),
                                 adsk.core.Point3D.create(cm(b[0]), cm(b[1]), 0))

    def extrude(sk, h, op, name, target=None):
        profs = adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count):
            profs.add(sk.profiles.item(i))
        inp = root.features.extrudeFeatures.createInput(profs, op)
        inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(h)))
        if target:
            inp.participantBodies = [target]
        f = root.features.extrudeFeatures.add(inp)
        if name:
            f.bodies.item(0).name = name
        return f

    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation
    JOIN = adsk.fusion.FeatureOperations.JoinFeatureOperation
    c0 = adsk.core.Point3D.create(0, 0, 0)

    # glass + backlight stack as one body, with the bonding tab joined on
    s = sketch_at(0)
    s.sketchCurves.sketchCircles.addByCenterRadius(c0, cm(P['D_LCM'] / 2))
    panel = extrude(s, P['T_PANEL'], NEW, 'panel_LCM').bodies.item(0)
    x_edge = P['L_LCM'] - P['D_LCM'] / 2
    s = sketch_at(0)
    poly(s, [(P['TAB_ROOT_X'], -P['TAB_HALF_ROOT']), (x_edge, -P['TAB_HALF_EDGE']),
             (x_edge, P['TAB_HALF_EDGE']), (P['TAB_ROOT_X'], P['TAB_HALF_ROOT'])])
    extrude(s, P['T_PANEL'], JOIN, None, panel)

    # active area marker, flush with the front face (separate body, overlaps the panel)
    s = sketch_at(P['T_PANEL'] - P['T_ACTIVE'])
    s.sketchCurves.sketchCircles.addByCenterRadius(c0, cm(P['D_ACTIVE'] / 2))
    extrude(s, P['T_ACTIVE'], NEW, 'active_area_D32.4')

    # FPC, flat, in the back plane (z 0 to T_FPC), leaving the +X edge of the tab
    x0 = x_edge
    x_tip = x0 + P['FPC_LEN']
    x_neck_end = x0 + P['NECK_END']
    x_tip_w = x_neck_end + P['TAPER_L']
    hw, nw, tw = P['HEAD_W'] / 2, P['NECK_W'] / 2, P['TIP_W'] / 2
    outline = [(x0, -hw), (x0 + P['HEAD_L'], -hw), (x0 + P['HEAD_L'], -nw), (x_neck_end, -nw),
               (x_tip_w, -tw), (x_tip, -tw), (x_tip, tw), (x_tip_w, tw), (x_neck_end, nw),
               (x0 + P['HEAD_L'], nw), (x0 + P['HEAD_L'], hw), (x0, hw)]
    s = sketch_at(0)
    poly(s, outline)
    extrude(s, P['T_FPC'], NEW, 'fpc')

    # tip stiffener on the front side so FPC + PI = 0.30 total
    s = sketch_at(P['T_FPC'])
    poly(s, [(x_tip - P['STIFF_L'], -tw), (x_tip, -tw), (x_tip, tw), (x_tip - P['STIFF_L'], tw)])
    extrude(s, P['T_FPC_TOTAL'] - P['T_FPC'], NEW, 'fpc_stiffener')

    # 16 gold pads on the back face (z -PAD_T to 0), P0.5, centred on the FPC
    s = sketch_at(-P['PAD_T'])
    span = (P['PINS'] - 1) * P['PITCH']
    for i in range(P['PINS']):
        y = -span / 2 + i * P['PITCH']
        s.sketchCurves.sketchLines.addTwoPointRectangle(
            adsk.core.Point3D.create(cm(x_tip - P['PAD_L']), cm(y - P['PAD_W'] / 2), 0),
            adsk.core.Point3D.create(cm(x_tip), cm(y + P['PAD_W'] / 2), 0))
    f = extrude(s, P['PAD_T'], NEW, None)
    pads = sorted((f.bodies.item(i) for i in range(f.bodies.count)),
                  key=lambda b: b.boundingBox.minPoint.y)
    for i, b in enumerate(pads):
        b.name = 'pad_%02d' % (i + 1)   # numbered along +Y from -Y; real pin 1 end unknown

    paint(design)
    app.activeViewport.fit()
    for b in root.bRepBodies:
        bb = b.boundingBox
        print('%-18s x %7.2f..%7.2f  y %6.2f..%6.2f  z %5.2f..%5.2f' % (
            b.name, bb.minPoint.x * 10, bb.maxPoint.x * 10, bb.minPoint.y * 10,
            bb.maxPoint.y * 10, bb.minPoint.z * 10, bb.maxPoint.z * 10))
