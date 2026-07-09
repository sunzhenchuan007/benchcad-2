"""eye_bolt — the parametric part.

DIN 580 lifting eye bolt: a threaded shank, a cylindrical collar, and a forged
circular lifting eye (a torus loop) integral on top. The shank carries a
modelled external metric thread (ISO 261 coarse pitch helical V-groove). The eye,
collar and thread are one connected solid.

Proportions (DIN 580 style, relative to the nominal thread Ø d):
    collar Ø = 2 d,  collar height = 0.8 d
    eye ring centreline radius = 1.15 d,  eye ring wire radius = 0.55 d
"""

import math

import cadquery as cq

# ISO 261 coarse pitch by nominal thread diameter, mm
_PITCH = {6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 16: 2.0, 20: 2.5, 24: 3.0}


def build(thread_d, length):
    d, l = thread_d, length
    pitch = _PITCH[int(round(d))]
    col_d = 2.0 * d
    col_h = 0.8 * d
    eye_r = 1.15 * d          # eye ring centreline radius
    eye_w = 0.55 * d          # eye ring wire radius

    shank = cq.Workplane("XY").circle(d / 2.0).extrude(l)
    collar = cq.Workplane("XY").workplane(offset=l).circle(col_d / 2.0).extrude(col_h)
    # the lifting eye: a torus in the vertical (XZ) plane sitting on the collar,
    # overlapping it slightly so the union is one solid
    zc = l + col_h + eye_r - 0.6 * eye_w
    eye = cq.Solid.makeTorus(eye_r, eye_w, cq.Vector(0, 0, zc), cq.Vector(0, 1, 0))
    result = shank.union(collar).union(cq.Workplane("XY").newObject([eye]))

    # external metric thread on the shank: helical V-groove, crests at the major Ø
    r_maj = d / 2.0
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, l, r_maj))
    groove = (
        cq.Workplane("XZ").center(r_maj + 0.3, 0)
        .moveTo(0, -pitch / 2.0).lineTo(-(0.6134 * pitch + 0.3), 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=True)
    )
    result = result.cut(groove)

    return result
