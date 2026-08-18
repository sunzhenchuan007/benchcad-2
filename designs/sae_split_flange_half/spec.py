"""Catalog-row generator for the Code 61 split-flange clamp half.

Primary dimensions are Anfield Industries, ``Flange Catalog / Split Flanges``,
Rev. C p. 1, "Code 61 Split Flange". For 1/2-4 in, bolt spacing C uses Anchor
Fluid Power catalog p. 84 three-decimal values where Anfield prints only two
decimals; the 5 in value is Anfield's 6.00 in because Anchor stops at 4 in.
The row tuple is jointly sampled: no controlled dimension is independently
invented.
"""


_MM_PER_IN = 25.4
_COLUMNS = (
    "counterbore_d",  # A
    "bore_d",  # B
    "bolt_spacing",  # C (Anchor three-decimal value)
    "overall_length",  # D
    "split_to_bolt",  # E
    "half_width",  # F (manufacturer-specific outline)
    "overall_thickness",  # G
    "plate_thickness",  # H
    "lip_depth",  # I
    "bolt_hole_d",  # K
)

# SAE J518-1 / ISO 6162-1 Code 61 split-flange rows, inches.
# (nominal size, A, B, C, D, E, F, G, H, I, K)
# A/B/D/E/F/G/H/I/K: Anfield Rev. C p. 1.
# C: Anchor p. 84 exact bolt spacing through 4 in; Anfield for the 5 in row.
_ROWS_IN = [
    (0.50, 1.22, 0.96, 1.500, 2.13, 0.34, 0.91, 0.75, 0.51, 0.24, 0.33),
    (0.75, 1.53, 1.26, 1.875, 2.56, 0.44, 1.02, 0.87, 0.56, 0.24, 0.41),
    (1.00, 1.78, 1.53, 2.062, 2.76, 0.52, 1.16, 0.94, 0.63, 0.30, 0.41),
    (1.25, 2.04, 1.72, 2.312, 3.11, 0.59, 1.44, 0.87, 0.55, 0.30, 0.47),
    (1.50, 2.41, 2.00, 2.750, 3.66, 0.70, 1.63, 0.98, 0.63, 0.30, 0.53),
    (2.00, 2.84, 2.47, 3.062, 4.02, 0.84, 1.91, 1.02, 0.63, 0.35, 0.53),
    (2.50, 3.34, 2.95, 3.500, 4.49, 1.00, 2.13, 1.50, 0.75, 0.35, 0.53),
    (3.00, 4.03, 3.58, 4.188, 5.28, 1.22, 2.58, 1.61, 0.87, 0.35, 0.67),
    (3.50, 4.53, 4.03, 4.750, 5.98, 1.38, 2.76, 1.10, 0.87, 0.42, 0.67),
    (4.00, 5.03, 4.53, 5.125, 6.38, 1.53, 2.99, 1.38, 0.98, 0.42, 0.67),
    (5.00, 6.43, 5.53, 6.000, 7.24, 1.81, 3.56, 1.61, 1.10, 0.42, 0.67),
]

_TIER_ROWS = {
    "easy": _ROWS_IN[:3],
    "medium": _ROWS_IN[:6],
    "hard": _ROWS_IN,
}


def _mm(value):
    return round(value * _MM_PER_IN, 4)


def _ranges(column):
    index = _COLUMNS.index(column) + 1
    return {
        difficulty: (
            _mm(min(row[index] for row in rows)),
            _mm(max(row[index] for row in rows)),
        )
        for difficulty, rows in _TIER_ROWS.items()
    }


_ANFIELD = "Anfield Flange Catalog / Split Flanges Rev. C p. 1, Code 61 table"
_ANCHOR = (
    "Anchor Fluid Power Flange Catalog p. 84, Code 61 C through 4 in; "
    "Anfield Rev. C p. 1 for 5 in"
)


PARAM_SPEC = {
    "counterbore_d": dict(
        desc="counterbore diameter A for the flange head",
        unit="mm",
        range=_ranges("counterbore_d"),
        source=_ANFIELD,
        refine=True,
    ),
    "bore_d": dict(
        desc="through-bore diameter B behind the retaining shoulder",
        unit="mm",
        range=_ranges("bore_d"),
        source=_ANFIELD,
        refine=True,
    ),
    "bolt_spacing": dict(
        desc="centre distance C between the two bolt holes in one half",
        unit="mm",
        range=_ranges("bolt_spacing"),
        source=_ANCHOR,
        refine=True,
        coverage=[_mm(row[3]) for row in _ROWS_IN],
    ),
    "overall_length": dict(
        desc="overall end-to-end length D",
        unit="mm",
        range=_ranges("overall_length"),
        source=_ANFIELD,
        refine=True,
    ),
    "split_to_bolt": dict(
        desc="distance E from pattern centreline to each bolt centre",
        unit="mm",
        range=_ranges("split_to_bolt"),
        source=_ANFIELD,
        refine=True,
    ),
    "half_width": dict(
        desc="manufacturer-specific half width F from pattern centreline",
        unit="mm",
        range=_ranges("half_width"),
        source=_ANFIELD,
        refine=True,
    ),
    "overall_thickness": dict(
        desc="maximum forged-crown thickness G",
        unit="mm",
        range=_ranges("overall_thickness"),
        source=_ANFIELD,
        refine=True,
    ),
    "plate_thickness": dict(
        desc="bolt-ear plate thickness H",
        unit="mm",
        range=_ranges("plate_thickness"),
        source=_ANFIELD,
        refine=True,
    ),
    "lip_depth": dict(
        desc="axial counterbore/lip depth I",
        unit="mm",
        range=_ranges("lip_depth"),
        source=_ANFIELD,
        refine=True,
    ),
    "bolt_hole_d": dict(
        desc="bolt clearance-hole diameter K",
        unit="mm",
        range=_ranges("bolt_hole_d"),
        source=_ANFIELD,
        refine=True,
    ),
    "split_setback": dict(
        desc="split face setback from the bolt-pattern centreline",
        unit="mm",
        range={
            "easy": (_mm(0.039), _mm(0.060)),
            "medium": (_mm(0.039), _mm(0.060)),
            "hard": (_mm(0.039), _mm(0.060)),
        },
        source="Anfield Flange Catalog Rev. C p. 1 drawing note: 0.039-0.060 in",
    ),
}


def _is_catalog_row(p):
    for row in _ROWS_IN:
        if all(
            abs(p[column] - _mm(row[index + 1])) < 1e-6
            for index, column in enumerate(_COLUMNS)
        ):
            return True
    return False


def check(p: dict) -> list[str]:
    bad = []
    if not _is_catalog_row(p):
        bad.append("A-K dimensions are not one joint Code 61 catalog row")
    if not _mm(0.039) <= p["split_setback"] <= _mm(0.060):
        bad.append("split setback outside Anfield drawing note 0.039-0.060 in")
    if p["counterbore_d"] <= p["bore_d"]:
        bad.append("A <= B: stepped bore would have no retaining shoulder")
    if p["overall_thickness"] <= p["plate_thickness"]:
        bad.append("G <= H: forged crown must stand proud of the bolt-ear plate")
    if p["lip_depth"] >= p["plate_thickness"]:
        bad.append("I >= H: counterbore would consume the retaining plate")
    if p["half_width"] <= p["counterbore_d"] / 2.0 + p["split_setback"]:
        bad.append("F <= A/2 + setback: no outer bridge ligament")

    ear_r = (p["overall_length"] - p["bolt_spacing"]) / 2.0
    if ear_r <= p["bolt_hole_d"] / 2.0:
        bad.append("(D-C)/2 <= K/2: no material around bolt hole at an end")
    if p["split_to_bolt"] - p["split_setback"] <= p["bolt_hole_d"] / 2.0:
        bad.append("E-setback <= K/2: split face would break into bolt hole")
    if p["half_width"] - p["split_to_bolt"] <= p["bolt_hole_d"] / 2.0:
        bad.append("F-E <= K/2: bolt hole would break through outer edge")
    return bad


def refine(p: dict, difficulty: str, rng) -> None:
    """Choose one complete catalog row; only the documented setback varies."""
    rows = _TIER_ROWS[difficulty]
    row = rows[int(rng.integers(len(rows)))]
    for index, column in enumerate(_COLUMNS):
        p[column] = _mm(row[index + 1])
