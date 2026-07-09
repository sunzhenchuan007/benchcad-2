"""clevis_pin — the benchmark generator spec.

An ISO 2341 clevis pin is keyed by the nominal shank diameter d: once the size
is chosen, the flat-head diameter dk, head height k and the transverse cotter
(split-pin) hole Ø hd are all proportional to it and fixed by the standard's
size series. refine() therefore draws ONE nominal-size row and sets those three
together, so a size is never mixed across the table; only the pin length L is a
free draw per difficulty. check() audits that the row is a genuine ISO 2341
size, that the head is wider than the shank, that the cotter hole fits across
the shank, and that the pin is long enough to seat the head and carry the hole
below it.

Anchor: ISO 2341 (clevis pin with head, form B). The (d, dk, k, hd) rows below
follow the standard's proportions — dk ~ round(1.5 d), k ~ round(0.4 d) (min
1.5), hd ~ the standard split-pin size (~0.25 d, ISO 1234 / DIN 94) — over the
nominal shank series 3..20 mm.
"""

from bench2 import Resample  # noqa: F401 — refine may reject an infeasible draw

# ISO 2341 clevis-pin rows keyed by nominal shank Ø d ->
#   (shank_d d, head_d dk, head_h k, hole_d hd), mm
_ROWS = {
    "easy": [
        (3.0, 5.0, 1.5, 0.8),
        (4.0, 6.0, 1.6, 1.0),
        (5.0, 8.0, 2.0, 1.2),
        (6.0, 9.0, 2.4, 1.6),
    ],
    "medium": [
        (8.0, 12.0, 3.2, 2.0),
        (10.0, 15.0, 4.0, 2.5),
    ],
    "hard": [
        (12.0, 18.0, 4.8, 3.2),
        (16.0, 24.0, 6.4, 4.0),
        (20.0, 30.0, 8.0, 5.0),
    ],
}
_ALL_ROWS = [r for rows in _ROWS.values() for r in rows]
_ISO_SHANK = [r[0] for r in _ALL_ROWS]  # [3, 4, 5, 6, 8, 10, 12, 16, 20]


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "shank_d": dict(
        desc="nominal shank diameter d (ISO 2341 size-driver row)",
        unit="mm",
        range={"easy": (3.0, 6.0), "medium": (8.0, 10.0), "hard": (12.0, 20.0)},
        source="ISO 2341 nominal shank diameter d (3, 4, 5, 6, 8, 10, 12, 16, 20 mm)",
        askable=True,
        refine=True,
        coverage=[3, 4, 5, 6, 8, 10, 12, 16, 20],
    ),
    "length": dict(
        desc="pin length L (shank, free draw per difficulty)",
        unit="mm",
        range={"easy": (10.0, 40.0), "medium": (25.0, 80.0), "hard": (50.0, 160.0)},
        source="ISO 2341 length series (free length; catalog range per size band)",
        askable=True,
    ),
    "head_d": dict(
        desc="flat head diameter dk ~ round(1.5 d) (same ISO 2341 row)",
        unit="mm",
        range={"easy": (5.0, 9.0), "medium": (12.0, 15.0), "hard": (18.0, 30.0)},
        source="ISO 2341 head diameter dk (row-locked to shank_d)",
        askable=True,
        refine=True,
    ),
    "head_h": dict(
        desc="head height k ~ round(0.4 d, 1), min 1.5 (same ISO 2341 row)",
        unit="mm",
        range={"easy": (1.5, 2.4), "medium": (3.2, 4.0), "hard": (4.8, 8.0)},
        source="ISO 2341 head height k (row-locked to shank_d)",
        askable=True,
        refine=True,
    ),
    "hole_d": dict(
        desc="transverse cotter (split-pin) hole Ø hd ~ 0.25 d (same ISO 2341 row)",
        unit="mm",
        range={"easy": (0.8, 1.6), "medium": (2.0, 2.5), "hard": (3.2, 5.0)},
        source="split-pin size (ISO 1234 / DIN 94), row-locked to shank_d",
        askable=True,
        refine=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    d, dk, k, hd, L = (
        p["shank_d"],
        p["head_d"],
        p["head_h"],
        p["hole_d"],
        p["length"],
    )
    if d not in _ISO_SHANK:
        bad.append(f"shank_d={d} is not an ISO 2341 nominal size {_ISO_SHANK}")
    if (d, dk, k, hd) not in _ALL_ROWS:
        bad.append("(shank_d, head_d, head_h, hole_d) is not an ISO 2341 size row")
    if dk <= d:
        bad.append("head_d must exceed shank_d (the head has to be wider than the shank)")
    if hd >= d:
        bad.append("hole_d must be smaller than shank_d (cotter hole has to fit across the shank)")
    if L < k + 3.0 * d:
        bad.append(
            "length < head_h + 3*shank_d: too short to seat the head and carry the cotter "
            "hole below it"
        )
    return bad


# ── refine — draw one ISO 2341 nominal-size row (length stays a free draw) ────
def refine(p: dict, difficulty: str, rng) -> None:
    rows = _ROWS[difficulty]
    d, dk, k, hd = rows[int(rng.integers(len(rows)))]
    p["shank_d"], p["head_d"], p["head_h"], p["hole_d"] = d, dk, k, hd
