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
start external metric V-thread (ISO 261 coarse pitch) over the tip length
thread_len_b, leaving a plain neck under the collar, with a lead-in chamfer at
the threaded end.

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
          thread_len_b, shank_len_l, n_knurls, knurl_depth):
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

    # raised collar (Ø ds) then the knurled head disk (Ø dk), stacked coaxially
    collar = cq.Workplane("XY").workplane(offset=l).circle(ds / 2.0).extrude(collar_h)
    head = cq.Workplane("XY").workplane(offset=z_disk_bot).circle(dk / 2.0).extrude(k)
    result = shank.union(collar).union(head)

    # small 45-degree chamfer on the head's free top outer edge (drawing dim c),
    # cut before the knurl so the top edge is still a clean circle to select
    result = result.faces(">Z").edges("%CIRCLE").chamfer(min(0.15 * k, 0.1 * dk))

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

    # external metric thread over the tip length b (single-start helical V-groove,
    # ISO 261 coarse pitch), leaving a plain neck under the collar; swept half a
    # pitch past the tip and cut flush by the chamfered shank end (isFrenet=False
    # for sweep stability).
    oc = 0.25 * pitch                        # overcut, keeps a constant 60-deg flank
    helix = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, b + 0.5 * pitch, r_maj))
    groove = (
        cq.Workplane("XZ").center(r_maj + oc, 0)
        .moveTo(0, -pitch / 2.0).lineTo(-(0.6134 * pitch + oc), 0).lineTo(0, pitch / 2.0)
        .close().sweep(helix, isFrenet=False).translate((0, 0, -0.5 * pitch))
    )
    result = result.cut(groove)

    return result
