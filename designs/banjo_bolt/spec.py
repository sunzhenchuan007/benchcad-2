"""banjo_bolt — the benchmark generator spec (DIN 7643 hollow screw).

The thread size fixes the whole part as one catalogue row (hex s, axial bore d4,
cross-hole d2, shank length l1, bore depth t1, head height m, cross-hole position
c1). Difficulty scales the size: easy = M10/M12, medium = M14/M16/M18,
hard = M22/M26. (M8x1 is omitted — the catalogue leaves its cross-hole blank.)
"""

# DIN 7643 rows (M10x1 .. M26x1.5): (d, s, d4, d2, l1, t1, m, c1).
# l1 for M14 corrected to 26 (the datasheet cell prints 16, out of sequence).
_ROWS = [
    (10, 14, 5.5, 2.8, 19, 17.0, 6, 8.5),
    (12, 17, 7.0, 3.5, 24, 22.0, 6, 11.0),
    (14, 19, 9.0, 4.5, 26, 24.0, 6, 11.0),
    (16, 22, 11.0, 5.5, 28, 26.0, 6, 11.0),
    (18, 24, 13.0, 7.0, 32, 29.0, 6, 11.0),
    (22, 27, 16.0, 9.0, 39, 35.5, 7, 13.0),
    (26, 32, 20.0, 11.0, 45, 41.0, 7, 13.0),
]
_BY_D = {r[0]: r for r in _ROWS}
_DIFF_ROWS = {"easy": [0, 1], "medium": [2, 3, 4], "hard": [5, 6]}
_KEYS = ("hex_s", "bore_dia_d4", "cross_hole_d2", "shank_len_l1",
         "bore_depth_t1", "head_h_m", "cross_pos_c1")


PARAM_SPEC = {
    "thread_dia_d": dict(
        desc="thread nominal Ø d (= shank Ø d3), fine pitch", unit="mm",
        range={"easy": (10, 12), "medium": (14, 18), "hard": (22, 26)},
        source="DIN 7643 thread size", askable=True, integer=True,
        refine=True, coverage=[10, 12, 14, 16, 18, 22, 26],
    ),
    "hex_s": dict(
        desc="hex head width across flats s", unit="mm",
        range={"easy": (12.0, 32.0), "medium": (12.0, 32.0), "hard": (12.0, 32.0)},
        source="DIN 7643 hex width table (row-locked to d)", askable=True, refine=True,
    ),
    "bore_dia_d4": dict(
        desc="axial hollow bore Ø d4 (drilled from the free end)", unit="mm",
        range={"easy": (5.0, 20.0), "medium": (5.0, 20.0), "hard": (5.0, 20.0)},
        source="DIN 7643 bore table (row-locked to d)", askable=True, refine=True,
    ),
    "cross_hole_d2": dict(
        desc="transverse cross-hole Ø d2 feeding the axial bore", unit="mm",
        range={"easy": (2.5, 11.0), "medium": (2.5, 11.0), "hard": (2.5, 11.0)},
        source="DIN 7643 cross-hole table (row-locked to d)", askable=True, refine=True,
    ),
    "shank_len_l1": dict(
        desc="shank length l1 (head underside to tip)", unit="mm",
        range={"easy": (17.0, 45.0), "medium": (17.0, 45.0), "hard": (17.0, 45.0)},
        source="DIN 7643 length table (row-locked to d)", askable=True, refine=True,
    ),
    "bore_depth_t1": dict(
        desc="axial-bore depth t1 from the tip", unit="mm",
        range={"easy": (15.0, 41.0), "medium": (15.0, 41.0), "hard": (15.0, 41.0)},
        source="DIN 7643 bore-depth table (row-locked to d)", askable=True, refine=True,
    ),
    "head_h_m": dict(
        desc="hex head height m", unit="mm",
        range={"easy": (5.0, 7.0), "medium": (5.0, 7.0), "hard": (5.0, 7.0)},
        source="DIN 7643 head-height table (row-locked to d)", askable=True, refine=True,
    ),
    "cross_pos_c1": dict(
        desc="cross-hole centre distance c1 below the head underside", unit="mm",
        range={"easy": (8.0, 13.0), "medium": (8.0, 13.0), "hard": (8.0, 13.0)},
        source="DIN 7643 cross-hole location (row-locked to d)", askable=True, refine=True,
    ),
    "n_cross_holes": dict(
        desc="number of cross-drills feeding the bore (1 = 2 ports, 2 = 4 ports)", unit="",
        range={"easy": (1, 2), "medium": (1, 2), "hard": (1, 2)},
        choices={"easy": [1, 2], "medium": [1, 2], "hard": [1, 2]},
        source="banjo-bolt cross-drill variants (single / double)",
        integer=True, feature=True, coverage=[1, 2],
    ),
}


def check(p: dict) -> list[str]:
    bad = []
    d = int(round(p["thread_dia_d"]))
    if d not in _BY_D:
        bad.append("thread_dia_d is not a DIN 7643 size (10/12/14/16/18/22/26)")
        return bad
    row = _BY_D[d]
    for key, val in zip(_KEYS, row[1:]):
        if abs(p[key] - val) > 0.11:
            bad.append(f"{key}={p[key]} does not match the DIN 7643 M{d} row ({val})")
    if p["bore_dia_d4"] >= p["thread_dia_d"] - 1.0:
        bad.append("bore d4 leaves < 0.5 mm shank wall (d4 too close to d)")
    z_cross = p["shank_len_l1"] - p["cross_pos_c1"]
    if z_cross >= p["bore_depth_t1"]:
        bad.append("cross-hole sits above the axial bore: it would not reach the bore")
    if z_cross <= p["cross_hole_d2"]:
        bad.append("cross-hole runs off the tip end of the shank")
    if p["hex_s"] <= p["thread_dia_d"]:
        bad.append("hex_s must be wider than the shank Ø")
    return bad


def refine(p: dict, difficulty: str, rng) -> None:
    rows = _DIFF_ROWS[difficulty]
    row = _ROWS[rows[int(rng.integers(len(rows)))]]
    p["thread_dia_d"] = row[0]
    for key, val in zip(_KEYS, row[1:]):
        p[key] = val
