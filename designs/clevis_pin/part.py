"""clevis_pin — the parametric part.

ISO 2341 clevis pin with head, form B (with a transverse split-pin / cotter
hole near the free end): a plain cylindrical shank of diameter d and length L
carrying a flat cylindrical HEAD (Ø dk ~ 1.5 d, height k ~ 0.4 d) at the top
end, and a transverse COTTER HOLE (Ø hd) drilled straight through the shank
near the free end so a split pin can retain it. The head underside and the
shank free end are lightly chamfered. Modelled as ONE connected solid on the
XY plane, extruded up +Z; bench2 derives each instance's stand-alone program.

    dk = head_d  ~ round(1.5 * d)              flat head diameter
    k  = head_h  ~ round(0.4 * d, 1) (min 1.5) head height
    hd = hole_d  ~ standard split-pin size (~0.25 d), e.g. d6->1.6, d10->2.5
"""

import cadquery as cq


def build(shank_d, length, head_d, head_h, hole_d):
    d, L, dk, k, hd = shank_d, length, head_d, head_h, hole_d

    # shank: plain cylinder Ø d from z = 0 (free end) up to z = L
    shank = cq.Workplane("XY").circle(d / 2.0).extrude(L)
    # flat head: a wider cylinder Ø dk seated on top of the shank (z = L .. L+k)
    head = cq.Workplane("XY").workplane(offset=L).circle(dk / 2.0).extrude(k)
    result = shank.union(head)

    # lightly chamfer the circular edges — head top/underside + shank free end
    result = result.edges("%CIRCLE").chamfer(0.12 * d)

    # transverse cotter hole through the shank, near the free end (z ~ 0.15 L).
    # Drilled on the XZ plane so its axis lies along Y (horizontal, perpendicular
    # to the pin axis); extruded 2*d from y = +d to y = -d so the drilled
    # cylinder fully crosses the Ø d shank (which spans y = -d/2 .. +d/2).
    zc = 0.15 * L
    hole = (
        cq.Workplane("XZ")
        .workplane(offset=-d)
        .center(0.0, zc)
        .circle(hd / 2.0)
        .extrude(2.0 * d)
    )
    result = result.cut(hole)

    return result
