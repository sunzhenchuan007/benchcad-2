"""STAUFF STC/SPC cushion clamp for 41.3 mm SCS channel rail."""

import math

import cadquery as cq


def _thread_diameter(thread_code):
    """UNC nominal major diameter in mm for the catalogue thread codes."""
    return (6.35, 7.9375, 9.525)[int(thread_code)]


def _unc_pitch(thread_code):
    """Return catalogue UNC pitch in mm from 20/18/16 threads per inch."""
    return 25.4 / (20.0, 18.0, 16.0)[int(thread_code)]


def _modeled_external_unc_thread(thread_d, pitch, length):
    """Return a simplified visible 60-degree UNC external thread."""
    major_r = thread_d / 2.0
    root_r = (thread_d - 1.226869 * pitch) / 2.0
    radial_embed = min(0.08, 0.05 * pitch)
    half_width = (major_r - root_r + radial_embed) / math.sqrt(3.0)
    path_r = (major_r + root_r) / 2.0
    path_h = length - 2.0 * half_width
    core = cq.Workplane("XY").circle(root_r).extrude(length)
    path = cq.Wire.makeHelix(pitch, path_h, path_r)
    profile = (cq.Workplane("XZ")
               .polyline([(root_r - radial_embed, -half_width),
                          (major_r, 0.0),
                          (root_r - radial_embed, half_width)])
               .close())
    ridge = profile.sweep(path, isFrenet=True).translate((0.0, 0.0, half_width))
    return core.union(ridge)


def _modeled_internal_unc_groove(thread_d, pitch, length):
    """Return a simplified visible 60-degree UNC internal-groove cutter."""
    major_r = thread_d / 2.0
    minor_r = (thread_d - 1.082532 * pitch) / 2.0
    radial_embed = min(0.08, 0.05 * pitch)
    half_width = (major_r - minor_r + radial_embed) / math.sqrt(3.0)
    path = cq.Wire.makeHelix(pitch, length + 2.0 * half_width, minor_r)
    profile = (cq.Workplane("XZ")
               .polyline([(minor_r - radial_embed, -half_width),
                          (major_r, 0.0),
                          (minor_r - radial_embed, half_width)])
               .close())
    return profile.sweep(path, isFrenet=True).translate((0.0, 0.0, -half_width))


def _make_unc_stud(thread_d, pitch, length, thread_length):
    """Return a stud with a modeled UNC thread at its positive-Z end."""
    plain_l = length - thread_length
    plain = cq.Workplane("XY").circle(thread_d / 2.0).extrude(plain_l + 0.05)
    threaded = (_modeled_external_unc_thread(thread_d, pitch, thread_length)
                .translate((0.0, 0.0, plain_l)))
    return plain.union(threaded)


def _make_unc_lock_nut(thread_d, pitch, nut_af, nut_h):
    """Return a chamfered hex lock-nut with a modeled UNC internal thread."""
    corner_d = nut_af / 0.8660254037844386
    blank = cq.Workplane("XY").polygon(6, corner_d).extrude(nut_h).val()
    chamfer_h = min(0.12 * nut_h, 0.18 * thread_d)
    land_r = 0.475 * nut_af
    crown_r = corner_d / 2.0 + 0.01
    envelope = (cq.Workplane("XZ")
                .moveTo(0.0, 0.0)
                .lineTo(land_r, 0.0)
                .lineTo(crown_r, chamfer_h)
                .lineTo(crown_r, nut_h - chamfer_h)
                .lineTo(land_r, nut_h)
                .lineTo(0.0, nut_h)
                .close()
                .revolve(360.0, (0.0, 0.0), (0.0, 1.0)).val())
    nut = blank.intersect(envelope)
    minor_d = thread_d - 1.082532 * pitch
    bore = (cq.Workplane("XY").workplane(offset=-0.05)
            .circle(minor_d / 2.0).extrude(nut_h + 0.10).val())
    nut = nut.cut(bore)
    nut = nut.cut(_modeled_internal_unc_groove(thread_d, pitch, nut_h).val())
    return cq.Workplane(obj=nut)


def _plate_frame(install_width_min, c, height_d, edge_e, thread_code, depth):
    """Return the stamped inverted-U plate envelope in its local XY plane."""
    outer_r = install_width_min / 2.0
    inner_r = outer_r - edge_e
    thread_d = _thread_diameter(thread_code)
    ear_r = max(0.9 * thread_d, 1.35 * edge_e)
    stud_y = height_d - ear_r
    annulus = (cq.Workplane("XY").circle(outer_r).circle(inner_r).extrude(depth)
               .translate((0.0, c, 0.0)))
    upper = annulus.intersect(
        cq.Workplane("XY").box(2.2 * outer_r, outer_r + edge_e, depth + 2.0,
                                 centered=(True, False, True))
        .translate((0.0, c, depth / 2.0)))
    legs = (cq.Workplane("XY")
            .pushPoints([(-outer_r + edge_e / 2.0, c / 2.0),
                         (outer_r - edge_e / 2.0, c / 2.0)])
            .rect(edge_e, max(c, edge_e)).extrude(depth))
    neck_h = max(stud_y - (c + outer_r) + ear_r, ear_r)
    neck = (cq.Workplane("XY").center(0.0, c + outer_r - 0.25 * edge_e)
            .rect(1.6 * ear_r, neck_h).extrude(depth))
    ear = cq.Workplane("XY").center(0.0, stud_y).circle(ear_r).extrude(depth)
    return upper.union(legs).union(neck).union(ear), stud_y


def build(catalog_row, material_code, tube_od, install_width_min, c, height_d,
          edge_e, thread_code):
    """Build the named four-solid clamp assembly; rail and tube are excluded."""
    del catalog_row, material_code
    channel_width = 41.3
    plate_depth = min(6.0, 0.145 * channel_width)
    axial_gap = 0.35
    cushion_depth = channel_width - 2.0 * (plate_depth + axial_gap)
    plate_offset = cushion_depth / 2.0 + axial_gap
    thread_d = _thread_diameter(thread_code)
    thread_pitch = _unc_pitch(thread_code)
    plate, stud_y = _plate_frame(install_width_min, c, height_d, edge_e,
                                  thread_code, plate_depth)
    outer_r = install_width_min / 2.0
    cushion_outer_r = outer_r - edge_e - 0.35
    bore_r = tube_od / 2.0 + 0.20
    cushion_outer = (cq.Workplane("XY").circle(cushion_outer_r)
                     .extrude(cushion_depth).translate((0.0, c, -cushion_depth / 2.0)))
    cushion_base = (cq.Workplane("XY").center(0.0, c / 2.0)
                    .rect(2.0 * cushion_outer_r, max(c, edge_e))
                    .extrude(cushion_depth).translate((0.0, 0.0, -cushion_depth / 2.0)))
    tube_clearance = (cq.Workplane("XY").circle(bore_r).extrude(cushion_depth + 2.0)
                      .translate((0.0, c, -cushion_depth / 2.0 - 1.0)))
    cushion = cushion_outer.union(cushion_base).cut(tube_clearance)
    slit_w = max(0.9, 0.55 * edge_e)
    slit = (cq.Workplane("XY").center(0.0, c + cushion_outer_r / 2.0)
            .rect(slit_w, cushion_outer_r + 1.0).extrude(cushion_depth + 2.0)
            .translate((0.0, 0.0, -cushion_depth / 2.0 - 1.0)))
    cushion = cushion.cut(slit)

    left_z = -plate_offset - plate_depth
    right_z = plate_offset
    left_plate = plate.translate((0.0, 0.0, left_z))
    right_plate = plate.translate((0.0, 0.0, right_z))
    toe_h = max(1.2, 0.55 * edge_e)
    toe_l = 2.4 * edge_e
    toe_x = outer_r - edge_e / 2.0
    toes = (cq.Workplane("XY").pushPoints([(-toe_x, toe_h / 2.0),
                                             (toe_x, toe_h / 2.0)])
            .rect(toe_l, toe_h).extrude(plate_depth + 1.8))
    hook_relief = (cq.Workplane("XY")
                   .pushPoints([(-outer_r - toe_l / 4.0, toe_h),
                                (outer_r + toe_l / 4.0, toe_h)])
                   .rect(toe_l / 2.0, 2.0 * toe_h)
                   .extrude(plate_depth + 3.8))
    toes = toes.cut(hook_relief)
    left_plate = left_plate.union(toes.translate((0.0, 0.0, left_z - 1.8)))
    right_plate = right_plate.union(toes.translate((0.0, 0.0, right_z)))

    nut_h = 0.82 * thread_d
    nut_z = right_z + plate_depth + 0.45
    stud_start = left_z - 0.6
    stud_end = nut_z + nut_h + 1.5
    stud_length = stud_end - stud_start
    modeled_thread_length = min(stud_length - 0.5, nut_h + 3.0 * thread_pitch)
    stud = (_make_unc_stud(thread_d, thread_pitch, stud_length,
                           modeled_thread_length)
            .translate((0.0, stud_y, stud_start)))
    left_plate = left_plate.union(stud)
    clearance = (cq.Workplane("XY").center(0.0, stud_y)
                 .circle(thread_d / 2.0 + 0.18).extrude(plate_depth + 1.0)
                 .translate((0.0, 0.0, right_z - 0.5)))
    right_plate = right_plate.cut(clearance)

    nut_af = 1.62 * thread_d
    nut = (_make_unc_lock_nut(thread_d, thread_pitch, nut_af, nut_h)
           .translate((0.0, stud_y, nut_z)))

    result = cq.Assembly(name="stc_spc_channel_cushion_clamp_asm")
    result.add(left_plate, name="left_clamp_half")
    result.add(right_plate, name="right_clamp_half")
    result.add(cushion, name="cushion_insert")
    result.add(nut, name="lock_nut")
    return result
