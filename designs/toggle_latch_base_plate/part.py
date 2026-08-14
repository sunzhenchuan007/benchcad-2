"""Parametric reconstruction of the complete Ganter GN 832 toggle latch.

Coordinate system follows the supplied Size 55 / Size 200 STEP files:
X = product length, Y = shell depth, Z = frontal width.  The latch body is a
formed rectangular shell, the separate catch is a thin plate in the XZ plane,
and the elastic U-wire returns in the XZ plane between them.
"""

import cadquery as cq


def _swept_strip_xy(points, strip_width, strip_t, z_center):
    """Sweep one rectangular sheet strip along a smooth centreline in XY."""
    vectors = [cq.Vector(x, y, z_center) for x, y in points]
    edge = cq.Edge.makeSpline(vectors)
    path = cq.Wire.assembleEdges([edge])
    tangent = edge.tangentAt(0.0).normalized()
    normal = cq.Vector(-tangent.y, tangent.x, 0.0).normalized()
    z_dir = cq.Vector(0.0, 0.0, 1.0)
    start = vectors[0]
    corners = [
        start - normal * (strip_t / 2.0) - z_dir * (strip_width / 2.0),
        start + normal * (strip_t / 2.0) - z_dir * (strip_width / 2.0),
        start + normal * (strip_t / 2.0) + z_dir * (strip_width / 2.0),
        start - normal * (strip_t / 2.0) + z_dir * (strip_width / 2.0),
    ]
    section = cq.Wire.assembleEdges([
        cq.Edge.makeLine(corners[i], corners[(i + 1) % 4]) for i in range(4)
    ])
    return cq.Workplane(obj=cq.Solid.sweep(section, [], path, True, True))


def _formed_handle_tab(x0, length, depth, width, sheet_t):
    """Bent operating tab interpolated from both supplied STEP boundaries."""
    # Each list runs root -> free tip.  These are samples of the actual outer
    # and inner BSPLINE edges in Size 55 and Size 200, not guessed arc points.
    outer_55 = (
        (0.0, 8.7950), (-0.5741, 7.3387), (-1.9433, 6.6766),
        (-3.4827, 6.7091), (-5.0253, 7.1078), (-6.5424, 7.6008),
        (-8.0576, 8.0993), (-9.5515, 8.6507), (-11.0285, 9.2478),
        (-12.5917, 9.5589), (-14.1573, 9.8440), (-15.3459, 10.8676),
        (-15.9605, 11.6333),
    )
    inner_55 = (
        (-15.9605, 11.6333), (-15.2706, 10.2443), (-14.0057, 9.3811),
        (-12.5068, 8.9882), (-11.0441, 8.5011), (-9.6315, 7.8537),
        (-8.2087, 7.2328), (-6.7170, 6.7983), (-5.2187, 6.4137),
        (-3.7010, 6.0747), (-2.1502, 6.0647), (-0.6674, 6.3578),
        (0.0, 7.7228),
    )
    outer_200 = (
        (0.0, 16.7950), (-1.0498, 15.0802), (-2.9957, 14.4471),
        (-5.0326, 14.2001), (-7.0767, 14.2205), (-9.0397, 14.8129),
        (-11.0445, 15.2421), (-12.9513, 15.9786), (-14.7754, 16.9129),
        (-16.7559, 17.4461), (-18.5731, 18.3785), (-20.1771, 19.6576),
        (-20.8294, 19.3674),
    )
    inner_200 = (
        (-20.8294, 19.3674), (-19.7138, 17.7868), (-18.1097, 16.7230),
        (-16.3391, 15.9327), (-14.5984, 15.0774), (-12.7604, 14.4611),
        (-10.8779, 13.9927), (-8.9909, 13.5426), (-7.0807, 13.2075),
        (-5.1506, 13.0144), (-3.2133, 12.9140), (-1.3878, 13.4283),
        (0.0, 14.7546),
    )
    alpha = max(0.0, min(1.0, (width - 14.0) / 12.0))
    def blend(a, b):
        return tuple((x0 + ax + alpha * (bx - ax), ay + alpha * (by - ay))
                     for (ax, ay), (bx, by) in zip(a, b))
    outer = blend(outer_55, outer_200)
    inner = list(blend(inner_55, inner_200))
    # Seven samples retain the measured inflection while avoiding the nearly
    # coincident high-order poles that OCCT cannot mesh at Size 55.
    sample_ids = (0, 2, 4, 6, 8, 10, 12)
    outer = tuple(outer[i] for i in sample_ids)
    inner = [inner[i] for i in sample_ids]
    inner = tuple(inner)
    # Build one closed side face from the two actual STEP boundaries.  This
    # produces two continuous BSPLINE edges and one smooth extruded face; the
    # former centreline sweep exposed many transverse patch boundaries.
    outer_edge = cq.Edge.makeSpline([cq.Vector(x, y, 0.0) for x, y in outer])
    inner_edge = cq.Edge.makeSpline([cq.Vector(x, y, 0.0) for x, y in inner])
    root_edge = cq.Edge.makeLine(
        cq.Vector(*inner[-1], 0.0), cq.Vector(*outer[0], 0.0)
    )
    side_face = cq.Face.makeFromWires(
        cq.Wire.assembleEdges([outer_edge, inner_edge, root_edge])
    )
    # STEP extremes: 2.0 mm side margin at Size 55 and 1.5 mm at Size 200.
    z_margin = 2.5833 - 0.041667 * width
    solid = cq.Solid.extrudeLinear(
        side_face, cq.Vector(0.0, 0.0, width - 2.0 * z_margin)
    ).translate(cq.Vector(0.0, 0.0, z_margin))
    return cq.Workplane(obj=solid)


def _formed_catch(x0, plate_len, body_width, width, z0, sheet_t):
    """Complete flat plate and upturned catch made as one formed sheet."""
    # Closed Size-200 STEP hook boundary, root-top -> rounded crown ->
    # root-bottom.  Scaling it between the supplied extremes preserves the
    # real raised/returned sheet profile instead of turning it into a slanted
    # rectangular strip.
    ref_boundary = (
        (0.0, 1.9546), (-0.5493, 5.1704), (0.2685, 8.4699),
        (1.2361, 11.7248), (3.3721, 14.3258), (6.3832, 15.8931),
        (3.6947, 16.0240), (0.7087, 14.5464), (-0.6796, 11.4471),
        (-1.8186, 8.2444), (-2.7222, 4.9680), (-2.5711, 1.6183),
        (0.0, 0.0),
    )
    alpha = max(0.0, min(1.0, (body_width - 14.0) / 12.0))
    x_scale = 0.55 + 0.45 * alpha
    hook_h = 8.249 + alpha * (16.221 - 8.249)
    def scale_y(y):
        if y <= 1.9546:
            return -sheet_t + (y / 1.9546) * sheet_t
        return (y - 1.9546) / (16.0240 - 1.9546) * hook_h
    hook = [(x0 + 0.35 * sheet_t + x_scale * x, scale_y(y))
            for x, y in ref_boundary]
    hook_profile = (cq.Workplane("XY").moveTo(*hook[0])
                    .spline(hook[1:]).close())
    formed = hook_profile.extrude(width).translate((0, 0, z0))
    plate = (cq.Workplane("XZ").box(
        plate_len + 0.7 * sheet_t, width, sheet_t,
        centered=(False, False, False)
    ).translate((x0 - 0.35 * sheet_t, 0.0, z0)))
    return cq.Workplane(obj=plate.val().fuse(formed.val()))


def _swept_wire(points, wire_d):
    vectors = [cq.Vector(*p) for p in points]
    edge = cq.Edge.makeSpline(vectors)
    path = cq.Wire.assembleEdges([edge])
    tangent = (vectors[1] - vectors[0]).normalized()
    section = cq.Wire.makeCircle(wire_d / 2.0, vectors[0], tangent)
    return cq.Solid.sweep(section, [], path, True, True)


def _u_wire(catalog_index, wire_d, body_width):
    """Regular U-wire translated back to its own two mounting holes.

    The shape is intentionally the approved narrow rounded rectangle: two
    straight parallel legs and a straight catch bar joined by short corners.
    Only its roots differ from the earlier version: they use the dedicated
    wire holes, not the transverse pivot-pin hole.
    """
    alpha = int(catalog_index) / 2.0
    def mix(a, b):
        return a + alpha * (b - a)

    # Circular STEP edges of the wire's own pair of side holes.
    hole_x = mix(18.426, 51.269)
    hole_y = mix(6.303, 10.644)
    upper_root = cq.Vector(hole_x, hole_y, body_width)
    lower_root = cq.Vector(hole_x, hole_y, 0.0)

    far_x = mix(44.0, 92.0)
    corner_r = min(mix(3.0, 5.5), 0.28 * body_width)
    k = 2.0 ** -0.5

    upper_straight = cq.Edge.makeLine(
        upper_root, cq.Vector(far_x - corner_r, hole_y, body_width)
    )
    upper_corner = cq.Edge.makeThreePointArc(
        cq.Vector(far_x - corner_r, hole_y, body_width),
        cq.Vector(
            far_x - corner_r + corner_r * k,
            hole_y,
            body_width - corner_r + corner_r * k,
        ),
        cq.Vector(far_x, hole_y, body_width - corner_r),
    )
    # The small catch plate hangs on this true straight span.
    catch_bar = cq.Edge.makeLine(
        cq.Vector(far_x, hole_y, body_width - corner_r),
        cq.Vector(far_x, hole_y, corner_r),
    )
    lower_corner = cq.Edge.makeThreePointArc(
        cq.Vector(far_x, hole_y, corner_r),
        cq.Vector(
            far_x - corner_r + corner_r * k,
            hole_y,
            corner_r - corner_r * k,
        ),
        cq.Vector(far_x - corner_r, hole_y, 0.0),
    )
    lower_straight = cq.Edge.makeLine(
        cq.Vector(far_x - corner_r, hole_y, 0.0), lower_root
    )
    path = cq.Wire.assembleEdges([
        upper_straight, upper_corner, catch_bar,
        lower_corner, lower_straight,
    ])
    tangent = cq.Vector(1.0, 0.0, 0.0)
    section = cq.Wire.makeCircle(wire_d / 2.0, upper_root, tangent)
    return cq.Workplane(obj=cq.Solid.sweep(section, [], path, True, True))


def build(catalog_index, sheet_t):
    # size,FH,b1,b2,b3,b4,b5,b6,d1,d2,d3,h1,h2,l1,l2,l3,m1,m2,m3,m4,r
    rows = (
        (55, 550, 23.0, 17.0, 14.0, 44.0, 13.0, 30.0,
         2.0, 3.2, 2.6, 11.0, 9.0, 102.0, 60.0, 34.0,
         9.5, 12.5, 5.0, 12.0, 26.0),
        (150, 1500, 34.0, 23.0, 20.0, 70.0, 19.0, 43.0,
         3.0, 4.1, 3.1, 12.5, 11.0, 140.0, 86.0, 38.0,
         13.0, 22.5, 8.0, 20.0, 30.0),
        (200, 2000, 43.0, 30.0, 26.0, 90.0, 27.0, 66.0,
         4.0, 5.3, 5.3, 19.0, 15.0, 191.0, 111.0, 57.5,
         10.0, 31.5, 15.0, 25.5, 36.0),
    )
    idx = int(catalog_index)
    if idx < 0 or idx > 2:
        raise ValueError("catalog_index must be 0, 1, or 2")
    (
        size, holding_capacity_n,
        b1, b2, b3, b4, b5, b6,
        d1, d2, d3, h1, h2,
        l1, l2, l3, m1, m2, m3, m4, r,
    ) = rows[idx]

    # These two extreme depths are measured directly from the supplied STEP
    # files.  The middle value is linearly interpolated by official h1.
    # The main formed body depth is exactly the catalog h1 in both references.
    body_depth = h1
    body_x0 = -18.75
    body_x1 = body_x0 + b4
    body_width = b3

    # The supplied references show a 16.0 / 21.1 mm formed operating tab.
    tab_len = 10.05 + 0.425 * body_width

    # Catch position measured from the two extreme references.  Its plate is
    # vertical (XZ), not horizontal as in the discarded first reconstruction.
    gap = 17.560 - 0.04048 * b4
    catch_x0 = body_x1 + gap
    catch_x1 = catch_x0 + b6
    catch_z0 = (body_width - b5) / 2.0

    # Hole locations measured from the two supplied STEP extremes.
    rear_hole_x = body_x0 + (-0.010 + 0.05250 * b4)
    rear_hole_y = 1.129 + 0.03074 * b4
    front_hole_x = body_x1 - (1.836 + 0.03753 * b4)
    front_hole_y = 2.151 + 0.09437 * b4
    # Dedicated U-wire hole, read from circular edges in the supplied STEP.
    # This is separate from both the rear safety bore and transverse pin hole.
    alpha = idx / 2.0
    wire_hole_x = 18.426 + alpha * (51.269 - 18.426)
    wire_hole_y = 6.303 + alpha * (10.644 - 6.303)

    # The front is NOT a solid rectangular block.  The formed shell stops
    # before the pivot and continues as two thin, separately formed side ears.
    # Their open middle is the visible clevis gap through which the pin passes.
    ear_t = max(sheet_t, 0.50 * d1)
    # STEP: the open formed-ear segment is short (about 4.68 mm at Size 55
    # and 15.15 mm at Size 200); the solid-looking body must not stop early.
    clevis_len = -5.563 + 0.23045 * b4
    ear_start = body_x1 - clevis_len
    body_len = ear_start - body_x0
    result = cq.Workplane("XY").box(
        body_len, body_depth, body_width, centered=(False, False, False)
    ).translate((body_x0, 0.0, 0.0))

    # Smooth side-view profile: each ear rises gently around the pivot and
    # rounds down at its free end instead of forming a square tab.
    ear_tip_x = body_x1
    ear_root_y = 0.963 + 0.01296 * (b4 - 44.0)
    ear_top = body_depth - 0.08 * max(sheet_t, 0.5)
    ear_bottom = ear_root_y
    ear_side_tip_x = min(body_x1, front_hole_x + 0.78 * d3)
    ear_profile = (
        cq.Workplane("XY")
        .moveTo(ear_start, ear_bottom)
        .lineTo(ear_start, body_depth)
        .threePointArc(
            (front_hole_x + 0.25 * d3, ear_top),
            (ear_side_tip_x, front_hole_y),
        )
        .threePointArc(
            (front_hole_x + 0.25 * d3, ear_bottom),
            (ear_start, ear_bottom),
        )
        .close()
    )
    # Intersect the rounded side envelope with one continuous U-section.  The
    # two lower corners are real bend arcs, so this reads as one folded sheet
    # (bottom web + two upturned ears), not separate paper-thin plates.
    side_envelope = ear_profile.extrude(body_width)
    bend_r = max(0.85 * ear_t, 0.45 * d1)
    outer_y = ear_bottom
    inner_y = ear_bottom + ear_t
    left_outer_z = 0.0
    left_inner_z = ear_t
    right_inner_z = body_width - ear_t
    right_outer_z = body_width
    u_section = (
        cq.Workplane("YZ", origin=(ear_start - 0.20 * ear_t, 0.0, 0.0))
        .moveTo(ear_top, left_outer_z)
        .lineTo(outer_y + bend_r, left_outer_z)
        .threePointArc(
            (outer_y + 0.293 * bend_r, 0.293 * bend_r),
            (outer_y, bend_r),
        )
        .lineTo(outer_y, right_outer_z - bend_r)
        .threePointArc(
            (outer_y + 0.293 * bend_r, right_outer_z - 0.293 * bend_r),
            (outer_y + bend_r, right_outer_z),
        )
        .lineTo(ear_top, right_outer_z)
        .lineTo(ear_top, right_inner_z)
        .lineTo(inner_y + bend_r, right_inner_z)
        .threePointArc(
            (inner_y + 0.293 * bend_r, right_inner_z - 0.293 * bend_r),
            (inner_y, right_inner_z - bend_r),
        )
        .lineTo(inner_y, left_inner_z + bend_r)
        .threePointArc(
            (inner_y + 0.293 * bend_r, left_inner_z + 0.293 * bend_r),
            (inner_y + bend_r, left_inner_z),
        )
        .lineTo(ear_top, left_inner_z)
        .close()
        .extrude(clevis_len + 0.40 * ear_t)
    )
    formed_clevis = side_envelope.intersect(u_section)
    # Rear bent operating tab.
    tab = _formed_handle_tab(
        body_x0, tab_len, body_depth, body_width, sheet_t
    )
    # Keep the formed rear tab as a distinct sheet body.  Its STEP-derived
    # root boundary touches the shell along the real seam; forcing a Boolean
    # union there can create a null result in OCCT.
    body_shape = result.val().fuse(formed_clevis.val())

    # Transverse pivot through the two clevis walls.
    anchor_x = front_hole_x
    center_z = body_width / 2.0
    pin = cq.Solid.makeCylinder(
        d3 / 2.0,
        body_width,
        cq.Vector(anchor_x, front_hole_y, 0.0),
        cq.Vector(0, 0, 1),
    )
    # Safety bore d3 and the second visible side drilling.  These pass through
    # the two broad SIDE faces (Z=0 / Z=body_width), as in the supplied STEP;
    # the discarded version incorrectly drilled along Y through top/bottom.
    rear_bore = cq.Solid.makeCylinder(
        d3 / 2.0, body_width + 2.0,
        cq.Vector(rear_hole_x, rear_hole_y, -1.0), cq.Vector(0, 0, 1),
    )
    front_bore = cq.Solid.makeCylinder(
        d3 / 2.0, body_width + 2.0,
        cq.Vector(front_hole_x, front_hole_y, -1.0), cq.Vector(0, 0, 1),
    )
    wire_bore = cq.Solid.makeCylinder(
        d3 / 2.0, body_width + 2.0,
        cq.Vector(wire_hole_x, wire_hole_y, -1.0), cq.Vector(0, 0, 1),
    )
    body_shape = body_shape.cut(rear_bore)
    body_shape = body_shape.cut(front_bore)
    body_shape = body_shape.cut(wire_bore)
    result = cq.Workplane(obj=cq.Compound.makeCompound(
        body_shape.Solids() + tab.val().Solids() + [pin]
    ))

    # Catch plate and its upturned nose are one continuous formed sheet.
    catch = _formed_catch(
        catch_x0, b6, body_width, b5, catch_z0, sheet_t
    )
    hole_2_x = catch_x1 - m3
    hole_1_x = hole_2_x - m4
    catch_center_z = catch_z0 + b5 / 2.0
    for hole_x in (hole_1_x, hole_2_x):
        hole = cq.Solid.makeCylinder(
            d2 / 2.0,
            sheet_t + 2.0,
            cq.Vector(hole_x, -1.0, catch_center_z),
            cq.Vector(0, 1, 0),
        )
        catch = catch.cut(hole)

    # Full U-shaped elastic wire.  Its legs are separated in Z and the return
    # overlaps the formed catch nose in the closed reference position.
    # U-wire diameter follows d1: Ø2 / Ø3 / Ø4.  Dimension d3 belongs to the
    # spring-cotter bore and must not be applied to this elastic latch wire.
    modeled_wire_d = d1
    wire = _u_wire(idx, modeled_wire_d, body_width)

    # The wire begins and ends inside the two shell side faces and its closed
    # return bears on the raised catch nose. No exterior connector block is
    # added; this preserves the real visible topology of both STEP extremes.
    visible_parts = result.val().Solids() + wire.val().Solids() + catch.val().Solids()
    # A Compound keeps the real modeled bodies visible without expensive and
    # fragile Boolean merging at the spring-wire contacts.
    result = cq.Workplane(obj=cq.Compound.makeCompound(visible_parts))
    return result
