"""lifting_eye_bolt — the parametric part.

DIN 580 lifting eye bolt: a threaded shank, a collar, and a forged circular
lifting eye (a torus) integral on top, as one connected solid. The eye inner /
outer diameters (DIN 580 d2 / d3) and the thread length (l) are the tabulated
values for the nominal thread size; the shank carries a modelled external metric
thread — a real single-start helical V-groove of the ISO 261 coarse pitch swept
and cut into the shank, flush at both ends.

    eye centreline radius R = (eye_id + eye_od)/4 ;  wire radius = (eye_od - eye_id)/4
"""

import cadquery as cq

_PITCH = {8: 1.25, 10: 1.5, 12: 1.75, 16: 2.0, 20: 2.5, 24: 3.0}


def build(thread_d, eye_id, eye_od, thread_len):
    d, l = thread_d, thread_len
    pitch = _PITCH[int(round(d))]
    col_d = 1.7 * d
    col_h = 0.8 * d
    R = (eye_id + eye_od) / 4.0
    rw = (eye_od - eye_id) / 4.0
    r_maj = d / 2.0

    # threaded shank: a plain cylinder with a helical V-groove of the coarse pitch
    # cut into it (real single-start helix; isFrenet=False keeps the sweep stable),
    # swept a half-pitch past each end and cut flush by the shank
    shank = cq.Workplane("XY").circle(r_maj).extrude(l)
    fb = max(0.6, 0.12 * d)                  # smooth, rounded tip stub at the bottom
    shank = shank.faces("<Z").fillet(0.45 * fb)
    oc = 0.25 * pitch
    th = l - fb                              # thread above the rounded tip
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, th + pitch, r_maj))
    groove = (
        cq.Workplane("XZ").center(r_maj + oc, 0)
        .moveTo(0, -pitch / 2.0).lineTo(-(0.6134 * pitch + oc), 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=False).translate((0, 0, fb - 0.5 * pitch))
    )
    shank = shank.cut(groove)

    collar = cq.Workplane("XY").workplane(offset=l).circle(col_d / 2.0).extrude(col_h)

    # eye-to-collar transition: a cylindrical neck, then a loft flaring up to the
    # eye base (the benchcad 1.0 form) so the ring joins the collar smoothly
    z0 = l + col_h
    neck_h, loft_h = 0.45 * d, 0.55 * d
    neck_d, eye_neck_d = 1.3 * d, max(2.0 * rw, 0.85 * d)
    neck = cq.Workplane("XY").workplane(offset=z0).circle(neck_d / 2.0).extrude(neck_h)
    trans = (cq.Workplane("XY").workplane(offset=z0 + neck_h).circle(neck_d / 2.0)
             .workplane(offset=loft_h).circle(eye_neck_d / 2.0).loft())
    zc = z0 + neck_h + loft_h + R + rw - 0.35 * rw
    eye = cq.Solid.makeTorus(R, rw, cq.Vector(0, 0, zc), cq.Vector(0, 1, 0))
    result = (shank.union(collar).union(neck).union(trans)
              .union(cq.Workplane("XY").newObject([eye])))
    return result
