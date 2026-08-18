"""SAE J518-1 / ISO 6162-1 Code 61 split-flange clamp half.

The part is one forged half: a kidney-shaped bridge with two bolt ears and a
stepped, open bore.  Two identical copies clamp behind a hydraulic flange head.
All dimensions are millimetres; spec.py selects complete catalog rows so the
standard bolt pattern and the manufacturer envelope cannot drift apart.
"""

import cadquery as cq


def _half_disc(radius, split_setback, thickness):
    """Disc clipped at the real split face, just right of its pattern centre."""
    disc = cq.Workplane("XY").circle(radius).extrude(thickness)
    trim = (
        cq.Workplane("XY")
        .center((radius + split_setback) / 2.0, 0.0)
        .box(
            radius - split_setback,
            2.0 * radius + 2.0,
            thickness,
            centered=(True, True, False),
        )
    )
    return disc.intersect(trim)


def _half_crown_dome(
    inner_radius,
    outer_radius,
    split_setback,
    plate_thickness,
    overall_thickness,
    front_start,
    transition_start,
):
    """Rounded forged crown clipped to the catalog split face.

    The Anfield Rev. C side view shows the bridge's whole outer face bulging
    from ear thickness H to overall thickness G, rather than as a flat-topped
    prism or an inward cut. The forging curve is not dimensioned, so a smooth
    symmetric spline keeps both radial edges at H and the bridge centre at G.
    """
    mid_radius = (inner_radius + outer_radius) / 2.0
    # Let the cap overlap the H-thick plate by a small amount.  This avoids
    # coincident-face booleans while leaving the catalog H/G envelope visible.
    epsilon = 0.50  # mm; small hidden overlap for robust booleans
    cap_base = plate_thickness - epsilon
    span = outer_radius - inner_radius
    full_crown = (
        cq.Workplane("XZ")
        .moveTo(inner_radius, cap_base)
        # A spline is used instead of a three-point circle: the latter's
        # circular continuation overshoots the F envelope at both edges.
        .spline(
            [
                (inner_radius + 0.25 * span,
                 cap_base + 0.68 * (overall_thickness - cap_base)),
                (mid_radius, overall_thickness),
                (outer_radius - 0.25 * span,
                 cap_base + 0.68 * (overall_thickness - cap_base)),
                (outer_radius, cap_base),
            ]
        )
        .lineTo(inner_radius, cap_base)
        .close()
        .revolve(360.0, (0.0, 0.0), (0.0, 1.0))
    )
    clip = (
        cq.Workplane("XY", origin=(0.0, 0.0, cap_base))
        .center((outer_radius + split_setback) / 2.0, 0.0)
        .box(
            outer_radius - split_setback,
            2.0 * outer_radius + 2.0,
            overall_thickness - cap_base,
            centered=(True, True, False),
        )
    )
    # The photo/drawing show the crown starting only after the end pads.  A
    # A sloped X-Z ramp starts outside the circular ear land, so the complete
    # bolt-pad region stays at H.  The transition length is an explicit
    # proportion because no forging radius is dimensioned by either catalog.
    ramp = (
        cq.Workplane("XZ")
        .polyline(
            [
                (split_setback - epsilon, cap_base),
                (outer_radius + epsilon, cap_base),
                (outer_radius + epsilon, overall_thickness),
                (front_start - epsilon, overall_thickness),
                (transition_start - epsilon, cap_base),
            ]
        )
        .close()
        .extrude(2.0 * outer_radius + 2.0, both=True)
    )
    return full_crown.intersect(clip).intersect(ramp)


def build(
    counterbore_d,
    bore_d,
    bolt_spacing,
    overall_length,
    split_to_bolt,
    half_width,
    overall_thickness,
    plate_thickness,
    lip_depth,
    bolt_hole_d,
    split_setback,
):
    # The two end pads set catalog length D exactly; the broad half-disc makes
    # the forged bridge and sets manufacturer-specific half width F.
    ear_r = (overall_length - bolt_spacing) / 2.0
    bolt_pts = [
        (split_to_bolt, bolt_spacing / 2.0),
        (split_to_bolt, -bolt_spacing / 2.0),
    ]
    bridge_plate = _half_disc(half_width, split_setback, plate_thickness)
    ears = (
        cq.Workplane("XY")
        .pushPoints(bolt_pts)
        .circle(ear_r)
        .extrude(plate_thickness)
    )
    # The catalog setback applies to the complete mating split face, including
    # both bolt ears.  Clip the circular forging allowance so no ear protrudes
    # past the same face used by the open bridge.
    ear_trim = (
        cq.Workplane("XY")
        .center((half_width + split_setback) / 2.0, 0.0)
        .box(
            half_width - split_setback,
            overall_length + 2.0,
            plate_thickness,
            centered=(True, True, False),
        )
    )
    ears = ears.intersect(ear_trim)
    base = bridge_plate.union(ears)

    # The forged bridge has the rounded crown shown in the catalog side view:
    # it rises smoothly from H to G between the B bore and the F outer envelope.
    # Start the crown after the circular end-pad transition so the bolt-hole
    # lands remain at the catalog ear thickness H.
    crown = _half_crown_dome(
        bore_d / 2.0,
        half_width,
        split_setback,
        plate_thickness,
        overall_thickness,
        split_to_bolt + 1.25 * ear_r,
        split_to_bolt + 1.00 * ear_r,
    )
    result = base.union(crown)

    # B passes through; larger A is recessed by I and leaves the shoulder that
    # hooks behind the mating flange head.  Both cylinders open at the clipped
    # split face rather than making a closed central hole.
    bore = cq.Workplane("XY").circle(bore_d / 2.0).extrude(overall_thickness)
    counterbore = cq.Workplane("XY").circle(counterbore_d / 2.0).extrude(lip_depth)
    result = result.cut(bore).cut(counterbore)

    bolt_holes = (
        cq.Workplane("XY")
        .pushPoints(bolt_pts)
        .circle(bolt_hole_d / 2.0)
        .extrude(overall_thickness)
    )
    result = result.cut(bolt_holes)
    return result
