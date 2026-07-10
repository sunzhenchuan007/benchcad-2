"""lifting_eye_bolt — the parametric part.

DIN 580 lifting eye bolt: a threaded shank, a cylindrical collar, and a forged
circular lifting eye (a torus) integral on top, as one connected solid. The
transition follows the DIN 580 / BenchCAD-1.0 form — a **cylinder (collar) plus a
lofted neck**: the collar is Ø d2 (the eye inner Ø), the neck lofts from a wider
base at the collar top down to the neck width at the ring root, and the ring sits
low so its legs come down to the collar (not perched on a thin stalk). An
engineering fillet blends the collar/neck junction, and the shank tip is rounded.

The eye inner / outer diameters (DIN 580 d2 / d3) and the thread length (l) are
the tabulated values for the nominal thread size; the shank carries a modelled
external metric thread — a real single-start helical V-groove of the ISO 261
coarse pitch swept and cut into the shank, flush at both ends.

    ring centreline radius R = (eye_id + eye_od)/4 ;  wire radius = (eye_od - eye_id)/4
"""

import cadquery as cq

_PITCH = {8: 1.25, 10: 1.5, 12: 1.75, 16: 2.0, 20: 2.5, 24: 3.0}


def build(thread_d, eye_id, eye_od, thread_len):
    d, l = thread_d, thread_len
    pitch = _PITCH[int(round(d))]
    d2, d3 = eye_id, eye_od
    R = (eye_id + eye_od) / 4.0              # ring centreline (major) radius
    rw = (eye_od - eye_id) / 4.0             # ring wire (minor) radius
    r_maj = d / 2.0
    e = 0.75 * d                             # collar height (DIN 580 e ~ 0.75 d)
    m = max(2.0 * rw, 0.9 * d)               # neck (root) width, DIN 580 m
    z_cb = l                                 # collar bottom = shank top

    # threaded shank (Z 0..l): a plain cylinder with a helical V-groove of the
    # coarse pitch cut into it (real single-start helix, isFrenet=False for a
    # stable sweep), with a rounded tip fillet at the bottom of the bolt
    shank = cq.Workplane("XY").circle(r_maj).extrude(l)
    fb = max(0.8, 0.15 * d)                  # rounded-tip stub height
    shank = shank.faces("<Z").fillet(0.5 * fb)
    oc = 0.25 * pitch
    th = l - fb                              # thread above the rounded tip
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, th + pitch, r_maj))
    groove = (
        cq.Workplane("XZ").center(r_maj + oc, 0)
        .moveTo(0, -pitch / 2.0).lineTo(-(0.6134 * pitch + oc), 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=False).translate((0, 0, fb - 0.5 * pitch))
    )
    shank = shank.cut(groove)

    # collar cylinder, Ø = d2 (DIN 580 eye inner), height e
    collar = cq.Workplane("XY").workplane(offset=z_cb).circle(d2 / 2.0).extrude(e)

    # forged ring (torus), positioned low: ring top ~ z_cb + d3, so the ring legs
    # come down to the collar (BenchCAD-1.0 / DIN 580 form)
    eye_center_z = z_cb + d3 / 2.0
    eye = cq.Solid.makeTorus(R, rw, cq.Vector(0, 0, eye_center_z), cq.Vector(0, 1, 0))

    # lofted neck: collar top -> ring root (the "loft + cylinder" transition)
    neck_base_d = min(m * 1.5, d2 * 0.8)
    ring_root_z = eye_center_z - rw
    neck_top_z = ring_root_z - rw            # poke into the ring for a clean union
    z_ct = z_cb + e                          # collar top
    neck = (cq.Workplane("XY").workplane(offset=z_ct).circle(neck_base_d / 2.0)
            .workplane(offset=neck_top_z - z_ct).circle(m / 2.0).loft())

    result = (shank.union(collar).union(neck)
              .union(cq.Workplane("XY").newObject([eye])))

    # engineering fillet at the collar / neck junction (DIN 580 R)
    try:
        result = result.edges(
            cq.selectors.NearestToPointSelector((0, 0, z_ct))
        ).fillet(min(1.5, 0.12 * d))
    except Exception:
        pass
    return result
