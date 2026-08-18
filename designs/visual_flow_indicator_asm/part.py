"""ELESA HVF inline visual flow indicator as ten fitted components."""

import cadquery as cq


def _rod_points(body_style, plan_l):
    if int(body_style) == 0:
        x = plan_l / 2.0 - 5.0
        return [(-x, 0.0), (x, 0.0)]
    x = plan_l / 2.0 - 7.0
    return [(-x, -x), (-x, x), (x, -x), (x, x)]


def _end_plate(
    body_style,
    plan_l,
    plan_b,
    plate_t,
    z0,
    sleeve_d,
    seal_seat_d,
    seal_from_top,
    rod_points,
    rod_hole_d,
):
    """One molded end with boss, seal, and tie-rod seats removed."""
    if int(body_style) == 0:
        plate = (
            cq.Workplane("XY")
            .workplane(offset=z0)
            .polyline(
                [
                    (-plan_l / 2.0, 0.0),
                    (0.0, plan_b / 2.0),
                    (plan_l / 2.0, 0.0),
                    (0.0, -plan_b / 2.0),
                ]
            )
            .close()
            .extrude(plate_t)
        )
    else:
        plate = (
            cq.Workplane("XY")
            .workplane(offset=z0)
            .box(plan_l, plan_l, plate_t, centered=(True, True, False))
            .edges("|Z")
            .fillet(4.0)
        )

    centre = (
        cq.Workplane("XY")
        .workplane(offset=z0 - 0.2)
        .circle(sleeve_d / 2.0)
        .extrude(plate_t + 0.4)
    )
    rod_holes = (
        cq.Workplane("XY")
        .workplane(offset=z0 - 0.2)
        .pushPoints(rod_points)
        .circle(rod_hole_d / 2.0)
        .extrude(plate_t + 0.4)
    )
    plate = plate.cut(centre).cut(rod_holes)

    # The O-ring minor radius is 0.9 mm and its centre is inset 0.55 mm.
    # A 1.5 mm seat therefore clears the complete ring while retaining the
    # axial shoulder that locates it against the glass tube.
    seat_depth = 1.5
    seat_z = z0 + plate_t if seal_from_top else z0
    seat_direction = -seat_depth if seal_from_top else seat_depth
    seal_seat = (
        cq.Workplane("XY")
        .workplane(offset=seat_z)
        .circle(seal_seat_d / 2.0)
        .extrude(seat_direction)
    )
    return plate.cut(seal_seat)


def _threaded_boss_local(
    thread_major_d,
    thread_pitch,
    thread_form,
    plate_t,
    boss_h,
    sleeve_d,
):
    """Female pipe boss with visible major/minor relief along local +Z."""
    sleeve = cq.Workplane("XY").circle(sleeve_d / 2.0).extrude(plate_t)
    hex_corner_d = thread_major_d + 12.0
    flange = (
        cq.Workplane("XY")
        .workplane(offset=plate_t)
        .polygon(6, hex_corner_d)
        .extrude(boss_h)
    )
    boss = sleeve.union(flange)

    diametral_thread_depth = 1.28 if int(thread_form) == 0 else 1.60
    root_d = thread_major_d - diametral_thread_depth * thread_pitch
    total_h = plate_t + boss_h
    root_bore = (
        cq.Workplane("XY")
        .workplane(offset=-0.3)
        .circle(root_d / 2.0)
        .extrude(total_h + 0.6)
    )
    boss = boss.cut(root_bore)

    entrance = (
        cq.Workplane("XY")
        .workplane(offset=total_h - 1.15 * thread_pitch)
        .circle(thread_major_d / 2.0)
        .extrude(1.2 * thread_pitch)
    )
    boss = boss.cut(entrance)

    for index in range(1, 4):
        depth = (index + 0.8) * thread_pitch
        taper = depth / 16.0 if int(thread_form) == 1 else 0.0
        groove_d = thread_major_d - taper
        groove = (
            cq.Workplane("XY")
            .workplane(offset=total_h - depth - 0.22 * thread_pitch)
            .circle(groove_d / 2.0)
            .extrude(0.44 * thread_pitch)
        )
        boss = boss.cut(groove)
    return boss


def _tie_rod(rod_d, screw_shank_d, z0, length):
    """One hollow stainless tie rod located between the molded ends."""
    outer = cq.Workplane("XY").workplane(offset=z0).circle(rod_d / 2.0).extrude(length)
    bore = (
        cq.Workplane("XY")
        .workplane(offset=z0 - 0.1)
        .circle((screw_shank_d + 0.3) / 2.0)
        .extrude(length + 0.2)
    )
    return outer.cut(bore)


def _through_screw(screw_shank_d, head_d, shank_z0, shank_length, head_h):
    """One through screw with a shallow hexagonal drive recess."""
    shank = (
        cq.Workplane("XY")
        .workplane(offset=shank_z0)
        .circle(screw_shank_d / 2.0)
        .extrude(shank_length)
    )
    head_z0 = shank_z0 + shank_length
    head = cq.Workplane("XY").workplane(offset=head_z0).circle(head_d / 2.0).extrude(head_h)
    socket = (
        cq.Workplane("XY")
        .workplane(offset=head_z0 + 0.62 * head_h)
        .polygon(6, 0.52 * head_d)
        .extrude(0.4 * head_h)
    )
    return shank.union(head).cut(socket)


def _retaining_nut(screw_shank_d, nut_corner_d, z0, nut_h):
    """One hexagonal retaining nut below the lower molded end."""
    nut = cq.Workplane("XY").workplane(offset=z0).polygon(6, nut_corner_d).extrude(nut_h)
    bore = (
        cq.Workplane("XY")
        .workplane(offset=z0 - 0.1)
        .circle((screw_shank_d + 0.25) / 2.0)
        .extrude(nut_h + 0.2)
    )
    return nut.cut(bore)


def _seal_ring(tube_od, z):
    ring = cq.Solid.makeTorus(
        tube_od / 2.0 + 1.2,
        0.9,
        cq.Vector(0.0, 0.0, z),
        cq.Vector(0.0, 0.0, 1.0),
    )
    return cq.Workplane(obj=ring)


def build(
    catalog_row,
    material_code,
    thread_form,
    thread_size_code,
    body_style,
    rod_count,
    thread_major_d,
    thread_pitch,
    overall_h,
    plan_l,
    plan_b,
    window_h1,
    rod_spacing_s,
    rotor_angle,
):
    """Build end bodies, glass, rotor, axle, bosses, seals, and tie cage."""
    del catalog_row, thread_size_code

    end_stack = (overall_h - window_h1) / 2.0
    plate_t = 0.36 * end_stack
    boss_h = end_stack - plate_t
    tube_od = rod_spacing_s
    tube_wall = 2.0
    tube_inner_d = tube_od - 2.0 * tube_wall
    sleeve_d = thread_major_d + 5.0
    seal_seat_d = tube_od + 5.0
    rod_d = 3.6 if int(body_style) == 0 else 4.4
    rod_points = _rod_points(body_style, plan_l)

    lower_inner_z = -window_h1 / 2.0
    lower_outer_z = lower_inner_z - plate_t
    upper_inner_z = window_h1 / 2.0

    lower_end = _end_plate(
        body_style,
        plan_l,
        plan_b,
        plate_t,
        lower_outer_z,
        sleeve_d,
        seal_seat_d,
        True,
        rod_points,
        rod_d + 0.6,
    )
    upper_end = _end_plate(
        body_style,
        plan_l,
        plan_b,
        plate_t,
        upper_inner_z,
        sleeve_d,
        seal_seat_d,
        False,
        rod_points,
        rod_d + 0.6,
    )

    glass = (
        cq.Workplane("XY")
        .workplane(offset=lower_inner_z)
        .circle(tube_od / 2.0)
        .circle(tube_inner_d / 2.0)
        .extrude(window_h1)
    )

    boss_local = _threaded_boss_local(
        thread_major_d,
        thread_pitch,
        thread_form,
        plate_t,
        boss_h,
        sleeve_d,
    )
    upper_boss = boss_local.translate((0.0, 0.0, upper_inner_z))
    lower_boss = boss_local.mirror("XY").translate((0.0, 0.0, lower_inner_z))

    lower_seal = _seal_ring(tube_od, lower_inner_z - 0.55)
    upper_seal = _seal_ring(tube_od, upper_inner_z + 0.55)

    if len(rod_points) != int(rod_count):
        raise ValueError("rod_count must match the selected end-body layout")

    screw_shank_d = 0.46 * rod_d
    head_d = rod_d + 2.2
    head_h = 0.42 * rod_d
    nut_h = 0.55 * rod_d
    nut_corner_d = rod_d + 2.4
    upper_outer_z = upper_inner_z + plate_t
    screw_z0 = lower_outer_z - 0.35 * nut_h
    screw_length = upper_outer_z - screw_z0

    tie_rods = []
    screws = []
    nuts = []
    for x, y in rod_points:
        offset = (x, y, 0.0)
        tie_rods.append(
            _tie_rod(rod_d, screw_shank_d, lower_inner_z, window_h1).translate(offset)
        )
        screws.append(
            _through_screw(screw_shank_d, head_d, screw_z0, screw_length, head_h).translate(offset)
        )
        nuts.append(
            _retaining_nut(
                screw_shank_d,
                nut_corner_d,
                lower_outer_z - nut_h,
                nut_h,
            ).translate(offset)
        )

    axle_d = 2.2
    axle = (
        cq.Workplane("XY")
        .workplane(offset=lower_inner_z)
        .circle(axle_d / 2.0)
        .extrude(window_h1)
    )

    rotor_h = window_h1 - 4.0
    hub = (
        cq.Workplane("XY")
        .workplane(offset=-rotor_h / 2.0)
        .circle(2.6)
        .extrude(rotor_h)
    )
    blade_length = tube_inner_d - 2.4
    blade_width = 3.0
    blade_t = 1.1
    blade_pitch = 32.0
    blade_lower = (
        cq.Workplane("XY")
        .box(blade_length, blade_width, blade_t, centered=(True, True, True))
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), blade_pitch)
        .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), rotor_angle)
        .translate((0.0, 0.0, -0.24 * rotor_h))
    )
    blade_upper = (
        cq.Workplane("XY")
        .box(blade_length, blade_width, blade_t, centered=(True, True, True))
        .rotate((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), blade_pitch)
        .rotate(
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
            rotor_angle + 90.0,
        )
        .translate((0.0, 0.0, 0.24 * rotor_h))
    )
    rotor = hub.union(blade_lower).union(blade_upper)
    rotor_bore = (
        cq.Workplane("XY")
        .workplane(offset=-rotor_h / 2.0 - 0.2)
        .circle(1.4)
        .extrude(rotor_h + 0.4)
    )
    rotor = rotor.cut(rotor_bore)

    result = cq.Assembly(name="visual_flow_indicator_asm")
    result.add(lower_end, name="end_body_01", color=cq.Color(0.10, 0.11, 0.12))
    result.add(upper_end, name="end_body_02", color=cq.Color(0.10, 0.11, 0.12))
    result.add(glass, name="tubular_window", color=cq.Color(0.72, 0.92, 0.96))
    result.add(rotor, name="rotor_propeller", color=cq.Color(0.86, 0.12, 0.14))
    result.add(axle, name="rotor_axle", color=cq.Color(0.82, 0.18, 0.18))
    boss_color = cq.Color(0.72, 0.54, 0.25) if int(material_code) == 0 else cq.Color(0.68, 0.71, 0.73)
    result.add(lower_boss, name="threaded_boss_01", color=boss_color)
    result.add(upper_boss, name="threaded_boss_02", color=boss_color)
    result.add(lower_seal, name="end_seal_01", color=cq.Color(0.08, 0.08, 0.08))
    result.add(upper_seal, name="end_seal_02", color=cq.Color(0.08, 0.08, 0.08))
    for index, tie_rod in enumerate(tie_rods, start=1):
        result.add(tie_rod, name=f"tie_rod_{index:02d}", color=cq.Color(0.65, 0.68, 0.70))
    for index, screw in enumerate(screws, start=1):
        result.add(screw, name=f"screw_{index:02d}", color=cq.Color(0.62, 0.64, 0.66))
    for index, nut in enumerate(nuts, start=1):
        result.add(nut, name=f"nut_{index:02d}", color=cq.Color(0.62, 0.64, 0.66))
    return result
