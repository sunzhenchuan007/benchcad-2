"""weld_neck_flange — the parametric part.

A pipe flange in the ASME B16.5 class-150 weld-neck style: a circular flange
disc drilled with a bolt circle, a central bore, an optional raised face (a
gasket seat) on the front, and a tapered weld-neck hub on the back. The hub is
the defining feature of a weld-neck flange — it tapers from the hub base Ø
(`hub_od`, X, at the flange back) down to the pipe OD (`pipe_od`, A, at the weld
point) over `hub_len`, so the flange welds to a pipe of that OD. Plain
parametric CadQuery — bench2 derives each instance's stand-alone program.

Axis = Z. The flange disc sits on the XY plane (back face at z=0, front face at
z=flange_t); the tapered weld-neck hub grows in -Z, the raised face in +Z.
"""

import math

import cadquery as cq


def build(bore, flange_od, flange_t, bolt_circle_d, n_bolts, bolt_hole_d,
          raised_face_d, rf_t, hub_od, pipe_od, hub_len):
    # flange disc: back face on z=0, front face on z=flange_t
    result = cq.Workplane("XY").circle(flange_od / 2).extrude(flange_t)

    # weld-neck hub on the BACK: a frustum tapering from hub_od (X, at the flange
    # back, z=0) down to pipe_od (A, at the weld end, z=-hub_len)
    hub = (
        cq.Workplane("XY").circle(hub_od / 2)
        .workplane(offset=-hub_len).circle(pipe_od / 2)
        .loft(combine=True)
    )
    result = result.union(hub)

    # raised face (gasket seat) on the FRONT — medium/hard only (rf_t=0 => flat)
    if rf_t:
        result = result.union(
            cq.Workplane("XY").workplane(offset=flange_t)
            .circle(raised_face_d / 2).extrude(rf_t)
        )

    # central bore pierces hub + flange + raised face in one long through-cut
    result = result.cut(
        cq.Workplane("XY").workplane(offset=-hub_len - 1)
        .circle(bore / 2).extrude(hub_len + flange_t + rf_t + 2)
    )

    # bolt circle: n_bolts holes on radius bolt_circle_d/2, through the flange
    r = bolt_circle_d / 2
    pts = [
        (r * math.cos(2 * math.pi * i / n_bolts),
         r * math.sin(2 * math.pi * i / n_bolts))
        for i in range(n_bolts)
    ]
    result = result.cut(
        cq.Workplane("XY").workplane(offset=-1)
        .pushPoints(pts).circle(bolt_hole_d / 2).extrude(flange_t + 2)
    )

    return result
