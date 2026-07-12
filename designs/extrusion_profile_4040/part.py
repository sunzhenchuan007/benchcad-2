"""extrusion_profile_4040 — the parametric part.

40 x 40 aluminium T-slot extrusion, item Profile 8 (art. 0.0.026.03). The real
Profile-8 cross-section is NOT a solid bar: it is a webbed hollow section — a
central boss (carrying the optional ∅6.8 core bore) with four diagonal webs (the
"arrows") running out to the four corners, an "item slot 8" T-groove cut into the
middle of each of the four faces (8 mm surface opening, 4.5 mm lip, widening to
the inner chamber), a thin continuous outer wall, and four hollow cells between
the webs. Optional rounded outer corners (R4).

Modelling keeps it one connected solid: the four T-slots are cut from the bar
first (their wide chambers are the hollow cells), then the central boss and the
two diagonal web bars are unioned back on — added after the cuts so the webs
bridge the boss to the four corners and cannot be severed — and finally the thin
outer wall is unioned and the four surface slots re-opened through it.

    face = 40 mm; the cross-section runs full length along the extrusion axis Z.
"""

import cadquery as cq

FACE = 40.0            # the 40 x 40 profile
SLOT_OPEN = 8.0        # item slot-8 surface opening
CHAMBER_W = 15.3       # inner chamber width (catalog-approximate)
CHAMBER_DEPTH = 8.0    # chamber depth behind the lip (catalog-approximate)
LIP_DEPTH = 4.5        # narrow lip before the chamber opens
SKIN = 2.0             # continuous outer wall thickness (proportion)
HUB = 12.0             # central boss across flats (proportion)
WEB = 4.5              # diagonal web ("arrow") width (proportion)


def build(length, core_bore=0.0, corner_r=0.0):
    h = FACE / 2.0
    angles = (0.0, 90.0, 180.0, 270.0)

    bar = cq.Workplane("XY").rect(FACE, FACE).extrude(length)
    if corner_r:
        # round the four outer corners before slotting them
        bar = bar.edges("|Z").fillet(corner_r)

    # one T-void (surface opening widening to the inner chamber) per face; the
    # wide chambers are the hollow cells of the section
    opening = (
        cq.Workplane("XY").center(0, h - LIP_DEPTH / 2.0)
        .rect(SLOT_OPEN, LIP_DEPTH).extrude(length)
    )
    chamber = (
        cq.Workplane("XY").center(0, h - LIP_DEPTH - CHAMBER_DEPTH / 2.0)
        .rect(CHAMBER_W, CHAMBER_DEPTH).extrude(length)
    )
    void = opening.union(chamber)
    void = void.edges("|Z").fillet(1.0)   # rounded T-slot chamber corners (item section)
    result = bar
    for ang in angles:
        result = result.cut(void.rotate((0, 0, 0), (0, 0, 1), ang))

    # central boss + four diagonal webs ("arrows"), unioned AFTER the slot cuts
    # so they bridge the boss to the four corners as one connected solid
    hub = cq.Workplane("XY").circle(HUB / 2.0).extrude(length)   # round boss around the core bore
    diag = FACE * 1.6
    web_a = cq.Workplane("XY").rect(diag, WEB).extrude(length).rotate((0, 0, 0), (0, 0, 1), 45.0)
    web_b = cq.Workplane("XY").rect(diag, WEB).extrude(length).rotate((0, 0, 0), (0, 0, 1), 135.0)
    result = result.union(hub).union(web_a).union(web_b)

    # thin continuous outer wall (rounded like the corners), then re-open the four
    # surface slots through it
    outer = cq.Workplane("XY").rect(FACE, FACE).extrude(length)
    if corner_r:
        outer = outer.edges("|Z").fillet(corner_r)
    inner = cq.Workplane("XY").rect(FACE - 2.0 * SKIN, FACE - 2.0 * SKIN).extrude(length)
    result = result.union(outer.cut(inner))
    for ang in angles:
        result = result.cut(opening.rotate((0, 0, 0), (0, 0, 1), ang))

    # clip everything to the 40x40 (R4) envelope so the diagonal webs cannot spike
    # past the outline
    boundary = cq.Workplane("XY").rect(FACE, FACE).extrude(length)
    if corner_r:
        boundary = boundary.edges("|Z").fillet(corner_r)
    result = result.intersect(boundary)

    if core_bore:
        # central fastening bore down the boss, along the extrusion axis
        result = result.faces(">Z").workplane().hole(core_bore)

    return result
