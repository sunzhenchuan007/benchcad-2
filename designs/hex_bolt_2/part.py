"""hex_bolt_2 — the parametric part.

Hex-head bolt, ISO 4014 (hexagon head + threaded shank). The head is a hexagonal
prism with width `head_af` across the flats and height `head_h`; the shank is a
cylinder of the nominal thread diameter carrying a modelled external metric
thread (ISO 261 coarse pitch, a helical V-groove cut in to the external minor Ø
d - 1.2268*P), with a short unthreaded lead at the tip. A head top chamfer
appears on the hard tier. Plain parametric CadQuery.

    across-corners = head_af / cos(30°) = head_af * 2/sqrt(3)   (polygon diameter)
"""

import math

import cadquery as cq

# ISO 261 coarse pitch by nominal thread diameter, mm
_PITCH = {4: 0.7, 5: 0.8, 6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 14: 2.0, 16: 2.0,
          20: 2.5, 24: 3.0}


def build(thread_d, head_af, head_h, length, head_chamfer=0.0):
    # hexagonal head (across-flats head_af) sitting on z = 0 .. head_h
    across_corners = head_af * 2.0 / math.sqrt(3.0)
    result = cq.Workplane("XY").polygon(6, across_corners).extrude(head_h)

    # plain shank extending downward from the head underside (z = 0 .. -length)
    result = result.union(
        cq.Workplane("XY").circle(thread_d / 2.0).extrude(-length)
    )

    if head_chamfer:
        # chamfer the top face of the head (ISO 4014 head top chamfer)
        result = result.faces(">Z").chamfer(head_chamfer)

    # external metric thread on the shank: a helical V-groove of the coarse pitch
    # cut in to the external minor Ø, leaving ~one pitch unthreaded at the tip
    pitch = _PITCH[int(round(thread_d))]
    r_maj = thread_d / 2.0
    thr_len = max(pitch, length - pitch)
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, thr_len, r_maj))
    groove = (
        cq.Workplane("XZ").center(r_maj + 0.3, 0)
        .moveTo(0, -pitch / 2.0).lineTo(-(0.6134 * pitch + 0.3), 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=True).translate((0, 0, -thr_len))
    )
    result = result.cut(groove)

    return result
