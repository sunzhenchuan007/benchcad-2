"""hex_bolt_2 — the parametric part.

Hex-head bolt, ISO 4014 (hexagon head + partially-threaded shank). The head is a
hexagonal prism with width `head_af` across the flats and height `head_h`; the
shank is a cylinder of the nominal thread diameter with a smooth portion under
the head and an external metric thread over the tip length b ≈ 2d + 6 (ISO 4014),
so the free end is threaded and the grip stays plain. The thread is the ISO 261
coarse pitch with the external minor Ø d - 2*0.6134*P. A head top chamfer appears
on the hard tier. Plain parametric CadQuery.

The thread is modelled by REVOLVING a sawtooth section (crest at the major Ø,
root at the minor Ø, one V per pitch) rather than sweeping a helix: a single
revolve is robust for every size/length, whereas a swept helix silently fails to
cut for some (d, length) pairs (it left a few medium instances un-threaded). The
lead angle of a single-start thread is negligible.

    across-corners = head_af / cos(30°) = head_af * 2/sqrt(3)   (polygon diameter)
"""

import math

import cadquery as cq

# ISO 261 coarse pitch by nominal thread diameter, mm
_PITCH = {4: 0.7, 5: 0.8, 6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 14: 2.0, 16: 2.0,
          20: 2.5, 24: 3.0}


def build(thread_d, head_af, head_h, length, head_chamfer=0.0):
    # hexagonal head (across-flats head_af) sitting on z = 0 .. head_h
    across_corners = head_af * 2.0 / math.sqrt(3.0)
    head = cq.Workplane("XY").polygon(6, across_corners).extrude(head_h)

    # shank (z = 0 .. -length): a smooth grip under the head, then a threaded tip
    # of length b ≈ 2d + 6 (ISO 4014). Built as one revolved sawtooth section.
    pitch = _PITCH[int(round(thread_d))]
    r_maj = thread_d / 2.0
    r_min = r_maj - 0.6134 * pitch          # ISO external-thread root radius
    thread_len = min(length, 2.0 * thread_d + 6.0)
    z0 = -(length - thread_len)             # where the thread starts (0 if fully threaded)

    pts = [(0.0, 0.0), (r_maj, 0.0)]
    if length - thread_len > 1e-6:
        pts.append((r_maj, z0))             # smooth grip down to the thread start
    k = 0
    z = z0
    while z > -length + 1e-9:
        pts.append((r_min, max(z0 - (k + 0.5) * pitch, -length)))     # root
        z = max(z0 - (k + 1.0) * pitch, -length)
        pts.append((r_maj, z))                                        # crest
        k += 1
    pts.append((0.0, -length))
    shank = cq.Workplane("XZ").polyline(pts).close().revolve(360)

    result = head.union(shank)

    if head_chamfer:
        # chamfer the top face of the head (ISO 4014 head top chamfer)
        result = result.faces(">Z").chamfer(head_chamfer)

    return result
