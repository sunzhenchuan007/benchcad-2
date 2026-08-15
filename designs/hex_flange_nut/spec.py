"""hex_flange_nut — the benchmark generator spec.

The five dimensioned parameters are one jointly-sampled row of the DIN 6923
(ISO 4161) hexagon flange nut table: width across flats s, flange diameter dc,
total height m and flange edge thickness c are all locked to the nominal thread
size d, so every sampled nut is a real catalog nut. Difficulty is split by SIZE
(easy = M5-M8, medium = M10-M14, hard = M16-M20) so the tiers are genuinely
distinct rather than one nut at three caps.

Two features vary within the real envelope. The conical flange-seat height is
NOT tabulated by DIN 6923 (the table fixes dc, c, m, s but not the rim->hex
cone), so it is drawn per instance as a declared proportion of m. An integer
count of radial locking serrations on the bearing face selects the serrated
DIN 6923 variant (medium/hard, features on) versus the plain variant (easy).

Anchor: DIN 6923 / ISO 4161 hexagon flange nut dimension table; internal thread
minor diameter D1 = d - 1.0825*P and coarse pitch per ISO 261 / ISO 965.
Table cross-checked against fasteners.eu and fullerfasteners DIN 6923 sheets.
"""

import math

from bench2 import Resample  # noqa: F401 — refine may reject an infeasible draw
from part import _PITCH  # ISO 261 coarse pitch, shared with build() (no drift)

# DIN 6923 (ISO 4161): (name, d, P, s across-flats, dc flange, m height, c edge), mm
_DIN6923 = [
    ("M5",   5.0, 0.8,   8.0, 11.8,  5.0, 1.0),
    ("M6",   6.0, 1.0,  10.0, 14.2,  6.0, 1.1),
    ("M8",   8.0, 1.25, 13.0, 17.9,  8.0, 1.2),
    ("M10", 10.0, 1.5,  15.0, 21.8, 10.0, 1.5),
    ("M12", 12.0, 1.75, 18.0, 26.0, 12.0, 1.8),
    ("M14", 14.0, 2.0,  21.0, 29.9, 14.0, 2.1),
    ("M16", 16.0, 2.0,  24.0, 34.5, 16.0, 2.4),
    ("M20", 20.0, 2.5,  30.0, 42.8, 20.0, 3.0),
]
_BY_NAME = {r[0]: r for r in _DIN6923}
_ROWS = {(r[1], r[3], r[4], r[5], r[6]) for r in _DIN6923}  # (d, s, dc, m, c)

# difficulty split by nut size (not by a feature cap) so tiers don't overlap
_TIER = {
    "easy":   ["M5", "M6", "M8"],
    "medium": ["M10", "M12", "M14"],
    "hard":   ["M16", "M20"],
}


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "thread_dia_d": dict(
        desc="nominal metric thread diameter d (DIN 6923 row, jointly with s/dc/m/c)",
        unit="mm",
        range={"easy": (5.0, 8.0), "medium": (10.0, 14.0), "hard": (16.0, 20.0)},
        source="DIN 6923 / ISO 4161 (ISO 261 coarse thread series)",
        askable=True,
        refine=True,
        coverage=[5.0, 6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0],
    ),
    "hex_s": dict(
        desc="width across flats s (same DIN 6923 row)",
        unit="mm",
        range={"easy": (8.0, 13.0), "medium": (15.0, 21.0), "hard": (24.0, 30.0)},
        source="DIN 6923 / ISO 4161 (row-locked to thread_dia_d)",
        askable=True,
        refine=True,
    ),
    "flange_dia_dc": dict(
        desc="flange (bearing washer-face) diameter dc (same DIN 6923 row)",
        unit="mm",
        range={"easy": (11.8, 17.9), "medium": (21.8, 29.9), "hard": (34.5, 42.8)},
        source="DIN 6923 / ISO 4161 (row-locked to thread_dia_d)",
        askable=True,
        refine=True,
    ),
    "total_h_m": dict(
        desc="total nut height m, bearing face to top (same DIN 6923 row)",
        unit="mm",
        range={"easy": (5.0, 8.0), "medium": (10.0, 14.0), "hard": (16.0, 20.0)},
        source="DIN 6923 / ISO 4161 (row-locked to thread_dia_d)",
        askable=True,
        refine=True,
    ),
    "flange_thk_c": dict(
        desc="flange edge (rim) thickness c (same DIN 6923 row)",
        unit="mm",
        range={"easy": (1.0, 1.2), "medium": (1.5, 2.1), "hard": (2.4, 3.0)},
        source="DIN 6923 / ISO 4161 (row-locked to thread_dia_d)",
        askable=True,
        refine=True,
    ),
    "flange_seat_h": dict(
        desc="height of the conical flange seat (rim -> hex blend), fraction of m",
        unit="mm",
        range={"easy": (1.5, 3.9), "medium": (3.0, 6.8), "hard": (4.8, 9.7)},
        source="proportion (0.30-0.48*m; the rim->hex cone is not tabulated by DIN 6923)",
        askable=True,
        refine=True,
    ),
    "serrations": dict(
        desc="radial locking serrations on the bearing face (0 = plain variant)",
        unit="",
        range={"easy": (0, 0), "medium": (12, 18), "hard": (14, 22)},
        source="DIN 6923 serrated (locking) vs plain variant; tooth count a proportion",
        integer=True,
        feature=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    d, s, dc = p["thread_dia_d"], p["hex_s"], p["flange_dia_dc"]
    m, c, fh, ns = p["total_h_m"], p["flange_thk_c"], p["flange_seat_h"], p["serrations"]
    # 1. the (d, s, dc, m, c) quintuple must be a real DIN 6923 row
    if (d, s, dc, m, c) not in _ROWS:
        bad.append("(thread_dia_d, hex_s, flange_dia_dc, total_h_m, flange_thk_c) is not a DIN 6923 row")
    # 2. the flange must overhang the hex: dc > across-corners e = s/cos(30)
    e = s / math.cos(math.radians(30.0))
    if dc <= e:
        bad.append("flange_dia_dc <= hex across-corners e: no flange overhang (not a flange nut)")
    # 3. the thread must fit inside the wrench flats with a wall: (s - d)/2 >= 1 mm
    if (s - d) / 2.0 < 1.0:
        bad.append("(hex_s - thread_dia_d)/2 < 1 mm: no wall between the thread and the flat")
    # 4. the flange is a thin skirt, not the whole nut: edge thickness c < height m
    if c >= m:
        bad.append("flange_thk_c >= total_h_m: flange thicker than the whole nut")
    # 5. the conical seat sits between the rim top and the hex top
    if not (c < fh < m):
        bad.append("flange_seat_h outside (flange_thk_c, total_h_m): seat can't blend rim to hex")
    # 6. the internal thread leaves a positive minor diameter D1 = d - 1.0825*P
    pitch = _PITCH[int(round(d))]
    if d - 1.0825 * pitch <= 0.0:
        bad.append("minor diameter D1 <= 0: thread deeper than the bore")
    # 7. serrations: plain (0) or a plausible tooth count that fits the bearing ring
    if ns and not (6 <= ns <= 24):
        bad.append("serrations outside 6-24: not a plausible locking-serration count")
    return bad


# ── refine — DIN 6923 row draw + the untabulated conical seat height ──────────
def refine(p: dict, difficulty: str, rng) -> None:
    """Draw one DIN 6923 row from this tier's size band (fixing d, s, dc, m, c
    together) and a conical flange-seat height as a proportion of m."""
    name = _TIER[difficulty][int(rng.integers(len(_TIER[difficulty])))]
    _, d, _p, s, dc, m, c = _BY_NAME[name]
    p["thread_dia_d"], p["hex_s"], p["flange_dia_dc"] = d, s, dc
    p["total_h_m"], p["flange_thk_c"] = m, c
    p["flange_seat_h"] = round(m * float(rng.uniform(0.30, 0.48)), 2)
