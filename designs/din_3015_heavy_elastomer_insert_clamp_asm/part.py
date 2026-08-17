"""DIN 3015 Part 2 heavy clamp with one stepped elastomer insert."""

import cadquery as cq


def _half_blank(length, width, height, split_gap, corner_radius, upper):
    """Return one molded half in the construction frame (height along Z)."""
    half_height = (height - split_gap) / 2.0
    split_z = split_gap / 2.0 if upper else -split_gap / 2.0
    direction = half_height if upper else -half_height
    blank = cq.Workplane("XY").workplane(offset=split_z).rect(length, width).extrude(direction)
    return blank.edges("|Z").fillet(corner_radius)


def _transverse_cylinder(diameter, length):
    """Return a cylinder whose axis follows construction-frame Y."""
    return cq.Workplane("XZ").circle(diameter / 2.0).extrude(length / 2.0, both=True)


def _mounting_points(mount_spacing):
    return [(-mount_spacing / 2.0, 0.0), (mount_spacing / 2.0, 0.0)]


def _mounting_hole_cutter(mount_spacing, height, mount_hole_d):
    return (
        cq.Workplane("XY")
        .workplane(offset=-height / 2.0 - 1.0)
        .pushPoints(_mounting_points(mount_spacing))
        .circle(mount_hole_d / 2.0)
        .extrude(height + 2.0)
    )


def _outside_counterbore_cutter(mount_spacing, height, counterbore_d, counterbore_depth, upper):
    outside_z = height / 2.0 + 0.05 if upper else -height / 2.0 - 0.05
    depth = -(counterbore_depth + 0.05) if upper else counterbore_depth + 0.05
    return (
        cq.Workplane("XY")
        .workplane(offset=outside_z)
        .pushPoints(_mounting_points(mount_spacing))
        .circle(counterbore_d / 2.0)
        .extrude(depth)
    )


def _molded_relief_cutter(
    length,
    width,
    height,
    split_gap,
    mount_spacing,
    counterbore_d,
    upper,
):
    """Cut the deep perimeter/rib/boss lattice present on each outside face."""
    half_height = (height - split_gap) / 2.0
    pocket_depth = 0.408 * half_height
    edge_wall = max(2.0, 0.08 * width)
    z_start = height / 2.0 - pocket_depth if upper else -height / 2.0

    cutter = (
        cq.Workplane("XY")
        .box(
            length - 2.0 * edge_wall,
            width - 2.0 * edge_wall,
            pocket_depth + 0.2,
            centered=(True, True, False),
        )
        .translate((0.0, 0.0, z_start - 0.1))
    )

    centre_rib = (
        cq.Workplane("XY")
        .box(
            length,
            0.085 * width,
            pocket_depth + 0.4,
            centered=(True, True, False),
        )
        .translate((0.0, 0.0, z_start - 0.2))
    )
    cutter = cutter.cut(centre_rib)

    transverse_rib_width = max(2.0, 0.08 * width)
    for x_pos in (-mount_spacing / 2.0, 0.0, mount_spacing / 2.0):
        rib = (
            cq.Workplane("XY")
            .box(
                transverse_rib_width,
                width,
                pocket_depth + 0.4,
                centered=(True, True, False),
            )
            .translate((x_pos, 0.0, z_start - 0.2))
        )
        cutter = cutter.cut(rib)

    boss_radius = counterbore_d / 2.0 + 0.09 * width
    for x_pos, _ in _mounting_points(mount_spacing):
        boss = (
            cq.Workplane("XY")
            .workplane(offset=z_start - 0.2)
            .center(x_pos, 0.0)
            .circle(boss_radius)
            .extrude(pocket_depth + 0.4)
        )
        cutter = cutter.cut(boss)
    return cutter


def _insert_cavity_cutter(
    insert_outer_d,
    width,
    radial_clearance,
    seat_groove_depth,
    seat_groove_width,
):
    """Match the full-width insert core and its single central retention band."""
    core = _transverse_cylinder(
        insert_outer_d + 2.0 * radial_clearance,
        width + 2.0,
    )
    centre_band = _transverse_cylinder(
        insert_outer_d + 2.0 * seat_groove_depth,
        seat_groove_width,
    )
    return core.union(centre_band)


def _clamp_half(
    length,
    mount_spacing,
    height,
    width,
    insert_outer_d,
    split_gap,
    radial_clearance,
    seat_groove_depth,
    seat_groove_width,
    mount_hole_d,
    counterbore_d,
    counterbore_depth,
    corner_radius,
    upper,
):
    body = _half_blank(length, width, height, split_gap, corner_radius, upper)
    cavity = _insert_cavity_cutter(
        insert_outer_d,
        width,
        radial_clearance,
        seat_groove_depth,
        seat_groove_width,
    )
    holes = _mounting_hole_cutter(mount_spacing, height, mount_hole_d)
    counterbores = _outside_counterbore_cutter(
        mount_spacing,
        height,
        counterbore_d,
        counterbore_depth,
        upper,
    )
    molded_relief = _molded_relief_cutter(
        length,
        width,
        height,
        split_gap,
        mount_spacing,
        counterbore_d,
        upper,
    )
    return body.cut(cavity).cut(holes).cut(counterbores).cut(molded_relief)


def _stepped_insert(
    pipe_od,
    insert_outer_d,
    insert_width,
    rib_height,
    rib_width,
):
    """Build the STEP-observed annular core and one wider central band."""
    core = _transverse_cylinder(insert_outer_d, insert_width)
    centre_band = _transverse_cylinder(
        insert_outer_d + 2.0 * rib_height,
        rib_width,
    )
    stepped_blank = core.union(centre_band)

    # Match the Part-1 reference strategy: cut one cylinder through the full
    # finished width after all insert sections have been fused.  This leaves a
    # single continuous pipe bore through both the core and central band.
    bore = _transverse_cylinder(pipe_od, insert_width + 2.0)
    return stepped_blank.cut(bore)


def build(
    catalog_row,
    pipe_od,
    insert_outer_d,
    length,
    mount_spacing,
    height,
    width,
    body_material,
    insert_material,
    split_gap,
    radial_clearance,
    axial_clearance,
    insert_width,
    seat_groove_depth,
    seat_groove_width,
    mount_hole_d,
    counterbore_d,
    counterbore_depth,
    corner_radius,
    rib_height,
    rib_width,
):
    """Build the two molded halves and one stepped annular insert."""
    del catalog_row, body_material, insert_material, axial_clearance

    upper = _clamp_half(
        length,
        mount_spacing,
        height,
        width,
        insert_outer_d,
        split_gap,
        radial_clearance,
        seat_groove_depth,
        seat_groove_width,
        mount_hole_d,
        counterbore_d,
        counterbore_depth,
        corner_radius,
        True,
    )
    lower = _clamp_half(
        length,
        mount_spacing,
        height,
        width,
        insert_outer_d,
        split_gap,
        radial_clearance,
        seat_groove_depth,
        seat_groove_width,
        mount_hole_d,
        counterbore_d,
        counterbore_depth,
        corner_radius,
        False,
    )
    insert = _stepped_insert(
        pipe_od,
        insert_outer_d,
        insert_width,
        rib_height,
        rib_width,
    )

    # Align with the supplied 4006_PPR STEP: X=length, Y=height, Z=width.
    rotation_axis = ((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), -90.0)
    upper = upper.rotate(*rotation_axis)
    lower = lower.rotate(*rotation_axis)
    insert = insert.rotate(*rotation_axis)

    result = cq.Assembly(name="din_3015_heavy_elastomer_insert_clamp_asm")
    result.add(upper, name="upper_half", color=cq.Color(0.18, 0.20, 0.22))
    result.add(lower, name="lower_half", color=cq.Color(0.18, 0.20, 0.22))
    result.add(insert, name="insert", color=cq.Color(0.10, 0.12, 0.11))
    return result
