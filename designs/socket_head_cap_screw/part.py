"""socket_head_cap_screw — the parametric part.

ISO 4762 hexagon socket head cap screw: a cylindrical head (Ø `head_d`, height
`head_h`) with a hexagon drive socket (width across flats `socket_s`) recessed
into its top, on a `length`-long shank carrying a modelled external metric thread
(ISO 261 coarse pitch helical V-groove, crests at the major Ø). The head top
outer edge carries a small chamfer. Plain parametric CadQuery.

    shank z = 0 .. length ;  head z = length .. length + head_h
"""

import math

import cadquery as cq

# ISO 261 coarse pitch by nominal thread diameter, mm
_PITCH = {6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 16: 2.0, 20: 2.5}


def build(thread_d, head_d, head_h, socket_s, length):
    d, dk, k, sh, l = thread_d, head_d, head_h, socket_s, length
    pitch = _PITCH[int(round(d))]

    shank = cq.Workplane("XY").circle(d / 2.0).extrude(l)
    head = cq.Workplane("XY").workplane(offset=l).circle(dk / 2.0).extrude(k)
    result = shank.union(head)
    result = result.faces(">Z").edges("%CIRCLE").chamfer(0.08 * dk)  # head top edge

    # hexagon drive socket, across-flats socket_s, recessed ~0.6*k into the head top
    e = sh / math.cos(math.radians(30.0))          # across corners
    socket = cq.Workplane("XY").workplane(offset=l + k).polygon(6, e).extrude(-0.6 * k)
    result = result.cut(socket)

    # external metric thread on the shank: helical V-groove, crests at the major Ø,
    # cut inward by the ISO thread height to the root
    r_maj = d / 2.0
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, l, r_maj))
    groove = (
        cq.Workplane("XZ").center(r_maj + 0.3, 0)
        .moveTo(0, -pitch / 2.0).lineTo(-(0.6134 * pitch + 0.3), 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=True)
    )
    result = result.cut(groove)

    return result
