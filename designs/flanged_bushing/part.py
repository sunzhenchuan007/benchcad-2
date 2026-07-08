"""flanged_bushing — the parametric part.

Plain sleeve bearing with a collar (flange) at one end, ISO 3547 / DIN 1850
style: a cylindrical sleeve (bore d, wall s, length L) with a wider collar at
the base, an internal circumferential oil groove fed by a radial lubrication
cross-hole (medium/hard), and a lead-in chamfer on the open rim (hard). Plain
parametric CadQuery; bench2 derives each instance's stand-alone program.

    outer_d  = bore_d + 2*wall_t          sleeve outside diameter
    collar_d = outer_d + 2*collar_over    collar (flange) diameter
"""

import cadquery as cq


def build(bore_d, wall_t, length, collar_t, collar_over,
          lead_chamfer=0.0, oil_hole_d=0.0, oil_groove=0.0):
    outer_d = bore_d + 2.0 * wall_t
    collar_d = outer_d + 2.0 * collar_over

    # sleeve for the full length, wider collar at the base (z = 0 .. collar_t)
    result = cq.Workplane("XY").circle(outer_d / 2.0).extrude(length)
    result = result.union(cq.Workplane("XY").circle(collar_d / 2.0).extrude(collar_t))

    # bore through everything
    result = result.faces(">Z").workplane().hole(bore_d)

    # lubrication: a groove around the bore fed by a radial cross-hole, in the
    # sleeve wall above the collar
    z_lube = collar_t + 0.55 * (length - collar_t)
    if oil_groove:
        # internal circumferential oil groove (enlarges the bore over a 3 mm band)
        result = result.cut(
            cq.Workplane("XY").workplane(offset=z_lube - 1.5)
            .circle(bore_d / 2.0 + oil_groove).circle(bore_d / 2.0).extrude(3.0)
        )
    if oil_hole_d:
        # radial lubrication cross-hole through the wall at the groove
        result = result.cut(
            cq.Workplane("YZ").center(0, z_lube).circle(oil_hole_d / 2.0)
            .extrude(outer_d, both=True)
        )

    if lead_chamfer:
        # lead-in chamfer on the open rim (opposite the collar)
        result = result.edges(">Z").chamfer(lead_chamfer)

    return result
