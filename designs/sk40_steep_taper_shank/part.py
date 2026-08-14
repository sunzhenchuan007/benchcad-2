"""Parametric SK40 steep-taper holder reconstructed from the Issue #187 evidence.

The DIN/ISO interface is kept separate from the product-side reconstruction:
the 7:24 taper, flange and pull-stud thread use source-backed SK40 dimensions;
the long cylindrical body and ER25-style nose follow the supplied human STEP.
"""

import cadquery as cq
import math


# Source-locked SK40 drawing dimensions that do not vary in this reconstruction.
_GAUGE_D = 44.45
_FLANGE_D = 63.55
_TAPER_LENGTH = 68.40
_ENTRY_BORE_D = 17.0
_THREAD_NOMINAL_D = 16.0
_THREAD_LENGTH = 32.0
_ENTRY_BORE_LENGTH = 8.2
_DRIVE_SLOT_WIDTH = 16.1
_GAUGE_TO_FLANGE = 3.2
_GRIPPER_CENTER = 11.10
_FLANGE_WIDTH = 15.90
_D2_MAX = 50.0
_L4 = 22.80
_L5 = 25.0
_L6 = 18.50
_ORIENTATION_STEP = 4.60
_ORIENTATION_D = 10.0
_NUT_SLOT_COUNT = 6

# Product-side baseline measured from the supplied human STEP.  Only body_d,
# body_length and nose_d are independent; every other product dimension below
# is derived from these three baseline ratios.
_BASE_BODY_D = 42.0
_BASE_NECK_D = 33.0
_BASE_NECK_LENGTH = 4.5
_BASE_NOSE_D = 42.0
_BASE_NOSE_LENGTH = 25.0
_BASE_THROUGH_BORE_D = 18.0
_BASE_COLLET_OPENING_D = 19.0718
_BASE_NUT_SLOT_WIDTH = 4.5
_BASE_NUT_SLOT_DEPTH = 3.2
_BASE_EDGE_BREAK = 0.5
_BODY_TRANSITION_ANGLE = 45.0
_NUT_NOSE_ANGLE = 60.0
_COLLET_SEAT_ANGLE = 8.0

# Human-reconstructed flange cutter outlines, expressed in the SK40 end view.
# The two large cuts are the opposed drive-interface cuts.  The third is kept
# neutral because its function is not identified by the supplied evidence.
_FLANGE_CUTS = (
    (
        120.0,
        _L5,
        "drive",
        ((-5.3895, 25.5249), (-19.4105, 17.4299),
         (-24.0741, 25.5075), (-10.0531, 33.6025)),
    ),
    (
        -60.0,
        _L4,
        "drive",
        ((18.3105, -15.5247), (4.2895, -23.6197),
         (11.1219, -35.4537), (25.1428, -27.3587)),
    ),
    (
        120.0,
        _L6,
        "orientation",
        ((6.7166, 25.0666), (14.5067, 29.5642),
         (9.6375, 37.9979), (1.8474, 33.5003)),
    ),
)


def _metric_thread_pitch(thread_nominal_d):
    """ISO metric coarse pitch for the source-locked M16 pull-stud thread."""
    if thread_nominal_d <= 12.0:
        return 1.75
    if thread_nominal_d <= 16.0:
        return 2.0
    return 3.0


def _scaled_flange_cut(
    points, center_angle, floor_landmark, cut_kind, flange_d, drive_slot_width
):
    """Map a reconstructed cutter onto the printed SK40 end-view landmarks."""
    a = math.radians(center_angle)
    ux, uy = math.cos(a), math.sin(a)
    tx, ty = -uy, ux
    radial_scale = flange_d / 63.55
    local = []
    for x, y in points:
        local.append((x * ux + y * uy, x * tx + y * ty))
    base_floor = min(v[0] for v in local)
    tangent_center = 0.5 * (min(v[1] for v in local) + max(v[1] for v in local))
    base_width = max(v[1] for v in local) - min(v[1] for v in local)
    target_width = drive_slot_width if cut_kind == "drive" else _ORIENTATION_D
    width_scale = target_width / base_width
    scaled = []
    for radial, tangent in local:
        radial = floor_landmark * radial_scale + (radial - base_floor) * radial_scale
        # The 4.60 drawing value fixes the shallow orientation step; preserve it
        # as a lower bound on the radial run while the excess remains overshoot.
        if cut_kind == "orientation" and radial < floor_landmark + _ORIENTATION_STEP:
            radial = floor_landmark + min(
                radial - floor_landmark, _ORIENTATION_STEP
            )
        tangent = tangent_center * radial_scale + (
            tangent - tangent_center
        ) * width_scale
        scaled.append(
            (
                radial * ux + tangent * tx,
                radial * uy + tangent * ty,
            )
        )
    return scaled


def _thread_cutter(minor_r, major_r, pitch, z_start, length):
    """Triangular helical cutter for the internal metric pull-stud thread."""
    depth = major_r - minor_r
    path_r = minor_r + 0.45 * depth
    path = cq.Wire.makeHelix(pitch, length, path_r).translate(
        cq.Vector(0.0, 0.0, z_start)
    )
    plane = cq.Plane(
        origin=(path_r, 0.0, z_start),
        xDir=(1.0, 0.0, 0.0),
        normal=(0.0, 1.0, 0.0),
    )
    profile = (
        cq.Workplane(plane)
        .moveTo(-0.45 * depth, -0.38 * pitch)
        .lineTo(0.55 * depth, 0.0)
        .lineTo(-0.45 * depth, 0.38 * pitch)
        .close()
    )
    return profile.sweep(path, isFrenet=True)


def _fillet_circles_at_z(body, z_targets, radius):
    """Round only circular transition edges at named axial landmarks."""
    edges = [
        edge
        for edge in body.edges().vals()
        if edge.geomType() == "CIRCLE"
        and any(abs(edge.Center().z - z) < 1e-5 for z in z_targets)
    ]
    return body.newObject(edges).fillet(radius)


def build(
    body_d,
    body_length,
    nose_d,
):
    """Build one complete reconstructed SK40-to-ER25 holder as one solid."""

    # Three independent controls -> all remaining product-side dimensions.
    neck_d = body_d * _BASE_NECK_D / _BASE_BODY_D
    neck_length = body_d * _BASE_NECK_LENGTH / _BASE_BODY_D
    body_transition_angle = _BODY_TRANSITION_ANGLE
    nut_d = nose_d
    nut_length = nose_d * _BASE_NOSE_LENGTH / _BASE_NOSE_D
    nut_nose_angle = _NUT_NOSE_ANGLE
    through_bore_d = body_d * _BASE_THROUGH_BORE_D / _BASE_BODY_D
    collet_seat_angle = _COLLET_SEAT_ANGLE
    collet_opening_d = nose_d * _BASE_COLLET_OPENING_D / _BASE_NOSE_D
    nut_slot_width = nose_d * _BASE_NUT_SLOT_WIDTH / _BASE_NOSE_D
    nut_slot_depth = nose_d * _BASE_NUT_SLOT_DEPTH / _BASE_NOSE_D
    edge_break = min(body_d, nose_d) * _BASE_EDGE_BREAK / _BASE_BODY_D

    # ---------------- source-backed SK40 interface ----------------
    z_taper_end = -_TAPER_LENGTH
    z_flange_front = _GAUGE_TO_FLANGE
    z_flange_back = z_flange_front + _FLANGE_WIDTH
    taper_r = _GAUGE_D / 2.0
    taper_end_r = taper_r - 7.0 * _TAPER_LENGTH / 48.0  # diameter taper 7:24
    flange_r = _FLANGE_D / 2.0

    # The V-flange groove depth is reconstructed from the supplied STEP; only
    # its axial datums (3.2 / 11.10 / 15.90) are printed on the KTA drawing.
    groove_half = 1.6
    groove_flank = max(0.8, 1.5 * edge_break)
    groove_root_r = flange_r - 0.059 * _FLANGE_D

    # ---------------- human-reconstructed product side ----------------
    body_r = body_d / 2.0
    neck_r = neck_d / 2.0
    transition_len = (body_r - neck_r) / math.tan(math.radians(body_transition_angle))
    z_body_end = z_flange_back + body_length
    z_neck_start = z_body_end + transition_len
    z_nut_start = z_neck_start + neck_length
    z_nut_end = z_nut_start + nut_length
    nut_r = nut_d / 2.0
    nut_end_r = max(collet_opening_d / 2.0 + 4.0, 0.715 * nut_d / 2.0)
    nose_len = (nut_r - nut_end_r) / math.tan(math.radians(nut_nose_angle))
    z_nose_start = z_nut_end - nose_len

    outer_profile = [
        (0.0, z_taper_end),
        (max(taper_end_r - edge_break, 0.1), z_taper_end),
        (taper_end_r + 7.0 * edge_break / 48.0, z_taper_end + edge_break),
        (taper_r, 0.0),
        (taper_r, z_flange_front),
        (flange_r - edge_break, z_flange_front),
        (flange_r, z_flange_front + edge_break),
        (flange_r, _GRIPPER_CENTER - groove_half - groove_flank),
        (groove_root_r + edge_break, _GRIPPER_CENTER - groove_half),
        (groove_root_r, _GRIPPER_CENTER - groove_half + edge_break),
        (groove_root_r, _GRIPPER_CENTER + groove_half - edge_break),
        (groove_root_r + edge_break, _GRIPPER_CENTER + groove_half),
        (flange_r, _GRIPPER_CENTER + groove_half + groove_flank),
        (flange_r, z_flange_back - edge_break),
        (flange_r - edge_break, z_flange_back),
        (body_r, z_flange_back),
        (body_r, z_body_end),
        (neck_r, z_neck_start),
        (neck_r, z_nut_start),
        (nut_r, z_nut_start),
        (nut_r, z_nose_start),
        (nut_end_r, z_nut_end),
        (0.0, z_nut_end),
    ]
    result = (
        cq.Workplane("XZ")
        .polyline(outer_profile)
        .close()
        .revolve(360.0, axisStart=(0.0, z_taper_end), axisEnd=(0.0, z_nut_end))
    )
    result = _fillet_circles_at_z(
        result,
        (z_body_end, z_neck_start, z_nut_start, z_nose_start),
        edge_break,
    )

    # Continuous internal cavity: SK pull-thread entry, central passage, 8 deg
    # ER-style collet seat, reconstructed nut reliefs and a 30 deg entry flare.
    pitch = _metric_thread_pitch(_THREAD_NOMINAL_D)
    minor_d = _THREAD_NOMINAL_D - 1.082532 * pitch
    z_thread_start = z_taper_end + _ENTRY_BORE_LENGTH
    z_through_start = z_flange_back + 0.165 * body_length
    z_seat_start = z_body_end - 0.06 * body_length
    z_seat_end = z_nut_start + 0.52 * nut_length
    seat_r = through_bore_d / 2.0 + (
        z_seat_end - z_seat_start
    ) * math.tan(math.radians(collet_seat_angle))
    relief_r = max(seat_r, nut_r - 5.0)
    opening_r = collet_opening_d / 2.0
    entry_flare_len = min(0.24 * nut_length, (relief_r - opening_r) / math.tan(math.radians(30.0)))

    cavity_profile = [
        (0.0, z_taper_end - 1.0),
        (_ENTRY_BORE_D / 2.0, z_taper_end - 1.0),
        (_ENTRY_BORE_D / 2.0, z_thread_start),
        (minor_d / 2.0, z_thread_start + edge_break),
        (minor_d / 2.0, z_through_start),
        (through_bore_d / 2.0, z_through_start + edge_break),
        (through_bore_d / 2.0, z_seat_start),
        (seat_r, z_seat_end),
        (relief_r, z_seat_end + edge_break),
        (relief_r, z_nut_end - entry_flare_len - 2.0 * edge_break),
        (relief_r - edge_break, z_nut_end - entry_flare_len - edge_break),
        (opening_r + math.tan(math.radians(30.0)) * entry_flare_len,
         z_nut_end - entry_flare_len),
        (opening_r, z_nut_end),
        (0.0, z_nut_end),
    ]
    cavity = (
        cq.Workplane("XZ")
        .polyline(cavity_profile)
        .close()
        .revolve(360.0, axisStart=(0.0, z_taper_end - 1.0), axisEnd=(0.0, z_nut_end))
    )
    result = result.cut(cavity)

    thread_run = max(pitch, _THREAD_LENGTH - _ENTRY_BORE_LENGTH)
    thread = _thread_cutter(
        minor_d / 2.0,
        _THREAD_NOMINAL_D / 2.0,
        pitch,
        z_thread_start + 0.5 * pitch,
        thread_run - pitch,
    )
    result = result.cut(thread)

    # Three separate flange cuts, recreated semantically from the human STEP.
    for center_angle, floor_landmark, cut_kind, points in _FLANGE_CUTS:
        cut_points = _scaled_flange_cut(
            points,
            center_angle,
            floor_landmark,
            cut_kind,
            _FLANGE_D,
            _DRIVE_SLOT_WIDTH,
        )
        cutter = (
            cq.Workplane("XY", origin=(0.0, 0.0, z_flange_front - 1.0))
            .polyline(cut_points)
            .close()
            .extrude(_FLANGE_WIDTH + 2.0)
        )
        result = result.cut(cutter)

    # Six equally-spaced product-end slots.  Their outward overshoot is purely
    # construction geometry; the meaningful controls are width/depth/length.
    slot_length = min(0.87 * nut_length, nut_length - 2.0 * edge_break)
    slot_floor = nut_r - nut_slot_depth
    slot_cutter = (
        cq.Workplane("XY", origin=(0.0, slot_floor, z_nut_end - slot_length))
        .box(
            nut_slot_width,
            nut_slot_depth + 2.0,
            slot_length + 1.0,
            centered=(True, False, False),
        )
    )
    for i in range(_NUT_SLOT_COUNT):
        cutter = slot_cutter.rotate(
            (0.0, 0.0, 0.0),
            (0.0, 0.0, 1.0),
            i * 360.0 / _NUT_SLOT_COUNT,
        )
        result = result.cut(cutter)

    return result
