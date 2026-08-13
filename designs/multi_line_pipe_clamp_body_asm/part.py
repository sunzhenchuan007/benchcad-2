"""STAUFF MLC multi-line pipe-clamp body halves."""

import math

import cadquery as cq


def _line_centres(line_count, pitch):
    return [(i - (line_count - 1) / 2.0) * pitch for i in range(line_count)]


def _passage_centres(line_count, span):
    if line_count in (2, 3, 4):
        return [-span / 2.0, span / 2.0]
    return [-span, 0.0, span]


def _modeled_internal_metric_thread_cutter(nominal_d, pitch, length):
    """Return a basic minor bore plus a visible 60-degree helical groove."""
    major_r = nominal_d / 2.0
    minor_r = (nominal_d - 1.082532 * pitch) / 2.0
    radial_embed = min(0.08, 0.05 * pitch)
    half_width = (major_r - minor_r + radial_embed) / math.sqrt(3.0)
    bore = (cq.Workplane("XY").workplane(offset=-0.05)
            .circle(minor_r).extrude(length + 0.10))
    path = cq.Wire.makeHelix(pitch, length + 2.0 * half_width, minor_r)
    profile = (cq.Workplane("XZ")
               .polyline([(minor_r - radial_embed, -half_width),
                          (major_r, 0.0),
                          (minor_r - radial_embed, half_width)])
               .close())
    groove = profile.sweep(path, isFrenet=True).translate((0.0, 0.0, -half_width))
    return bore.union(groove)


def build(line_count, group, tube_od, length, pitch, span, height,
          fastener_passage_count, body_depth, passage_d, counterbore_d,
          counterbore_depth, thread_nominal_d, thread_pitch,
          tension_clearance):
    """Build two separated halves; X=L1, Y=depth, Z=H."""
    del group
    half_h = (height - tension_clearance) / 2.0
    lower = (cq.Workplane("XY")
             .box(length, body_depth, half_h, centered=(True, True, False))
             .translate((0.0, 0.0, -height / 2.0)))
    upper = (cq.Workplane("XY")
             .box(length, body_depth, half_h, centered=(True, True, False))
             .translate((0.0, 0.0, tension_clearance / 2.0)))
    for x in _line_centres(line_count, pitch):
        seat = (cq.Workplane("XZ").center(x, 0.0).circle(tube_od / 2.0)
                .extrude(body_depth / 2.0 + 1.0, both=True))
        lower = lower.cut(seat)
        upper = upper.cut(seat)
    centres = _passage_centres(line_count, span)
    if len(centres) != fastener_passage_count:
        raise ValueError("passage count does not match topology")
    for x in centres:
        # The upper half remains a bolt-clearance passage. The lower half is
        # tapped from the split plane, after the outside-face counterbore.
        upper_through = (cq.Workplane("XY").workplane(offset=tension_clearance / 2.0 - 0.1)
                         .center(x, 0.0).circle(passage_d / 2.0)
                         .extrude(half_h + 0.2))
        upper = upper.cut(upper_through)
        tapped = (_modeled_internal_metric_thread_cutter(
            thread_nominal_d, thread_pitch, half_h + 0.2)
            .translate((x, 0.0, -height / 2.0 - 0.1)))
        lower = lower.cut(tapped)
        low_cb = (cq.Workplane("XY").workplane(offset=-height / 2.0 - 0.1)
                  .center(x, 0.0).circle(counterbore_d / 2.0)
                  .extrude(counterbore_depth + 0.1))
        up_cb = (cq.Workplane("XY").workplane(offset=height / 2.0 + 0.1)
                 .center(x, 0.0).circle(counterbore_d / 2.0)
                 .extrude(-(counterbore_depth + 0.1)))
        lower = lower.cut(low_cb)
        upper = upper.cut(up_cb)
    result = cq.Assembly(name="multi_line_pipe_clamp_body_asm")
    result.add(lower.val(), name="lower_half")
    result.add(upper.val(), name="upper_half")
    return result
