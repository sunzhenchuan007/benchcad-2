"""Catalog-row sampling for the DIN 3015 Part 2 heavy RI clamp."""

CATALOG_ROWS = [
    # group, D, D1, L1, L2, H, B, insert material (0=SA73, 1=E70)
    (4, 6.0, 25.0, 70.0, 45.0, 46.5, 30.5, 0),
    (4, 8.0, 25.0, 70.0, 45.0, 46.5, 30.5, 0),
    (4, 10.0, 25.0, 70.0, 45.0, 46.5, 30.5, 0),
    (4, 12.0, 25.0, 70.0, 45.0, 46.5, 30.5, 0),
    (4, 12.7, 25.0, 70.0, 45.0, 46.5, 30.5, 0),
    (4, 14.0, 25.0, 70.0, 45.0, 46.5, 30.5, 0),
    (4, 15.0, 25.0, 70.0, 45.0, 46.5, 30.5, 0),
    (4, 16.0, 25.0, 70.0, 45.0, 46.5, 30.5, 0),
    (4, 17.2, 25.0, 70.0, 45.0, 46.5, 30.5, 0),
    (4, 18.0, 25.0, 70.0, 45.0, 46.5, 30.5, 0),
    (4, 19.0, 25.0, 70.0, 45.0, 46.5, 30.5, 0),
    (5, 20.0, 38.0, 85.0, 60.0, 58.0, 30.5, 0),
    (5, 21.3, 38.0, 85.0, 60.0, 58.0, 30.5, 0),
    (5, 22.0, 38.0, 85.0, 60.0, 58.0, 30.5, 0),
    (5, 25.0, 38.0, 85.0, 60.0, 58.0, 30.5, 0),
    (5, 26.9, 38.0, 85.0, 60.0, 58.0, 30.5, 0),
    (5, 28.0, 38.0, 85.0, 60.0, 58.0, 30.5, 0),
    (5, 30.0, 38.0, 85.0, 60.0, 58.0, 30.5, 0),
    (5, 32.0, 38.0, 85.0, 60.0, 58.0, 30.5, 0),
    (6, 32.0, 64.0, 115.0, 90.0, 87.0, 45.0, 0),
    (6, 33.7, 64.0, 115.0, 90.0, 87.0, 45.0, 0),
    (6, 35.0, 64.0, 115.0, 90.0, 87.0, 45.0, 0),
    (6, 38.7, 64.0, 115.0, 90.0, 87.0, 45.0, 0),
    (6, 40.0, 64.0, 115.0, 90.0, 87.0, 45.0, 0),
    (6, 42.0, 64.0, 115.0, 90.0, 87.0, 45.0, 0),
    (6, 45.5, 64.0, 115.0, 90.0, 87.0, 45.0, 0),
    (6, 48.0, 64.0, 115.0, 90.0, 87.0, 45.0, 0),
    (6, 51.0, 64.0, 115.0, 90.0, 87.0, 45.0, 0),
    (6, 53.4, 64.0, 115.0, 90.0, 87.0, 45.0, 0),
    (6, 56.4, 64.0, 115.0, 90.0, 87.0, 45.0, 0),
    (8, 80.0, 114.0, 208.0, 168.0, 168.0, 80.0, 1),
    (8, 88.9, 114.0, 208.0, 168.0, 168.0, 80.0, 1),
    (8, 102.0, 114.0, 208.0, 168.0, 168.0, 80.0, 1),
    (9, 114.0, 150.0, 251.0, 205.0, 200.0, 91.0, 1),
    (9, 133.0, 150.0, 251.0, 205.0, 200.0, 91.0, 1),
    (9, 140.0, 150.0, 251.0, 205.0, 200.0, 91.0, 1),
    (10, 150.0, 200.0, 336.0, 265.0, 270.0, 120.0, 1),
    (10, 165.0, 200.0, 336.0, 265.0, 270.0, 120.0, 1),
    (10, 168.0, 200.0, 336.0, 265.0, 270.0, 120.0, 1),
    (10, 172.0, 200.0, 336.0, 265.0, 270.0, 120.0, 1),
]

# The catalogue prints all eight Group 7S dimensional rows, but its material
# field does not assign SA73 or E70. They are retained as explicit held data,
# not silently discarded or sampled with a fabricated material.
HELD_7S_ROWS = [
    (7, 55.0, 88.0, 154.0, 122.0, 120.0, 60.0),
    (7, 57.0, 88.0, 154.0, 122.0, 120.0, 60.0),
    (7, 60.0, 88.0, 154.0, 122.0, 120.0, 60.0),
    (7, 63.5, 88.0, 154.0, 122.0, 120.0, 60.0),
    (7, 65.0, 88.0, 154.0, 122.0, 120.0, 60.0),
    (7, 70.0, 88.0, 154.0, 122.0, 120.0, 60.0),
    (7, 72.0, 88.0, 154.0, 122.0, 120.0, 60.0),
    (7, 76.0, 88.0, 154.0, 122.0, 120.0, 60.0),
]

DIFFICULTY_ROWS = {
    "easy": list(range(0, 19)) + [0, 18] * 4,
    "medium": list(range(19, 30)) + [19, 29] * 4,
    "hard": list(range(30, 40)) + [30, 39] * 4,
}

ROW_FIELDS = (
    "group",
    "pipe_od",
    "insert_outer_d",
    "length",
    "mount_spacing",
    "height",
    "width",
    "insert_material",
)

CATALOG_SOURCE = (
    "STAUFF Catalogue 1 - STAUFF Clamps, English 06/2026, p.42, "
    "Heavy Series DIN 3015 Part 2 type RI drawing and table"
)
PROPORTION_SOURCE = (
    "STAUFF 1110008634 STEP, 4006_PPR Group 4; "
    "other catalogue groups use documented proportional scaling"
)


def _row_range(column):
    index = ROW_FIELDS.index(column)
    return {
        difficulty: (
            min(CATALOG_ROWS[i][index] for i in rows),
            max(CATALOG_ROWS[i][index] for i in rows),
        )
        for difficulty, rows in DIFFICULTY_ROWS.items()
    }


def _row_index_range():
    return {difficulty: (min(rows), max(rows)) for difficulty, rows in DIFFICULTY_ROWS.items()}


def _derived_geometry(row):
    _, pipe_od, insert_outer_d, length, mount_spacing, height, width, _ = row
    split_gap = 0.0
    radial_clearance = 0.0
    axial_clearance = 0.0
    insert_width = width
    seat_groove_depth = 0.13 * insert_outer_d
    seat_groove_width = 0.50 * width
    cavity_radius = insert_outer_d / 2.0 + seat_groove_depth
    cavity_limited_hole_d = 2.0 * (mount_spacing / 2.0 - cavity_radius - 0.5)
    mount_hole_d = min(
        0.341 * width,
        0.416 * (length - mount_spacing),
        cavity_limited_hole_d,
    )
    counterbore_d = min(0.590 * width, 0.720 * (length - mount_spacing))
    half_height = (height - split_gap) / 2.0
    counterbore_depth = 0.387 * half_height
    corner_radius = 0.262 * width
    rib_height = seat_groove_depth
    rib_width = seat_groove_width
    return {
        "split_gap": split_gap,
        "radial_clearance": radial_clearance,
        "axial_clearance": axial_clearance,
        "insert_width": insert_width,
        "seat_groove_depth": seat_groove_depth,
        "seat_groove_width": seat_groove_width,
        "mount_hole_d": mount_hole_d,
        "counterbore_d": counterbore_d,
        "counterbore_depth": counterbore_depth,
        "corner_radius": corner_radius,
        "rib_height": rib_height,
        "rib_width": rib_width,
    }


def _derived_range(name):
    return {
        difficulty: (
            min(_derived_geometry(CATALOG_ROWS[i])[name] for i in rows),
            max(_derived_geometry(CATALOG_ROWS[i])[name] for i in rows),
        )
        for difficulty, rows in DIFFICULTY_ROWS.items()
    }


PARAM_SPEC = {
    "catalog_row": dict(
        desc=("selector for one of 40 material-complete p.42 rows; eight 7S rows are held"),
        unit="",
        range=_row_index_range(),
        choices=DIFFICULTY_ROWS,
        integer=True,
        coverage=[0, 18, 19, 30, 39],
        source=CATALOG_SOURCE,
    ),
    "pipe_od": dict(
        desc="supported pipe, tube or hose outside diameter D",
        unit="mm",
        range=_row_range("pipe_od"),
        refine=True,
        source=CATALOG_SOURCE,
    ),
    "insert_outer_d": dict(
        desc="elastomer insert outside diameter D1",
        unit="mm",
        range=_row_range("insert_outer_d"),
        refine=True,
        source=CATALOG_SOURCE,
    ),
    "length": dict(
        desc="overall clamp-body length L1",
        unit="mm",
        range=_row_range("length"),
        refine=True,
        source=CATALOG_SOURCE,
    ),
    "mount_spacing": dict(
        desc="mounting-hole centre spacing L2",
        unit="mm",
        range=_row_range("mount_spacing"),
        refine=True,
        source=CATALOG_SOURCE,
    ),
    "height": dict(
        desc="assembled clamp-body height H",
        unit="mm",
        range=_row_range("height"),
        refine=True,
        source=CATALOG_SOURCE,
    ),
    "width": dict(
        desc="clamp-body axial width B",
        unit="mm",
        range=_row_range("width"),
        refine=True,
        source=CATALOG_SOURCE,
    ),
    "body_material": dict(
        desc=("metadata-only body material code: 0=PP-R, 1=PA-R; no constitutive simulation"),
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        integer=True,
        source="STAUFF Catalogue 1, English 06/2026, p.42 material key",
    ),
    "insert_material": dict(
        desc="metadata-only insert material: 0=SA73 (4S-6S), 1=E70 (8S-10S)",
        unit="",
        range=_row_range("insert_material"),
        refine=True,
        integer=True,
        source="STAUFF Catalogue 1, English 06/2026, p.42 material key",
    ),
}

for _name, _desc in (
    ("split_gap", "closed-pose separation at the clamp split plane"),
    ("radial_clearance", "nominal radial clearance at the insert core"),
    ("axial_clearance", "nominal axial clearance at each insert end"),
    ("insert_width", "full axial width of the stepped insert"),
    ("seat_groove_depth", "radial depth of the central retention groove"),
    ("seat_groove_width", "axial width of the central retention groove"),
    ("mount_hole_d", "mounting through-passage diameter"),
    ("counterbore_d", "outside counterbore diameter"),
    ("counterbore_depth", "outside counterbore depth"),
    ("corner_radius", "clamp-body plan corner radius"),
    ("rib_height", "radial height of the insert central band"),
    ("rib_width", "axial width of the insert central band"),
):
    PARAM_SPEC[_name] = dict(
        desc=_desc,
        unit="mm",
        range=_derived_range(_name),
        refine=True,
        source=PROPORTION_SOURCE,
    )


def _selected_row(p):
    index = int(p["catalog_row"])
    if index < 0 or index >= len(CATALOG_ROWS):
        return None
    return CATALOG_ROWS[index]


def refine(p, difficulty, rng):
    del difficulty, rng
    row = _selected_row(p)
    if row is None:
        return
    for name, value in zip(ROW_FIELDS[1:], row[1:]):
        p[name] = value
    p.update(_derived_geometry(row))


def _different(actual, expected):
    return abs(float(actual) - float(expected)) > 1e-9


def check(p):
    bad = []
    row = _selected_row(p)
    if row is None:
        return ["catalog_row does not select one of the 40 sampleable p.42 rows"]

    for name, expected in zip(ROW_FIELDS[1:], row[1:]):
        if _different(p[name], expected):
            bad.append(f"{name} must match the selected STAUFF p.42 row")

    expected_geometry = _derived_geometry(row)
    for name, expected in expected_geometry.items():
        if _different(p[name], expected):
            bad.append(f"{name} drifted from its documented proportion")

    if int(p["body_material"]) not in (0, 1):
        bad.append("body_material must be metadata code PP-R or PA-R")
    if int(p["insert_material"]) not in (0, 1):
        bad.append("insert_material must be metadata code SA73 or E70")

    split_gap = p["split_gap"]
    if split_gap < 0.0 or split_gap >= p["height"]:
        bad.append("split gap must be nonnegative and smaller than assembled height")

    insert_wall = (p["insert_outer_d"] - p["pipe_od"]) / 2.0
    if insert_wall <= 0.0:
        bad.append("D must be smaller than D1 so the insert has positive radial wall")
    if p["radial_clearance"] < 0.0:
        bad.append("insert-to-body radial clearance must be nonnegative")
    if p["axial_clearance"] < 0.0:
        bad.append("insert-to-body axial end clearance must be nonnegative")
    if _different(p["width"] - p["insert_width"], 2.0 * p["axial_clearance"]):
        bad.append("insert width must leave the declared clearance at both axial ends")
    if p["rib_height"] <= 0.0 or p["rib_width"] <= 0.0:
        bad.append("the insert central retention band must have positive dimensions")
    if _different(p["seat_groove_depth"], p["rib_height"]):
        bad.append("the body groove must match the insert central-band height")
    if _different(p["seat_groove_width"], p["rib_width"]):
        bad.append("the body groove must match the insert central-band width")

    half_height = (p["height"] - split_gap) / 2.0
    if p["counterbore_depth"] <= 0.0 or p["counterbore_depth"] >= half_height:
        bad.append("counterbore must leave positive clamp-half thickness")
    if p["counterbore_d"] <= p["mount_hole_d"]:
        bad.append("counterbore must be wider than its through passage")

    end_land = (p["length"] - p["mount_spacing"]) / 2.0
    side_land = p["width"] / 2.0
    if end_land <= p["mount_hole_d"] / 2.0 or side_land <= p["mount_hole_d"] / 2.0:
        bad.append("mounting through holes must retain positive end and side walls")
    if end_land <= p["counterbore_d"] / 2.0 or side_land <= p["counterbore_d"] / 2.0:
        bad.append("counterbores must retain positive end and side walls")

    cavity_radius = p["insert_outer_d"] / 2.0 + p["seat_groove_depth"]
    if cavity_radius >= p["height"] / 2.0:
        bad.append("insert seating grooves must leave positive top and bottom walls")
    hole_centre_radius = p["mount_spacing"] / 2.0
    if hole_centre_radius <= cavity_radius + p["mount_hole_d"] / 2.0:
        bad.append("mounting through holes must clear the insert cavity")
    return bad
