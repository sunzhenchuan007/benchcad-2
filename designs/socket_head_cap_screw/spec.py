"""socket_head_cap_screw — the benchmark generator spec.

The head diameter, head height and hex-socket width are the jointly-sampled ISO
4762 row for the nominal thread size; refine() draws a row and sets them from the
catalog table. The shank `length` is a free stock dimension. check() audits that
the head trio is a real ISO 4762 row and that the geometry is consistent.

Anchor: ISO 4762 hexagon socket head cap screw — head Ø dk, head height k and
socket width s per the standard; the coarse pitch is ISO 261.
"""

# ISO 4762 rows: nominal thread d -> (head Ø dk, head height k, socket width s), mm
_ROWS = {
    "easy": [(6.0, 10.0, 6.0, 5.0), (8.0, 13.0, 8.0, 6.0)],
    "medium": [(10.0, 16.0, 10.0, 8.0), (12.0, 18.0, 12.0, 10.0), (14.0, 22.0, 14.0, 12.0)],
    "hard": [(16.0, 24.0, 16.0, 14.0), (20.0, 30.0, 20.0, 17.0)],
}
_ALL_ROWS = [r for rows in _ROWS.values() for r in rows]
_PITCH = {6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 14: 2.0, 16: 2.0, 20: 2.5}


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "thread_d": dict(
        desc="nominal metric thread diameter M (ISO 4762 row)",
        unit="mm",
        range={"easy": (6.0, 8.0), "medium": (10.0, 14.0), "hard": (16.0, 20.0)},
        source="ISO 4762 nominal thread size",
        askable=True,
        refine=True,
        coverage=[6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0],
    ),
    "head_d": dict(
        desc="head diameter dk (same ISO 4762 row)",
        unit="mm",
        range={"easy": (10.0, 30.0), "medium": (10.0, 30.0), "hard": (10.0, 30.0)},
        source="ISO 4762 head diameter dk (row-locked to thread_d)",
        askable=True,
        refine=True,
    ),
    "head_h": dict(
        desc="head height k (same ISO 4762 row; ≈ thread_d)",
        unit="mm",
        range={"easy": (6.0, 20.0), "medium": (6.0, 20.0), "hard": (6.0, 20.0)},
        source="ISO 4762 head height k (row-locked to thread_d)",
        askable=True,
        refine=True,
    ),
    "socket_s": dict(
        desc="hex drive socket width across flats s (same ISO 4762 row)",
        unit="mm",
        range={"easy": (5.0, 17.0), "medium": (5.0, 17.0), "hard": (5.0, 17.0)},
        source="ISO 4762 socket size s (row-locked to thread_d)",
        askable=True,
        refine=True,
    ),
    "length": dict(
        desc="shank length l (under the head; free stock length)",
        unit="mm",
        range={"easy": (12.0, 40.0), "medium": (20.0, 80.0), "hard": (40.0, 160.0)},
        source="stock length (proportion)",
        askable=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    row = (p["thread_d"], p["head_d"], p["head_h"], p["socket_s"])
    if row not in _ALL_ROWS:
        bad.append("(thread_d, head_d, head_h, socket_s) is not an ISO 4762 row")
    d, dk, k, sh = p["thread_d"], p["head_d"], p["head_h"], p["socket_s"]
    if int(round(d)) not in _PITCH:
        bad.append("thread_d has no ISO 261 coarse pitch")
    if dk <= d:
        bad.append("head diameter must exceed the thread diameter")
    if sh >= dk:
        bad.append("socket width across flats must fit inside the head")
    if p["length"] < 1.5 * d:
        bad.append("shank length below ~1.5 d (not a practical cap screw)")
    return bad


# ── refine — draw the ISO 4762 row ──────────────────────────────────────────
def refine(p: dict, difficulty: str, rng) -> None:
    rows = _ROWS[difficulty]
    d, dk, k, sh = rows[int(rng.integers(len(rows)))]
    p["thread_d"], p["head_d"], p["head_h"], p["socket_s"] = d, dk, k, sh
