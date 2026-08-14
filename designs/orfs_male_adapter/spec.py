"""Parker F5OLO ORFS / SAE-ORB straight-thread connector specification.

Parker Catalog 4300 page A14 supplies 39 complete ordering rows. Each row
locks the ORFS end size, SAE-ORB stud thread T5, hex H, and overall length L5.
The current A14 table supersedes the older B21 snapshot quoted in issue #201:
for example, 8-6 F5OLO is L5=1.48 in here rather than 1.47 in the snapshot.

The catalog does not publish the two O-ring groove profiles or bore diameters
on A14. Those dimensions, and the allocation of L5 among threads, necks, and
hex, are therefore explicitly sourced as ``proportion``. They create visible
sealing features and a viable passage without claiming an SAE groove table.

Source: Parker Hannifin, Catalog 4300, Seal-Lok O-Ring Face Seal Tube Fittings,
page A14, F5OLO Straight Thread Connector, SAE 520120 (ORFS / SAE-ORB):
https://www.hydradynellc.com/images/document/Seal-Lok_O-Ring_Face_Seal_Tube_Fittings_FLO.pdf
"""

_IN = 25.4

# Nominal tube OD -> male ORFS Unified thread (inches, TPI). Sizes 14 and 32
# are Parker extensions marked outside SAE J1453 on the catalog page.
_ORFS_ENDS = {
    4: (0.25, 9 / 16, 18),
    6: (0.375, 11 / 16, 16),
    8: (0.50, 13 / 16, 16),
    10: (0.625, 1.0, 14),
    12: (0.75, 1 + 3 / 16, 12),
    14: (0.875, 1 + 5 / 16, 12),
    16: (1.0, 1 + 7 / 16, 12),
    20: (1.25, 1 + 11 / 16, 12),
    24: (1.50, 2.0, 12),
    32: (2.0, 2.50, 12),
}

# SAE-ORB dash -> nominal tube OD and UN/UNF-2A stud thread (inches, TPI).
_ORB_ENDS = {
    4: (0.25, 7 / 16, 20),
    5: (5 / 16, 0.50, 20),
    6: (0.375, 9 / 16, 18),
    8: (0.50, 0.75, 16),
    10: (0.625, 0.875, 14),
    12: (0.75, 1 + 1 / 16, 12),
    14: (0.875, 1 + 3 / 16, 12),
    16: (1.0, 1 + 5 / 16, 12),
    20: (1.25, 1 + 5 / 8, 12),
    24: (1.50, 1 + 7 / 8, 12),
    32: (2.0, 2.50, 12),
}

# Parker Catalog 4300 A14 F5OLO rows:
# (part code, ORFS dash, ORB dash, H across flats in, L5 overall in).
# The rendered page was visually checked, notably 12-6 = 9/16-18 and
# 24-20 = 1 5/8-12. Parker marks sizes 14 and 32 as outside SAE J1453.
_CATALOG = [
    ("4 F5OLO", 4, 4, 5 / 8, 1.13),
    ("4-5 F5OLO", 4, 5, 5 / 8, 1.16),
    ("4-6 F5OLO", 4, 6, 3 / 4, 1.20),
    ("4-8 F5OLO", 4, 8, 7 / 8, 1.32),
    ("6 F5OLO", 6, 6, 3 / 4, 1.26),
    ("6-4 F5OLO", 6, 4, 3 / 4, 1.34),
    ("6-5 F5OLO", 6, 5, 3 / 4, 1.22),
    ("6-8 F5OLO", 6, 8, 7 / 8, 1.38),
    ("6-10 F5OLO", 6, 10, 1.0, 1.52),
    ("6-12 F5OLO", 6, 12, 1 + 1 / 4, 1.67),
    ("8 F5OLO", 8, 8, 7 / 8, 1.44),
    ("8-4 F5OLO", 8, 4, 7 / 8, 1.44),
    ("8-6 F5OLO", 8, 6, 7 / 8, 1.48),
    ("8-10 F5OLO", 8, 10, 1.0, 1.59),
    ("8-12 F5OLO", 8, 12, 1 + 1 / 4, 1.75),
    ("8-16 F5OLO", 8, 16, 1 + 1 / 2, 1.79),
    ("10 F5OLO", 10, 10, 1 + 1 / 16, 1.69),
    ("10-6 F5OLO", 10, 6, 1 + 1 / 16, 1.63),
    ("10-8 F5OLO", 10, 8, 1 + 1 / 16, 1.77),
    ("10-12 F5OLO", 10, 12, 1 + 1 / 4, 1.85),
    ("10-16 F5OLO", 10, 16, 1 + 1 / 2, 1.89),
    ("12 F5OLO", 12, 12, 1 + 1 / 4, 1.91),
    ("12-6 F5OLO", 12, 6, 1 + 1 / 4, 1.77),
    ("12-8 F5OLO", 12, 8, 1 + 1 / 4, 1.91),
    ("12-10 F5OLO", 12, 10, 1 + 1 / 4, 1.99),
    ("12-16 F5OLO", 12, 16, 1 + 1 / 2, 1.95),
    ("14 F5OLO", 14, 14, 1 + 3 / 8, 1.91),
    ("16 F5OLO", 16, 16, 1 + 1 / 2, 1.97),
    ("16-8 F5OLO", 16, 8, 1 + 1 / 2, 1.96),
    ("16-10 F5OLO", 16, 10, 1 + 1 / 2, 2.05),
    ("16-12 F5OLO", 16, 12, 1 + 1 / 2, 2.15),
    ("16-20 F5OLO", 16, 20, 1 + 7 / 8, 2.07),
    ("16-24 F5OLO", 16, 24, 2 + 1 / 8, 2.13),
    ("20 F5OLO", 20, 20, 1 + 7 / 8, 2.07),
    ("20-16 F5OLO", 20, 16, 1 + 7 / 8, 2.28),
    ("20-24 F5OLO", 20, 24, 2 + 1 / 8, 2.13),
    ("24 F5OLO", 24, 24, 2 + 1 / 8, 2.13),
    ("24-20 F5OLO", 24, 20, 2 + 1 / 8, 2.34),
    ("32 F5OLO", 32, 32, 2 + 3 / 4, 2.32),
]

_DIFF_ROWS = {
    "easy": list(range(0, 13)),
    "medium": list(range(13, 26)),
    "hard": list(range(26, 39)),
}

_PARAM_KEYS = (
    "orfs_thread_d",
    "orfs_tpi",
    "orb_thread_d",
    "orb_tpi",
    "hex_af",
    "hex_len",
    "orfs_thread_len",
    "orfs_neck_len",
    "orb_thread_len",
    "orb_neck_len",
    "orfs_bore_d",
    "orb_bore_d",
    "orfs_groove_inner_d",
    "orfs_groove_outer_d",
    "orfs_groove_depth",
    "orb_groove_root_d",
    "orb_groove_width",
    "orb_groove_from_tip",
)


def _params_for_row(row_index):
    """Convert one Parker ordering row to catalog and proportion parameters."""
    _, orfs_dash, orb_dash, hex_in, overall_in = _CATALOG[row_index]
    orfs_tube_in, orfs_major_in, orfs_tpi = _ORFS_ENDS[orfs_dash]
    orb_tube_in, orb_major_in, orb_tpi = _ORB_ENDS[orb_dash]

    orfs_major = orfs_major_in * _IN
    orb_major = orb_major_in * _IN
    hex_af = hex_in * _IN
    overall = overall_in * _IN
    orfs_pitch = _IN / orfs_tpi
    orb_pitch = _IN / orb_tpi

    # Visualization proportions constrained to sum exactly to catalog L5.
    hex_len = 0.36 * hex_af
    orfs_neck_len = max(0.50 * orfs_pitch, 0.05 * orfs_major)
    # The ORB neck carries the radial O-ring groove, so it must be longer than
    # the groove width rather than only a token thread relief.
    orb_neck_len = max(1.80 * orb_pitch, 0.13 * orb_major)
    thread_total = overall - hex_len - orfs_neck_len - orb_neck_len
    orfs_thread_len = 0.52 * thread_total
    orb_thread_len = thread_total - orfs_thread_len

    # A14 omits D/D2 and manufacturing grooves, so these remain proportions.
    orfs_bore_d = 0.70 * orfs_tube_in * _IN
    orb_bore_d = 0.70 * orb_tube_in * _IN
    face_width = max(1.2, 0.12 * orfs_major)
    orfs_groove_inner_d = max(orfs_bore_d + 1.0, 0.52 * orfs_major)
    orfs_groove_outer_d = min(orfs_major - 1.2, orfs_groove_inner_d + 2.0 * face_width)
    orfs_groove_depth = 0.32 * (orfs_groove_outer_d - orfs_groove_inner_d)
    orb_groove_width = min(max(1.2, 0.10 * orb_major), 0.70 * orb_neck_len)
    orb_groove_root_d = max(orb_bore_d + 2.0, 0.78 * orb_major)
    orb_groove_from_tip = orb_thread_len + 0.50 * orb_neck_len

    values = (
        orfs_major,
        orfs_tpi,
        orb_major,
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
    )
    return {key: round(float(value), 4) for key, value in zip(_PARAM_KEYS, values)}


_ROW_PARAMS = [_params_for_row(i) for i in range(len(_CATALOG))]


def _tier_ranges(key):
    """Exact min/max contract for one row-locked parameter in each tier."""
    return {
        difficulty: (
            min(_ROW_PARAMS[i][key] for i in rows),
            max(_ROW_PARAMS[i][key] for i in rows),
        )
        for difficulty, rows in _DIFF_ROWS.items()
    }


_CATALOG_SOURCE = "Parker Catalog 4300 p.A14 F5OLO table (row-locked; SAE 520120)"
_ORFS_SOURCE = "ISO 8434-3 / SAE J1453 ORFS thread series (row-locked)"
_ORB_SOURCE = "SAE J1926-1 UN/UNF-2A ORB stud thread (Parker A14 T5 row)"
_PROP_SOURCE = "proportion"


def _entry(desc, unit, key, source, *, integer=False):
    entry = dict(desc=desc, unit=unit, range=_tier_ranges(key), source=source)
    entry["refine"] = True
    if integer:
        entry["integer"] = True
    return entry


PARAM_SPEC = {
    "catalog_row": dict(
        desc="Parker A14 F5OLO ordering-row index (1-39; locks all dimensions)",
        unit="",
        range={"easy": (1, 13), "medium": (14, 26), "hard": (27, 39)},
        source=_CATALOG_SOURCE,
        integer=True,
        refine=True,
        coverage=list(range(1, 40)),
    ),
    "orfs_thread_d": _entry(
        "male ORFS nominal major diameter T", "mm", "orfs_thread_d", _ORFS_SOURCE
    ),
    "orfs_tpi": _entry(
        "male ORFS Unified thread pitch",
        "TPI",
        "orfs_tpi",
        _ORFS_SOURCE,
        integer=True,
    ),
    "orb_thread_d": _entry(
        "male SAE-ORB stud nominal major diameter T5",
        "mm",
        "orb_thread_d",
        _ORB_SOURCE,
    ),
    "orb_tpi": _entry(
        "male SAE-ORB stud Unified thread pitch T5",
        "TPI",
        "orb_tpi",
        _ORB_SOURCE,
        integer=True,
    ),
    "hex_af": _entry("center wrench hex width across flats H", "mm", "hex_af", _CATALOG_SOURCE),
    "hex_len": _entry(
        "axial center-hex length allocated within catalog L5",
        "mm",
        "hex_len",
        _PROP_SOURCE,
    ),
    "orfs_thread_len": _entry(
        "visible ORFS external-thread length allocated within catalog L5",
        "mm",
        "orfs_thread_len",
        _PROP_SOURCE,
    ),
    "orfs_neck_len": _entry(
        "ORFS relief-neck length between thread and hex",
        "mm",
        "orfs_neck_len",
        _PROP_SOURCE,
    ),
    "orb_thread_len": _entry(
        "visible SAE-ORB external-thread length allocated within catalog L5",
        "mm",
        "orb_thread_len",
        _PROP_SOURCE,
    ),
    "orb_neck_len": _entry(
        "SAE-ORB seal-neck length between thread and hex",
        "mm",
        "orb_neck_len",
        _PROP_SOURCE,
    ),
    "orfs_bore_d": _entry("ORFS-side flow-bore diameter", "mm", "orfs_bore_d", _PROP_SOURCE),
    "orb_bore_d": _entry("SAE-ORB-side flow-bore diameter", "mm", "orb_bore_d", _PROP_SOURCE),
    "orfs_groove_inner_d": _entry(
        "ORFS face-seal groove inner diameter",
        "mm",
        "orfs_groove_inner_d",
        _PROP_SOURCE,
    ),
    "orfs_groove_outer_d": _entry(
        "ORFS face-seal groove outer diameter",
        "mm",
        "orfs_groove_outer_d",
        _PROP_SOURCE,
    ),
    "orfs_groove_depth": _entry(
        "ORFS face-seal groove depth", "mm", "orfs_groove_depth", _PROP_SOURCE
    ),
    "orb_groove_root_d": _entry(
        "SAE-ORB circumferential O-ring groove root diameter",
        "mm",
        "orb_groove_root_d",
        _PROP_SOURCE,
    ),
    "orb_groove_width": _entry(
        "SAE-ORB circumferential O-ring groove axial width",
        "mm",
        "orb_groove_width",
        _PROP_SOURCE,
    ),
    "orb_groove_from_tip": _entry(
        "SAE-ORB groove center distance from stud tip",
        "mm",
        "orb_groove_from_tip",
        _PROP_SOURCE,
    ),
}


def check(p: dict) -> list[str]:
    """Verify exact catalog-row coupling and physically viable proportions."""
    bad = []
    row_number = int(round(p["catalog_row"]))
    if row_number < 1 or row_number > len(_CATALOG):
        return ["catalog_row is outside Parker A14 rows 1-39"]

    expected = _ROW_PARAMS[row_number - 1]
    for key in _PARAM_KEYS:
        if abs(float(p[key]) - expected[key]) > 1e-4:
            bad.append(
                f"{key}={p[key]} does not match Parker row {row_number} "
                f"({_CATALOG[row_number - 1][0]}: {expected[key]})"
            )

    overall = (
        p["orb_thread_len"]
        + p["orb_neck_len"]
        + p["hex_len"]
        + p["orfs_neck_len"]
        + p["orfs_thread_len"]
    )
    catalog_l5 = _CATALOG[row_number - 1][4] * _IN
    if abs(overall - catalog_l5) > 0.02:
        bad.append("axial thread/neck/hex allocation does not sum to catalog L5")
    if p["orfs_thread_len"] <= _IN / p["orfs_tpi"]:
        bad.append("ORFS thread length is not greater than one pitch")
    if p["orb_thread_len"] <= _IN / p["orb_tpi"]:
        bad.append("SAE-ORB thread length is not greater than one pitch")
    if not (
        p["orfs_bore_d"] < p["orfs_groove_inner_d"] < p["orfs_groove_outer_d"] < p["orfs_thread_d"]
    ):
        bad.append("ORFS face groove must lie between bore and thread envelope")
    if not p["orb_bore_d"] + 1.0 < p["orb_groove_root_d"] < p["orb_thread_d"]:
        bad.append("SAE-ORB groove root must leave wall inside thread envelope")
    if p["orb_groove_width"] > 0.70 * p["orb_neck_len"] + 1e-4:
        bad.append("SAE-ORB groove does not fit inside its seal neck")
    return bad


def refine(p: dict, difficulty: str, rng) -> None:
    """Select one complete Parker row; no catalog dimensions are mixed."""
    rows = _DIFF_ROWS[difficulty]
    # A uniform row draw which also reaches all 13 rows in validate's 40 seeds.
    row_index = rows[int(rng.permutation(len(rows))[0])]
    p["catalog_row"] = row_index + 1
    p.update(_ROW_PARAMS[row_index])
