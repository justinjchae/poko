"""Build the ring-rig print set as ONE pre-arranged 3MF for Bambu Studio (run with /usr/bin/python3, which has numpy).

Input: STLs exported from Fusion by the rig scripts (cover, disc, plate_t056/044/032, base, spacer_*). Orients each part for
support-free printing, places it on the 256x256 bed (clear of the purge corner x<18, y<28), writes Metadata/model_settings.config with a per-object
layer_height (0.12 for the fine parts, the rest follows the selected preset, 0.20). Opens nothing; the caller does `open -a BambuStudio file.3mf`.

usage: export_ring_rig_3mf.py STL_DIR OUT.3mf
"""
import sys, os, struct, zipfile
import numpy as np

# name, file stem, flip (180 deg about X: face-down parts), centre (x, y) on the bed, layer height or None
PARTS = [
    ('Cover',            'cover',      True,  (70, 90),   0.12),
    ('Disc',             'disc',       True,  (200, 90),  0.12),
    ('Plate_t0.56',      'plate_t056', False, (60, 160),  0.12),
    ('Plate_t0.44_soft', 'plate_t044', False, (110, 160), 0.12),
    ('Plate_t0.32_softest', 'plate_t032', False, (160, 160), 0.12),
    ('Base',             'base',       False, (140, 90),  None),
    ('Spacer_0.2',       'spacer_0.2', False, (60, 215),  None),
    ('Spacer_0.4',       'spacer_0.4', False, (95, 215),  None),
    ('Spacer_0.8',       'spacer_0.8', False, (130, 215), None),
    ('Spacer_1.6',       'spacer_1.6', False, (165, 215), None),
]


def read_stl(path):
    raw = open(path, 'rb').read()
    n = struct.unpack('<I', raw[80:84])[0]
    rec = np.frombuffer(raw, dtype=np.dtype([('n', '<3f4'), ('v', '<9f4'), ('a', '<u2')]), count=n, offset=84)
    return rec['v'].reshape(-1, 3).astype(np.float64)          # 3 vertices per triangle, flat


def main(stl_dir, out):
    objs = []
    for name, stem, flip, (cx, cy), lh in PARTS:
        tri = read_stl(os.path.join(stl_dir, stem + '.stl'))
        size = tri.max(0) - tri.min(0)
        if size.max() < 10:                                      # Fusion STLs can come out in cm
            tri = tri * 10.0
        if flip:
            tri = tri * np.array([1.0, -1.0, -1.0])
        lo, hi = tri.min(0), tri.max(0)
        tri = tri - np.array([(lo[0] + hi[0]) / 2 - cx, (lo[1] + hi[1]) / 2 - cy, lo[2]])
        key = np.round(tri, 4)
        uniq, inv = np.unique(key, axis=0, return_inverse=True)
        faces = inv.reshape(-1, 3)
        ok = faces[(faces[:, 0] != faces[:, 1]) & (faces[:, 1] != faces[:, 2]) & (faces[:, 0] != faces[:, 2])]
        objs.append((name, uniq, ok, lh))
        lo, hi = uniq.min(0), uniq.max(0)
        print('%-18s %6d tri  X %6.1f..%6.1f  Y %6.1f..%6.1f  Z %5.2f..%5.2f  layer %s' % (
            name, len(ok), lo[0], hi[0], lo[1], hi[1], lo[2], hi[2], lh or 'preset'))

    model = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">',
             '<metadata name="Title">ring rig</metadata>', '<resources>']
    for i, (name, v, f, lh) in enumerate(objs, 1):
        model.append('<object id="%d" name="%s" type="model"><mesh><vertices>' % (i, name))
        model.extend('<vertex x="%.5f" y="%.5f" z="%.5f"/>' % tuple(p) for p in v)
        model.append('</vertices><triangles>')
        model.extend('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t) for t in f)
        model.append('</triangles></mesh></object>')
    model.append('</resources><build>')
    model.extend('<item objectid="%d"/>' % i for i in range(1, len(objs) + 1))
    model.append('</build></model>')

    cfg = ['<?xml version="1.0" encoding="UTF-8"?>', '<config>']
    for i, (name, v, f, lh) in enumerate(objs, 1):
        cfg.append('  <object id="%d">' % i)
        cfg.append('    <metadata key="name" value="%s"/>' % name)
        cfg.append('    <metadata key="extruder" value="1"/>')
        if lh:
            cfg.append('    <metadata key="layer_height" value="%.2f"/>' % lh)
        cfg.append('  </object>')
    cfg.append('</config>')

    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
          '<Default Extension="config" ContentType="text/xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', ct)
        z.writestr('_rels/.rels', rels)
        z.writestr('3D/3dmodel.model', '\n'.join(model))
        z.writestr('Metadata/model_settings.config', '\n'.join(cfg))
    print('wrote', out, '(%d objects, %.0f kB)' % (len(objs), os.path.getsize(out) / 1024))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
