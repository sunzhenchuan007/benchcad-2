"""flanged_bushing — the benchmark generator spec.

The bore (a shaft size) is drawn by the framework; the wall, length and collar
are proportional to it (refine), and a lead-in chamfer appears on the hard tier.

Anchor: norelem 23761 (plain bearing, sintered bronze, with collar) — 61
articles over the bore series; the sheet cites no ISO/DIN number, so the wall /
length / collar proportions here are declared as `proportion` (ISO 3547 /
DIN 1850 give the same wrapped-bushing style).
"""

from bench2 import Resample  # noqa: F401 — refine may reject infeasible draws


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "bore_d": dict(
        desc="bearing bore = shaft diameter d",
        unit="mm",
        range={"easy": (6, 20), "medium": (10, 40), "hard": (16, 60)},
        source="catalog bore series (shaft sizes)",
        integer=True,
    ),
    "wall_t": dict(
        desc="sleeve wall thickness s",
        unit="mm",
        range={"easy": (1.5, 12.0), "medium": (1.5, 12.0), "hard": (1.5, 12.0)},
        source="proportion (s ~ 0.10-0.18 d, wrapped-bushing convention)",
        refine=True,
    ),
    "length": dict(
        desc="sleeve length L",
        unit="mm",
        range={"easy": (3.5, 100.0), "medium": (3.5, 100.0), "hard": (3.5, 100.0)},
        source="proportion (L/d = 0.6-1.6, plain-bearing convention)",
        refine=True,
    ),
    "collar_t": dict(
        desc="collar (flange) thickness",
        unit="mm",
        range={"easy": (2.0, 24.0), "medium": (2.0, 24.0), "hard": (2.0, 24.0)},
        source="proportion (~ 1-2 x wall)",
        refine=True,
    ),
    "collar_over": dict(
        desc="collar radial overhang beyond the sleeve OD",
        unit="mm",
        range={"easy": (1.5, 22.0), "medium": (1.5, 22.0), "hard": (1.5, 22.0)},
        source="proportion (~ 0.9-1.8 x wall)",
        refine=True,
    ),
    "lead_chamfer": dict(
        desc="lead-in chamfer on the open rim (0 = none; hard only)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (0.0, 0.0), "hard": (0.0, 5.0)},
        source="assembly lead-in (deburr convention)",
        feature=True,
        refine=True,
    ),
    "oil_hole_d": dict(
        desc="radial lubrication cross-hole diameter (0 = none; medium/hard)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (0.0, 14.0), "hard": (0.0, 14.0)},
        source="lubrication feed hole (plain-bearing convention)",
        feature=True,
        refine=True,
    ),
    "oil_groove": dict(
        desc="internal oil-groove depth in the bore (0 = none; hard only)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (0.0, 0.0), "hard": (0.0, 5.0)},
        source="lubrication distribution groove (proportion)",
        feature=True,
        refine=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    # a bushing is thin-walled relative to the bore, not a solid slug
    if p["wall_t"] < 1.0:
        bad.append("wall_t < 1 mm: below a practical sleeve wall")
    if p["wall_t"] > 0.4 * p["bore_d"]:
        bad.append("wall_t > 0.4*bore: too thick to be a bushing (it's a bar)")
    # L/d range for a plain sleeve bearing (edge-loading vs alignment)
    if not (0.4 * p["bore_d"] <= p["length"] <= 2.2 * p["bore_d"]):
        bad.append("length/bore outside 0.4-2.2: not a usual sleeve-bearing ratio")
    if p["collar_t"] < 1.5:
        bad.append("collar_t < 1.5 mm: collar too thin to seat")
    if p["collar_t"] > p["length"]:
        bad.append("collar_t > length: collar deeper than the sleeve")
    if p["collar_over"] < 1.0:
        bad.append("collar_over < 1 mm: no usable flange")
    if p["lead_chamfer"] and p["lead_chamfer"] > 0.5 * p["wall_t"]:
        bad.append("lead_chamfer > 0.5*wall: chamfer would break through the wall")
    # lubrication: the cross-hole sits in the sleeve wall above the collar
    sleeve = p["length"] - p["collar_t"]
    if p["oil_hole_d"]:
        if p["oil_hole_d"] < 1.5:
            bad.append("oil_hole_d < 1.5 mm: below a drillable feed hole")
        if p["oil_hole_d"] > 0.8 * sleeve:
            bad.append("oil_hole_d too big to fit the sleeve length above the collar")
    if p["oil_groove"]:
        if p["oil_groove"] > 0.6 * p["wall_t"]:
            bad.append("oil_groove > 0.6*wall: groove would breach the sleeve wall")
        if not p["oil_hole_d"]:
            bad.append("oil_groove without an oil_hole: the groove has no lube feed")
    return bad


# ── refine — bore drives the proportional sleeve / collar / chamfer ──────────
def refine(p: dict, difficulty: str, rng) -> None:
    d = p["bore_d"]
    p["wall_t"] = round(max(1.5, d * float(rng.uniform(0.10, 0.18))), 1)
    p["length"] = round(d * float(rng.uniform(0.6, 1.6)), 1)
    p["collar_t"] = round(max(2.0, p["wall_t"] * float(rng.uniform(1.0, 2.0))), 1)
    p["collar_over"] = round(max(1.5, p["wall_t"] * float(rng.uniform(0.9, 1.8))), 1)
    p["lead_chamfer"] = (
        round(p["wall_t"] * float(rng.uniform(0.2, 0.4)), 1) if difficulty == "hard" else 0.0
    )
    # lubrication cross-hole (medium/hard) + oil groove (hard)
    if difficulty in ("medium", "hard"):
        p["oil_hole_d"] = round(max(1.5, min(0.3 * d, 1.2 * p["wall_t"])), 1)
    else:
        p["oil_hole_d"] = 0.0
    p["oil_groove"] = round(max(0.5, 0.35 * p["wall_t"]), 1) if difficulty == "hard" else 0.0
