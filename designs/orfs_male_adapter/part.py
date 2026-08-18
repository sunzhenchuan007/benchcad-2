"""Parker F5OLO-style male ORFS to male SAE-ORB straight adapter.

The fitting axis is +Z.  The SAE-ORB stud starts at ``z=0``; the ORFS
face-seal end is at the opposite end.  Thread diameters, pitches, port bores,
hex size, and seal-groove dimensions are explicit so ``spec.py`` can row-lock
the catalog dimensions and honestly label the visualization proportions.

The 60-degree external-thread construction follows the reviewed reusable
standard-component helper, generalized here for inch Unified threads.  It is
a deterministic visible thread, not a tolerance-class or manufacturing model.
"""

import math

import cadquery as cq


def _modeled_external_thread(major_d, tpi, length):
    """Build a simplified 60-degree Unified external thread along +Z.

    This uses the stable existing-family idiom: start from the major-diameter
    envelope and subtract a single-start helical V groove.  The 0.6134 pitch
    radial depth is the same basic external-thread depth used by the reusable
    standard-component implementation (1.226869 pitch on diameter).
    """
    pitch = 25.4 / float(tpi)
    major_r = float(major_d) / 2.0
    root_r = major_r - 0.6134345 * pitch
    if root_r <= 0.0 or float(length) <= pitch:
        raise ValueError("thread dimensions do not leave a valid threaded solid")

    blank = cq.Workplane("XY").circle(major_r).extrude(float(length))
    path = cq.Workplane("XY").add(cq.Wire.makeHelix(pitch, float(length) + 0.5 * pitch, major_r))
    overcut = 0.25 * pitch
    groove = (
        cq.Workplane("XZ")
        .center(major_r + overcut, 0.0)
        .moveTo(0.0, -pitch / 2.0)
        .lineTo(-(0.6134345 * pitch + overcut), 0.0)
        .lineTo(0.0, pitch / 2.0)
        .close()
        .sweep(path, isFrenet=False)
        .translate((0.0, 0.0, -0.5 * pitch))
    )
    return cq.Workplane(obj=blank.val().cut(groove.val()))


def _chamfered_hex(across_flats, length, base_z):
    """Build a wrench hex with equal proportioned end-face chamfers."""
    corner_d = float(across_flats) / math.cos(math.pi / 6.0)
    hex_blank = (
        cq.Workplane("XY")
        .workplane(offset=float(base_z))
        .polygon(6, corner_d)
        .extrude(float(length))
        .val()
    )

    chamfer_h = min(0.12 * float(length), 0.08 * float(across_flats))
    face_land_r = 0.475 * float(across_flats)
    crown_r = corner_d / 2.0 + 0.01
    envelope = (
        cq.Workplane("XZ")
        .moveTo(0.0, float(base_z))
        .lineTo(face_land_r, float(base_z))
        .lineTo(crown_r, float(base_z) + chamfer_h)
        .lineTo(crown_r, float(base_z) + float(length) - chamfer_h)
        .lineTo(face_land_r, float(base_z) + float(length))
        .lineTo(0.0, float(base_z) + float(length))
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
        .val()
    )
    return cq.Workplane(obj=hex_blank.intersect(envelope))


def build(
    catalog_row,
    orfs_thread_d,
    orfs_tpi,
    orb_thread_d,
    orb_tpi,
    hex_af,
    hex_len,
    orfs_thread_len,
    orfs_neck_len,
    orb_thread_len,
    orb_neck_len,
    orfs_bore_d,
    orb_bore_d,
    orfs_groove_inner_d,
    orfs_groove_outer_d,
    orfs_groove_depth,
    orb_groove_root_d,
    orb_groove_width,
    orb_groove_from_tip,
):
    """Build one hollow ORFS x ORB adapter body.

    ``catalog_row`` preserves the discrete Parker ordering in the generated
    program; ``spec.py`` locks every other argument to that same catalog row.
    ``orfs_groove_*`` describes the annular face-seal recess.  The
    ``orb_groove_*`` parameters describe the circumferential O-ring recess
    behind the ORB thread.  O-rings themselves are intentionally omitted so
    the family remains one metal solid.
    """
    if int(catalog_row) < 1:
        raise ValueError("catalog_row must be a positive Parker table row")

    orb_thread_end = float(orb_thread_len)
    hex_start = orb_thread_end + float(orb_neck_len)
    hex_end = hex_start + float(hex_len)
    orfs_thread_start = hex_end + float(orfs_neck_len)
    overall_len = orfs_thread_start + float(orfs_thread_len)

    # The two threaded studs overlap their plain necks slightly so all pieces
    # fuse into one robust solid after the thread sweeps are constructed.
    orb_thread = _modeled_external_thread(orb_thread_d, orb_tpi, orb_thread_len + 0.05)
    orb_neck = (
        cq.Workplane("XY")
        .workplane(offset=orb_thread_end - 0.05)
        .circle(float(orb_thread_d) / 2.0)
        .extrude(float(orb_neck_len) + 0.10)
    )
    wrench_hex = _chamfered_hex(hex_af, hex_len, hex_start - 0.05)
    orfs_neck = (
        cq.Workplane("XY")
        .workplane(offset=hex_end - 0.05)
        .circle(float(orfs_thread_d) / 2.0)
        .extrude(float(orfs_neck_len) + 0.10)
    )
    orfs_thread = _modeled_external_thread(
        orfs_thread_d, orfs_tpi, orfs_thread_len + 0.05
    ).translate((0.0, 0.0, orfs_thread_start - 0.05))

    # Fuse sequentially.  CadQuery 2.3/OCC is more reliable here than one
    # variadic fuse for the large Parker rows, where all five operands overlap.
    result_shape = orb_thread.val().fuse(orb_neck.val())
    result_shape = result_shape.fuse(wrench_hex.val())
    result_shape = result_shape.fuse(orfs_neck.val())
    result_shape = result_shape.fuse(orfs_thread.val())

    # Axial fluid passage: the two catalog port diameters transition smoothly
    # inside the hex instead of ending in a hidden internal step.
    transition_half = min(0.18 * float(hex_len), 1.5)
    transition_mid = hex_start + 0.5 * float(hex_len)
    transition_lo = transition_mid - transition_half
    transition_hi = transition_mid + transition_half
    overcut = 0.20
    bore = (
        cq.Workplane("XZ")
        .moveTo(0.0, -overcut)
        .lineTo(float(orb_bore_d) / 2.0, -overcut)
        .lineTo(float(orb_bore_d) / 2.0, transition_lo)
        .lineTo(float(orfs_bore_d) / 2.0, transition_hi)
        .lineTo(float(orfs_bore_d) / 2.0, overall_len + overcut)
        .lineTo(0.0, overall_len + overcut)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )
    result_shape = result_shape.cut(bore.val())

    # ORFS face groove, cut axially into the terminal sealing face.
    face_groove = (
        cq.Workplane("XY")
        .workplane(offset=overall_len - float(orfs_groove_depth))
        .circle(float(orfs_groove_outer_d) / 2.0)
        .circle(float(orfs_groove_inner_d) / 2.0)
        .extrude(float(orfs_groove_depth) + 0.10)
    )
    result_shape = result_shape.cut(face_groove.val())

    # SAE-ORB circumferential groove behind the thread.  The cutter begins at
    # the requested root diameter and removes material out through the surface.
    groove_z0 = float(orb_groove_from_tip) - 0.5 * float(orb_groove_width)
    groove_z1 = float(orb_groove_from_tip) + 0.5 * float(orb_groove_width)
    groove_outer_r = 0.5 * float(orb_thread_d) + 0.50
    orb_groove = (
        cq.Workplane("XZ")
        .moveTo(float(orb_groove_root_d) / 2.0, groove_z0)
        .lineTo(groove_outer_r, groove_z0)
        .lineTo(groove_outer_r, groove_z1)
        .lineTo(float(orb_groove_root_d) / 2.0, groove_z1)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )
    result_shape = result_shape.cut(orb_groove.val())

    result = cq.Workplane(obj=result_shape)
    return result
