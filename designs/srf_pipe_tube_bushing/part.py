"""STAUFF SRF split pipe/tube bushing."""

import cadquery as cq


def build(catalog_row, material_code, tube_od, flange_od, body_height,
          flange_height, mounting_bore):
    """Build one flanged, radially split through-panel bushing."""
    del catalog_row, material_code
    bore_clearance = 0.20
    stem_od = mounting_bore - 0.25
    bore_d = tube_od + 2.0 * bore_clearance
    shoulder_h = min(1.2, 0.25 * flange_height)

    # Z=0 is the underside of the retaining flange.  The insertion stem fits
    # the catalogued D3 mounting bore and the D2 flange retains it at the face.
    flange = (cq.Workplane("XY").circle(flange_od / 2.0)
              .circle(bore_d / 2.0).extrude(flange_height))
    stem_h = body_height - flange_height
    taper_h = 0.20 * stem_h
    straight_h = stem_h - taper_h
    top_od = bore_d + 0.62 * (stem_od - bore_d)
    straight_outer = (cq.Workplane("XY").workplane(offset=flange_height)
                      .circle(stem_od / 2.0).extrude(straight_h))
    tapered_outer = (cq.Workplane("XY")
                     .workplane(offset=flange_height + straight_h)
                     .circle(stem_od / 2.0)
                     .workplane(offset=taper_h)
                     .circle(top_od / 2.0).loft(combine=True))
    bore = (cq.Workplane("XY").workplane(offset=flange_height - 0.1)
            .circle(bore_d / 2.0).extrude(stem_h + 0.2))
    stem = straight_outer.union(tapered_outer).cut(bore)

    # A shallow annular barb below the flange represents the snap-retaining
    # interface shown in section; its unmarked size is an explicit proportion.
    barb_z = flange_height + shoulder_h
    barb_od = min(flange_od - 0.8, mounting_bore + 0.10 * (flange_od - mounting_bore))
    barb = (cq.Workplane("XY").workplane(offset=barb_z)
            .circle(barb_od / 2.0).circle(bore_d / 2.0)
            .extrude(min(1.2, 0.30 * flange_height)))
    result = flange.union(stem).union(barb)

    # Four axial relief slots divide the contracted top into compliant fingers.
    # Each slot starts at the open end and stops after two thirds of the stem,
    # leaving the lower third connected as one physical bushing solid.
    split_w = max(0.8, 0.06 * mounting_bore)
    split_depth = (2.0 / 3.0) * stem_h
    split_z = body_height - split_depth
    for angle in (0.0, 90.0, 180.0, 270.0):
        split = (cq.Workplane("XY")
                 .center(0.0, (stem_od + bore_d) / 4.0)
                 .rect(split_w, (stem_od - bore_d) / 2.0 + 2.0)
                 .extrude(split_depth + 0.2)
                 .translate((0.0, 0.0, split_z - 0.1))
                 .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), angle))
        result = result.cut(split)
    return result
