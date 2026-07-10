"""hex_cap_bolt — the parametric part.

Fully-threaded hex-head bolt, ISO 4017 (hexagon head + full-length thread). The hex
head (width across flats head_af, height head_h) has its top washed out by a conical
chamfer to a circle inscribed in the hexagon (tangent to the flats) — the standard
hex-head washout, not a per-edge chamfer. A fillet sits under the head where it
meets the shank, and the shank carries a modelled external metric thread — a real
single-start helical V-groove of the ISO 261 coarse pitch running the full length,
leaving only a short unthreaded run-out under the head; the threaded end
has a 45-degree lead-in chamfer (ISO 4753 chamfered end).

    across-corners  = head_af * 2/sqrt(3)   (hexagon polygon diameter)
    top-washout circle radius = head_af/2   (inscribed in the hexagon)
"""

import math

import cadquery as cq

# ISO 261 coarse pitch by nominal thread diameter, mm
_PITCH = {6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 14: 2.0, 16: 2.0, 20: 2.5, 24: 3.0}

# conical top-washout depth, as a fraction of the head height
_WASHOUT_FRAC = 0.25


def build(thread_d, head_af, head_h, length):
    d = thread_d
    pitch = _PITCH[int(round(d))]
    r_maj = d / 2.0

    across_corners = head_af * 2.0 / math.sqrt(3.0)
    head = cq.Workplane("XY").polygon(6, across_corners).extrude(head_h)

    # conical top washout: intersect the hex prism with a cone whose top radius is
    # the inscribed-circle radius (head_af/2, tangent to the flats). The top face
    # becomes a circle inscribed in the hexagon and the six corners are chamfered
    # down over the top _WASHOUT_FRAC of the head height (the real hex-head washout).
    r_top = head_af / 2.0
    r_corner = across_corners / 2.0
    r_bottom = (r_corner - (1.0 - _WASHOUT_FRAC) * r_top) / _WASHOUT_FRAC
    cone = (cq.Workplane("XY").circle(r_bottom)
            .workplane(offset=head_h).circle(r_top).loft())
    head = head.intersect(cone)

    shank = cq.Workplane("XY").circle(d / 2.0).extrude(-length)
    # lead-in chamfer at the threaded end (ISO 4753 chamfered end, ~45 deg) so the
    # thread starts cleanly into a nut, cut before threading
    shank = shank.faces("<Z").chamfer(1.2 * pitch)
    result = head.union(shank)

    # fillet under the head, on the clean smooth junction (before threading keeps
    # the junction edge unambiguous)
    fr = 0.1 * d
    result = result.edges(
        cq.selectors.BoxSelector((-(d / 2.0 + 0.6), -(d / 2.0 + 0.6), -0.3),
                                 (d / 2.0 + 0.6, d / 2.0 + 0.6, 0.3))
    ).fillet(fr)

    # full-length external metric thread (ISO 4017), leaving a short unthreaded
    # run-out under the head. Real single-start helix; isFrenet=False + a half-pitch
    # of run-out keep the makeHelix sweep stable at every size.
    grip = 1.5 * pitch
    thread_len = length - grip
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, thread_len + 0.5 * pitch, r_maj))
    groove = (
        cq.Workplane("XZ").center(r_maj + 0.3, 0)
        .moveTo(0, -pitch / 2.0).lineTo(-(0.6134 * pitch + 0.3), 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=False).translate((0, 0, -length))
    )
    result = result.cut(groove)

    return result
