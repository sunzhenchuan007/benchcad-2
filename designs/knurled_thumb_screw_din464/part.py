"""knurled_thumb_screw_din464 — the parametric part.

DIN 464 knurled thumb screw, high type: a tall KNURLED cylindrical head you grip
and turn by hand, sitting on a raised collar over a metric threaded shank. Built
bottom (thread tip) to top (head), coaxial on +Z:

    thread tip        z = 0
    threaded shank    z = 0 .. shank_len_l              (Ø thread_dia_d)
    collar / shoulder z = l .. l + (h - k)              (Ø collar_dia_ds)
    knurled head disk z = l + (h - k) .. l + h          (Ø head_dia_dk, height k)

Head = a plain cylinder; the KNURL is n_knurls shallow axial flutes cut evenly
around the head rim over the knurl band k — a straight knurl, approximated by
vertical slots (fast + stays one solid). A small 45-degree chamfer (drawing dim
c) breaks the head's free top outer edge. The shank carries a modelled single-
external metric thread (ISO 261 coarse pitch, revolved 60-deg V-rings) over the
tip length thread_len_b, leaving a plain neck under the collar, with a lead-in
chamfer at the threaded end. The drawing's r fillet blends the collar into the
head-disk underside and the c chamfer profiles both disk rims.

Drawing-symbol glossary (DIN 464):
    thread_dia_d   d   nominal metric thread diameter
    head_dia_dk    dk  knurled head outer diameter
    collar_dia_ds  ds  collar / raised shoulder diameter
    head_h         h   total head height (knurled disk + collar)
    knurl_band_k   k   height of the knurled disk (the knurl band)
    thread_len_b   b   threaded length measured from the tip
    shank_len_l    l   shank length under the collar (free stock length)
    n_knurls       -   number of straight-knurl flutes around the rim
    knurl_depth    -   radial depth of each knurl flute
"""

import math

import cadquery as cq

# ISO 261 coarse pitch by nominal thread diameter, mm (DIN 464 range M1..M10)
_PITCH = {1: 0.25, 2: 0.4, 3: 0.5, 4: 0.7, 5: 0.8, 6: 1.0, 8: 1.25, 10: 1.5}


def build(thread_dia_d, head_dia_dk, collar_dia_ds, head_h, knurl_band_k,
          thread_len_b, shank_len_l, collar_fillet_r, n_knurls, knurl_depth):
    d, dk, ds, h = thread_dia_d, head_dia_dk, collar_dia_ds, head_h
    k, b, l = knurl_band_k, thread_len_b, shank_len_l
    n = int(round(n_knurls))
    kd = knurl_depth
    pitch = _PITCH[int(round(d))]
    r_maj = d / 2.0

    collar_h = h - k                 # raised shoulder height (the disk is the top k)
    z_disk_bot = l + collar_h        # underside of the knurled head disk

    # threaded shank, z = 0 .. l, with a lead-in chamfer at the tip
    shank = cq.Workplane("XY").circle(d / 2.0).extrude(l)
    shank = shank.faces("<Z").chamfer(1.0 * pitch)

    # raised collar (Ø ds) then the knurled head disk (Ø dk), stacked coaxially.
    # The drawing's c chamfer profiles BOTH disk rims — cut them on the bare
    # disk before the union so the edges are clean circles to select.
    c_ch = min(0.15 * k, 0.1 * dk)
    collar = cq.Workplane("XY").workplane(offset=l).circle(ds / 2.0).extrude(collar_h)
    head = cq.Workplane("XY").workplane(offset=z_disk_bot).circle(dk / 2.0).extrude(k)
    head = head.faces(">Z").edges("%CIRCLE").chamfer(c_ch)
    head = head.faces("<Z").edges("%CIRCLE").chamfer(c_ch)
    result = shank.union(collar).union(head)

    # drawing dim r: fillet where the collar meets the head-disk underside —
    # the circular seam at (Ø ds, z_disk_bot); the disk rim sits outside the
    # selector box so only the seam is caught
    result = result.edges(
        cq.selectors.BoxSelector(
            (-(ds / 2.0 + 0.2), -(ds / 2.0 + 0.2), z_disk_bot - 0.05),
            (ds / 2.0 + 0.2, ds / 2.0 + 0.2, z_disk_bot + 0.05))
    ).fillet(collar_fillet_r)

    # straight knurl: n shallow axial flutes evenly around the head rim, cut over
    # the knurl band k. Flute width = half the rim pitch so equal lands remain and
    # the head stays ONE connected solid. Built as one compound -> a single cut.
    gw = 0.5 * math.pi * dk / n
    flutes = []
    for i in range(n):
        ang = 360.0 / n * i
        flute = (
            cq.Workplane("XY").workplane(offset=z_disk_bot - 0.1)
            .transformed(rotate=(0, 0, ang)).center(dk / 2.0, 0.0)
            .rect(2.0 * kd, gw).extrude(k + 0.2)
        )
        flutes.append(flute.val())
    result = result.cut(cq.Compound.makeCompound(flutes))

    # external metric thread over the tip length b as revolved 60-deg V-rings
    # (the swept helix silently no-ops on the M6 and M8 rows), leaving a plain
    # neck under the collar. The stack over-runs the tip so the lead-in chamfer
    # cuts the run-out flush; the last crest stays at or below z = b.
    oc = 0.25 * pitch                        # overcut, keeps a constant 60-deg flank
    ro = r_maj + oc
    ra = r_maj - 0.6134 * pitch
    n_teeth = max(1, int(b / pitch + 0.5))
    pts = [(ro + 0.5, -1.5 * pitch), (ro, -1.5 * pitch)]
    for i in range(-1, n_teeth):
        pts += [(ra, i * pitch), (ro, (i + 0.5) * pitch)]
    pts.append((ro + 0.5, (n_teeth - 0.5) * pitch))
    grooves = cq.Workplane("XZ").polyline(pts).close().revolve(360.0, (0, 0), (0, 1))
    result = result.cut(grooves)

    return result
