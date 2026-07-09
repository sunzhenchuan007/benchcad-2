"""lifting_eye_bolt — the benchmark generator spec.

DIN 580 lifting eye bolts are a nominal metric series; the eye inner/outer
diameter (d2/d3) and the thread length (l) are tabulated per size, so the nominal
thread diameter is the size driver (refine draws a row) and eye_id/eye_od/
thread_len are row-locked. The collar is a fixed proportion of the thread size.

Anchor: DIN 580 lifting eye bolt dimension table — d2 (eye inner), d3 (eye outer),
l (thread length), per nominal thread size.
"""

# DIN 580 rows: (thread d, eye_id d2, eye_od d3, thread_len l), mm
_ROWS = {
    "easy": [(8.0, 20.0, 36.0, 13.0), (10.0, 25.0, 45.0, 17.0)],
    "medium": [(12.0, 30.0, 54.0, 20.5), (16.0, 35.0, 63.0, 27.0)],
    "hard": [(20.0, 40.0, 72.0, 30.0), (24.0, 50.0, 90.0, 36.0)],
}
_ALL = [r for rows in _ROWS.values() for r in rows]
_PITCH = {8: 1.25, 10: 1.5, 12: 1.75, 16: 2.0, 20: 2.5, 24: 3.0}


PARAM_SPEC = {
    "thread_d": dict(
        desc="nominal metric thread diameter M (DIN 580 size; drives eye + length)",
        unit="mm", range={"easy": (8.0, 10.0), "medium": (12.0, 16.0), "hard": (20.0, 24.0)},
        source="DIN 580 nominal thread size", askable=True, refine=True,
        coverage=[8.0, 10.0, 12.0, 16.0, 20.0, 24.0],
    ),
    "eye_id": dict(
        desc="eye inner diameter d2 (same DIN 580 row; ~2-2.5 d)", unit="mm",
        range={"easy": (20.0, 90.0), "medium": (20.0, 90.0), "hard": (20.0, 90.0)},
        source="DIN 580 d2 (row-locked to thread_d)", askable=True, refine=True,
    ),
    "eye_od": dict(
        desc="eye outer diameter d3 (same DIN 580 row)", unit="mm",
        range={"easy": (36.0, 90.0), "medium": (36.0, 90.0), "hard": (36.0, 90.0)},
        source="DIN 580 d3 (row-locked to thread_d)", askable=True, refine=True,
    ),
    "thread_len": dict(
        desc="thread / shank length l (same DIN 580 row)", unit="mm",
        range={"easy": (13.0, 36.0), "medium": (13.0, 36.0), "hard": (13.0, 36.0)},
        source="DIN 580 l (row-locked to thread_d)", askable=True, refine=True,
    ),
}


def check(p: dict) -> list[str]:
    bad = []
    row = (p["thread_d"], p["eye_id"], p["eye_od"], p["thread_len"])
    if row not in _ALL:
        bad.append("(thread_d, eye_id, eye_od, thread_len) is not a DIN 580 row")
    if int(round(p["thread_d"])) not in _PITCH:
        bad.append("thread_d has no ISO 261 coarse pitch")
    if p["eye_od"] <= p["eye_id"]:
        bad.append("eye_od must exceed eye_id (a real ring section)")
    if p["eye_id"] <= p["thread_d"]:
        bad.append("eye inner Ø must exceed the thread Ø")
    if p["thread_len"] < 1.2 * p["thread_d"]:
        bad.append("thread length below ~1.2 d")
    return bad


def refine(p: dict, difficulty: str, rng) -> None:
    rows = _ROWS[difficulty]
    d, eid, eod, tl = rows[int(rng.integers(len(rows)))]
    p["thread_d"], p["eye_id"], p["eye_od"], p["thread_len"] = d, eid, eod, tl
