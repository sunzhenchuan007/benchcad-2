"""Independent CadQuery reconstruction of NEXUS NM mecanum wheels.

Official STEP files are measurement evidence only.  The output geometry is a
compact sandwich assembly: two mostly closed circular side plates, one stepped
central hub, eight 45-degree barrel rollers captured between the plates, and
eight coaxial pins.  No manufacturer geometry is imported by ``build()``.
"""

import math

import cadquery as cq


ROLLER_ANGLES = tuple(i * 45.0 for i in range(8))
ALL_BOLT_ANGLES = tuple(i * 45.0 for i in range(8))

# STEP-measured, catalog-derived construction data.  These are deliberately
# not independent random parameters.
CATALOG_DETAILS = {
    0: dict(
        hub_face_d=30.0,
        hub_length=62.0,
        bolt_pcd=40.0,
        hub_bolt_d=4.2,
        plate_bolt_d=5.0,
        counterbore_d=9.0,
        bolt_angle_offset=0.0,
        step_width=68.74,
        roller_profile_d=(28.0, 26.635, 24.917, 22.488, 21.001, 19.327),
    ),
    1: dict(
        hub_face_d=45.0,
        hub_length=76.0,
        bolt_pcd=58.0,
        hub_bolt_d=4.2,
        plate_bolt_d=5.0,
        counterbore_d=9.0,
        bolt_angle_offset=0.0,
        step_width=80.0,
        roller_profile_d=(33.0, 31.278, 29.109, 26.043, 24.163, 20.818),
    ),
    2: dict(
        hub_face_d=45.0,
        hub_length=101.0,
        bolt_pcd=58.0,
        hub_bolt_d=4.2,
        plate_bolt_d=5.0,
        counterbore_d=9.0,
        bolt_angle_offset=0.0,
        step_width=106.70,
        roller_profile_d=(43.0, 40.611, 37.600, 33.343, 30.734, 27.795),
    ),
    3: dict(
        hub_face_d=60.0,
        hub_length=122.0,
        bolt_pcd=80.0,
        hub_bolt_d=6.8,
        plate_bolt_d=8.0,
        counterbore_d=15.0,
        bolt_angle_offset=22.5,
        step_width=132.25,
        roller_profile_d=(56.0, 53.079, 49.400, 44.199, 41.012, 37.422),
    ),
    4: dict(
        hub_face_d=75.0,
        hub_length=152.0,
        bolt_pcd=100.0,
        hub_bolt_d=8.5,
        plate_bolt_d=10.0,
        counterbore_d=18.0,
        bolt_angle_offset=22.5,
        step_width=160.05,
        roller_profile_d=(68.5, 64.793, 60.122, 53.515, 49.463, 44.898),
    ),
}


def _x_cylinder(diameter, length):
    return cq.Solid.makeCylinder(
        diameter / 2.0,
        length,
        cq.Vector(-length / 2.0, 0.0, 0.0),
        cq.Vector(1.0, 0.0, 0.0),
    )


def _z_cylinder(diameter, length, z_start):
    return cq.Solid.makeCylinder(
        diameter / 2.0,
        length,
        cq.Vector(0.0, 0.0, z_start),
        cq.Vector(0.0, 0.0, 1.0),
    )


def _cut_each(shape, cutters):
    for cutter in cutters:
        shape = shape.cut(cutter)
    return shape


def _axis_vector(circumferential_angle, skew_angle):
    """Unit roller axis: local rim tangent plus the handed axial slope."""
    tangent = math.radians(circumferential_angle + 90.0)
    skew = math.radians(skew_angle)
    return (
        math.cos(skew) * math.cos(tangent),
        math.cos(skew) * math.sin(tangent),
        math.sin(skew),
    )


def _orient_x(shape, circumferential_angle, skew_angle, center):
    placed = shape.rotate(
        (0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        -float(skew_angle),
    )
    placed = placed.rotate(
        (0.0, 0.0, 0.0),
        (0.0, 0.0, 1.0),
        float(circumferential_angle) + 90.0,
    )
    return placed.translate(cq.Vector(*center))


def _barrel_envelope(length, profile_diameters):
    """Loft STEP-sampled circular sections with explicit flat end faces."""
    max_d, d20, d30, d40, d45, end_d = profile_diameters
    profile = [
        (-0.50 * length, end_d / 2.0),
        (-0.45 * length, d45 / 2.0),
        (-0.40 * length, d40 / 2.0),
        (-0.30 * length, d30 / 2.0),
        (-0.20 * length, d20 / 2.0),
        (0.0, max_d / 2.0),
        (0.20 * length, d20 / 2.0),
        (0.30 * length, d30 / 2.0),
        (0.40 * length, d40 / 2.0),
        (0.45 * length, d45 / 2.0),
        (0.50 * length, end_d / 2.0),
    ]
    sections = cq.Workplane(
        "YZ",
        origin=(profile[0][0], 0.0, 0.0),
    ).circle(profile[0][1])
    previous_x = profile[0][0]
    for x_position, radius in profile[1:]:
        sections = sections.workplane(
            offset=x_position - previous_x,
        ).circle(radius)
        previous_x = x_position
    return sections.loft(combine=True).val()


def _make_roller(roller_length, profile_diameters, bore_d, pin_d):
    """Barrel roller with a through bore and visible end counterbores."""
    roller = _barrel_envelope(roller_length, profile_diameters)
    roller = roller.cut(_x_cylinder(bore_d, roller_length + 2.0))
    counterbore_d = min(0.72 * profile_diameters[-1], 1.65 * pin_d)
    counterbore_depth = 0.055 * roller_length
    left = _x_cylinder(counterbore_d, counterbore_depth + 0.2).translate(
        cq.Vector(-roller_length / 2.0 + counterbore_depth / 2.0 - 0.1, 0.0, 0.0)
    )
    right = _x_cylinder(counterbore_d, counterbore_depth + 0.2).translate(
        cq.Vector(roller_length / 2.0 - counterbore_depth / 2.0 + 0.1, 0.0, 0.0)
    )
    return roller.cut(left, right)


def _place_roller(shape, angle, skew_angle, center):
    return _orient_x(shape, angle, skew_angle, center)


def _make_hub(
    overall_width,
    plate_thickness,
    hub_outer_d,
    hub_face_d,
    hub_length,
    hub_bore_d,
    bolt_pcd,
    hub_bolt_d,
    bolt_angle_offset,
    running_clearance,
):
    """One stepped hub spanning the inter-plate gap and both face openings."""
    middle_length = overall_width - 2.0 * plate_thickness - running_clearance
    hub = _z_cylinder(hub_face_d, hub_length, -hub_length / 2.0)
    hub = hub.fuse(
        _z_cylinder(
            hub_outer_d,
            middle_length,
            -middle_length / 2.0,
        )
    )
    hub = hub.cut(
        _z_cylinder(
            hub_bore_d,
            hub_length + 2.0,
            -hub_length / 2.0 - 1.0,
        )
    )

    # The STEP references show a keyed/non-circular shaft interface.  Exact
    # keyway manufacturing dimensions are unavailable and remain proportions.
    key_width = 0.16 * hub_bore_d
    key_depth = 0.08 * hub_bore_d
    keyway = (
        cq.Workplane(
            "XY",
            origin=(hub_bore_d / 2.0 - key_depth, -key_width / 2.0, -hub_length / 2.0 - 1.0),
        )
        .box(key_depth + 1.0, key_width, hub_length + 2.0, centered=(False, False, False))
        .val()
    )
    hub = hub.cut(keyway)
    bolt_cutters = []
    for angle in ALL_BOLT_ANGLES:
        radians = math.radians(angle + bolt_angle_offset)
        bolt_cutters.append(
            _z_cylinder(
                hub_bolt_d,
                hub_length + 2.0,
                -hub_length / 2.0 - 1.0,
            ).translate(
                cq.Vector(
                    bolt_pcd / 2.0 * math.cos(radians),
                    bolt_pcd / 2.0 * math.sin(radians),
                    0.0,
                )
            )
        )
    return _cut_each(hub, bolt_cutters)


def _make_side_plate(
    side,
    overall_width,
    plate_thickness,
    plate_outer_d,
    hub_face_d,
    bolt_pcd,
    plate_bolt_d,
    counterbore_d,
    bolt_angle_offset,
    roller_clearance_cutters,
    pin_channel_cutters,
    mount_bosses,
    running_clearance,
):
    """Mostly closed circular disk with a shallow face recess and rim seats."""
    z_center = side * (overall_width - plate_thickness) / 2.0
    z_min = z_center - plate_thickness / 2.0
    plate = _z_cylinder(plate_outer_d, plate_thickness, z_min)

    # The broad circular face recess preserves the source's closed-disk look;
    # it is shallow and leaves a load-bearing outer rim rather than spokes.
    recess_d = 0.78 * plate_outer_d
    recess_depth = 0.08 * plate_thickness
    outer_face_z = z_center + side * plate_thickness / 2.0
    recess = cq.Solid.makeCylinder(
        recess_d / 2.0,
        recess_depth + 0.1,
        cq.Vector(0.0, 0.0, outer_face_z + side * 0.05),
        cq.Vector(0.0, 0.0, -side),
    )
    center_opening = _z_cylinder(
        hub_face_d + 2.0 * running_clearance,
        plate_thickness + 2.0,
        z_min - 1.0,
    )
    plate = plate.cut(recess, center_opening)

    bolt_cutters = []
    counterbore_cutters = []
    counterbore_depth = 0.26 * plate_thickness
    for angle in ALL_BOLT_ANGLES:
        radians = math.radians(angle + bolt_angle_offset)
        translation = cq.Vector(
            bolt_pcd / 2.0 * math.cos(radians),
            bolt_pcd / 2.0 * math.sin(radians),
            0.0,
        )
        bolt_cutters.append(
            _z_cylinder(
                plate_bolt_d,
                plate_thickness + 2.0,
                z_min - 1.0,
            ).translate(translation)
        )
        counterbore_cutters.append(
            cq.Solid.makeCylinder(
                counterbore_d / 2.0,
                counterbore_depth + 0.1,
                cq.Vector(translation.x, translation.y, outer_face_z + side * 0.05),
                cq.Vector(0.0, 0.0, -side),
            )
        )
    plate = _cut_each(plate, [*bolt_cutters, *counterbore_cutters])

    # Roller pockets are cut into the disk; short bored bosses are then fused
    # at the exact skew-axis intersections.  This makes an embedded sandwich
    # mount instead of an external bridge/cage.
    plate = _cut_each(plate, roller_clearance_cutters)
    plate = _cut_each(plate, pin_channel_cutters)
    return plate.fuse(*mount_bosses)


def _assemble_wheel(
    catalog_index,
    handedness,
    wheel_d,
    overall_width,
    roller_skew_deg,
    roller_d,
    roller_length,
    plate_thickness,
    plate_outer_d,
    hub_bore_d,
    hub_outer_d,
    pin_d,
    running_clearance,
):
    details = CATALOG_DETAILS[int(catalog_index)]
    # NM254AL is the measured left-hand reference.  Right hand is its exact
    # axial mirror: only the common skew sign changes for all eight rollers.
    hand_sign = -1.0 if int(handedness) == 0 else 1.0
    skew_angle = hand_sign * roller_skew_deg
    roller_center_r = wheel_d / 2.0 - roller_d / 2.0
    roller_bore_d = pin_d + 2.5 * running_clearance
    pin_hole_d = pin_d + 2.0 * running_clearance
    skew_radians = math.radians(roller_skew_deg)
    pin_length = (details["step_width"] - pin_d * math.cos(skew_radians)) / math.sin(skew_radians)

    roller_local = _make_roller(
        roller_length,
        details["roller_profile_d"],
        roller_bore_d,
        pin_d,
    )
    clearance_profile = tuple(
        diameter + 2.0 * running_clearance for diameter in details["roller_profile_d"]
    )
    clearance_local = _barrel_envelope(
        roller_length + 2.0 * running_clearance,
        clearance_profile,
    )
    pin_local = _x_cylinder(pin_d, pin_length)
    pin_channel_local = _x_cylinder(pin_hole_d, pin_length + 2.0)

    rollers = []
    pins = []
    roller_clearance_cutters = []
    pin_channel_cutters = []
    front_bosses = []
    rear_bosses = []
    front_z = (overall_width - plate_thickness) / 2.0
    rear_z = -front_z
    mount_outer_d = max(
        2.4 * pin_d,
        0.62 * details["roller_profile_d"][-1],
    )
    mount_axis_length = (
        plate_thickness / math.sin(math.radians(roller_skew_deg)) + 2.0 * running_clearance
    )
    mount_local = _x_cylinder(mount_outer_d, mount_axis_length)
    # The official STEP silhouettes have eight integral axle-seat ears beyond
    # the nominal plate OD.  Keep those ears inside the published wheel
    # envelope instead of flattening them back to the circular disk outline.
    mount_envelope_d = wheel_d - 2.0 * running_clearance
    front_plate_clip = _z_cylinder(
        mount_envelope_d,
        plate_thickness,
        front_z - plate_thickness / 2.0,
    )
    rear_plate_clip = _z_cylinder(
        mount_envelope_d,
        plate_thickness,
        rear_z - plate_thickness / 2.0,
    )

    for angle in ROLLER_ANGLES:
        radians = math.radians(angle)
        center = (
            roller_center_r * math.cos(radians),
            roller_center_r * math.sin(radians),
            0.0,
        )
        axis = _axis_vector(angle, skew_angle)
        rollers.append(
            _place_roller(
                roller_local,
                angle,
                skew_angle,
                center,
            )
        )
        pins.append(_orient_x(pin_local, angle, skew_angle, center))
        roller_cutter = _orient_x(
            clearance_local,
            angle,
            skew_angle,
            center,
        )
        pin_cutter = _orient_x(
            pin_channel_local,
            angle,
            skew_angle,
            center,
        )
        roller_clearance_cutters.append(roller_cutter)
        pin_channel_cutters.append(pin_cutter)

        front_parameter = front_z / axis[2]
        rear_parameter = rear_z / axis[2]
        front_center = tuple(center[i] + front_parameter * axis[i] for i in range(3))
        rear_center = tuple(center[i] + rear_parameter * axis[i] for i in range(3))
        front_boss = _orient_x(
            mount_local,
            angle,
            skew_angle,
            front_center,
        )
        rear_boss = _orient_x(
            mount_local,
            angle,
            skew_angle,
            rear_center,
        )
        front_bosses.append(
            _cut_each(front_boss, [roller_cutter, pin_cutter]).intersect(
                front_plate_clip,
            )
        )
        rear_bosses.append(
            _cut_each(rear_boss, [roller_cutter, pin_cutter]).intersect(
                rear_plate_clip,
            )
        )

    front_plate = _make_side_plate(
        1.0,
        overall_width,
        plate_thickness,
        plate_outer_d,
        details["hub_face_d"],
        details["bolt_pcd"],
        details["plate_bolt_d"],
        details["counterbore_d"],
        details["bolt_angle_offset"],
        roller_clearance_cutters,
        pin_channel_cutters,
        front_bosses,
        running_clearance,
    )
    rear_plate = _make_side_plate(
        -1.0,
        overall_width,
        plate_thickness,
        plate_outer_d,
        details["hub_face_d"],
        details["bolt_pcd"],
        details["plate_bolt_d"],
        details["counterbore_d"],
        details["bolt_angle_offset"],
        roller_clearance_cutters,
        pin_channel_cutters,
        rear_bosses,
        running_clearance,
    )
    hub = _make_hub(
        overall_width,
        plate_thickness,
        hub_outer_d,
        details["hub_face_d"],
        details["hub_length"],
        hub_bore_d,
        details["bolt_pcd"],
        details["hub_bolt_d"],
        details["bolt_angle_offset"],
        running_clearance,
    )

    assembly = cq.Assembly(name="heavy_duty_mecanum_wheel")
    assembly.add(front_plate, name="front_plate")
    assembly.add(rear_plate, name="rear_plate")
    assembly.add(hub, name="hub_body")
    for index, roller in enumerate(rollers, start=1):
        assembly.add(roller, name=f"roller_{index:02d}")
    for index, pin in enumerate(pins, start=1):
        assembly.add(pin, name=f"pin_{index:02d}")
    return assembly


def build(
    catalog_index,
    handedness,
    wheel_d,
    overall_width,
    published_set_load_kg,
    roller_count,
    roller_skew_deg,
    roller_d,
    roller_length,
    plate_thickness,
    plate_outer_d,
    hub_bore_d,
    hub_outer_d,
    pin_d,
    running_clearance,
):
    """Return one fixed-topology 19-body left- or right-hand NM wheel."""
    del published_set_load_kg
    if int(roller_count) != 8:
        raise ValueError("NEXUS NM heavy-duty family uses exactly eight rollers")
    result = _assemble_wheel(
        catalog_index,
        handedness,
        wheel_d,
        overall_width,
        roller_skew_deg,
        roller_d,
        roller_length,
        plate_thickness,
        plate_outer_d,
        hub_bore_d,
        hub_outer_d,
        pin_d,
        running_clearance,
    )
    return result
