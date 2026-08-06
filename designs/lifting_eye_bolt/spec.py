"""lifting_eye_bolt — the benchmark generator spec (DIN 580).

Nominal metric series: the eye inner/outer diameter (d2/d3) and thread length (l)
are tabulated per size, so the nominal thread diameter d1 is the size driver
(refine draws a row) and d2/d3/l are row-locked.

Params carry their DIN 580 drawing symbol: thread_dia_d1 (d1), eye_inner_d2 (d2),
eye_outer_d3 (d3), thread_len_l (l).

Anchor: DIN 580 lifting eye bolt dimension table.
"""

# DIN 580 rows: (d1, d2, d3, l), mm
_ROWS = {
    "easy": [(8.0, 20.0, 36.0, 13.0), (10.0, 25.0, 45.0, 17.0)],
    "medium": [(12.0, 30.0, 54.0, 20.5), (16.0, 35.0, 63.0, 27.0)],
    "hard": [(20.0, 40.0, 72.0, 30.0), (24.0, 50.0, 90.0, 36.0)],
}
_ALL = [r for rows in _ROWS.values() for r in rows]
_PITCH = {8: 1.25, 10: 1.5, 12: 1.75, 16: 2.0, 20: 2.5, 24: 3.0}


PARAM_SPEC = {
    "thread_dia_d1": dict(
        desc="nominal metric thread diameter d1 (DIN 580 size; drives eye + length)",
        unit="mm", range={"easy": (8.0, 10.0), "medium": (12.0, 16.0), "hard": (20.0, 24.0)},
        source="DIN 580 nominal thread size", refine=True,
        coverage=[8.0, 10.0, 12.0, 16.0, 20.0, 24.0],
    ),
    "eye_inner_d2": dict(
        desc="eye inner diameter d2 (same DIN 580 row; ~2-2.5 d1; = collar Ø)", unit="mm",
        range={"easy": (20.0, 90.0), "medium": (20.0, 90.0), "hard": (20.0, 90.0)},
        source="DIN 580 d2 (row-locked to thread_dia_d1)", refine=True,
    ),
    "eye_outer_d3": dict(
        desc="eye outer diameter d3 (same DIN 580 row)", unit="mm",
        range={"easy": (36.0, 90.0), "medium": (36.0, 90.0), "hard": (36.0, 90.0)},
        source="DIN 580 d3 (row-locked to thread_dia_d1)", refine=True,
    ),
    "thread_len_l": dict(
        desc="thread / shank length l (same DIN 580 row)", unit="mm",
        range={"easy": (13.0, 36.0), "medium": (13.0, 36.0), "hard": (13.0, 36.0)},
        source="DIN 580 l (row-locked to thread_dia_d1)", refine=True,
    ),
}


def check(p: dict) -> list[str]:
    bad = []
    row = (p["thread_dia_d1"], p["eye_inner_d2"], p["eye_outer_d3"], p["thread_len_l"])
    if row not in _ALL:
        bad.append("(thread_dia_d1, eye_inner_d2, eye_outer_d3, thread_len_l) is not a DIN 580 row")
    if int(round(p["thread_dia_d1"])) not in _PITCH:
        bad.append("thread_dia_d1 has no ISO 261 coarse pitch")
    if p["eye_outer_d3"] <= p["eye_inner_d2"]:
        bad.append("eye_outer_d3 must exceed eye_inner_d2 (a real ring section)")
    if p["eye_inner_d2"] <= p["thread_dia_d1"]:
        bad.append("eye inner Ø must exceed the thread Ø")
    if p["thread_len_l"] < 1.2 * p["thread_dia_d1"]:
        bad.append("thread length below ~1.2 d1")
    return bad


def refine(p: dict, difficulty: str, rng) -> None:
    rows = _ROWS[difficulty]
    d1, d2, d3, l = rows[int(rng.integers(len(rows)))]
    p["thread_dia_d1"], p["eye_inner_d2"], p["eye_outer_d3"], p["thread_len_l"] = d1, d2, d3, l
