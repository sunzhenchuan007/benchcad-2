"""hex_cap_bolt — the parametric part.

Fully-threaded hex-head bolt, ISO 4017 (hexagon head + full-length thread). A hex
head (width across flats head_af, height head_h) with a fillet under the head where
it meets the shank; the shank carries a modelled external metric thread — a real
single-start helical V-groove of the ISO 261 coarse pitch running the full length,
leaving only a short unthreaded run-out under the head (for the fillet). A head top
chamfer appears on the hard tier.

    across-corners = head_af * 2/sqrt(3)   (polygon diameter)
"""

import math

import cadquery as cq

# ISO 261 coarse pitch by nominal thread diameter, mm
_PITCH = {6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 14: 2.0, 16: 2.0, 20: 2.5, 24: 3.0}


def build(thread_d, head_af, head_h, length, head_chamfer=0.0):
    d = thread_d
    pitch = _PITCH[int(round(d))]
    r_maj = d / 2.0

    across_corners = head_af * 2.0 / math.sqrt(3.0)
    head = cq.Workplane("XY").polygon(6, across_corners).extrude(head_h)
    shank = cq.Workplane("XY").circle(d / 2.0).extrude(-length)
    result = head.union(shank)

    # fillet under the head FIRST, on the clean smooth junction (the shank-to-
    # head-underside transition radius); doing it before the thread keeps the
    # junction edge unambiguous
    fr = 0.1 * d
    result = result.edges(
        cq.selectors.BoxSelector((-(d / 2.0 + 0.6), -(d / 2.0 + 0.6), -0.3),
                                 (d / 2.0 + 0.6, d / 2.0 + 0.6, 0.3))
    ).fillet(fr)

    # full-length external metric thread (ISO 4017), leaving a short unthreaded
    # run-out under the head for the fillet. Real single-start helix; isFrenet=False
    # + a half-pitch of run-out keep the makeHelix sweep stable at every size
    # (isFrenet=True silently deletes the shank on M12/M24).
    grip = 1.5 * pitch                       # short unthreaded run-out under the head
    thread_len = length - grip               # full-length thread
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, thread_len + 0.5 * pitch, r_maj))
    groove = (
        cq.Workplane("XZ").center(r_maj + 0.3, 0)
        .moveTo(0, -pitch / 2.0).lineTo(-(0.6134 * pitch + 0.3), 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=False).translate((0, 0, -length))
    )
    result = result.cut(groove)

    if head_chamfer:
        result = result.faces(">Z").chamfer(head_chamfer)

    return result
