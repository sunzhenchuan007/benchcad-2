"""duplex_sprocket — the parametric part.

Double-strand roller-chain sprocket, ISO 606 / DIN 8187. Two tooth discs (same
phase — duplex rollers are in phase), row centers one transverse pitch pt apart,
joined by an intermediate groove cylinder that clears the chain's inner link
plates. One-sided hub boss and a DIN 6885A keyway on the harder tiers.

Plain parametric CadQuery: named parameters, tooth profile + keyway seat from
`bench2.geomlib`. `_circles` (shared with the family's constraints in spec.py)
also gives the groove diameter build needs. bench2 derives each instance's
stand-alone program (params -> globals; sprocket_profile, keyway_dims and
_circles inlined), so the emitted program imports only cadquery + math.

Tooth geometry: identical to simplex_sprocket (ISO 606:2015 §8.2):
    dp = p / sin(pi/z)          pitch circle diameter   (== catalog D1)
    da = dp + 0.68 * d1         tip circle diameter     (fits catalog D)
    df = dp - 1.01 * d1         root circle diameter
"""

import math

import cadquery as cq
from bench2.geomlib import keyway_dims, sprocket_profile


def _circles(pitch, n_teeth, roller_d):
    """ISO 606 §8.2 derived circles + the intermediate-groove diameter. Shared
    with spec.py's check/refine (imported there) so build and the constraints
    use one groove definition."""
    dp = pitch / math.sin(math.pi / n_teeth)
    da = dp + 0.68 * roller_d
    df = dp - 1.01 * roller_d
    # groove between the rows must clear the inner link plates riding the
    # rollers; plate height is ~1.45*d1 (ISO 606 h2), sunk half below pitch
    groove_d = df - 1.5 * roller_d
    return dp, da, df, groove_d


def build(pitch, roller_d, tooth_width, trans_pitch, n_teeth, bore_d,
          hub_d=0.0, hub_len=0.0, has_keyway=0):
    z = n_teeth
    b1 = tooth_width
    pt = trans_pitch
    ch = 0.15 * b1  # deburr chamfer on the outer tooth-disc rims
    _, _, _, groove_d = _circles(pitch, n_teeth, roller_d)
    # rotate so a tooth tip sits on +Y — the keyway (cut toward +Y) is then
    # tip-aligned ("keyway is aligned with the tooth tip", catalog note).
    phase = math.pi / 2 - math.pi / z

    pts = sprocket_profile(z, pitch, roller_d, phase=phase)

    # two tooth rows in phase, row centers one transverse pitch apart;
    # outer rims chamfered, inner faces meet the groove cylinder
    row1 = cq.Workplane("XY").polyline(pts).close().extrude(b1).edges("<Z").chamfer(ch)
    row2 = (
        cq.Workplane("XY").workplane(offset=pt)
        .polyline(pts).close().extrude(b1).edges(">Z").chamfer(ch)
    )
    result = row1.union(row2)

    # intermediate groove: clears the chain's inner link plates
    result = result.union(
        cq.Workplane("XY").workplane(offset=b1)
        .circle(groove_d / 2).extrude(pt - b1)
    )

    if hub_d:
        # one-sided hub boss on the outer face of row 2
        result = result.union(
            cq.Workplane("XY").workplane(offset=pt + b1)
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
