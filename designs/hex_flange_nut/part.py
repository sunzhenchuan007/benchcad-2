"""hex_flange_nut — the parametric part.

DIN 6923 (ISO 4161) hexagon flange nut: a hexagon wrenching body (width across
flats hex_s, total height total_h_m) integral with a wide conical FLANGE at the
seating end (bearing diameter flange_dia_dc, edge thickness flange_thk_c), bored
and cut with a metric INTERNAL V-thread (ISO 261 coarse pitch) running the full
height. The thread is a single-start helix at the MINOR radius whose 60-degree V
is cut radially OUTWARD (apex just past the major radius), so the helical crest
stays at the minor radius — a real tapped hole, not a plain bore. The serrated
DIN 6923 variant adds radial locking teeth on the flange bearing face.

Drawing symbols (glossary):
    thread_dia_d  d   nominal metric thread diameter (thread major dia)
    hex_s         s   width across flats of the hexagon
    flange_dia_dc dc  flange (bearing washer-face) diameter
    total_h_m     m   total nut height, bearing face to top
    flange_thk_c  c   flange edge (rim) thickness
    flange_seat_h     height of the conical flange seat (rim -> hex); proportion
    serrations        number of radial locking serrations (0 = plain variant)

Geometry:
    bearing face at z = 0 ; top of nut at z = total_h_m
    hex across-corners  e  = hex_s / cos(30 deg)          (polygon diameter)
    internal minor dia  D1 = thread_dia_d - 1.0825 * pitch
"""

import math

import cadquery as cq

# ISO 261 coarse pitch by nominal thread diameter, mm
_PITCH = {5: 0.8, 6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 14: 2.0, 16: 2.0, 20: 2.5}


def build(thread_dia_d, hex_s, flange_dia_dc, total_h_m, flange_thk_c,
          flange_seat_h, serrations=0):
    d, s, dc, m, c = thread_dia_d, hex_s, flange_dia_dc, total_h_m, flange_thk_c
    pitch = _PITCH[int(round(d))]
    r_maj = d / 2.0                              # internal thread major radius (D/2)
    r_min = r_maj - 0.54125 * pitch              # minor radius D1/2 = (d-1.0825P)/2

    # hexagon body, across-flats s, full height, standing on the bearing face
    e = s / math.cos(math.radians(30.0))         # across corners (polygon diameter)
    result = cq.Workplane("XY").polygon(6, e).extrude(m)

    # integral flange at the bearing end: a full-diameter rim of edge thickness c,
    # then a conical seat rising to the hex inscribed circle (tangent to the flats)
    rim = cq.Workplane("XY").circle(dc / 2.0).extrude(c)
    seat = (cq.Workplane("XY").workplane(offset=c).circle(dc / 2.0)
            .workplane(offset=flange_seat_h - c).circle(s / 2.0).loft(combine=True))
    result = result.union(rim).union(seat)

    # tapping bore at the minor diameter, straight through (bearing face to top)
    result = result.cut(
        cq.Workplane("XY").workplane(offset=-1.0).circle(r_min).extrude(m + 2.0)
    )

    # internal metric thread: single-start helix at the minor radius; a 60-degree
    # V groove swept and cut radially OUTWARD (apex just past the major radius) so
    # the helical crest is left at the minor radius. isFrenet=False for stability;
    # the helix over-runs half a pitch past each end so the thread cuts clean.
    oc = 0.25 * pitch
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, m + pitch, r_min))
    groove = (
        cq.Workplane("XZ").center(r_min - oc, 0)
        .moveTo(0, -pitch / 2.0).lineTo(0.6134 * pitch + oc, 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=False).translate((0, 0, -0.5 * pitch))
    )
    # fuzzy tolerance: the swept V sits nearly tangent to the bore wall, which
    # makes the exact boolean fail on some pitches (e.g. M8); a 1e-4 mm fuzz
    # resolves the coincidence without moving any nominal dimension.
    result = result.cut(groove, tol=1.0e-4)

    # serrated DIN 6923 variant: radial locking teeth on the flange bearing face —
    # shallow radial grooves cut into the bearing plane (tooth tips left flush at
    # z = 0), in the solid flange ring outside the tapped hole. serrations == 0 is
    # the plain (unserrated) DIN 6923 nut.
    if serrations:
        depth = 0.4 * c
        r_i = r_maj + 0.6 * (s / 2.0 - r_maj)    # start out past the thread wall
        r_o = dc / 2.0 - 0.3                      # stop just inside the flange edge
        for i in range(int(serrations)):
            slot = (cq.Workplane("XY").center((r_i + r_o) / 2.0, 0)
                    .box(r_o - r_i, 0.35 * (r_o - r_i), depth, centered=(True, True, False))
                    .rotate((0, 0, 0), (0, 0, 1), i * 360.0 / serrations))
            result = result.cut(slot)

    return result
