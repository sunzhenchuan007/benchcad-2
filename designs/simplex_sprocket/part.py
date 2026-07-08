"""simplex_sprocket — the parametric part.

Single-strand roller-chain sprocket, ISO 606 / DIN 8187. Plain parametric
CadQuery: named parameters, the tooth profile and keyway seat pulled from
`bench2.geomlib`. bench2 derives each instance's stand-alone program from this
body (parameters become globals; sprocket_profile and keyway_dims are inlined),
so the emitted program imports only cadquery + math.

Heterogeneous variants in one family (catalog "Form" column):
  Form A — toothed disc + one-sided hub boss,
  Form B — straight barrel hub through the disc, larger bores.
"""

import math

import cadquery as cq
from bench2.geomlib import keyway_dims, sprocket_profile


def build(pitch, roller_d, tooth_width, n_teeth, bore_d,
          form_b=0, hub_d=0.0, hub_len=0.0, has_keyway=0):
    z = n_teeth
    ch = 0.15 * tooth_width  # deburr chamfer on the tooth-disc rims
    # rotate so a tooth tip sits on +Y — the keyway (cut toward +Y) is then
    # tip-aligned ("keyway is aligned with the tooth tip", catalog note).
    phase = math.pi / 2 - math.pi / z

    pts = sprocket_profile(z, pitch, roller_d, phase=phase)
    result = cq.Workplane("XY").polyline(pts).close().extrude(tooth_width)
    result = result.edges(">Z").chamfer(ch).edges("<Z").chamfer(ch)

    if hub_d and form_b:
        # Form B: straight barrel hub through the disc, symmetric overhang
        result = result.union(
            cq.Workplane("XY").workplane(offset=-hub_len / 2)
            .circle(hub_d / 2).extrude(tooth_width + hub_len)
        )
    elif hub_d:
        # Form A: one-sided hub boss on the top face
        result = result.union(
            cq.Workplane("XY").workplane(offset=tooth_width)
            .circle(hub_d / 2).extrude(hub_len)
        )

    # center bore
    result = result.faces(">Z").workplane().hole(bore_d)

    if has_keyway:
        kw, kd = keyway_dims(bore_d)
        rect_h = kd + bore_d / 2
        # DIN 6885A keyway (tip-aligned)
        result = (
            result.faces(">Z").workplane()
            .center(0, rect_h / 2).rect(kw, rect_h).cutThruAll()
        )

    return result
