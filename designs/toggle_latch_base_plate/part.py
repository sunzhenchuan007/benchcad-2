"""toggle_latch_base_plate — the parametric part.

Stamped / formed mounting base for a Ganter GN 832 toggle latch: a flat base
plate carrying two mounting holes and an upstanding U-clevis whose two ears hold
the toggle pivot pin. The swinging lever, the U-bolt latch hook and the separate
catch bracket are the mating pieces of the assembly and are OUT OF SCOPE — this
family models the base plate + clevis only (prismatic base + bracket + holes).

Plain parametric CadQuery: named parameters, `result` bound and returned; bench2
derives each instance's stand-alone program from this body (the arguments become
module globals and the `_helpers` are inlined).

Drawing-symbol -> build() parameter glossary (GN 832 dimensioned sketch):
  l2  -> plate_l       base-plate length (X), left end to pivot axis
  b1  -> plate_w       base-plate width (Y)
  s   -> plate_t       stamped sheet / plate thickness (Z)     [proportion]
  --  -> corner_r      rounded plate-corner radius             [proportion]
  d2  -> mount_hole_d  mounting-hole diameter (2 holes)
  d1  -> pin_d         pivot pin-hole diameter (through the ears)
  h1  -> brk_h         overall height, plate underside to clevis top
  b2  -> brk_w         clevis outer width (Y)
  --  -> wall_t        clevis wall (ear) thickness             [proportion]
  --  -> fold_r        base<->clevis fold fillet radius        [proportion]
  b3  -> nose_w        keeper-nose tab width (Y)               [feature has_nose]
  d3  -> cotter_d      spring-cotter-pin bore diameter         [feature has_nose]

IMPORTANT: `corner_r` is a modeled plate-corner round (a proportion). It is NOT
the drawing symbol `r` — that `r` is the U-bolt reach of the (un-modeled) lever.

Longitudinal layout (X, left->right): [keeper nose] .. [2 mounting holes] ..
[U-clevis + pivot pin] at the right end. The clevis length, its X inset, the
nose length, the hole X-positions and the pin height are fixed internal
proportions of plate_l / brk_h (see the `_helpers`), so build and spec.check()
share them and never drift.
"""

import cadquery as cq


def _brk_len(plate_l):
    """Clevis (pivot bracket) length along X — a proportion of the plate."""
    return 0.20 * plate_l


def _nose_len(plate_l):
    """Keeper-nose tab length along X — a proportion of the plate."""
    return 0.14 * plate_l


def _clevis_cx(plate_l):
    """X of the clevis centre / pivot axis: the bracket sits against the right
    end, inset 6% of the length so the rounded right corners stay clear."""
    return plate_l - 0.06 * plate_l - _brk_len(plate_l) / 2.0


def _mount_hole_x(plate_l, has_nose):
    """X of the two mounting-hole centres, spaced across the flat plate region
    between the left/nose end and the clevis base. Shared with spec.check() so
    the part and the edge-distance checks never drift."""
    left = _nose_len(plate_l) if has_nose else 0.0
    clevis_left = _clevis_cx(plate_l) - _brk_len(plate_l) / 2.0
    span = clevis_left - left
    return left + 0.24 * span, left + 0.66 * span


def _pin_z(plate_t, brk_h):
    """Height of the pivot-pin axis: 60% up the ear, above the base plate."""
    return plate_t + 0.60 * (brk_h - plate_t)


def build(plate_l, plate_w, plate_t, corner_r, mount_hole_d, pin_d,
          brk_h, brk_w, wall_t, fold_r, has_nose, nose_w, cotter_d):
    L, B, s, H = plate_l, plate_w, plate_t, brk_h
    bl = _brk_len(L)             # clevis length along X
    cx = _clevis_cx(L)           # clevis centre / pivot axis (X)

    # --- base plate: flat stamped sheet on XY, extruded +Z ------------------
    if has_nose:
        nl = _nose_len(L)
        # stepped outline: narrow keeper nose over [0, nl], then full-width body
        pts = [
            (0.0, nose_w / 2.0), (nl, nose_w / 2.0), (nl, B / 2.0),
            (L, B / 2.0), (L, -B / 2.0), (nl, -B / 2.0),
            (nl, -nose_w / 2.0), (0.0, -nose_w / 2.0),
        ]
        result = cq.Workplane("XY").polyline(pts).close().extrude(s)
    else:
        result = cq.Workplane("XY").box(L, B, s, centered=(False, True, False))

    # rounded plate corners (the drawing's formed/stamped rounds): the two
    # exposed convex ends — right corners at x=L and the nose tip / left at x=0.
    result = result.edges("|Z and >X").fillet(corner_r)
    nose_r = min(corner_r, 0.8 * nose_w / 2.0) if has_nose else corner_r
    result = result.edges("|Z and <X").fillet(nose_r)

    # --- upstanding U-clevis: two ears rising from the plate top -----------
    ear_off = brk_w / 2.0 - wall_t / 2.0        # ear centre-line offset in Y
    for y in (ear_off, -ear_off):
        ear = (cq.Workplane("XY").workplane(offset=s).center(cx, y)
               .box(bl, wall_t, H - s, centered=(True, True, False)))
        result = result.union(ear)

    # base<->clevis fold fillet on the outer bend line of each ear (the visible
    # formed fold); the inner base stays sharp inside the lever slot.
    for yb in (brk_w / 2.0, -brk_w / 2.0):
        sel = cq.selectors.BoxSelector(
            (cx - bl, yb - 0.15, s - 0.2), (cx + bl, yb + 0.15, s + 0.2))
        result = result.edges(sel).fillet(fold_r)

    # --- mounting holes: two through-holes on the centreline ---------------
    xf, xn = _mount_hole_x(L, has_nose)
    for xh in (xf, xn):
        cyl = (cq.Workplane("XY").workplane(offset=-1.0).center(xh, 0.0)
               .circle(mount_hole_d / 2.0).extrude(s + 2.0))
        result = result.cut(cyl)

    # --- pivot pin hole: through both ears, axis along Y -------------------
    zc = _pin_z(s, H)
    pin = cq.Solid.makeCylinder(pin_d / 2.0, B + 2.0,
                                cq.Vector(cx, -(B / 2.0 + 1.0), zc),
                                cq.Vector(0, 1, 0))
    result = result.cut(pin)

    # --- keeper-nose cotter bore (feature) --------------------------------
    if has_nose:
        xb = _nose_len(L) * 0.5
        bore = (cq.Workplane("XY").workplane(offset=-1.0).center(xb, 0.0)
                .circle(cotter_d / 2.0).extrude(s + 2.0))
        result = result.cut(bore)

    return result
