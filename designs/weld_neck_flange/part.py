"""weld_neck_flange — the parametric part.

A pipe flange in the ASME B16.5 class-150 weld-neck style, built base-up: a
raised face (gasket seat) on the bottom as the mating surface, a circular flange
disc drilled with a bolt circle and a central bore, and the defining tapered
weld-neck hub rising from the flange face and tapering from the hub base Ø
(`hub_od`, X) down to the pipe OD (`pipe_od`, A) at the weld end on top, with a
fillet blending the hub base into the flange face. Plain parametric CadQuery.

Axis = Z, base at z=0: raised face z=[0, rf_t]; flange disc on top of it; the
weld-neck hub rises in +Z and tapers to the pipe OD at the weld end.
"""

import math

import cadquery as cq


def build(bore, flange_od, flange_t, bolt_circle_d, n_bolts, bolt_hole_d,
          raised_face_d, rf_t, hub_od, pipe_od, hub_len):
    # raised face (gasket seat) as the base — the mating surface sits at z=0 so
    # nothing hangs below the flange plate
    z0 = 0.0
    raised = None
    if rf_t:
        raised = cq.Workplane("XY").circle(raised_face_d / 2).extrude(rf_t)  # z=[0, rf_t]
        z0 = rf_t

    # flange disc on top of the raised face
    disc = cq.Workplane("XY").workplane(offset=z0).circle(flange_od / 2).extrude(flange_t)
    z_hub = z0 + flange_t                       # flange face the hub grows from

    # weld-neck hub rising from the flange face, tapering hub_od (X, base) -> pipe_od
    # (A, weld end) over hub_len
    hub = (
        cq.Workplane("XY").workplane(offset=z_hub).circle(hub_od / 2)
        .workplane(offset=hub_len).circle(pipe_od / 2)
        .loft(combine=True)
    )
    result = disc.union(hub)
    if raised is not None:
        result = result.union(raised)

    # weld-neck fillet: blend the hub base into the flange face (the concave
    # junction the standard rounds)
    fr = min(0.4 * flange_t, 0.3 * hub_len, 0.55 * (flange_od - hub_od) / 2)
    result = result.edges(
        cq.selectors.BoxSelector((-(hub_od / 2 + 0.6), -(hub_od / 2 + 0.6), z_hub - 0.4),
                                 (hub_od / 2 + 0.6, hub_od / 2 + 0.6, z_hub + 0.4))
    ).fillet(fr)

    # weld-end chamfer on the hub top outer edge (the top detail the drawing rings)
    wc = min(0.35 * flange_t, 0.3 * hub_len, 0.35 * (pipe_od - bore) / 2.0)
    result = result.faces(">Z").chamfer(wc)

    # central bore through the whole stack
    top = z_hub + hub_len
    result = result.cut(
        cq.Workplane("XY").workplane(offset=-1).circle(bore / 2).extrude(top + 2)
    )

    # bolt circle: n_bolts holes through the flange disc
    r = bolt_circle_d / 2
    pts = [(r * math.cos(2 * math.pi * i / n_bolts), r * math.sin(2 * math.pi * i / n_bolts))
           for i in range(n_bolts)]
    result = result.cut(
        cq.Workplane("XY").workplane(offset=z0 - 1)
        .pushPoints(pts).circle(bolt_hole_d / 2).extrude(flange_t + 2)
    )

    return result
