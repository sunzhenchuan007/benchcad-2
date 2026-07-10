"""hex_cap_bolt — the benchmark generator spec.

The head is table-driven: (thread_d, head_af, head_h) is one jointly-sampled row
of the ISO 4014 hex-head table, so the width across flats and head height are
locked to the nominal thread size. Difficulty is split by BOLT SIZE (easy = the
small M6–M8 rows, medium = M10–M14, hard = M16–M24) so the tiers are genuinely
distinct rather than the same bolt at three length caps. The shank length is a
real ISO 888 nominal length, at least 2·d and at most a realistic 16·d
slenderness; a head top-chamfer appears on the hard tier.

Anchor: ISO 4017 (fully-threaded hexagon head screws); head dims s (across
flats) and k (height) share the ISO 4014 hex-head table.
"""

from bench2 import Resample

# ISO 4014 — (name, thread d, s = width across flats, k = head height), mm
_ISO4014 = [
    ("M6", 6.0, 10.0, 4.0),
    ("M8", 8.0, 13.0, 5.3),
    ("M10", 10.0, 16.0, 6.4),
    ("M12", 12.0, 18.0, 7.5),
    ("M14", 14.0, 21.0, 8.8),
    ("M16", 16.0, 24.0, 10.0),
    ("M20", 20.0, 30.0, 12.5),
    ("M24", 24.0, 36.0, 15.0),
]
_BY_NAME = {r[0]: r for r in _ISO4014}

# tiers split by bolt size (not by a length cap) so the tiers don't overlap
_TIER = {
    "easy": ["M6", "M8"],
    "medium": ["M10", "M12", "M14"],
    "hard": ["M16", "M20", "M24"],
}

# ISO 888 nominal length series, mm
_LENGTHS = [10, 12, 16, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 80, 90, 100, 110, 120]

# realistic max slenderness (length / thread_d) — a proportion, not a standard
_MAX_LD = 16.0


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "thread_d": dict(
        desc="nominal thread diameter d (ISO 4014 row, jointly with head_af, head_h)",
        unit="mm",
        range={"easy": (6.0, 8.0), "medium": (10.0, 14.0), "hard": (16.0, 24.0)},
        source="ISO 4014 / ISO 261 coarse thread series",
        askable=True,
        refine=True,
        coverage=[6.0, 8.0, 10.0, 12.0, 14.0, 16.0, 20.0, 24.0],
    ),
    "head_af": dict(
        desc="head width across flats s (same table row as thread_d)",
        unit="mm",
        range={"easy": (10.0, 13.0), "medium": (16.0, 21.0), "hard": (24.0, 36.0)},
        source="ISO 4014 (row-locked to thread_d)",
        askable=True,
        refine=True,
    ),
    "head_h": dict(
        desc="head height k (same table row as thread_d)",
        unit="mm",
        range={"easy": (4.0, 5.3), "medium": (6.4, 8.8), "hard": (10.0, 15.0)},
        source="ISO 4014 (row-locked to thread_d)",
        askable=True,
        refine=True,
    ),
    "length": dict(
        desc="shank length L (ISO 888 nominal length series)",
        unit="mm",
        range={"easy": (12.0, 120.0), "medium": (20.0, 120.0), "hard": (32.0, 120.0)},
        source="ISO 888 nominal length series",
        askable=True,
        refine=True,
    ),
    "head_chamfer": dict(
        desc="head top chamfer (0 = none; hard only)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (0.0, 0.0), "hard": (0.0, 4.0)},
        source="ISO 4014 head chamfer (deburr convention)",
        feature=True,
        refine=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    # the (thread_d, head_af, head_h) triple must be an ISO 4014 row
    if not any(
        abs(p["thread_d"] - r[1]) < 1e-6 and abs(p["head_af"] - r[2]) < 1e-6
        and abs(p["head_h"] - r[3]) < 1e-6
        for r in _ISO4014
    ):
        bad.append("(thread_d, head_af, head_h) is not an ISO 4014 row")
    if p["length"] not in _LENGTHS:
        bad.append("length is not an ISO 888 nominal length")
    # a bolt shorter than 2d isn't a bolt; longer than 16d is an unreal proportion
    if p["length"] < 2.0 * p["thread_d"]:
        bad.append("length < 2*thread_d: below a usable bolt length")
    if p["length"] > _MAX_LD * p["thread_d"]:
        bad.append(f"length > {_MAX_LD:g}*thread_d: too slender a bolt proportion")
    if p["head_chamfer"] and p["head_chamfer"] > 0.25 * p["head_h"]:
        bad.append("head_chamfer > 0.25*head_h: chamfer would gut the head")
    return bad


# ── refine — size-tiered head-table draw + a valid length ────────────────────
def refine(p: dict, difficulty: str, rng) -> None:
    """Draw an ISO 4014 head row from this tier's size band and a matching
    nominal length. Raises Resample if no listed length fits (never happens for
    the tabulated sizes, but keeps the contract explicit)."""
    name = _TIER[difficulty][int(rng.integers(len(_TIER[difficulty])))]
    _, d, s, k = _BY_NAME[name]
    p["thread_d"], p["head_af"], p["head_h"] = d, s, k

    ok = [L for L in _LENGTHS if 2.0 * d <= L <= min(120.0, _MAX_LD * d)]
    if not ok:
        raise Resample
    p["length"] = float(ok[int(rng.integers(len(ok)))])
    p["head_chamfer"] = round(s * 0.08, 1) if difficulty == "hard" else 0.0
