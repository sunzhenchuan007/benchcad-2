"""example_tee_bracket — the parametric part (BenchCAD 2.0 reference).

A T-section mounting bracket: a flange plate with a central web standing on it,
optionally bolted through the flange, with a chamfered web top on hard parts.
This is what a contributor writes: plain parametric CadQuery, named parameters,
no dictionaries and no code generation. `bench2` derives each instance's
stand-alone program from this body (arguments become module globals, the
_hole_layout helper is inlined).

Chosen as the reference because it exercises the whole interface in a part
anyone can picture: continuous dimensions, an integer feature (bolt holes), and
a hard-only feature (chamfer). This family is a TEACHING ARTIFACT — it does not
enter the released dataset.
"""

import cadquery as cq


def _hole_layout(flange_w, web_t, length, hole_d):
    """Bolt-hole positions: the lateral offset onto each exposed flange strip,
    and the axial offset used by the 4-hole pattern. Shared with the family's
    edge-distance checks (spec.py imports it) so build and check never drift."""
    y_off = (flange_w + web_t) / 4.0                 # mid-line of each flange strip
    x_off = length / 2.0 - max(2.0 * hole_d, 8.0)    # end margin >= 2d (>= 8 mm)
    return y_off, x_off


def build(length, flange_w, flange_t, web_h, web_t, n_holes, hole_d, chamfer_c):
    # flange plate on the XY plane, web standing on its centerline
    flange = cq.Workplane("XY").box(
        length, flange_w, flange_t, centered=(True, True, False)
    )
    web = cq.Workplane("XY").workplane(offset=flange_t).box(
        length, web_t, web_h, centered=(True, True, False)
    )
    result = flange.union(web)

    if n_holes:
        y_off, x_off = _hole_layout(flange_w, web_t, length, hole_d)
        if n_holes == 2:
            pts = [(0.0, y_off), (0.0, -y_off)]
        else:
            pts = [(x, y) for x in (x_off, -x_off) for y in (y_off, -y_off)]
        # bolt holes through the flange, clear of the web
        result = result.faces("<Z").workplane().pushPoints(pts).hole(hole_d)

    if chamfer_c:
        # deburr chamfer on the web top edges
        result = result.edges(">Z").chamfer(chamfer_c)

    return result
