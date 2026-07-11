"""v_belt_pulley — the parametric part.

V-belt pulley (sheave), ISO 4183: a rim with N circumferential V-grooves, a
central bore through the hub, and a lightened web between the hub and the rim.
The whole rim cross-section (bore -> grooved outer edge -> back) is revolved once
about the axis, so the grooves are part of the profile (no boolean cuts). The web
is then lightened: an annular recess on each face plus three lightening holes.

Each groove is a trapezoid: the flanks close at the ISO belt angle `groove_angle`
(34 deg, stepping to 38 deg on large datum diameters) and stop at a flat bottom
of width C = groove_top_w - 2*groove_depth*tan(groove_angle/2), so a V-belt seats
on the flanks and never bottoms out. Grooves are spaced by groove_pitch, centred
across the width.
"""

import math

import cadquery as cq


def build(outer_d, width, n_grooves, groove_pitch, groove_top_w, groove_depth,
          groove_angle, bore_d, hub_d=0.0, hub_len=0.0):
    ro = outer_d / 2.0
    ri = bore_d / 2.0
    span = (n_grooves - 1) * groove_pitch
    z0 = width / 2.0 - span / 2.0

    half_top = groove_top_w / 2.0
    half_bot = half_top - groove_depth * math.tan(math.radians(groove_angle / 2.0))

    # outer edge (r, z) from z=0 to z=width, dipping into a trapezoidal V at each
    # groove: two flanks at the belt angle down to a flat bottom of width 2*half_bot
    outer = [(ro, 0.0)]
    for i in range(n_grooves):
        zc = z0 + i * groove_pitch
        outer += [
            (ro, zc - half_top),
            (ro - groove_depth, zc - half_bot),
            (ro - groove_depth, zc + half_bot),
            (ro, zc + half_top),
        ]
    outer += [(ro, width)]

    # closed half-profile: inner-bottom -> grooved outer edge -> inner-top
    pts = [(ri, 0.0)] + outer + [(ri, width)]
    # revolve around the profile plane's own axis (global Z). NOTE: passing an
    # explicit (0,0,0)-(0,0,1) here spins about the XZ-workplane LOCAL z (global
    # -Y) instead, collapsing the sheave into a flat lamina with the hub off-axis.
    result = cq.Workplane("XZ").polyline(pts).close().revolve(360)

    if hub_d:
        result = result.union(
            cq.Workplane("XY").workplane(offset=width).circle(hub_d / 2.0).extrude(hub_len)
        )

    # lighten the web (the solid disc between hub and rim): an annular recess on
    # each face (the "hollow big cylinder") plus three lightening holes (the
    # "three small cylinders"), spaced 120 deg apart
    rim_wall = max(3.0, 0.05 * outer_d)
    rim_ir = ro - groove_depth - rim_wall              # inner edge of the grooved rim
    hub_boss_r = max((hub_d / 2.0) if hub_d else 0.0,
                     ri + max(4.0, 0.05 * outer_d))     # keep a boss around the bore
    if rim_ir - hub_boss_r > 10.0:                      # only if there is room for a web
        web_t = max(4.0, 0.18 * width)                  # central web thickness kept
        rec = (width - web_t) / 2.0                     # recess depth per face
        for zoff in (0.0, width - rec):
            result = result.cut(
                cq.Workplane("XY").workplane(offset=zoff)
                .circle(rim_ir).circle(hub_boss_r).extrude(rec)
            )
        r_bolt = (hub_boss_r + rim_ir) / 2.0
        d_hole = min(0.55 * (rim_ir - hub_boss_r), 0.8 * r_bolt)
        for k in range(3):
            a = math.radians(120 * k + 30)
            cx, cy = r_bolt * math.cos(a), r_bolt * math.sin(a)
            result = result.cut(
                cq.Workplane("XY").workplane(offset=-1)
                .circle(d_hole / 2.0).extrude(width + 2).translate((cx, cy, 0))
            )

    # the bore runs through the hub too
    if hub_d and hub_len:
        result = result.cut(
            cq.Workplane("XY").workplane(offset=-1).circle(ri).extrude(width + hub_len + 2)
        )

    return result
