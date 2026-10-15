"""Exploded copy of the ring rig (ring_rig.py), placed beside the assembled rig. Run it AFTER ring_rig.py in the same design.

Adds occurrences tagged with attribute ring/exp (new instances of the RIG2_* components, so geometry stays linked) at x = X0, spread along Z in assembly order
(top = user side): cover, disc, magnet, plate (+ rib tape and tape dots lifted above it), then spacers, breakout, base group.
Deletes its own earlier copies first (attribute ring/exp, or anything sitting at X0); ring_rig.py deletes them too when it rebuilds (rerun this afterwards). Offsets are in mm.
"""
import adsk.core, adsk.fusion

AS5600_ID = 'urn:adsk.wipprod:dm.lineage:td3I6-p2Qy2UHJECxqpHuQ'
X0 = -95.0                                   # exploded view centre X (assembled rig is centred at 0)
BOARD, BOARD_TOP = 23.0, -4.605              # breakout size, board top at the nominal 1.0 spacer stack
DZ = dict(Cover=0.0, Disc=-6.0, Magnet=-13.0, Tape_flange=-3.0, Plate=-26.0, Tape_rib=-22.0, Tape_dots=-22.0,
          Spacer_0_8=-38.0, Spacer_0_2=-44.0, Breakout=-32.0, Base=-50.0, Rail_L=-50.0, Rail_R=-50.0)


def cm(v):
    return v / 10.0


def run(_context: str):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    root = design.rootComponent
    def is_exp(o):                                   # Occurrence.name is read-only: tag with an attribute (and catch strays by position)
        return o.attributes.itemByName('ring', 'exp') is not None or abs(o.transform.translation.x - cm(X0)) < 1e-6 and o.transform.translation.z != 0 or \
            abs(o.transform.translation.x - cm(X0)) < 1e-6 and o.component.name.startswith('RIG2_Cover')

    for i in range(root.occurrences.count - 1, -1, -1):
        if is_exp(root.occurrences.item(i)):
            root.occurrences.item(i).deleteMe()

    comps = {}
    for o in root.occurrences:
        comps.setdefault(o.component.name, o.component)
    n_exp = [0]

    def place(cname, dz, tag, show_only=None):
        m = adsk.core.Matrix3D.create()
        m.translation = adsk.core.Vector3D.create(cm(X0), 0, cm(dz))
        occ = root.occurrences.addExistingComponent(comps['RIG2_' + cname], m)
        occ.attributes.add('ring', 'exp', tag)
        n_exp[0] += 1
        if show_only is not None:
            for b in occ.bRepBodies:
                b.isLightBulbOn = b.name in show_only
        return occ

    place('Cover', DZ['Cover'], 'Cover')
    place('Disc', DZ['Disc'], 'Disc')
    place('Magnet', DZ['Magnet'], 'Magnet')
    place('Plate', DZ['Plate'], 'Plate')
    place('Tape', DZ['Tape_rib'], 'RibTape', ('RibTape',))
    place('Tape', DZ['Tape_dots'], 'DotTape', ('DotTape1', 'DotTape2', 'DotTape3'))
    place('Spacer_0.8', DZ['Spacer_0_8'], 'Spacer_0.8')
    place('Spacer_0.2', DZ['Spacer_0_2'], 'Spacer_0.2')
    place('Base', DZ['Base'], 'Base')
    place('Rail_L', DZ['Rail_L'], 'Rail_L')
    place('Rail_R', DZ['Rail_R'], 'Rail_R')
    m = adsk.core.Matrix3D.create()
    m.translation = adsk.core.Vector3D.create(cm(X0 - BOARD / 2), cm(-BOARD / 2), cm(BOARD_TOP + DZ['Breakout']))
    occ = root.occurrences.addByInsert(app.data.findFileById(AS5600_ID), m, True)
    occ.attributes.add('ring', 'exp', 'AS5600')
    n_exp[0] += 1
    for b in occ.bRepBodies:
        if b.name == 'Magnet_ref':
            b.isLightBulbOn = False
    print('exploded copy added at X %.0f: %d EXP_ occurrences' % (X0, n_exp[0]))
    app.activeViewport.fit()
