"""t_slot_nut — the parametric part.

T-slot nut (DIN 508): a prism with an inverted-T cross-section — a wide base
that sits under the slot lips and a narrower neck that passes through the slot
opening — with a vertical THREADED bore through the centre. The bore carries a
modelled internal metric thread (drilled to the minor Ø, a helical V-groove of
the coarse pitch cut out to the major Ø) — the nut's function is the thread.
Plain parametric CadQuery.

    base_w  wide base (under the lips)   >   neck_w  neck (through the opening)
    length  runs along the slot
"""

import cadquery as cq

# ISO 261 coarse pitch by nominal thread diameter, mm
_PITCH = {6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 16: 2.0, 20: 2.5, 24: 3.0}


def build(slot_w, thread_d, base_w, neck_w, base_h, neck_h, length, chamfer=0.0):
    # wide base (z = 0 .. base_h) + narrower neck on top (z = base_h .. +neck_h)
    base = cq.Workplane("XY").box(base_w, length, base_h, centered=(True, True, False))
    neck = (
        cq.Workplane("XY").workplane(offset=base_h)
        .box(neck_w, length, neck_h, centered=(True, True, False))
    )
    result = base.union(neck)

    if chamfer:
        # lead-in chamfer on the base underside (before the bore, on clean edges)
        result = result.edges("<Z").chamfer(chamfer)

    # threaded central bore: drill to the minor Ø, then cut a helical V-groove of
    # the coarse pitch out to the major Ø, leaving the thread crests at the minor Ø
    pitch = _PITCH[int(round(thread_d))]
    r_maj = thread_d / 2.0
    r_min = r_maj - 0.5413 * pitch          # ISO internal-thread minor: d - 1.0825*P
    total_h = base_h + neck_h
    result = result.faces(">Z").workplane().hole(2.0 * r_min)
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, total_h, r_min))
    groove = (
        cq.Workplane("XZ").center(r_min - 0.3, 0)
        .moveTo(0, -pitch / 2.0).lineTo(0.5413 * pitch + 0.3, 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=True)
    )
    result = result.cut(groove)

    return result
