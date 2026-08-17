"""NAS6203 through NAS6220 close-tolerance tension bolt.

The bolt is built on the Z axis with a washed hex head, close-tolerance plain
grip and a short, reduced-major-diameter UNJF thread.  The thread is a real
single-start helical V groove; catalog grip remains smooth and cylindrical.
"""

import math

import cadquery as cq


def build(
    head_af,
    head_height,
    bearing_d,
    shank_d,
    thread_major_d,
    thread_pitch,
    grip_length,
    thread_length,
):
    across_corners = head_af * 2.0 / math.sqrt(3.0)

    # NAS Figure 1 draws C across flats.  The conical intersection gives the
    # characteristic circular washout on the free face of the hex head.
    head = cq.Workplane("XY").polygon(6, across_corners).extrude(head_height)
    washout_depth = 0.22 * head_height
    top_r = head_af / 2.0
    corner_r = across_corners / 2.0
    bottom_r = (
        corner_r - (1.0 - washout_depth / head_height) * top_r
    ) / (washout_depth / head_height)
    washout = (
        cq.Workplane("XY")
        .circle(bottom_r)
        .workplane(offset=head_height)
        .circle(top_r)
        .loft()
    )
    head = head.intersect(washout)

    # Figure 1 gives the thin under-head land as .020 +/- .005 in.  E controls
    # its diameter while D controls the close-tolerance grip cylinder.
    land_h = 0.508
    bearing_land = cq.Workplane("XY").circle(bearing_d / 2.0).extrude(-land_h)
    grip = cq.Workplane("XY").circle(shank_d / 2.0).extrude(-grip_length)

    thread = (
        cq.Workplane("XY")
        .workplane(offset=-grip_length)
        .circle(thread_major_d / 2.0)
        .extrude(-thread_length)
    )
    lead = min(0.75 * thread_pitch, 0.20 * thread_major_d)
    thread = thread.faces("<Z").chamfer(lead)

    result = head.union(bearing_land).union(grip).union(thread)

    # External UNJF representation: single-start 60-degree helical groove over
    # only dimension T, with a half-pitch run-out into the plain-grip junction.
    r_major = thread_major_d / 2.0
    helix = cq.Workplane("XY").add(
        cq.Wire.makeHelix(
            thread_pitch,
            thread_length + 0.5 * thread_pitch,
            r_major,
        )
    )
    groove = (
        cq.Workplane("XZ")
        .center(r_major + 0.25, 0.0)
        .moveTo(0.0, -thread_pitch / 2.0)
        .lineTo(-(0.55 * thread_pitch + 0.25), 0.0)
        .lineTo(0.0, thread_pitch / 2.0)
        .close()
        .sweep(helix, isFrenet=False)
        .translate((0.0, 0.0, -(grip_length + thread_length)))
    )
    result = result.cut(groove)
    return result
