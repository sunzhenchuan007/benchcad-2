"""spur_gear_2 — the benchmark generator spec.

Table-driven module (ISO 54 preferred series) + catalog tooth count, with the
bore and hub coupled to the computed root circle. The framework samples from
PARAM_SPEC; refine() draws the discrete module and fills the coupled bore/hub.

Style follows the tooth count, not the difficulty: the norelem 22400 catalog is
Style A (hub) up to z = 30 and Style B (plain disc) from z = 32 — so a hub is
present iff z <= 30, and n_teeth carries coverage across the 30/32 boundary.

Anchor: norelem 22400 (spur gears in steel, milled straight teeth, 20°) prints
the module series and pressure angle; the ISO 53 involute profile itself is a
convention (geomlib.involute_gear_profile). z = 12 is the catalog minimum; a 20°
full-depth tooth undercuts below z ~= 17, so the low-z profiles bridge the root
(an approximation — see NOTES.md).

Tooth geometry (ISO 53, 20°): dp = m*z, da = m*(z+2), df = m*(z-2.5).
"""

import math  # noqa: F401 — kept for parity with sibling specs / future constraints

from bench2 import Resample
from bench2.geomlib import keyway_dims

# ISO 54 preferred module series (series 1), mm
_MODULES = [1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0]
_Z_STYLE_A_MAX = 30  # hub up to z = 30; plain disc from z = 32 (norelem 22400)


def _circles(module, z):
    """ISO 53 pitch / tip / root diameters."""
    dp = module * z
    da = module * (z + 2.0)
    df = module * (z - 2.5)
    return dp, da, df


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "module": dict(
        desc="gear module m (ISO 54 preferred series; sets tooth size)",
        unit="mm",
        range={"easy": (1.0, 6.0), "medium": (1.0, 6.0), "hard": (1.0, 6.0)},
        source="ISO 54 preferred module series 1",
        askable=True,
        refine=True,
        coverage=[1.0, 1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0],
    ),
    "n_teeth": dict(
        desc="number of teeth z (catalog tooth counts; drives Style A/B)",
        unit="",
        range={"easy": (12, 30), "medium": (20, 45), "hard": (24, 90)},
        choices={
            "easy": [12, 15, 18, 24, 30],
            "medium": [20, 25, 30, 36, 45],
            "hard": [24, 28, 32, 60, 90],
        },
        source="norelem 22400 catalog tooth counts (z >= 12 catalog minimum)",
        askable=True,
        coverage=[12, 30, 32, 90],
    ),
    "face_width": dict(
        desc="gear face width b (tooth length along the axis)",
        unit="mm",
        range={"easy": (6.0, 66.0), "medium": (6.0, 66.0), "hard": (6.0, 66.0)},
        source="machine-design convention b = 6-12 x module",
        askable=True,
        refine=True,
    ),
    "bore_d": dict(
        desc="center bore diameter",
        unit="mm",
        range={"easy": (3.0, 30.0), "medium": (4.0, 45.0), "hard": (5.0, 60.0)},
        source="shaft-fit convention; bounded by the root circle (refine + check)",
        askable=True,
        refine=True,
    ),
    "hub_d": dict(
        desc="hub outside diameter (0 = plain disc / Style B, z >= 32)",
        unit="mm",
        range={"easy": (0.0, 160.0), "medium": (0.0, 160.0), "hard": (0.0, 160.0)},
        source="catalog Style A hub (z <= 30); tied to tooth count, not difficulty",
        feature=True,
        refine=True,
    ),
    "hub_len": dict(
        desc="hub protrusion beyond the gear face",
        unit="mm",
        range={"easy": (0.0, 50.0), "medium": (0.0, 50.0), "hard": (0.0, 50.0)},
        source="proportion (hub length ~ 3-7 x module)",
        askable=True,
        refine=True,
    ),
    "has_keyway": dict(
        desc="DIN 6885A keyway in the bore (1 = yes; hard-tier hub gears)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 0), "hard": (0, 1)},
        source="DIN 6885 Form A key seats (needs a hub)",
        feature=True,
        refine=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    # z = 12 is the catalog minimum; the low-z profiles bridge the root (approx.)
    if p["n_teeth"] < 12:
        bad.append("n_teeth < 12: below the catalog minimum")
    if not any(abs(p["module"] - m) < 1e-6 for m in _MODULES):
        bad.append("module is not an ISO 54 preferred value")
    _, _, df = _circles(p["module"], p["n_teeth"])
    # face width stays in the 5-15 x module band (narrower = fragile, wider = misalign)
    if not (5.0 * p["module"] <= p["face_width"] <= 15.0 * p["module"]):
        bad.append("face_width outside 5-15 x module: not a usual gear proportion")
    if p["bore_d"] > 0.5 * df:
        bad.append("bore_d > 0.5*root_diameter: gear rim too thin")
    if p["bore_d"] < 3.0:
        bad.append("bore_d < 3 mm: below practical shaft sizes")
    # Style follows z: hub iff z <= 30, plain disc from z = 32
    if p["n_teeth"] <= _Z_STYLE_A_MAX and not p["hub_d"]:
        bad.append("z <= 30 is catalog Style A: needs a hub")
    if p["n_teeth"] >= 32 and p["hub_d"]:
        bad.append("z >= 32 is catalog Style B: must be a plain disc (no hub)")
    if p["hub_d"]:
        if p["hub_d"] < 1.55 * p["bore_d"]:
            bad.append("hub_d < 1.55*bore_d: hub wall too thin for a set screw / key")
        if p["hub_d"] > 0.8 * df:
            bad.append("hub_d > 0.8*root_diameter: hub would merge into the tooth root")
        if p["hub_len"] < 2.0 * p["module"] or p["hub_len"] > 8.0 * p["module"]:
            bad.append("hub_len outside 2-8 x module: not a catalog proportion")
    if p["has_keyway"]:
        kw, _ = keyway_dims(p["bore_d"])
        if kw >= 0.5 * p["bore_d"]:
            bad.append("keyway width >= half the bore: DIN 6885 table misapplied")
        if not p["hub_d"]:
            bad.append("keyway without a hub: key seat needs hub material")
    return bad


# ── refine — discrete module draw + z-driven style + bore/hub coupling ───────
def refine(p: dict, difficulty: str, rng) -> None:
    """Fill the coupled parameters after the framework's base draw. Style A/B is
    set by the tooth count (hub iff z <= 30), not the difficulty."""
    m = _MODULES[int(rng.integers(len(_MODULES)))]
    p["module"] = m
    z = p["n_teeth"]
    _, _, df = _circles(m, z)

    # face width b = 6-11 x module, clamped to the declared range
    fw_lo, fw_hi = PARAM_SPEC["face_width"]["range"][difficulty]
    p["face_width"] = round(min(max(m * float(rng.uniform(6.0, 11.0)), fw_lo), fw_hi), 1)

    # bore: rim proportion (0.2-0.42 df) clamped to the declared range
    b_lo, b_hi = PARAM_SPEC["bore_d"]["range"][difficulty]
    hi_b = min(0.42 * df, b_hi)
    lo_b = max(3.0, b_lo, 0.2 * df)
    if lo_b >= hi_b:
        lo_b = 0.6 * hi_b
    p["bore_d"] = round(float(rng.uniform(lo_b, hi_b)), 1)

    # Style A hub iff z <= 30 (sized off the bore and root circle); else plain disc
    if z <= _Z_STYLE_A_MAX:
        hub_lo = 1.7 * p["bore_d"]
        hub_hi = min(0.78 * df, 160.0)
        if hub_lo >= hub_hi:
            raise Resample  # no hub fits this module/tooth draw — resample
        p["hub_d"] = round(float(rng.uniform(hub_lo, hub_hi)), 1)
        p["hub_len"] = round(m * float(rng.uniform(3.0, 7.0)), 1)
        # a keyway appears on the hard tier's hub gears
        p["has_keyway"] = 1 if difficulty == "hard" else 0
    else:
        p["hub_d"] = 0.0
        p["hub_len"] = 0.0
        p["has_keyway"] = 0
