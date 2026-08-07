"""extrusion_profile_4040 — the parametric part.

40 x 40 aluminium T-slot extrusion, item Profile 8 (art. 0.0.026.03).

The section is built the way the drawing draws it: ONE closed 2-D void, cut four
times out of the 40 x 40 (R4) envelope, plus the core bore. What is left is the
profile's real anatomy and it falls out of the geometry rather than being unioned
back on — four corner blocks with their slot lips, four continuously curved webs,
and a FREE-STANDING round boss carrying the bore, with open cavity all around it.

Each void runs from the face right in to the boss:

    8 mm opening at the face -> 4.5 mm lip -> hammerhead out to 15.5 wide
    -> straight down the chamber -> an arc that curves in to meet the boss on
       its 45 deg tangent -> around the boss -> mirrored back out

Because the four voids each reach the boss and stop on its 45 deg tangents, the
material between adjacent voids IS the web, and it comes out curved and flared
where it meets the boss and the corner blocks — no straight diagonal anywhere
inside, which is what the drawing shows.

An earlier revision started from a solid bar, subtracted two small boxes per face
and unioned a hub and two straight 45 deg bars back on. That left the section
60.1 % solid against the drawing's ~51 %, the bore drilled through a solid lump
instead of a boss on webs, and every internal transition a straight line.

    face = 40 mm; the cross-section runs full length along the extrusion axis Z.
"""

import math

import cadquery as cq

FACE = 40.0            # the 40 x 40 profile
SLOT_OPEN = 8.0        # item slot-8 surface opening (drawing)
LIP_DEPTH = 4.5        # narrow lip before the chamber opens (drawing)
CHAMBER_W = 15.5       # chamber width: the drawing's 12.25 from the centreline
                       # to the far face gives 20 - 12.25 = 7.75 per side
BOSS_R = 5.0           # boss radius around the core bore (proportion)
KNEE_Y = 9.0           # where the chamber wall leaves the straight and curves
                       # in toward the boss (proportion)
WEB_ARC_R = 30.0       # radius of that curve — sets the web's flare (proportion)
WEB_HALF_ANG = 14.0    # half-angle each void stops short of the 45 deg diagonal,
                       # which is what gives the web its width (proportion)

# BOSS_R / KNEE_Y / WEB_ARC_R / WEB_HALF_ANG are the only free numbers left, and
# they are set together so the section comes out 51.62 % solid against the ~52.1 %
# measured off the reference raster (itself inflated by its outline strokes), with
# a 2.42 mm web where it meets the boss. Everything else here is published.
#
# WEB_HALF_ANG must not be 0. Running each void's arc all the way to the 45 deg
# tangent makes adjacent voids meet at a single point, the web has no width, and
# the section falls apart into FIVE solids -- four corner blocks and a boss that
# only touches them. It still builds, and every dimension still measures right.


def _void_profile():
    """One face's void, as a closed 2-D wire: slot, chamber, curved web flanks,
    and the arc that wraps the boss."""
    h = FACE / 2.0
    half_open = SLOT_OPEN / 2.0
    half_ch = CHAMBER_W / 2.0
    y_lip = h - LIP_DEPTH
    a_r = math.radians(45.0 + WEB_HALF_ANG)     # stop short of the diagonal so
    a_l = math.radians(135.0 - WEB_HALF_ANG)    # the web between voids has width
    pr = (BOSS_R * math.cos(a_r), BOSS_R * math.sin(a_r))
    pl = (BOSS_R * math.cos(a_l), BOSS_R * math.sin(a_l))
    return (
        cq.Workplane("XY")
        .moveTo(-half_open, h + 0.5)            # overshoot the face
        .lineTo(half_open, h + 0.5)
        .lineTo(half_open, y_lip)               # down the slot lip
        .lineTo(half_ch, y_lip)                 # out to the chamber
        .lineTo(half_ch, KNEE_Y)                # down the chamber wall
        .radiusArc(pr, -WEB_ARC_R)              # curve in toward the boss
        .threePointArc((0.0, BOSS_R), pl)       # around the boss
        .radiusArc((-half_ch, KNEE_Y), -WEB_ARC_R)
        .lineTo(-half_ch, y_lip)
        .lineTo(-half_open, y_lip)
        .close()
    )


def build(length, core_bore=0.0, corner_r=0.0):
    result = cq.Workplane("XY").rect(FACE, FACE).extrude(length)
    if corner_r:
        result = result.edges("|Z").fillet(corner_r)

    void = _void_profile().extrude(length)
    for ang in (0.0, 90.0, 180.0, 270.0):
        result = result.cut(void.rotate((0, 0, 0), (0, 0, 1), ang))

    if core_bore:
        # central fastening bore down the boss, along the extrusion axis
        result = result.cut(
            cq.Workplane("XY").circle(core_bore / 2.0).extrude(length)
        )
    return result
