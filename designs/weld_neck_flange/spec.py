"""weld_neck_flange — the benchmark generator spec.

Two coupling patterns, like the sprocket reference:

  * table-driven — (bore, flange_od, flange_t, bolt_circle_d, n_bolts,
    bolt_hole_d, hub_od, pipe_od, hub_len) is ONE jointly-sampled row of the
    ASME B16.5 class-150 weld-neck flange table (NPS 1"–24"), not free numbers.
    refine() draws the row (a real NPS size), with coverage over the bore column
    so every listed NPS — through the 12-bolt (NPS 12) and 20-bolt (NPS 20/24)
    rows — is exercised. The weld-neck hub taper (hub base X -> pipe OD A over
    length H) is row-locked from the table.
  * coupled proportion — only the raised-face seat diameter is sized off the
    drawn row (RF must clear the bolts), filled in refine() after the base draw.

Difficulty: easy = small NPS (1–3", raised face); medium = mid NPS (4–10", raised
face); hard = large NPS (12–24", raised face, 12–20 bolts).

Sources:
  * ASME B16.5 "Pipe Flanges and Flanged Fittings" — class-150 weld-neck flange
    dimensions (O, tf, bolt circle, bolt count/dia, bore, hub base Ø X, length
    through hub Y). Rows below are the class-150 NPS 1"–24" rows in mm.
  * pipe OD A at the weld end = the nominal pipe outside diameter for the NPS.
  * hub_len = Y (length through hub) - flange_t. The raised-face height
    (~1.6 mm, the 1/16-in class-150 RF) and the RF seat diameter are "proportion"
    — sized to clear the bolting, not a dimension column.
"""


# ASME B16.5 class-150 weld-neck flanges — one row = one NPS size, mm:
#   (NPS, bore, flange_od, flange_t, bolt_circle_d, n_bolts, bolt_hole_d,
#    hub_od [X = hub base Ø], pipe_od [A = pipe OD at weld end], hub_len [Y - tf])
_B16_5_CL150 = [
    ('1"',   26.7, 108.0, 14.3,  79.4,  4, 15.9,  49.3,  33.4,  41.3),
    ('2"',   52.5, 152.0, 19.1, 120.7,  4, 19.1,  77.7,  60.3,  44.4),
    ('3"',   77.9, 190.0, 23.9, 152.4,  4, 19.1, 108.0,  88.9,  46.0),
    ('4"',  102.3, 229.0, 23.9, 190.5,  8, 19.1, 134.6, 114.3,  52.3),
    ('6"',  154.1, 279.0, 25.4, 241.3,  8, 22.2, 191.8, 168.3,  63.5),
    ('8"',  202.7, 343.0, 28.6, 298.5,  8, 22.2, 246.1, 219.1,  73.0),
    ('10"', 254.5, 406.4, 30.2, 362.0, 12, 25.4, 305.0, 273.0,  69.8),
    ('12"', 304.8, 482.6, 31.8, 431.8, 12, 25.4, 365.0, 323.9,  81.2),
    ('16"', 387.4, 596.9, 36.6, 539.8, 16, 28.6, 457.0, 406.4,  88.4),
    ('20"', 488.9, 698.5, 42.9, 635.0, 20, 31.8, 559.0, 508.0, 100.1),
    ('24"', 590.5, 812.8, 47.8, 749.3, 20, 35.1, 663.0, 610.0, 103.2),
]

# per-difficulty NPS subset (indices): small / mid / large. Their union is all
# eleven rows, so the coverage gate over `bore` is satisfied.
_ROWS = {"easy": [0, 1, 2], "medium": [3, 4, 5, 6], "hard": [7, 8, 9, 10]}


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
_TABLE_SRC = "ASME B16.5 class-150 weld-neck flange table (discrete NPS rows; row-locked in refine)"

PARAM_SPEC = {
    "bore": dict(
        desc="pipe bore through the flange, hub and raised face (B16.5 row)",
        unit="mm",
        range={"easy": (26.7, 77.9), "medium": (102.3, 254.5), "hard": (304.8, 590.5)},
        source=_TABLE_SRC,
        refine=True,
        coverage=[26.7, 52.5, 77.9, 102.3, 154.1, 202.7, 254.5, 304.8, 387.4, 488.9, 590.5],
    ),
    "flange_od": dict(
        desc="flange disc outside diameter (same B16.5 row as bore)",
        unit="mm",
        range={"easy": (108.0, 190.0), "medium": (229.0, 406.4), "hard": (482.6, 812.8)},
        source=_TABLE_SRC,
        refine=True,
    ),
    "flange_t": dict(
        desc="flange disc thickness (same B16.5 row)",
        unit="mm",
        range={"easy": (14.3, 23.9), "medium": (23.9, 30.2), "hard": (31.8, 47.8)},
        source=_TABLE_SRC,
        refine=True,
    ),
    "bolt_circle_d": dict(
        desc="bolt-circle diameter (same B16.5 row)",
        unit="mm",
        range={"easy": (79.4, 152.4), "medium": (190.5, 362.0), "hard": (431.8, 749.3)},
        source=_TABLE_SRC,
        refine=True,
    ),
    "n_bolts": dict(
        desc="number of bolt holes (same B16.5 row; 4 -> 8 -> 12 -> 16 -> 20 with NPS)",
        unit="",
        range={"easy": (4, 4), "medium": (8, 12), "hard": (12, 20)},
        source=_TABLE_SRC,
        refine=True,
    ),
    "bolt_hole_d": dict(
        desc="bolt-hole diameter (same B16.5 row)",
        unit="mm",
        range={"easy": (15.9, 19.1), "medium": (19.1, 25.4), "hard": (25.4, 35.1)},
        source=_TABLE_SRC,
        refine=True,
    ),
    "hub_od": dict(
        desc="weld-neck hub base Ø X at the flange back (same B16.5 row)",
        unit="mm",
        range={"easy": (49.3, 108.0), "medium": (134.6, 305.0), "hard": (365.0, 663.0)},
        source=_TABLE_SRC,
        refine=True,
    ),
    "pipe_od": dict(
        desc="pipe OD A at the weld end (hub small end; nominal pipe OD for the NPS)",
        unit="mm",
        range={"easy": (33.4, 88.9), "medium": (114.3, 273.0), "hard": (323.9, 610.0)},
        source="nominal pipe outside diameter for the NPS (weld-end of the hub)",
        refine=True,
    ),
    "hub_len": dict(
        desc="weld-neck hub length off the flange back (Y length-through-hub minus flange_t)",
        unit="mm",
        range={"easy": (41.3, 46.0), "medium": (52.3, 73.0), "hard": (81.2, 103.2)},
        source=_TABLE_SRC,
        refine=True,
    ),
    # --- proportions coupled to the row (declared "proportion", not a table) ---
    "raised_face_d": dict(
        desc="raised-face (gasket seat) diameter; sized inboard of the bolts on every tier",
        unit="mm",
        range={"easy": (50.0, 135.0), "medium": (150.0, 340.0), "hard": (390.0, 715.0)},
        source="proportion (RF seat inboard of the bolt holes, larger than the bore)",
        refine=True,
    ),
    "rf_t": dict(
        desc="raised-face height (class-150 ~1.6 mm; present on every tier)",
        unit="mm",
        range={"easy": (1.6, 2.0), "medium": (1.6, 2.0), "hard": (1.6, 2.0)},
        source="proportion (class-150 raised face is nominally 1/16 in ~= 1.6 mm)",
        feature=True,  # toggles the raised-face feature -> drives add/remove edits
    ),
}


# ── 2. check — the engineering truth reviewers audit ─────────────────────────
def check(p: dict) -> list[str]:
    bad = []

    # the row values must be ONE real ASME B16.5 class-150 row, not free numbers
    row = (p["bore"], p["flange_od"], p["flange_t"], p["bolt_circle_d"],
           p["n_bolts"], p["bolt_hole_d"], p["hub_od"], p["pipe_od"], p["hub_len"])
    if not any(all(abs(a - b) < 1e-6 for a, b in zip(row, r[1:10])) for r in _B16_5_CL150):
        bad.append("(bore, flange_od, flange_t, bolt_circle_d, n_bolts, bolt_hole_d, "
                   "hub_od, pipe_od, hub_len) is not an ASME B16.5 class-150 row")

    # B16.5 flanges are drilled in an even, straddle-the-centerline pattern
    if p["n_bolts"] % 2 != 0:
        bad.append("n_bolts odd: B16.5 flanges are drilled in an even bolt pattern")

    # bolt holes must leave a rim of material out to the flange OD (not break the
    # disc edge): ligament from hole edge to OD >= 0.25 * hole (tear-out guideline)
    rim = p["flange_od"] / 2.0 - p["bolt_circle_d"] / 2.0 - p["bolt_hole_d"] / 2.0
    if rim < 0.25 * p["bolt_hole_d"]:
        bad.append("bolt hole < 0.25 d ligament to the flange OD: rim tear-out")

    # weld-neck hub: a taper from the hub base X (at the flange back) down to the
    # pipe OD at the weld end, leaving a real pipe wall, inside the disc + bolts
    if p["pipe_od"] >= p["hub_od"]:
        bad.append("pipe_od >= hub_od: the weld-neck hub does not taper down")
    if p["bore"] >= p["pipe_od"]:
        bad.append("bore >= pipe_od: no pipe wall at the weld end")
    if p["pipe_od"] - p["bore"] < 4.0:
        bad.append("pipe_od - bore < 4 mm: pipe wall too thin at the weld end")
    if p["hub_od"] >= p["flange_od"]:
        bad.append("hub_od >= flange_od: hub base wider than the flange disc")
    if p["hub_od"] >= p["bolt_circle_d"] - p["bolt_hole_d"]:
        bad.append("hub_od >= bolt_circle - bolt_hole: hub base runs into the bolt holes")

    # raised face (when present): an annular gasket seat, larger than the bore,
    # whose outer edge stays inboard of the bolt holes
    if p["rf_t"]:
        if p["raised_face_d"] <= p["bore"]:
            bad.append("raised_face_d <= bore: no annular gasket seat")
        if p["raised_face_d"] >= p["bolt_circle_d"] - p["bolt_hole_d"]:
            bad.append("raised_face_d >= bolt_circle - bolt_hole: RF seat runs into the bolts")
        if not (1.0 <= p["rf_t"] <= 3.0):
            bad.append("rf_t outside 1-3 mm: not a class-150 raised-face height")

    return bad


# ── 3. refine — the coupling, and only the coupling (no rejection loop) ───────
def refine(p: dict, difficulty: str, rng) -> None:
    """Fill the row-locked and proportional parameters after the framework has
    drawn the base ones (only rf_t is drawn there). The B16.5 row is ONE discrete
    choice; the hub taper (X / A / H) is row-locked; only the raised-face seat is
    a proportion. Every row admits a valid draw, so no Resample is needed."""
    idx = _ROWS[difficulty][int(rng.integers(len(_ROWS[difficulty])))]
    _, bore, od, t, bc, n, bh, x, a, hl = _B16_5_CL150[idx]
    p["bore"], p["flange_od"], p["flange_t"] = bore, od, t
    p["bolt_circle_d"], p["n_bolts"], p["bolt_hole_d"] = bc, n, bh
    p["hub_od"], p["pipe_od"], p["hub_len"] = x, a, hl

    # raised-face seat: only when a raised face is present (rf_t drawn > 0).
    # Sit its outer edge a few mm inboard of the bolt holes so the gasket seat
    # clears the bolting; it is comfortably larger than the bore.
    if p["rf_t"]:
        clear = float(rng.uniform(4.0, 10.0))
        p["raised_face_d"] = round((bc - bh) - clear, 1)
    else:
        p["raised_face_d"] = 0.0
