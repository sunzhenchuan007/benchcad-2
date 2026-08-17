"""STAUFF STC/SPC channel cushion clamp as four real components."""

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
    """Build one steel clamp, one cushion, one cross-bolt, and one lock nut."""
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
    steel = steel_outer.cut(steel_inner)

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
    steel = steel.union(legs)

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
    steel = steel.union(seats)

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
    steel = steel.union(hooks)

    # A central transverse lug joins both sides of the steel shell.  Its planar
    # +/-X faces are the bolt-head and nut bearing datums.
    overall_top = leg_bottom + height_d
    crown_h = min(0.80 * thread_d, 0.42 * (overall_top - outer_half))
    bolt_z = overall_top - 0.55 * crown_h
    lug_bottom = outer_half - 0.75 * steel_t
    lug_half_x = thread_lug_half
    lug_width_x = 2.0 * lug_half_x
    shoulder_z = bolt_z + 0.12 * crown_h
    top_half_y = 0.58 * steel_depth / 2.0
    lug = (
        cq.Workplane("YZ", origin=(-lug_half_x, 0.0, 0.0))
        .moveTo(-steel_depth / 2.0, lug_bottom)
        .lineTo(steel_depth / 2.0, lug_bottom)
        .lineTo(steel_depth / 2.0, shoulder_z)
        .lineTo(top_half_y, overall_top)
        .lineTo(-top_half_y, overall_top)
        .lineTo(-steel_depth / 2.0, shoulder_z)
        .close()
        .extrude(lug_width_x)
    )
    bolt_hole = (
        cq.Workplane("YZ", origin=(-lug_half_x - 0.5, 0.0, bolt_z))
        .circle(thread_d / 2.0)
        .extrude(lug_width_x + 1.0)
    )
    steel = steel.union(lug).cut(bolt_hole)

    # The local bolt +Z axis is rotated onto global -X.  Its head face lands on
    # +X of the lug and the nut starts exactly on the -X lug face.
    nut_h = 0.82 * thread_d
    projection = max(1.5, 0.85 * thread_pitch)
    threaded_length = nut_h + projection
    head_r = 0.82 * thread_d
    head_h = 0.45 * thread_d
    bolt_local = _make_cross_bolt_local(
        thread_d,
        thread_pitch,
        lug_width_x,
        threaded_length,
        head_r,
        head_h,
    )
    nut_af = 1.62 * thread_d
    nut_local = _make_lock_nut_local(
        bolt_local, thread_d, nut_af, nut_h, lug_width_x
    )
    orient_axis = (0.0, 1.0, 0.0)
    bolt = bolt_local.rotate((0.0, 0.0, 0.0), orient_axis, -90.0)
    bolt = bolt.translate((lug_half_x, 0.0, bolt_z))
    nut = nut_local.rotate((0.0, 0.0, 0.0), orient_axis, -90.0)
    nut = nut.translate((lug_half_x, 0.0, bolt_z))

    result = cq.Assembly(name="stc_spc_channel_cushion_clamp_asm")
    result.add(steel, name="steel_strut_clamp", color=cq.Color(0.62, 0.67, 0.72))
    result.add(cushion, name="cushion_insert", color=cq.Color(0.12, 0.27, 0.30))
    result.add(bolt, name="cross_bolt", color=cq.Color(0.78, 0.70, 0.45))
    result.add(nut, name="lock_nut", color=cq.Color(0.62, 0.48, 0.26))
    return result
