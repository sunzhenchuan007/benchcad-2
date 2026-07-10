"""v_belt_pulley — the parametric part.

V-belt pulley (sheave), ISO 4183: a rim with N circumferential V-grooves, a
central bore and an optional hub. The whole rim cross-section (bore -> grooved
outer edge -> back) is revolved once about the axis, so the grooves are part of
the profile (no boolean cuts). Plain parametric CadQuery.

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

    return result
