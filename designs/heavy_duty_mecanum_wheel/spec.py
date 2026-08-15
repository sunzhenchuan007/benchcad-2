"""Discrete NEXUS NM catalog rows with STEP-measured assembly geometry."""

CATALOG_ROWS = [
    dict(
        model="NM127A",
        diameter=127.0,
        width=66.0,
        set_load=200,
        roller_d=28.0,
        roller_l=63.0,
        plate_t=12.0,
        plate_od=120.0,
        bore_d=17.0,
        hub_od=50.0,
        pin_d=5.0,
        clearance=0.40,
    ),
    dict(
        model="NM152A",
        diameter=152.4,
        width=80.0,
        set_load=300,
        roller_d=33.0,
        roller_l=77.0,
        plate_t=14.0,
        plate_od=144.0,
        bore_d=30.0,
        hub_od=68.0,
        pin_d=6.0,
        clearance=0.50,
    ),
    dict(
        model="NM203A",
        diameter=203.0,
        width=105.0,
        set_load=600,
        roller_d=43.0,
        roller_l=105.0,
        plate_t=17.0,
        plate_od=192.0,
        bore_d=30.0,
        hub_od=68.0,
        pin_d=8.0,
        clearance=0.60,
    ),
    # NM254AL is the official left-hand STEP measurement reference.  The same
    # dimensions are mirrored for the catalog's right-hand variant.
    dict(
        model="NM254A",
        diameter=254.0,
        width=128.0,
        set_load=1500,
        roller_d=56.0,
        roller_l=130.0,
        plate_t=20.0,
        plate_od=240.0,
        bore_d=35.0,
        hub_od=98.0,
        pin_d=10.0,
        clearance=0.80,
    ),
    dict(
        model="NM305A",
        diameter=304.8,
        width=156.0,
        set_load=3000,
        roller_d=68.5,
        roller_l=160.0,
        plate_t=25.0,
        plate_od=288.0,
        bore_d=45.0,
        hub_od=120.0,
        pin_d=12.0,
        clearance=1.00,
    ),
]

DIFFICULTY_INDICES = {
    "easy": [1, 2],
    "medium": [0, 1, 2, 3],
    "hard": [0, 1, 2, 3, 4],
}
HAND_CHOICES = {"easy": [0], "medium": [0, 1], "hard": [0, 1]}

CATALOG_SOURCE = (
    "NEXUS Robot NM127A/NM152A/NM203A/NM254A/NM305A official dimensioned "
    "PDFs and BenchCAD public issue #65 dimension table"
)
STEP_SOURCE = (
    "Measurements from official NEXUS NM127A/NM152A/NM203A/NM254AL/NM305A "
    "STEP files; evidence only and never imported by build()"
)
PROPORTION_SOURCE = "proportion: deterministic running allowance documented in NOTES.md"


def _row_range(key, difficulty):
    values = [CATALOG_ROWS[index][key] for index in DIFFICULTY_INDICES[difficulty]]
    return min(values), max(values)


def _ranges(key):
    return {difficulty: _row_range(key, difficulty) for difficulty in ("easy", "medium", "hard")}


PARAM_SPEC = {
    "catalog_index": dict(
        desc="Complete NEXUS catalog row, NM127A through NM305A",
        unit="row",
        range={"easy": (1, 2), "medium": (0, 3), "hard": (0, 4)},
        choices=DIFFICULTY_INDICES,
        coverage=[0, 1, 2, 3, 4],
        integer=True,
        source=CATALOG_SOURCE,
    ),
    "handedness": dict(
        desc="Mecanum hand: 0=left (NM254AL reference), 1=right mirror",
        unit="enum",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        choices=HAND_CHOICES,
        coverage=[0, 1],
        integer=True,
        feature=True,
        source="Official NM254AL left-hand STEP; right hand is axial mirror",
    ),
    "wheel_d": dict(
        desc="Published whole-wheel outside diameter",
        unit="mm",
        range=_ranges("diameter"),
        refine=True,
        source=CATALOG_SOURCE,
    ),
    "overall_width": dict(
        desc="Published side-plate outer-face width",
        unit="mm",
        range=_ranges("width"),
        refine=True,
        source=CATALOG_SOURCE,
    ),
    "published_set_load_kg": dict(
        desc="Published complete four-wheel-set load; not per-wheel rating",
        unit="kg/set",
        range=_ranges("set_load"),
        refine=True,
        integer=True,
        source=CATALOG_SOURCE,
    ),
    "roller_count": dict(
        desc="Eight equally indexed external rollers",
        unit="count",
        range={d: (8, 8) for d in DIFFICULTY_INDICES},
        refine=True,
        integer=True,
        source="Official NM drawings and STEP: 8",
    ),
    "roller_skew_deg": dict(
        desc="Absolute roller-axis skew from rim tangent",
        unit="deg",
        range={d: (45.0, 45.0) for d in DIFFICULTY_INDICES},
        refine=True,
        source="Official NM 45-degree mecanum arrangement",
    ),
    "roller_d": dict(
        desc="STEP-measured maximum barrel-roller diameter",
        unit="mm",
        range=_ranges("roller_d"),
        refine=True,
        source=STEP_SOURCE,
    ),
    "roller_length": dict(
        desc="STEP-measured roller length along local axis",
        unit="mm",
        range=_ranges("roller_l"),
        refine=True,
        source=STEP_SOURCE,
    ),
    "plate_thickness": dict(
        desc="STEP-measured side-plate thickness",
        unit="mm",
        range=_ranges("plate_t"),
        refine=True,
        source=STEP_SOURCE,
    ),
    "plate_outer_d": dict(
        desc="STEP-measured closed side-plate outside diameter",
        unit="mm",
        range=_ranges("plate_od"),
        refine=True,
        source=STEP_SOURCE,
    ),
    "hub_bore_d": dict(
        desc="STEP-measured keyed shaft-bore diameter",
        unit="mm",
        range=_ranges("bore_d"),
        refine=True,
        source=STEP_SOURCE,
    ),
    "hub_outer_d": dict(
        desc="STEP-measured central hub-body outside diameter",
        unit="mm",
        range=_ranges("hub_od"),
        refine=True,
        source=STEP_SOURCE,
    ),
    "pin_d": dict(
        desc="Measured/inferred visible roller-pin diameter",
        unit="mm",
        range=_ranges("pin_d"),
        refine=True,
        source=STEP_SOURCE,
    ),
    "running_clearance": dict(
        desc="Positive roller/pin/plate running allowance",
        unit="mm",
        range=_ranges("clearance"),
        refine=True,
        source=PROPORTION_SOURCE,
    ),
}


ROW_KEYS = {
    "wheel_d": "diameter",
    "overall_width": "width",
    "published_set_load_kg": "set_load",
    "roller_d": "roller_d",
    "roller_length": "roller_l",
    "plate_thickness": "plate_t",
    "plate_outer_d": "plate_od",
    "hub_bore_d": "bore_d",
    "hub_outer_d": "hub_od",
    "pin_d": "pin_d",
    "running_clearance": "clearance",
}


def refine(p, difficulty, rng):
    del difficulty, rng
    row = CATALOG_ROWS[int(p["catalog_index"])]
    for parameter, key in ROW_KEYS.items():
        p[parameter] = row[key]
    p["roller_count"] = 8
    p["roller_skew_deg"] = 45.0


def check(p):
    bad = []
    index = int(p["catalog_index"])
    if index < 0 or index >= len(CATALOG_ROWS):
        return ["catalog_index must select one of the five official NM rows"]
    row = CATALOG_ROWS[index]
    for parameter, key in ROW_KEYS.items():
        if p[parameter] != row[key]:
            bad.append(f"{parameter} must remain coupled to its NEXUS row")
    if p["roller_count"] != 8:
        bad.append("NEXUS NM topology requires exactly eight rollers")
    if p["roller_skew_deg"] != 45.0:
        bad.append("NEXUS NM roller axes require an absolute 45-degree skew")
    if int(p["handedness"]) not in (0, 1):
        bad.append("handedness must select left or its right-hand mirror")
    if p["overall_width"] <= 2.0 * p["plate_thickness"]:
        bad.append("side plates must leave a positive inter-plate roller space")
    if p["hub_bore_d"] >= p["hub_outer_d"]:
        bad.append("shaft bore must leave positive hub wall")
    if p["plate_outer_d"] >= p["wheel_d"]:
        bad.append("rollers must remain exposed outside the side-plate diameter")
    if p["pin_d"] + 2.0 * p["running_clearance"] >= p["roller_d"]:
        bad.append("roller bore must leave positive barrel wall")
    return bad
