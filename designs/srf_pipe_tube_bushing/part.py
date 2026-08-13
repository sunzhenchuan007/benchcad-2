"""STAUFF SRF split pipe/tube bushing."""

import cadquery as cq


def build(catalog_row, material_code, tube_od, flange_od, body_height,
          flange_height, mounting_bore):
    """Build one flanged, radially split through-panel bushing."""
    del catalog_row, material_code
    bore_clearance = 0.20
    stem_od = mounting_bore - 0.25
    bore_d = tube_od + 2.0 * bore_clearance
    lead_h = min(1.6, 0.32 * flange_height)
    shoulder_h = min(1.2, 0.25 * flange_height)

    # Z=0 is the underside of the retaining flange.  The insertion stem fits
    # the catalogued D3 mounting bore and the D2 flange retains it at the face.
    flange = (cq.Workplane("XY").circle(flange_od / 2.0)
              .circle(bore_d / 2.0).extrude(flange_height))
    stem_h = body_height - flange_height
    stem = (cq.Workplane("XY").workplane(offset=flange_height)
            .circle(stem_od / 2.0).circle(bore_d / 2.0).extrude(stem_h))

    # A shallow annular barb below the flange represents the snap-retaining
    # interface shown in section; its unmarked size is an explicit proportion.
    barb_z = flange_height + shoulder_h
    barb_od = min(flange_od - 0.8, mounting_bore + 0.10 * (flange_od - mounting_bore))
    barb = (cq.Workplane("XY").workplane(offset=barb_z)
            .circle(barb_od / 2.0).circle(bore_d / 2.0)
            .extrude(min(1.2, 0.30 * flange_height)))
    result = flange.union(stem).union(barb)

    # Chamfer the exposed insertion end and cut the full radial installation
    # opening. The split is a material gap, not a second solid.
    result = result.edges(">Z").chamfer(min(lead_h, 0.18 * (stem_od - bore_d)))
    split_w = max(0.8, 0.06 * mounting_bore)
    split = (cq.Workplane("XY").center(0.0, flange_od / 4.0)
             .rect(split_w, flange_od / 2.0 + 1.0)
             .extrude(body_height + 2.0).translate((0.0, 0.0, -1.0)))
    result = result.cut(split)
    return result
