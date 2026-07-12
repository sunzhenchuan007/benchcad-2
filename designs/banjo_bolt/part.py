"""banjo_bolt — the parametric part.

DIN 7643 banjo bolt ("hollow screw"): a hex head on a shank (Ø d3 = the thread
nominal) carrying an external fine metric thread, an AXIAL BORE (Ø d4) drilled up
from the free end, and a TRANSVERSE CROSS-HOLE (Ø d2) through the shank into that
bore in the banjo-seat region below the head — so fluid from the banjo ring fitting
crosses into the axial bore. Modelled as ONE connected solid.

Drawing symbols -> parameters (DIN 7643):
    d   thread_dia_d      thread nominal Ø (= shank Ø d3), fine pitch
    s   hex_s             hex head width across flats
    d4  bore_dia_d4       axial hollow bore (drilled from the free end)
    d2  cross_hole_d2     transverse cross-hole feeding the axial bore
    l1  shank_len_l1      shank length (head underside to tip)
    t1  bore_depth_t1     axial-bore depth from the tip
    m   head_h_m          hex head height
    c1  cross_pos_c1      cross-hole centre distance below the head

Coordinate frame: tip (threaded free end) at z = 0; shank z = 0..l1; hex head
z = l1..l1+m. The axial bore runs up from z = 0; the cross-hole axis lies along Y.
"""

import math

import cadquery as cq

# DIN 7643 fine pitch by nominal thread Ø, mm (M8x1/M10x1 = 1.0, the rest = 1.5)
_PITCH_FINE = {10: 1.0, 12: 1.5, 14: 1.5, 16: 1.5, 18: 1.5, 22: 1.5, 26: 1.5}


def build(thread_dia_d, hex_s, bore_dia_d4, cross_hole_d2, shank_len_l1,
          bore_depth_t1, head_h_m, cross_pos_c1, n_cross_holes=1):
    d, s, l1, m = thread_dia_d, hex_s, shank_len_l1, head_h_m
    pitch = _PITCH_FINE[int(round(d))]
    r_maj = d / 2.0

    # shank Ø d3 = d (tip at z=0), lead-in chamfer at the free end before threading
    shank = cq.Workplane("XY").circle(d / 2.0).extrude(l1)
    shank = shank.faces("<Z").chamfer(1.0 * pitch)
    # hex head
    e = s / math.cos(math.radians(30.0))
    head = cq.Workplane("XY").workplane(offset=l1).polygon(6, e).extrude(m)
    result = shank.union(head)
    # small chamfer on the head top outer edges
    result = result.faces(">Z").chamfer(0.1 * m)

    # axial hollow bore Ø d4, drilled up from the free end to depth t1
    result = result.cut(
        cq.Workplane("XY").workplane(offset=-1.0).circle(bore_dia_d4 / 2.0).extrude(bore_depth_t1 + 1.0)
    )

    # transverse cross-hole(s) Ø d2 through the shank into the axial bore, in the
    # banjo-seat region a distance c1 below the head underside. n=1 is a single
    # cross-drill (2 ports, axis along Y); n=2 adds a second at 90° (4 ports).
    z_cross = l1 - cross_pos_c1
    for k in range(int(n_cross_holes)):
        cross = (
            cq.Workplane("XZ").workplane(offset=-d)
            .center(0.0, z_cross).circle(cross_hole_d2 / 2.0).extrude(2.0 * d)
        )
        if k:
            cross = cross.rotate((0, 0, 0), (0, 0, 1), 90.0 * k)
        result = result.cut(cross)

    # external fine metric thread on the shank up to just below the cross-hole,
    # a single-start helical V-groove (leaves a plain banjo-seat under the head)
    thr_len = max(pitch, z_cross - cross_hole_d2)
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, thr_len + 0.5 * pitch, r_maj))
    oc = 0.25 * pitch
    groove = (
        cq.Workplane("XZ").center(r_maj + oc, 0)
        .moveTo(0, -pitch / 2.0).lineTo(-(0.6134 * pitch + oc), 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=False).translate((0, 0, -0.5 * pitch))
    )
    result = result.cut(groove)

    return result
