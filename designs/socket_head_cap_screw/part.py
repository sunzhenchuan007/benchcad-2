"""socket_head_cap_screw — the parametric part.

ISO 4762 hexagon socket head cap screw: a cylindrical head (diameter head_d,
height head_h) with a hexagon drive socket (width across flats socket_s) recessed
into its top and a small chamfer on the head top outer edge; a fillet under the
head where it meets the shank; and a shank of length `length` carrying a modelled
external metric thread (ISO 261 coarse pitch, a single-start helical V-groove) over
the tip length b = 2d + 12 (ISO 4762), leaving a plain grip under the head, with a
lead-in chamfer at the threaded end.

    shank z = 0 .. length ;  head z = length .. length + head_h ;  tip at z = 0
"""

import math

import cadquery as cq

# ISO 261 coarse pitch by nominal thread diameter, mm
_PITCH = {6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 16: 2.0, 20: 2.5}


def build(thread_d, head_d, head_h, socket_s, length):
    d, dk, k, sh, l = thread_d, head_d, head_h, socket_s, length
    pitch = _PITCH[int(round(d))]
    r_maj = d / 2.0

    shank = cq.Workplane("XY").circle(d / 2.0).extrude(l)
    # lead-in chamfer at the threaded end (ISO 4753 chamfered end), cut before threading
    shank = shank.faces("<Z").chamfer(1.0 * pitch)

    head = cq.Workplane("XY").workplane(offset=l).circle(dk / 2.0).extrude(k)
    result = shank.union(head)

    # small chamfer on the head top outer edge
    result = result.faces(">Z").edges("%CIRCLE").chamfer(0.08 * dk)

    # fillet under the head where it meets the shank (ISO 4762 shows it); on the
    # smooth grip, before threading so the junction edge is unambiguous
    result = result.edges(
        cq.selectors.BoxSelector((-(d / 2.0 + 0.6), -(d / 2.0 + 0.6), l - 0.3),
                                 (d / 2.0 + 0.6, d / 2.0 + 0.6, l + 0.3))
    ).fillet(0.08 * d)

    # hexagon drive socket, across-flats socket_s, recessed ~0.6*k into the head top
    e = sh / math.cos(math.radians(30.0))          # across corners
    socket = cq.Workplane("XY").workplane(offset=l + k).polygon(6, e).extrude(-0.6 * k)
    result = result.cut(socket)

    # external metric thread over the tip length b = 2d + 12 (ISO 4762), leaving a
    # plain grip under the head. Single-start helix swept a half-pitch past the tip
    # and cut flush by the shank end (isFrenet=False for sweep stability).
    grip = 1.5 * pitch
    b = min(l - grip, 2.0 * d + 12.0)
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, b + 0.5 * pitch, r_maj))
    groove = (
        cq.Workplane("XZ").center(r_maj + 0.3, 0)
        .moveTo(0, -pitch / 2.0).lineTo(-(0.6134 * pitch + 0.3), 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=False).translate((0, 0, -0.5 * pitch))
    )
    result = result.cut(groove)

    return result
