"""Xinhailong L090835H-008678999-8160 X-axis LRA (spec LL-3-J-30510 rev A.1, page 7 outline).

All dimensions mm, Fusion API wants cm. Origin = centre of the body in plan, Z = 0 at the
bottom face, +Z up. The tail leaves the +X side. Pads-down orientation: the drawing's plan
view (pads up) rotated 180 deg about X, so the tail sits on the -Y side and the pads face -Z.

Dimensioned on the drawing: body 8 +/-0.1 (X) x 9 +/-0.1 (Y) x 3.5 +/-0.05, plan corners
R0.5, tail 3.9 +/-0.1 wide, sticks out 2.75 +/-0.1, 0.3 +/-0.07 thick, flush with the pad-side
face (here the bottom), two pads 1.7 x 1.5 with 0.3 gaps, pads start 0.75 from the body edge, 0.3 from the tip.
Tail edge sits 0.8 in from the body edge in plan (the drawing also shows 1.1 +/-0.25;
checked against the pixel scale, 0.8 fits the pad stack, so 0.8 is used).
NOT on the drawing: bottom edge radius (the side view shows a small one, not modelled), pad
thickness (0.02 assumed, standing proud of the tail, so the part spans z -0.02 to 3.5), vibration axis
marker (the "X axis" direction is an open supplier question), pad polarity.
"""
import adsk.core, adsk.fusion

P = dict(
    W=8.0, L=9.0, H=3.5, R=0.5,
    TAIL_W=3.9, TAIL_OUT=2.75, TAIL_T=0.30, TAIL_TOP_OFFSET=0.8,
    PAD_L=1.7, PAD_W=1.5, PAD_GAP=0.3, PAD_START=0.75, PAD_T=0.02,
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
        if b.name == 'motor_body':
            apply(b, 'Steel - Satin', 'lra_can_steel')
        elif b.name == 'tail_fpc':
            apply(b, 'Plastic - Glossy (Yellow)', 'fpc_amber', (217, 138, 28))
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
    pt = lambda x, y: adsk.core.Point3D.create(cm(x), cm(y), 0)
    NEW = adsk.fusion.FeatureOperations.NewBodyFeatureOperation

    def sketch_at(z):
        if z == 0:
            return root.sketches.add(root.xYConstructionPlane)
        pl = root.constructionPlanes.createInput()
        pl.setByOffset(root.xYConstructionPlane, adsk.core.ValueInput.createByReal(cm(z)))
        return root.sketches.add(root.constructionPlanes.add(pl))

    def extrude(sk, h, name):
        profs = adsk.core.ObjectCollection.create()
        for i in range(sk.profiles.count):
            profs.add(sk.profiles.item(i))
        inp = root.features.extrudeFeatures.createInput(profs, NEW)
        inp.setDistanceExtent(False, adsk.core.ValueInput.createByReal(cm(h)))
        f = root.features.extrudeFeatures.add(inp)
        if name:
            f.bodies.item(0).name = name
        return f

    # body, then R0.5 on the four vertical edges
    s = sketch_at(0)
    s.sketchCurves.sketchLines.addTwoPointRectangle(pt(-P['W'] / 2, -P['L'] / 2),
                                                    pt(P['W'] / 2, P['L'] / 2))
    body = extrude(s, P['H'], 'motor_body').bodies.item(0)
    edges = adsk.core.ObjectCollection.create()
    for e in body.edges:
        if isinstance(e.geometry, adsk.core.Line3D):
            d = e.geometry.startPoint.vectorTo(e.geometry.endPoint)
            if abs(d.x) < 1e-6 and abs(d.y) < 1e-6:
                edges.add(e)
    fi = root.features.filletFeatures.createInput()
    fi.addConstantRadiusEdgeSet(edges, adsk.core.ValueInput.createByReal(cm(P['R'])), True)
    root.features.filletFeatures.add(fi)

    # tail, flush with the bottom face (pad side)
    x0 = P['W'] / 2
    y_lo = -(P['L'] / 2 - P['TAIL_TOP_OFFSET'])
    y_hi = y_lo + P['TAIL_W']
    s = sketch_at(0)
    s.sketchCurves.sketchLines.addTwoPointRectangle(pt(x0, y_lo), pt(x0 + P['TAIL_OUT'], y_hi))
    extrude(s, P['TAIL_T'], 'tail_fpc')

    # two pads on the bottom face, tip side margin 0.3, gap 0.3, edge margin 0.3
    s = sketch_at(-P['PAD_T'])   # pads stand PAD_T proud of the tail (avoids coplanar faces)
    xp = x0 + P['PAD_START']
    y1 = y_lo + P['PAD_GAP']
    for y_a in (y1, y1 + P['PAD_W'] + P['PAD_GAP']):
        s.sketchCurves.sketchLines.addTwoPointRectangle(pt(xp, y_a),
                                                        pt(xp + P['PAD_L'], y_a + P['PAD_W']))
    f = extrude(s, P['PAD_T'], None)
    pads = sorted((f.bodies.item(i) for i in range(f.bodies.count)),
                  key=lambda b: b.boundingBox.minPoint.y)
    for i, b in enumerate(pads):
        b.name = 'pad_%d' % (i + 1)   # pad_1 is the -Y one; polarity not given

    paint(design)
    app.activeViewport.fit()
    for b in root.bRepBodies:
        bb = b.boundingBox
        print('%-12s x %6.2f..%6.2f  y %6.2f..%6.2f  z %5.2f..%5.2f' % (
            b.name, bb.minPoint.x * 10, bb.maxPoint.x * 10, bb.minPoint.y * 10,
            bb.maxPoint.y * 10, bb.minPoint.z * 10, bb.maxPoint.z * 10))
