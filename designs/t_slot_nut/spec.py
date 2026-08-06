"""t_slot_nut — the benchmark generator spec.

The slot width drives everything: it pairs with a nominal thread (DIN 508 table)
and sets the base / height / length by proportion (refine). Two dimensions are
locked to DIN 508 exactly rather than proportioned: the (slot, thread) pairing
and the neck width B1 = slot − 0.4 (the slot-fit width). The slot series widens
with difficulty and a lead-in chamfer appears on the hard tier.

Anchor: norelem 07060 (nuts for T-slots, DIN 508) — the (slot → thread) pairing
and B1 = a − 0.4 are DIN 508; the base/neck heights, base width and length are
declared `proportion` (the datasheet's full per-size table is not transcribed).
"""

from bench2 import Resample

# DIN 508 slot width a -> paired nominal thread (the catalog/preferred row), mm
_THREAD = {8: 6.0, 10: 8.0, 12: 10.0, 14: 12.0, 18: 16.0, 22: 20.0, 28: 24.0}
# slot widths offered per difficulty (small slots easy, large slots hard)
_SLOTS = {"easy": [8, 10, 12], "medium": [10, 12, 14, 18], "hard": [18, 22, 28]}


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "slot_w": dict(
        desc="nominal T-slot width a (drives thread + all proportions)",
        unit="mm",
        range={"easy": (8.0, 12.0), "medium": (10.0, 18.0), "hard": (18.0, 28.0)},
        source="DIN 508 slot-width series",
        refine=True,
        coverage=[8.0, 10.0, 12.0, 14.0, 18.0, 22.0, 28.0],
    ),
    "thread_d": dict(
        desc="thread diameter (DIN 508 pairing with the slot width)",
        unit="mm",
        range={"easy": (6.0, 24.0), "medium": (6.0, 24.0), "hard": (6.0, 24.0)},
        source="DIN 508 slot-to-thread pairing (catalog row)",
        refine=True,
    ),
    "base_w": dict(
        desc="wide base width (sits under the slot lips)",
        unit="mm",
        range={"easy": (12.0, 50.0), "medium": (12.0, 50.0), "hard": (12.0, 50.0)},
        source="proportion (~ 1.55-1.75 a)",
        refine=True,
    ),
    "neck_w": dict(
        desc="neck width B1 = slot − 0.4 (the slot-fit width; passes through the opening)",
        unit="mm",
        range={"easy": (7.0, 28.0), "medium": (7.0, 28.0), "hard": (7.0, 28.0)},
        source="DIN 508 B1 = a − 0.4 (exact, row-locked to the slot)",
        refine=True,
    ),
    "base_h": dict(
        desc="base height",
        unit="mm",
        range={"easy": (3.5, 17.0), "medium": (3.5, 17.0), "hard": (3.5, 17.0)},
        source="proportion (~ 0.45-0.6 a)",
        refine=True,
    ),
    "neck_h": dict(
        desc="neck height",
        unit="mm",
        range={"easy": (2.3, 13.0), "medium": (2.3, 13.0), "hard": (2.3, 13.0)},
        source="proportion (~ 0.3-0.45 a)",
        refine=True,
    ),
    "length": dict(
        desc="nut length along the slot",
        unit="mm",
        range={"easy": (12.0, 73.0), "medium": (12.0, 73.0), "hard": (12.0, 73.0)},
        source="proportion (~ 1.6-2.6 a)",
        refine=True,
    ),
    "chamfer": dict(
        desc="lead-in chamfer on the base underside (0 = none; hard only)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (0.0, 0.0), "hard": (0.0, 3.5)},
        source="assembly lead-in (deburr convention)",
        feature=True,
        refine=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    a = int(round(p["slot_w"]))
    if a not in _THREAD:
        bad.append("slot_w is not a DIN 508 slot width")
    elif abs(p["thread_d"] - _THREAD[a]) > 1e-6:
        bad.append("thread_d does not match the DIN 508 pairing for this slot")
    # neck is the DIN 508 slot-fit width B1 = a − 0.4
    elif abs(p["neck_w"] - (a - 0.4)) > 1e-6:
        bad.append("neck_w is not the DIN 508 B1 = slot − 0.4")
    # the defining T: base wider than neck, neck wider than the thread
    if p["base_w"] <= p["neck_w"] + 2.0:
        bad.append("base_w <= neck_w + 2: no T-step to catch the slot lips")
    if p["neck_w"] < p["thread_d"] + 1.5:
        bad.append("neck_w < thread_d + 1.5: no wall left around the thread")
    if p["base_w"] < p["thread_d"] + 4.0:
        bad.append("base_w < thread_d + 4: base too small for the thread")
    if p["base_h"] < 2.0 or p["neck_h"] < 2.0:
        bad.append("base_h/neck_h < 2 mm: a section too thin to machine")
    # the nut runs along the slot: longer than it is wide (won't cock in the slot)
    if p["length"] < p["base_w"]:
        bad.append("length < base_w: nut would cock in the slot")
    if p["chamfer"] and p["chamfer"] > 0.4 * p["base_h"]:
        bad.append("chamfer > 0.4*base_h: chamfer eats the base")
    return bad


# ── refine — slot width drives thread + every proportion ─────────────────────
def refine(p: dict, difficulty: str, rng) -> None:
    a = _SLOTS[difficulty][int(rng.integers(len(_SLOTS[difficulty])))]
    p["slot_w"] = float(a)
    p["thread_d"] = _THREAD[a]
    p["neck_w"] = round(a - 0.4, 1)                 # DIN 508 B1 (slot-fit width)
    p["base_w"] = round(a * float(rng.uniform(1.55, 1.75)), 1)
    p["base_h"] = round(a * float(rng.uniform(0.45, 0.60)), 1)
    p["neck_h"] = round(a * float(rng.uniform(0.30, 0.45)), 1)
    p["length"] = round(max(p["base_w"] + 2.0, a * float(rng.uniform(1.6, 2.6))), 1)
    p["chamfer"] = round(a * 0.10, 1) if difficulty == "hard" else 0.0
