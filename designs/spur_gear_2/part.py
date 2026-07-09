"""spur_gear_2 — the parametric part.

Involute spur gear, ISO 53 basic rack (20° pressure angle), module series per
ISO 54. Plain parametric CadQuery: the tooth profile comes from
`bench2.geomlib.involute_gear_profile`; a one-sided hub boss (catalog Style A,
low tooth counts) and a DIN 6885A keyway appear on the harder tiers. bench2
derives each instance's stand-alone program (parameters -> globals;
involute_gear_profile and keyway_dims inlined), so the emitted program imports
only cadquery + math.

Tooth geometry (ISO 53, 20°):
    dp = m*z           pitch circle diameter
    da = m*(z + 2)     tip circle diameter
    df = m*(z - 2.5)   root circle diameter
"""

import math

import cadquery as cq
from bench2.geomlib import involute_gear_profile, keyway_dims


def build(module, n_teeth, face_width, bore_d,
          hub_d=0.0, hub_len=0.0, has_keyway=0):
    z = n_teeth
    ch = 0.12 * module  # deburr chamfer on the tooth-rim edges
    # rotate so a tooth gap sits on +Y, where the keyway is cut
    phase = math.pi / 2 - math.pi / z

    pts = involute_gear_profile(module, z, phase=phase)
    result = cq.Workplane("XY").polyline(pts).close().extrude(face_width)
    result = result.edges(">Z").chamfer(ch).edges("<Z").chamfer(ch)

    if hub_d:
        # Style A: one-sided hub boss on the top face
        result = result.union(
            cq.Workplane("XY").workplane(offset=face_width)
            .circle(hub_d / 2).extrude(hub_len)
        )

    # center bore
    result = result.faces(">Z").workplane().hole(bore_d)

    if has_keyway:
        kw, kd = keyway_dims(bore_d)
        rect_h = kd + bore_d / 2
        # DIN 6885A keyway
        result = (
            result.faces(">Z").workplane()
            .center(0, rect_h / 2).rect(kw, rect_h).cutThruAll()
        )

    return result
