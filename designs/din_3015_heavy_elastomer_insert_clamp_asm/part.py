"""DIN 3015 Part 2 heavy clamp with one film-hinged elastomer insert."""

import cadquery as cq


def _half_blank(length, width, height, split_gap, corner_radius, upper):
    half_height = (height - split_gap) / 2.0
    split_z = split_gap / 2.0 if upper else -split_gap / 2.0
    direction = half_height if upper else -half_height
    blank = (
        cq.Workplane("XY")
        .workplane(offset=split_z)
        .rect(length, width)
        .extrude(direction)
    )
    return blank.edges("|Z").fillet(corner_radius)


def _transverse_cylinder(diameter, length):
    return (
        cq.Workplane("XZ")
        .circle(diameter / 2.0)
        .extrude(length / 2.0, both=True)
    )


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


def _outside_counterbore_cutter(
    mount_spacing, height, counterbore_d, counterbore_depth, upper
):
    outside_z = height / 2.0 + 0.05 if upper else -height / 2.0 - 0.05
    depth = -(counterbore_depth + 0.05) if upper else counterbore_depth + 0.05
    return (
        cq.Workplane("XY")
        .workplane(offset=outside_z)
        .pushPoints(_mounting_points(mount_spacing))
        .circle(counterbore_d / 2.0)
        .extrude(depth)
    )


def _insert_cavity_cutter(
    insert_outer_d,
    width,
    insert_width,
    radial_clearance,
    seat_groove_depth,
    seat_groove_width,
):
    cavity = _transverse_cylinder(
        insert_outer_d + 2.0 * radial_clearance, width + 2.0
    )
    for y_pos in (-0.28 * insert_width, 0.28 * insert_width):
        groove = _transverse_cylinder(
            insert_outer_d + 2.0 * seat_groove_depth,
            seat_groove_width,
        ).translate((0.0, y_pos, 0.0))
        cavity = cavity.union(groove)
    return cavity


def _clamp_half(
    length,
    mount_spacing,
    height,
    width,
    insert_outer_d,
    split_gap,
    radial_clearance,
    insert_width,
    seat_groove_depth,
    seat_groove_width,
    mount_hole_d,
    counterbore_d,
    counterbore_depth,
    corner_radius,
    upper,
):
    body = _half_blank(
        length, width, height, split_gap, corner_radius, upper
    )
    cavity = _insert_cavity_cutter(
        insert_outer_d,
        width,
        insert_width,
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
    return body.cut(cavity).cut(holes).cut(counterbores)


def _annular_lobe(
    pipe_od, insert_outer_d, insert_width, split_gap, upper
):
    ring = _transverse_cylinder(insert_outer_d, insert_width).cut(
        _transverse_cylinder(pipe_od, insert_width + 2.0)
    )
    half_extent = insert_outer_d
    centre_z = (
        split_gap / 2.0 + half_extent / 2.0
        if upper
        else -split_gap / 2.0 - half_extent / 2.0
    )
    clip = (
        cq.Workplane("XY")
        .box(2.0 * insert_outer_d, insert_width + 2.0, half_extent)
        .translate((0.0, 0.0, centre_z))
    )
    return ring.intersect(clip)


def _retention_bands(
    insert_outer_d,
    insert_width,
    split_gap,
    rib_height,
    rib_width,
):
    bands = None
    for y_pos in (-0.28 * insert_width, 0.28 * insert_width):
        shell = _transverse_cylinder(
            insert_outer_d + 2.0 * rib_height, rib_width
        ).cut(
            _transverse_cylinder(
                insert_outer_d - 0.2 * rib_height, rib_width + 0.2
            )
        )
        shell = shell.translate((0.0, y_pos, 0.0))
        upper = shell.intersect(
            cq.Workplane("XY")
            .box(
                2.0 * insert_outer_d,
                insert_width + 2.0,
                insert_outer_d,
            )
            .translate(
                (0.0, 0.0, split_gap / 2.0 + insert_outer_d / 2.0)
            )
        )
        lower = shell.intersect(
            cq.Workplane("XY")
            .box(
                2.0 * insert_outer_d,
                insert_width + 2.0,
                insert_outer_d,
            )
            .translate(
                (0.0, 0.0, -split_gap / 2.0 - insert_outer_d / 2.0)
            )
        )
        pair = upper.union(lower)
        bands = pair if bands is None else bands.union(pair)
    return bands


def _hinged_insert(
    pipe_od,
    insert_outer_d,
    insert_width,
    split_gap,
    hinge_thickness,
    hinge_overlap,
    rib_height,
    rib_width,
):
    upper_lobe = _annular_lobe(
        pipe_od, insert_outer_d, insert_width, split_gap, True
    )
    lower_lobe = _annular_lobe(
        pipe_od, insert_outer_d, insert_width, split_gap, False
    )

    # The bridge overlaps both lobes by ``hinge_overlap``. It is a real film
    # hinge joining two explicit semicircular lobes, not an implied slit in a
    # cylindrical ring.
    bridge = (
        cq.Workplane("XY")
        .box(
            hinge_thickness,
            insert_width,
            split_gap + 2.0 * hinge_overlap,
        )
        .translate(
            (-insert_outer_d / 2.0 + hinge_thickness / 2.0, 0.0, 0.0)
        )
    )
    bands = _retention_bands(
        insert_outer_d,
        insert_width,
        split_gap,
        rib_height,
        rib_width,
    )
    return upper_lobe.union(lower_lobe).union(bridge).union(bands)


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
    hinge_thickness,
    hinge_overlap,
    rib_height,
    rib_width,
):
    """Build the three physical catalog components in a fixed closed pose.

    Material codes and ``catalog_row`` preserve source metadata; this static
    geometry does not simulate polymer constitutive behaviour or hinge motion.
    """
    del catalog_row, body_material, insert_material, axial_clearance

    upper = _clamp_half(
        length,
        mount_spacing,
        height,
        width,
        insert_outer_d,
        split_gap,
        radial_clearance,
        insert_width,
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
        insert_width,
        seat_groove_depth,
        seat_groove_width,
        mount_hole_d,
        counterbore_d,
        counterbore_depth,
        corner_radius,
        False,
    )
    insert = _hinged_insert(
        pipe_od,
        insert_outer_d,
        insert_width,
        split_gap,
        hinge_thickness,
        hinge_overlap,
        rib_height,
        rib_width,
    )

    result = cq.Assembly(
        name="din_3015_heavy_elastomer_insert_clamp_asm"
    )
    result.add(upper, name="upper_half", color=cq.Color(0.18, 0.20, 0.22))
    result.add(lower, name="lower_half", color=cq.Color(0.18, 0.20, 0.22))
    result.add(insert, name="insert", color=cq.Color(0.10, 0.12, 0.11))
    return result
