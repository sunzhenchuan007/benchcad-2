"""v_belt_pulley — the parametric part (norelem 22070 / DIN 2211, **Form J**).

Form J = a **multi-groove** V-belt sheave (N = 2 or 3) for a **taper clamping bush**.
It is a plain **solid of revolution**: one closed cross-section in the (r, z)
half-plane, revolved 360° about the axis. The profile has two boundaries —

  * **outer** = the grooved rim: the outside Ø D with a V-notch at each groove;
  * **inner** = the bore: a **frustum + a cylinder** — a conical taper seat that
    opens from Ø 2*D2 at the front face (z=0, the small end) out to Ø 0.8*D5, then
    a straight cylinder Ø 0.8*D5 to the back face. NO keyway (the bush carries it).

Variable naming: every dimension carries its **norelem/DIN drawing symbol** suffix
so the code reads against the drawing (see docs/DEBUGGING.md convention).

    D   = outer_dia_D     pulley outside diameter
    B   = rim_width_B     rim width = N*e  (grooves at e/2 from each edge → half teeth)
    N   = n_grooves       number of V-grooves (Form J: 2 or 3)
    e   = groove_pitch_e  groove pitch  (SPZ 12 / SPA 15 / SPB 19)
    lg  = groove_top_lg   groove top width  (ISO 4183 section)
    T   = groove_depth_T  groove depth below D
    α   = groove_angle_a  groove flank angle (34° small Ø, 38° large Ø)
    D5  = hub_dia_D5      hub Ø; the bore opens out to Ø 0.8*D5 at its large end
    L   = hub_width_L     taper length — the frustum runs z=0..L, cylinder L..B
    D2  = shaft_bore_D2   shaft bore; the taper seat's small end is Ø 2*D2 (z=0)

Coordinate frame:  z = 0 front face .. z = B back face; revolved about +Z.
"""

import math

import cadquery as cq


def build(outer_dia_D, rim_width_B, n_grooves, groove_pitch_e, groove_top_lg,
          groove_depth_T, groove_angle_a, hub_dia_D5, hub_width_L, shaft_bore_D2):
    R_outer = outer_dia_D / 2.0                 # rim outside radius (to D)
    B = rim_width_B
    r_bore_front = shaft_bore_D2                # taper seat small end: Ø 2*D2 at z=0
    r_bore_back = 0.4 * hub_dia_D5              # taper seat large end + bore: Ø 0.8*D5
    z_taper = min(hub_width_L, B)               # frustum over z=0..L, cylinder L..B

    # grooves centred across B = N*e → first groove e/2 from each edge, so the two
    # rim edges are HALF teeth and the N-1 lands between grooves are full teeth
    span = (n_grooves - 1) * groove_pitch_e
    z_g0 = B / 2.0 - span / 2.0
    half_lg = groove_top_lg / 2.0
    half_bot = half_lg - groove_depth_T * math.tan(math.radians(groove_angle_a / 2.0))

    # ---- one closed (r, z) profile, revolved once ----
    # inner boundary (bore), front → back: a frustum then a cylinder
    pts = [(r_bore_front, 0.0), (r_bore_back, z_taper), (r_bore_back, B)]
    # up the back face to the rim, then the grooved OD back → front (decreasing z)
    pts.append((R_outer, B))
    for i in reversed(range(n_grooves)):
        zc = z_g0 + i * groove_pitch_e
        pts += [
            (R_outer, zc + half_lg),
            (R_outer - groove_depth_T, zc + half_bot),
            (R_outer - groove_depth_T, zc - half_bot),
            (R_outer, zc - half_lg),
        ]
    pts.append((R_outer, 0.0))
    # front face closes back down to the bore front; revolve about global Z
    result = cq.Workplane("XZ").polyline(pts).close().revolve(360)

    return result
