"""hex_flange_nut — the parametric part.

DIN 6923 (ISO 4161) hexagon flange nut: a hexagon wrenching body (width across
flats hex_s, total height total_h_m) integral with a wide conical FLANGE at the
seating end (bearing diameter flange_dia_dc, edge thickness flange_thk_c), bored
and cut with a metric INTERNAL V-thread (ISO 261 coarse pitch) running the full
height. The thread is a single-start helical 60-degree V-groove cut radially
OUTWARD from the minor bore to the nominal major radius. The serrated
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
    upper end-face chamfer = 15 deg to the top face
    upper thread-entry included angle = 120 deg (allowed drawing range 90-120)
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

    # Hexagon body, across-flats s, with the drawing's 15-degree conical upper
    # chamfer. Intersecting the hex prism with a rotational envelope removes
    # only the six upper corners and leaves a circular top land, as on the nut.
    e = s / math.cos(math.radians(30.0))         # across corners (polygon diameter)
    corner_radius = e / 2.0
    top_land_radius = s / 2.0
    top_chamfer_h = (
        corner_radius - top_land_radius
    ) * math.tan(math.radians(15.0))
    hex_prism = cq.Workplane("XY").polygon(6, e).extrude(m)
    lower_envelope = (
        cq.Workplane("XY").circle(corner_radius + 0.05).extrude(m - top_chamfer_h)
    )
    conical_envelope = (
        cq.Workplane("XY")
        .workplane(offset=m - top_chamfer_h)
        .circle(corner_radius + 0.05)
        .workplane(offset=top_chamfer_h)
        .circle(top_land_radius)
        .loft(combine=True)
    )
    result = hex_prism.intersect(lower_envelope.union(conical_envelope))

    # integral flange at the bearing end: a full-diameter rim of edge thickness c,
    # then a conical seat rising to the hex inscribed circle (tangent to the flats)
    rim = cq.Workplane("XY").circle(dc / 2.0).extrude(c)
    seat = (cq.Workplane("XY").workplane(offset=c).circle(dc / 2.0)
            .workplane(offset=flange_seat_h - c).circle(s / 2.0).loft(combine=True))
    result = result.union(rim).union(seat)

    # Internal metric thread: sweep one 60-degree V cutter around a single-start
    # helix.  The path runs one pitch beyond each face so both thread mouths are
    # open. Cut the helix before the minor bore: OCP can silently skip a sweep
    # that is booleaned against an already-open, nearly tangent cylindrical wall.
    radial_overlap = max(0.08, 0.08 * pitch)
    thread_depth = r_maj - r_min
    path_radius = r_min + 0.45 * thread_depth
    start_z = -pitch
    helix = cq.Wire.makeHelix(
        pitch,
        m + 2.0 * pitch,
        path_radius,
        center=(0.0, 0.0, start_z),
    )
    groove = (
        cq.Workplane("XZ")
        .moveTo(r_min - radial_overlap, start_z - 0.25 * pitch)
        .lineTo(r_maj + radial_overlap, start_z)
        .lineTo(r_min - radial_overlap, start_z + 0.25 * pitch)
        .close()
        .sweep(helix, isFrenet=True)
    )
    result = result.cut(groove, tol=1.0e-4)

    # Upper internal lead-in chamfer. Use the shallow end of the drawing's
    # 90-120 degree included-angle allowance (120 degrees) and overrun the top
    # face slightly so the conical cut has no coincident cap.
    entry_included_angle = 120.0
    entry_half_angle = math.radians(entry_included_angle / 2.0)
    entry_radius = min(
        r_maj + 0.15 * pitch,
        top_land_radius - max(0.20, 0.12 * pitch),
    )
    entry_bottom_radius = r_min - max(0.04, 0.03 * pitch)
    entry_depth = (entry_radius - entry_bottom_radius) / math.tan(entry_half_angle)
    entry_overrun = 0.15 * pitch
    entry_chamfer = (
        cq.Workplane("XY")
        .workplane(offset=m - entry_depth)
        .circle(entry_bottom_radius)
        .workplane(offset=entry_depth + entry_overrun)
        .circle(entry_radius + entry_overrun * math.tan(entry_half_angle))
        .loft(combine=True)
    )
    result = result.cut(entry_chamfer)

    # Tapping bore at the minor diameter, straight through. This second cut
    # opens the inner side of the helical groove and leaves the thread crests at
    # the specified D1 radius.
    result = result.cut(
        cq.Workplane("XY").workplane(offset=-1.0).circle(r_min).extrude(m + 2.0)
    )

    # serrated DIN 6923 variant: radial locking teeth on the flange bearing face —
    # shallow radial grooves cut into the bearing plane (tooth tips left flush at
    # z = 0), in the solid flange ring outside the tapped hole. serrations == 0 is
    # the plain (unserrated) DIN 6923 nut.
    if serrations:
        depth = 0.4 * c
        r_i = r_maj + 0.6 * (s / 2.0 - r_maj)    # start out past the thread wall
        r_o = dc / 2.0 - 0.3                      # stop just inside the flange edge
        radial_span = r_o - r_i
        arc_pitch = 2.0 * math.pi * (r_i + r_o) / (2.0 * serrations)
        tooth_w = min(0.65 * arc_pitch, 0.45 * radial_span)
        for i in range(int(serrations)):
            # A triangular YZ section extruded radially makes a one-way ramp,
            # unlike a symmetric rectangular cosmetic groove.
            slot = (
                cq.Workplane("YZ")
                .moveTo(-tooth_w / 2.0, 0.0)
                .lineTo(tooth_w / 2.0, 0.0)
                .lineTo(tooth_w / 2.0, depth)
                .close()
                .extrude(radial_span)
                .translate((r_i, 0.0, 0.0))
                .rotate((0, 0, 0), (0, 0, 1), i * 360.0 / serrations)
            )
            result = result.cut(slot)

    return result
