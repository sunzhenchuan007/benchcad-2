"""STAUFF STC/SPC channel cushion clamp as five real components."""

import math

import cadquery as cq


def _thread_diameter(thread_code):
    """UNC nominal major diameter in mm for the catalogue thread codes."""
    return (6.35, 7.9375, 9.525)[int(thread_code)]


def _unc_pitch(thread_code):
    """Catalogue UNC pitch in mm from 20/18/16 threads per inch."""
    return 25.4 / (20.0, 18.0, 16.0)[int(thread_code)]


def _d_prism(half_width, bottom_z, depth):
    """D-profile prism centred on Y, with the pipe centre at Z=0."""
    return (
        cq.Workplane("XZ", origin=(0.0, depth / 2.0, 0.0))
        .moveTo(-half_width, bottom_z)
        .lineTo(-half_width, 0.0)
        .threePointArc((0.0, half_width), (half_width, 0.0))
        .lineTo(half_width, bottom_z)
        .close()
        .extrude(depth)
    )


def _modeled_external_unc_thread(thread_d, pitch, length):
    """Simplified visible 60-degree UNC external thread along local +Z."""
    major_r = thread_d / 2.0
    root_r = (thread_d - 1.226869 * pitch) / 2.0
    radial_embed = min(0.08, 0.05 * pitch)
    half_width = (major_r - root_r + radial_embed) / math.sqrt(3.0)
    path_r = (major_r + root_r) / 2.0
    path_h = length - 2.0 * half_width
    core = cq.Workplane("XY").circle(root_r).extrude(length)
    path = cq.Wire.makeHelix(pitch, path_h, path_r)
    profile = (
        cq.Workplane("XZ")
        .polyline(
            [
                (root_r - radial_embed, -half_width),
                (major_r, 0.0),
                (root_r - radial_embed, half_width),
            ]
        )
        .close()
    )
    ridge = profile.sweep(path, isFrenet=True).translate((0.0, 0.0, half_width))
    return core.union(ridge)


def _make_cross_bolt_local(
    thread_d, pitch, plain_length, threaded_length, head_r, head_h
):
    """Bolt along local +Z; the head bearing face is the Z=0 datum."""
    plain = cq.Workplane("XY").circle(thread_d / 2.0).extrude(plain_length + 0.05)
    threaded = _modeled_external_unc_thread(thread_d, pitch, threaded_length)
    threaded = threaded.translate((0.0, 0.0, plain_length))
    head = (
        cq.Workplane("XY")
        .workplane(offset=-head_h)
        .circle(head_r)
        .extrude(head_h)
    )
    return plain.union(threaded).union(head)


def _make_lock_nut_local(bolt_local, thread_d, nut_af, nut_h, bearing_z):
    """Hex nut whose internal thread is cut by the exact mating bolt shape."""
    corner_d = nut_af / 0.8660254037844386
    blank = (
        cq.Workplane("XY")
        .workplane(offset=bearing_z)
        .polygon(6, corner_d)
        .extrude(nut_h)
        .val()
    )
    chamfer_h = min(0.12 * nut_h, 0.18 * thread_d)
    land_r = 0.475 * nut_af
    crown_r = corner_d / 2.0 + 0.01
    envelope = (
        cq.Workplane("XZ")
        .moveTo(0.0, bearing_z)
        .lineTo(land_r, bearing_z)
        .lineTo(crown_r, bearing_z + chamfer_h)
        .lineTo(crown_r, bearing_z + nut_h - chamfer_h)
        .lineTo(land_r, bearing_z + nut_h)
        .lineTo(0.0, bearing_z + nut_h)
        .close()
        .revolve(360.0, (0.0, bearing_z), (0.0, bearing_z + 1.0))
        .val()
    )
    nut = blank.intersect(envelope).cut(bolt_local.val())
    return cq.Workplane(obj=nut)


def build(
    catalog_row,
    material_code,
    tube_od,
    install_width_min,
    c,
    height_d,
    edge_e,
    thread_code,
):
    """Build two steel clamp halves, one cushion, one cross-bolt, and one nut."""
    del catalog_row, material_code

    # Global frame: pipe axis +Y, cross-bolt axis -X, rail/down direction -Z.
    channel_width = 41.3
    cushion_depth = channel_width - 3.2
    cushion_overhang = cushion_depth / 12.0
    steel_depth = cushion_depth - 2.0 * cushion_overhang

    thread_d = _thread_diameter(thread_code)
    thread_pitch = _unc_pitch(thread_code)
    steel_t = edge_e
    outer_half = install_width_min / 2.0
    cushion_half = outer_half - steel_t
    bore_r = tube_od / 2.0
    cushion_bottom = -c

    # The cushion is one D-profile extrusion.  The tube bore and tapered
    # service opening pass through its full depth; its Y overhang retains it
    # axially beyond the narrower steel clamp.
    cushion_blank = _d_prism(cushion_half, cushion_bottom, cushion_depth)
    thread_lug_half = min(0.78 * thread_d, 0.60 * cushion_half)
    slot_half_inner = min(
        cushion_half - 0.55 * steel_t,
        max(0.42 * bore_r, thread_lug_half + 0.18 * steel_t),
    )
    slot_half_outer = min(
        cushion_half - 0.30 * steel_t,
        slot_half_inner + 0.45 * steel_t,
    )
    slot_start = max(0.55 * bore_r, bore_r - 0.45 * steel_t)
    slot = (
        cq.Workplane("XZ", origin=(0.0, cushion_depth / 2.0 + 0.5, 0.0))
        .moveTo(-slot_half_inner, slot_start)
        .lineTo(-slot_half_outer, cushion_half + 1.0)
        .lineTo(slot_half_outer, cushion_half + 1.0)
        .lineTo(slot_half_inner, slot_start)
        .close()
        .extrude(cushion_depth + 1.0)
    )
    tube_bore = (
        cq.Workplane("XZ", origin=(0.0, cushion_depth / 2.0 + 0.5, 0.0))
        .circle(bore_r)
        .extrude(cushion_depth + 1.0)
    )
    cushion = cushion_blank.cut(tube_bore).cut(slot)

    # The steel inner surface is cut with the same unperforated D blank used to
    # make the cushion.  This gives exact side/crown bearing surfaces without
    # overlap, while the lower centre stays open.
    steel_outer = _d_prism(outer_half, cushion_bottom, steel_depth)
    steel_inner = _d_prism(cushion_half, cushion_bottom, steel_depth)
    steel_frame = steel_outer.cut(steel_inner)

    headroom = height_d - c - outer_half
    leg_drop = max(1.5 * steel_t, min(0.12 * install_width_min, 0.35 * headroom))
    leg_bottom = cushion_bottom - leg_drop
    leg_h = cushion_bottom - leg_bottom + 0.10
    leg_x = outer_half - steel_t / 2.0
    legs = (
        cq.Workplane("XY")
        .pushPoints([(-leg_x, 0.0), (leg_x, 0.0)])
        .box(steel_t, steel_depth, leg_h)
        .translate((0.0, 0.0, leg_bottom + leg_h / 2.0))
    )
    steel_frame = steel_frame.union(legs)

    # Two lower seats touch the cushion's flat underside.  Their reduced Y span
    # matches local support patches instead of falsely closing the whole base.
    seat_w = min(1.30 * steel_t, 0.22 * cushion_half)
    seat_depth = 0.65 * steel_depth
    seat_x = cushion_half - seat_w / 2.0
    seats = (
        cq.Workplane("XY")
        .pushPoints([(-seat_x, 0.0), (seat_x, 0.0)])
        .box(seat_w, seat_depth, 0.70 * steel_t)
        .translate((0.0, 0.0, cushion_bottom - 0.35 * steel_t))
    )
    steel_frame = steel_frame.union(seats)

    # Inward lips create the down-facing channel engagement.  They remain below
    # the cushion datum and cannot intersect the elastomer.
    hook_reach = min(2.1 * steel_t, 0.18 * cushion_half)
    hook_h = 0.34 * leg_drop
    hook_x = cushion_half - hook_reach / 2.0
    hooks = (
        cq.Workplane("XY")
        .pushPoints([(-hook_x, 0.0), (hook_x, 0.0)])
        .box(hook_reach, steel_depth, hook_h)
        .translate((0.0, 0.0, leg_bottom + 0.58 * leg_drop))
    )
    steel_frame = steel_frame.union(hooks)

    # The steel strap is supplied as two independent left/right halves.  A
    # visible centre gap separates the halves through the crown, while a lug on
    # each half carries the transverse fastener at the top centre.
    overall_top = leg_bottom + height_d
    crown_h = min(0.80 * thread_d, 0.42 * (overall_top - outer_half))
    bolt_z = overall_top - 0.55 * crown_h
    center_gap = max(0.75 * thread_d, 1.50 * steel_t)
    ear_width = steel_t
    ear_outer_x = center_gap / 2.0 + ear_width
    upright_half_h = 0.85 * thread_d
    ear_top_z = bolt_z + upright_half_h
    ear_curve_z = bolt_z - upright_half_h

    # A long upright hole zone flows into the circular strap through a pair of
    # tangent splines.  The radial join segment overlaps the original annular
    # shell, so the result is one continuous bent plate rather than a block
    # attached to the crown.
    outer_join_x = min(
        0.65 * outer_half,
        ear_outer_x + 1.50 * thread_d,
    )
    outer_join_z = math.sqrt(outer_half * outer_half - outer_join_x * outer_join_x)
    join_scale = cushion_half / outer_half
    inner_join_x = outer_join_x * join_scale
    inner_join_z = outer_join_z * join_scale

    right_ear = (
        cq.Workplane("XZ", origin=(0.0, steel_depth / 2.0, 0.0))
        .moveTo(center_gap / 2.0, ear_top_z)
        .lineTo(ear_outer_x, ear_top_z)
        .lineTo(ear_outer_x, ear_curve_z)
        .spline(
            [(outer_join_x, outer_join_z)],
            tangents=[(0.0, -1.0), (outer_join_z, -outer_join_x)],
            includeCurrent=True,
        )
        .lineTo(inner_join_x, inner_join_z)
        .spline(
            [(center_gap / 2.0, ear_curve_z)],
            tangents=[(-inner_join_z, inner_join_x), (0.0, 1.0)],
            includeCurrent=True,
        )
        .lineTo(center_gap / 2.0, ear_top_z)
        .close()
        .extrude(steel_depth)
    )
    right_ear = right_ear.cut(cushion)
    left_ear = right_ear.mirror("YZ")

    mask_pad = 2.0 * steel_t
    mask_width = outer_half + mask_pad - center_gap / 2.0
    mask_height = overall_top - leg_bottom + 2.0 * mask_pad
    mask_center_z = (overall_top + leg_bottom) / 2.0
    left_mask = (
        cq.Workplane("XY")
        .box(mask_width, steel_depth + 2.0 * mask_pad, mask_height)
        .translate(
            (
                -(outer_half + mask_pad + center_gap / 2.0) / 2.0,
                0.0,
                mask_center_z,
            )
        )
    )
    right_mask = (
        cq.Workplane("XY")
        .box(mask_width, steel_depth + 2.0 * mask_pad, mask_height)
        .translate(
            (
                (outer_half + mask_pad + center_gap / 2.0) / 2.0,
                0.0,
                mask_center_z,
            )
        )
    )

    bolt_hole = (
        cq.Workplane("YZ", origin=(-ear_outer_x - 0.5, 0.0, bolt_z))
        .circle(thread_d / 2.0)
        .extrude(2.0 * ear_outer_x + 1.0)
    )
    steel_left = steel_frame.intersect(left_mask).union(left_ear).cut(bolt_hole)
    steel_right = steel_frame.intersect(right_mask).union(right_ear).cut(bolt_hole)

    # The local bolt +Z axis is rotated onto global -X.  Its head face lands on
    # the +X outer ear face and the nut starts on the -X outer ear face.
    nut_h = 0.82 * thread_d
    projection = max(1.5, 0.85 * thread_pitch)
    threaded_length = nut_h + projection
    head_r = 0.82 * thread_d
    head_h = 0.45 * thread_d
    bolt_local = _make_cross_bolt_local(
        thread_d,
        thread_pitch,
        2.0 * ear_outer_x,
        threaded_length,
        head_r,
        head_h,
    )
    nut_af = 1.62 * thread_d
    nut_local = _make_lock_nut_local(
        bolt_local, thread_d, nut_af, nut_h, 2.0 * ear_outer_x
    )
    orient_axis = (0.0, 1.0, 0.0)
    bolt = bolt_local.rotate((0.0, 0.0, 0.0), orient_axis, -90.0)
    bolt = bolt.translate((ear_outer_x, 0.0, bolt_z))
    nut = nut_local.rotate((0.0, 0.0, 0.0), orient_axis, -90.0)
    nut = nut.translate((ear_outer_x, 0.0, bolt_z))

    result = cq.Assembly(name="stc_spc_channel_cushion_clamp_asm")
    result.add(
        steel_left,
        name="steel_strut_clamp_half_01",
        color=cq.Color(0.62, 0.67, 0.72),
    )
    result.add(
        steel_right,
        name="steel_strut_clamp_half_02",
        color=cq.Color(0.62, 0.67, 0.72),
    )
    result.add(cushion, name="cushion_insert", color=cq.Color(0.12, 0.27, 0.30))
    result.add(bolt, name="cross_bolt", color=cq.Color(0.78, 0.70, 0.45))
    result.add(nut, name="lock_nut", color=cq.Color(0.62, 0.48, 0.26))
    return result
