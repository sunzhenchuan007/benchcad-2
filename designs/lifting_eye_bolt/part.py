"""lifting_eye_bolt — the parametric part.

DIN 580 lifting eye bolt: a threaded shank, a collar, and a forged circular
lifting eye (a torus) integral on top, as one connected solid. The eye inner /
outer diameters (DIN 580 d2 / d3) and the thread length (l) are the tabulated
values for the nominal thread size; the shank carries a modelled external metric
thread built as a revolved sawtooth section — robust, with flush ends and no
partial run-out at the collar face.

    eye centreline radius R = (eye_id + eye_od)/4 ;  wire radius = (eye_od - eye_id)/4
"""

import math

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
    r_min = r_maj - 0.6134 * pitch

    # threaded shank: revolve a sawtooth section (crest at major Ø, root at minor Ø)
    pts = [(0.0, 0.0), (r_maj, 0.0)]
    k = 0
    z = 0.0
    while z < l - 1e-9:
        pts.append((r_min, min((k + 0.5) * pitch, l)))
        z = min((k + 1.0) * pitch, l)
        pts.append((r_maj, z))
        k += 1
    pts.append((0.0, l))
    shank = cq.Workplane("XZ").polyline(pts).close().revolve(360)

    collar = cq.Workplane("XY").workplane(offset=l).circle(col_d / 2.0).extrude(col_h)
    zc = l + col_h + R - 0.6 * rw
    eye = cq.Solid.makeTorus(R, rw, cq.Vector(0, 0, zc), cq.Vector(0, 1, 0))
    result = shank.union(collar).union(cq.Workplane("XY").newObject([eye]))
    return result
