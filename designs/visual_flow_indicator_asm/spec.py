"""Complete catalog-row sampling for ELESA HVF visual flow indicators."""

from bench2 import Resample


CATALOG_SOURCE = "ELESA HVF datasheet, 10/2025, pp.1-2"
BSPP_SOURCE = "ISO 228-1 pipe threads where pressure-tight joints are not made on threads"
NPT_SOURCE = "ASME B1.20.1 NPT nominal thread table"
PROPORTION_SOURCE = (
    "proportion; unmarked glass wall, plate/boss split, rotor, axle, seals and "
    "tie-rod fastener dimensions reconstructed from official STEP SKU 111301 and product photo"
)

# code, material, thread form, size code, body style, rod count, major d, pitch,
# H, L, B, h1, s
CATALOG_ROWS = (
    ("111301", 0, 0, 0, 0, 2, 13.157, 1.337, 66.0, 44.0, 27.0, 22.0, 20.0),
    ("111311", 0, 0, 1, 0, 2, 16.662, 1.337, 92.0, 60.0, 40.0, 36.0, 28.0),
    ("111321", 0, 0, 2, 0, 2, 20.955, 1.814, 92.0, 60.0, 40.0, 36.0, 28.0),
    ("111302", 1, 0, 0, 0, 2, 13.157, 1.337, 66.0, 44.0, 27.0, 22.0, 20.0),
    ("111312", 1, 0, 1, 0, 2, 16.662, 1.337, 92.0, 60.0, 40.0, 36.0, 28.0),
    ("111322", 1, 0, 2, 0, 2, 20.955, 1.814, 92.0, 60.0, 40.0, 36.0, 28.0),
    ("111304", 0, 1, 0, 0, 2, 13.616, 1.411, 66.0, 44.0, 27.0, 22.0, 20.0),
    ("111317", 0, 1, 1, 0, 2, 17.055, 1.411, 92.0, 60.0, 40.0, 36.0, 28.0),
    ("111324", 0, 1, 2, 0, 2, 21.223, 1.814, 92.0, 60.0, 40.0, 36.0, 28.0),
    ("111331", 0, 0, 3, 1, 4, 26.441, 1.814, 114.0, 70.0, 70.0, 46.0, 46.0),
    ("111341", 0, 0, 4, 1, 4, 33.249, 2.309, 114.0, 70.0, 70.0, 46.0, 46.0),
    ("111332", 1, 0, 3, 1, 4, 26.441, 1.814, 114.0, 70.0, 70.0, 46.0, 46.0),
    ("111342", 1, 0, 4, 1, 4, 33.249, 2.309, 114.0, 70.0, 70.0, 46.0, 46.0),
    ("111333", 0, 1, 3, 1, 4, 26.568, 1.814, 114.0, 70.0, 70.0, 46.0, 46.0),
    ("111346", 0, 1, 4, 1, 4, 33.228, 2.209, 114.0, 70.0, 70.0, 46.0, 46.0),
)

ROW_FIELDS = (
    "catalog_code",
    "material_code",
    "thread_form",
    "thread_size_code",
    "body_style",
    "rod_count",
    "thread_major_d",
    "thread_pitch",
    "overall_h",
    "plan_l",
    "plan_b",
    "window_h1",
    "rod_spacing_s",
)

DIFFICULTY_ROWS = {
    "easy": [0, 3, 6],
    "medium": list(range(9)),
    "hard": list(range(15)),
}


def _range_for(column):
    index = ROW_FIELDS.index(column)
    return {
        difficulty: (
            min(CATALOG_ROWS[i][index] for i in rows),
            max(CATALOG_ROWS[i][index] for i in rows),
        )
        for difficulty, rows in DIFFICULTY_ROWS.items()
    }


PARAM_SPEC = {
    "catalog_row": dict(
        desc="zero-based selector for one complete HVF catalog row",
        unit="",
        range={difficulty: (min(rows), max(rows)) for difficulty, rows in DIFFICULTY_ROWS.items()},
        choices=DIFFICULTY_ROWS,
        integer=True,
        coverage=list(range(15)),
        source=f"{CATALOG_SOURCE}; all 15 printed BSPP/SST/NPT rows",
    ),
    "rotor_angle": dict(
        desc="rotor angular pose about the coaxial flow passage",
        unit="deg",
        range={"easy": (0.0, 20.0), "medium": (30.0, 60.0), "hard": (70.0, 110.0)},
        source=f"{PROPORTION_SOURCE}; free rotor pose",
        askable=True,
    ),
}

for _name, _desc, _unit, _source in (
    ("material_code", "boss material: 0=brass, 1=AISI 316", "", CATALOG_SOURCE),
    ("thread_form", "female pipe thread: 0=BSPP, 1=NPT", "", f"{CATALOG_SOURCE}; {BSPP_SOURCE}; {NPT_SOURCE}"),
    ("thread_size_code", "nominal size code 0=1/4 through 4=1 inch", "", CATALOG_SOURCE),
    ("body_style", "end-body layout: 0=two-rod lozenge, 1=four-rod square", "", CATALOG_SOURCE),
    ("rod_count", "number of tie rods, through screws, and retaining nuts", "", CATALOG_SOURCE),
    ("thread_major_d", "nominal pipe-thread major diameter", "mm", f"{BSPP_SOURCE}; {NPT_SOURCE}"),
    ("thread_pitch", "pipe-thread axial pitch", "mm", f"{BSPP_SOURCE}; {NPT_SOURCE}"),
    ("overall_h", "overall height H", "mm", CATALOG_SOURCE),
    ("plan_l", "end-body plan length L", "mm", CATALOG_SOURCE),
    ("plan_b", "end-body plan width B; large layout is square per p.2 drawing", "mm", CATALOG_SOURCE),
    ("window_h1", "clear tubular-window height h1", "mm", CATALOG_SOURCE),
    ("rod_spacing_s", "tie-rod spacing / chamber envelope s", "mm", CATALOG_SOURCE),
):
    PARAM_SPEC[_name] = dict(
        desc=_desc,
        unit=_unit,
        range=_range_for(_name),
        refine=True,
        integer=_name
        in {"material_code", "thread_form", "thread_size_code", "body_style", "rod_count"},
        source=_source,
    )


def _selected_row(p):
    value = p.get("catalog_row")
    if not isinstance(value, int) or isinstance(value, bool):
        return None
    if value < 0 or value >= len(CATALOG_ROWS):
        return None
    return CATALOG_ROWS[value]


def refine(p, difficulty, rng):
    del difficulty, rng
    row = _selected_row(p)
    if row is None:
        raise Resample
    for name, value in zip(ROW_FIELDS[1:], row[1:]):
        p[name] = value


def check(p):
    bad = []
    row = _selected_row(p)
    if row is None:
        return [f"catalog_row must select one complete row from {CATALOG_SOURCE}"]
    for name, expected in zip(ROW_FIELDS[1:], row[1:]):
        if p[name] != expected:
            bad.append(f"{name} must remain coupled to HVF row {row[0]} ({CATALOG_SOURCE})")

    if not 0.0 <= p["rotor_angle"] <= 110.0:
        bad.append(f"rotor pose must remain within the declared review range ({PROPORTION_SOURCE})")
    if p["overall_h"] <= p["window_h1"]:
        bad.append(f"H must leave positive end-stack height outside h1 ({CATALOG_SOURCE})")
    if p["rod_spacing_s"] <= p["thread_major_d"] + 3.0:
        bad.append(f"chamber envelope s must clear the threaded flow passage ({CATALOG_SOURCE}; {PROPORTION_SOURCE})")
    if p["body_style"] == 0 and p["plan_l"] <= 2.0 * p["rod_spacing_s"]:
        bad.append(f"two-rod end length L must retain positive outer lands around s ({CATALOG_SOURCE})")
    if p["body_style"] == 1 and p["plan_l"] != p["plan_b"]:
        bad.append(f"large four-rod end must remain square in plan ({CATALOG_SOURCE}, p.2 drawing)")
    expected_rods = 2 if p["body_style"] == 0 else 4
    if p["rod_count"] != expected_rods:
        bad.append(f"rod count must match the printed two- or four-rod end layout ({CATALOG_SOURCE})")
    if p["thread_form"] not in (0, 1):
        bad.append("thread_form must select BSPP or NPT")
    if p["material_code"] not in (0, 1):
        bad.append("material_code must select brass or AISI 316 boss rows")
    return bad
