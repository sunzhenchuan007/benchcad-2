"""STAUFF MLC multi-line pipe-clamp body halves."""

import math

import cadquery as cq


def _line_centres(line_count, pitch):
    return [(i - (line_count - 1) / 2.0) * pitch for i in range(line_count)]


def _passage_centres(line_count, span):
    if line_count in (2, 3, 4):
        return [-span / 2.0, span / 2.0]
    return [-span, 0.0, span]


def _weight_relief_cutter(length, body_depth, height, tension_clearance,
                          passage_centres, counterbore_d, upper):
    """Cut the STEP-visible perimeter, rib lattice, and fastener bosses."""
    half_h = (height - tension_clearance) / 2.0
    pocket_depth = 0.30 * half_h
    rim_width = max(1.5, 0.06 * body_depth)
    rib_width = max(1.5, 0.06 * body_depth)
    outside_z = height / 2.0 if upper else -height / 2.0
    z_start = outside_z - pocket_depth if upper else outside_z

    cutter = (cq.Workplane("XY")
              .box(length - 2.0 * rim_width,
                   body_depth - 2.0 * rim_width,
                   pocket_depth + 0.2,
                   centered=(True, True, False))
              .translate((0.0, 0.0, z_start - 0.1)))

    # A longitudinal rib joins all fastener lands. Cross-ribs at every
    # fastener axis and every intervening bay reproduce the molded lattice
    # without claiming the STEP's fine draft or tiny local radii.
    longitudinal = (cq.Workplane("XY")
                    .box(length, rib_width, pocket_depth + 0.4,
                         centered=(True, True, False))
                    .translate((0.0, 0.0, z_start - 0.2)))
    cutter = cutter.cut(longitudinal)

    cross_positions = list(passage_centres)
    cross_positions.extend((left + right) / 2.0
                           for left, right in zip(passage_centres,
                                                  passage_centres[1:]))
    for x_pos in cross_positions:
        cross_rib = (cq.Workplane("XY")
                     .box(rib_width, body_depth, pocket_depth + 0.4,
                          centered=(True, True, False))
                     .translate((x_pos, 0.0, z_start - 0.2)))
        cutter = cutter.cut(cross_rib)

    boss_radius = counterbore_d / 2.0 + max(1.2, 0.05 * body_depth)
    for x_pos in passage_centres:
        boss = (cq.Workplane("XY").workplane(offset=z_start - 0.2)
                .center(x_pos, 0.0).circle(boss_radius)
                .extrude(pocket_depth + 0.4))
        cutter = cutter.cut(boss)
    return cutter


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
    corner_radius = min(0.18 * body_depth, 0.08 * length)
    lower = (cq.Workplane("XY")
             .box(length, body_depth, half_h, centered=(True, True, False))
             .translate((0.0, 0.0, -height / 2.0))
             .edges("|Z").fillet(corner_radius))
    upper = (cq.Workplane("XY")
             .box(length, body_depth, half_h, centered=(True, True, False))
             .translate((0.0, 0.0, tension_clearance / 2.0))
             .edges("|Z").fillet(corner_radius))
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
    lower = lower.cut(_weight_relief_cutter(
        length, body_depth, height, tension_clearance, centres,
        counterbore_d, False))
    upper = upper.cut(_weight_relief_cutter(
        length, body_depth, height, tension_clearance, centres,
        counterbore_d, True))
    result = cq.Assembly(name="multi_line_pipe_clamp_body_asm")
    result.add(lower.val(), name="lower_half")
    result.add(upper.val(), name="upper_half")
    return result
