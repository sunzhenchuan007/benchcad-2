"""v_belt_pulley — the parametric part (norelem 22070 / DIN 2211, **Form J**).

Form J = a **multi-groove** V-belt sheave (N = 2 or 3) for a **taper clamping bush**:
a grooved rim, a narrower solid hub boss centred in it, and a **conical (tapered)
bore** — NO keyway, NO lightening holes (the bush carries the keyway).

Variable naming: every dimension carries its **norelem/DIN drawing symbol** as a
suffix so the code reads against the drawing (see docs/DEBUGGING.md convention).

    D   = outer_dia_D     pulley outside diameter
    B   = rim_width_B     rim width = N*e  (grooves at e/2 from each edge → half teeth)
    N   = n_grooves       number of V-grooves (Form J: 2 or 3)
    e   = groove_pitch_e  groove pitch  (SPZ 12 / SPA 15 / SPB 19)
    lg  = groove_top_lg   groove top width  (ISO 4183 section)
    T   = groove_depth_T  groove depth below D
    α   = groove_angle_a  groove flank angle (34° small Ø, 38° large Ø)
    D5  = hub_dia_D5      hub-boss diameter
    L   = hub_width_L     hub-boss width (centred in B)
    L1  = overhang_L1     rim overhang past the hub, total  →  **L + L1 = B**
    D2  = shaft_bore_D2   the shaft bore the taper bush accepts; the pulley's own
          conical bush seat runs from Ø 2*D2 (front, smaller end) to Ø 0.8*D at the
          hub end (larger end).

Coordinate frame:  z = 0 front rim face .. z = B back rim face; revolved about +Z;
the conical bore runs down the axis.
"""

import math

import cadquery as cq

# a small margin (mm) so boolean cuts run cleanly a hair past each end face,
# instead of ending exactly on the face (which leaves coincident-face slivers).
_CUT_MARGIN = 1.0


def build(outer_dia_D, rim_width_B, n_grooves, groove_pitch_e, groove_top_lg,
          groove_depth_T, groove_angle_a, hub_dia_D5, hub_width_L, shaft_bore_D2):
    R_outer = outer_dia_D / 2.0                     # rim outer radius (to D)
    R_hub = hub_dia_D5 / 2.0                        # hub-boss radius (to D5)
    overhang_L1 = rim_width_B - hub_width_L         # drawing relation: L + L1 = B
    z_hub0 = overhang_L1 / 2.0                      # hub centred → L1/2 of rim each side
    z_hub1 = z_hub0 + hub_width_L

    # grooves centred across B = N*e, so the first groove sits e/2 from each edge:
    # the two rim edges are HALF teeth and the N-1 lands between grooves are full
    # teeth (an N-groove rim reads as "N-1 full + 2 half teeth")
    span_e = (n_grooves - 1) * groove_pitch_e
    z_g0 = rim_width_B / 2.0 - span_e / 2.0
    half_lg = groove_top_lg / 2.0
    half_bot = half_lg - groove_depth_T * math.tan(math.radians(groove_angle_a / 2.0))

    # ---- grooved rim RING: revolve a half-profile from the hub radius (D5) out to
    #      the grooved OD (D); the outer edge dips into a V at each groove ----
    outer = [(R_outer, 0.0)]
    for i in range(n_grooves):
        zc = z_g0 + i * groove_pitch_e
        outer += [
            (R_outer, zc - half_lg),
            (R_outer - groove_depth_T, zc - half_bot),
            (R_outer - groove_depth_T, zc + half_bot),
            (R_outer, zc + half_lg),
        ]
    outer += [(R_outer, rim_width_B)]
    pts = [(R_hub, 0.0)] + outer + [(R_hub, rim_width_B)]
    # bare revolve(360) spins about global Z (correct); an explicit axis would
    # collapse it to a lamina.
    rim = cq.Workplane("XZ").polyline(pts).close().revolve(360)

    # ---- hub boss: a solid cylinder Ø D5, width L, centred in B (so the rim of
    #      width B overhangs it by L1/2 each side — the recessed-hub Form J look) ----
    hub = cq.Workplane("XY").workplane(offset=z_hub0).circle(R_hub).extrude(hub_width_L)
    result = rim.union(hub)

    # ---- conical taper-bush seat (per review): a frustum (NOT a cylinder) — Ø 2*D2
    #      at the front (z=0, the smaller end) opening to Ø 0.8*D5 at the hub end
    #      (z=B, the larger end); measured off the HUB Ø D5, not the outside Ø D, so
    #      it stays inside the hub and never breaches the rim. NO keyway (the bush
    #      carries it). Lofted from _CUT_MARGIN before the front face to _CUT_MARGIN
    #      past the back face so it cuts clean through. ----
    r_front = shaft_bore_D2                    # front Ø = 2*D2   → radius = D2
    r_back = 0.4 * hub_dia_D5                   # hub-end Ø = 0.8*D5 → radius = 0.4*D5
    taper_bore = (
        cq.Workplane("XY").workplane(offset=-_CUT_MARGIN).circle(r_front)
        .workplane(offset=rim_width_B + 2.0 * _CUT_MARGIN).circle(r_back).loft()
    )
    result = result.cut(taper_bore)

    return result
