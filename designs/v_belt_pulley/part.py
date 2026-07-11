"""v_belt_pulley — the parametric part (norelem 22070 / DIN 2211, **Form J**).

Form J of the norelem 22070 catalogue = a **multi-groove** V-belt sheave (N = 2 or 3)
made for a **taper clamping bush**: a grooved rim, a solid web, a **hub boss on ONE
side** (diameter D5), and a **conical (tapered) bore** — NO keyway, NO lightening
holes (the taper bush carries the keyway and clamps the shaft). Form A is the
single-groove sister (N = 1, no hub boss); we only build Form J here.

Coordinate frame (so you can read the code against the drawing):
    z = 0 ....... front rim face (grooves start here)
    z = B ....... back rim face; the hub boss starts here
    z = B+hub_len  hub-boss end face (the taper bush is inserted from THIS end)
    the whole thing is revolved about +Z; the bore runs down the axis.

Dimension glossary (norelem symbols → code params):
    D   = outer_d      pulley outside diameter
    B   = width        rim width  = 2*E + (N-1)*e   (ISO 4183, set in spec.refine)
    N   = n_grooves    number of V-grooves (Form J: 2 or 3)
    e   = groove_pitch groove spacing  (SPZ 12 / SPA 15 / SPB 19)
    D5  = hub_d        hub-boss diameter  (~0.68*D in the catalogue)
    -   = hub_len      how far the hub boss sticks out past the back rim face
    -   = bore_d       conical-bore diameter at the SMALL (front) end
    lg  = groove_top_w / groove_depth / groove_angle   the ISO V-groove section

To DEBUG in a 3D GUI, keep this file a clean build() and drive it from a tiny
show_object wrapper (CQ-editor) or `tools/debug_family.py` — see docs/DEBUGGING.md.
"""

import math

import cadquery as cq

# how much the taper-bush bore narrows from the hub end to the rim end (per side,
# as a fraction of length) — a shallow cone, ~Taper-Lock proportions. Bigger =
# more obviously conical. Tweak this first if the bore looks wrong.
_BORE_TAPER = 0.06


def build(outer_d, width, n_grooves, groove_pitch, groove_top_w, groove_depth,
          groove_angle, bore_d, hub_d, hub_len):
    ro = outer_d / 2.0                       # rim outer radius
    B = width
    span = (n_grooves - 1) * groove_pitch    # centre-to-centre of the groove set
    z0 = B / 2.0 - span / 2.0                # first groove centre (grooves centred on B)

    half_top = groove_top_w / 2.0
    half_bot = half_top - groove_depth * math.tan(math.radians(groove_angle / 2.0))

    # ---- grooved rim: revolve a half-profile (bore radius -> grooved OD -> back) ----
    # the outer edge dips into a trapezoidal V at each groove; flanks at groove_angle
    ri = bore_d / 2.0
    outer = [(ro, 0.0)]
    for i in range(n_grooves):
        zc = z0 + i * groove_pitch
        outer += [
            (ro, zc - half_top),
            (ro - groove_depth, zc - half_bot),
            (ro - groove_depth, zc + half_bot),
            (ro, zc + half_top),
        ]
    outer += [(ro, B)]
    pts = [(ri, 0.0)] + outer + [(ri, B)]
    # NOTE: bare revolve(360) spins about global Z (correct). Passing an explicit
    # axis here would spin about the XZ-plane local z and collapse it to a lamina.
    result = cq.Workplane("XZ").polyline(pts).close().revolve(360)

    # ---- hub boss (D5) protruding on ONE side (the back, z = B .. B+hub_len) ----
    result = result.union(
        cq.Workplane("XY").workplane(offset=B).circle(hub_d / 2.0).extrude(hub_len)
    )

    # ---- conical bore for the taper clamping bush (big at the hub end, small at
    #      the front rim face); NO keyway — the bush carries it ----
    top = B + hub_len
    r_small = bore_d / 2.0
    r_big = r_small + _BORE_TAPER * top       # widen toward the hub end
    taper_bore = (
        cq.Workplane("XY").workplane(offset=-1)         # start just below the front face
        .circle(r_small).workplane(offset=top + 2)      # up to just past the hub end
        .circle(r_big).loft()
    )
    result = result.cut(taper_bore)

    return result
