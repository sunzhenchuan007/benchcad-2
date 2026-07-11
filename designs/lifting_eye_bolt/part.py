"""lifting_eye_bolt — the parametric part (DIN 580).

DIN 580 lifting eye bolt: a threaded shank, a cylindrical collar, and a forged
circular lifting eye (torus), one connected solid. The transition is a collar
cylinder (Ø d2) plus a lofted neck whose BOTTOM is the full collar Ø d2 (flush
with the collar top — no step) tapering up to the neck width m at the ring root;
the ring sits low so its legs come down to the collar.

Drawing symbols (DIN 580) → params / vars:
    d1 = thread_dia_d1    nominal metric thread Ø (the size driver)
    d2 = eye_inner_d2     eye inner Ø  (= collar Ø)
    d3 = eye_outer_d3     eye outer Ø
    l  = thread_len_l     thread / shank length
  derived: collar_h_e (e), neck_width_m (m),
           ring_R = (d2+d3)/4, wire_rw = (d3-d2)/4
"""

import cadquery as cq

_PITCH = {8: 1.25, 10: 1.5, 12: 1.75, 16: 2.0, 20: 2.5, 24: 3.0}


def build(thread_dia_d1, eye_inner_d2, eye_outer_d3, thread_len_l):
    d1, l = thread_dia_d1, thread_len_l
    d2, d3 = eye_inner_d2, eye_outer_d3
    pitch = _PITCH[int(round(d1))]
    ring_R = (d2 + d3) / 4.0                  # ring centreline (major) radius
    wire_rw = (d3 - d2) / 4.0                 # ring wire (minor) radius
    thread_maj_r = d1 / 2.0
    collar_h_e = 0.75 * d1                    # DIN 580 collar height e
    neck_width_m = max(2.0 * wire_rw, 0.9 * d1)   # DIN 580 neck width m
    z_collar_bot = l                          # collar bottom = shank top

    # threaded shank (Z 0..l): a helical V-groove of the coarse pitch cut into a
    # plain cylinder; a plain unthreaded gap sits under the collar and a rounded
    # stub caps the bottom tip.
    shank = cq.Workplane("XY").circle(thread_maj_r).extrude(l)
    tip_stub = max(0.8, 0.15 * d1)            # rounded, unthreaded tip
    shank = shank.faces("<Z").fillet(0.5 * tip_stub)
    gap = max(0.18 * d1, 1.5 * pitch)         # plain unthreaded shank under the collar
    overcut = 0.25 * pitch
    thread_h = (l - gap) - tip_stub
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, thread_h + pitch, thread_maj_r))
    groove = (
        cq.Workplane("XZ").center(thread_maj_r + overcut, 0)
        .moveTo(0, -pitch / 2.0).lineTo(-(0.6134 * pitch + overcut), 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=False).translate((0, 0, tip_stub - 0.5 * pitch))
    )
    shank = shank.cut(groove)

    # collar cylinder, Ø d2, height e
    collar = (cq.Workplane("XY").workplane(offset=z_collar_bot)
              .circle(d2 / 2.0).extrude(collar_h_e))

    # forged ring (torus), positioned low: ring top ~ z_collar_bot + d3
    eye_center_z = z_collar_bot + d3 / 2.0
    eye = cq.Solid.makeTorus(ring_R, wire_rw, cq.Vector(0, 0, eye_center_z),
                             cq.Vector(0, 1, 0))

    # lofted neck: its BOTTOM is the full collar Ø d2 (flush with the collar top,
    # no step) tapering up to the neck width m at the ring root
    neck_base_dia = d2                        # loft bottom Ø == collar top Ø d2
    z_collar_top = z_collar_bot + collar_h_e
    ring_root_z = eye_center_z - wire_rw
    neck_top_z = ring_root_z - wire_rw        # poke into the ring for a clean union
    neck = (cq.Workplane("XY").workplane(offset=z_collar_top).circle(neck_base_dia / 2.0)
            .workplane(offset=neck_top_z - z_collar_top).circle(neck_width_m / 2.0).loft())

    result = (shank.union(collar).union(neck)
              .union(cq.Workplane("XY").newObject([eye])))

    # small blend at the collar/neck junction (same-Ø tangent edge)
    try:
        result = result.edges(
            cq.selectors.NearestToPointSelector((0, 0, z_collar_top))
        ).fillet(min(1.5, 0.12 * d1))
    except Exception:
        pass
    return result
