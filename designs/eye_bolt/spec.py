"""eye_bolt — the benchmark generator spec.

DIN 580 lifting eye bolts come in a nominal metric thread series; the eye and
collar are fixed proportions of the thread size, so the nominal thread diameter
is the size driver (drawn by refine from the standard series) and the shank
`length` is a free dimension. check() audits that the thread size is a real ISO
261 coarse size and the shank is long enough to be threaded.

Anchor: DIN 580 lifting eye bolt (metric thread series); the eye/collar
proportions are `proportion` (relative to the nominal thread Ø).
"""

# DIN 580 nominal metric thread sizes (mm), split by difficulty
_SIZES = {
    "easy": [6.0, 8.0, 10.0],
    "medium": [12.0, 16.0],
    "hard": [20.0, 24.0],
}
_ALL = [6.0, 8.0, 10.0, 12.0, 16.0, 20.0, 24.0]
_PITCH = {6: 1.0, 8: 1.25, 10: 1.5, 12: 1.75, 16: 2.0, 20: 2.5, 24: 3.0}


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "thread_d": dict(
        desc="nominal metric thread diameter M (DIN 580 size; drives eye/collar)",
        unit="mm",
        range={"easy": (6.0, 10.0), "medium": (12.0, 16.0), "hard": (20.0, 24.0)},
        source="DIN 580 nominal thread size series",
        askable=True,
        refine=True,
        coverage=[6.0, 8.0, 10.0, 12.0, 16.0, 20.0, 24.0],
    ),
    "length": dict(
        desc="threaded shank length l (free; DIN 580 shanks are short)",
        unit="mm",
        range={"easy": (10.0, 24.0), "medium": (18.0, 40.0), "hard": (30.0, 64.0)},
        source="shank thread length (proportion)",
        askable=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    d = p["thread_d"]
    if d not in _ALL:
        bad.append("thread_d is not a DIN 580 nominal thread size")
    if int(round(d)) not in _PITCH:
        bad.append("thread_d has no ISO 261 coarse pitch")
    if p["length"] < 1.2 * d:
        bad.append("shank length below ~1.2 d (too short to thread)")
    return bad


# ── refine — draw the nominal thread size ────────────────────────────────────
def refine(p: dict, difficulty: str, rng) -> None:
    sizes = _SIZES[difficulty]
    p["thread_d"] = sizes[int(rng.integers(len(sizes)))]
