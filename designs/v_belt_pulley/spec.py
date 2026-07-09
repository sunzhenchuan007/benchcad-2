"""v_belt_pulley — the benchmark generator spec.

The outer diameter and groove count are drawn by the framework; refine() picks
a belt section (SPZ/SPA/SPB — sets the groove top width, depth, pitch e and the
edge distance E), rejects a section too big for the drawn diameter, sets the ISO
rim width and groove angle, and couples the bore and hub. Groove count + hub grow
with difficulty.

Anchor: ISO 4183 (narrow V-belt pulleys, SPZ/SPA/SPB) — groove datum widths,
depths, pitch `e`, edge distance E, the minimum datum diameter per section, and
the groove angle (34 deg, stepping to 38 deg above a per-section datum diameter).
The rim width is the ISO relation B = 2E + (N-1)e (exact), not a proportion.
"""

import math

from bench2 import Resample

# ISO 4183 sections:
#   (groove_top_w lg, groove_depth, groove_pitch e = E1, edge distance E,
#    datum-diameter step above which the groove angle is 38 deg), mm
_SECTIONS = [
    (9.7, 9.0, 12.0, 8.0, 80.0),     # SPZ
    (12.7, 11.0, 15.0, 10.0, 118.0),  # SPA
    (16.3, 14.0, 19.0, 12.5, 190.0),  # SPB
]
# ISO 4183 minimum (datum) diameter per section, by pitch, mm
_MIN_DIA = {12.0: 63.0, 15.0: 80.0, 19.0: 112.0}


def _section(top_w, depth, pitch):
    for s in _SECTIONS:
        if (s[0], s[1], s[2]) == (top_w, depth, pitch):
            return s
    return None


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "outer_d": dict(
        desc="pulley outside diameter",
        unit="mm",
        range={"easy": (63.0, 120.0), "medium": (80.0, 200.0), "hard": (112.0, 280.0)},
        source="ISO 4183 datum-diameter range (narrow V sections)",
        askable=True,
    ),
    "n_grooves": dict(
        desc="number of V-grooves",
        unit="",
        range={"easy": (1, 2), "medium": (2, 4), "hard": (3, 6)},
        source="multi-groove drive practice",
        askable=True,
        integer=True,
    ),
    "groove_pitch": dict(
        desc="groove pitch e (ISO 4183 section spacing)",
        unit="mm",
        range={"easy": (12.0, 19.0), "medium": (12.0, 19.0), "hard": (12.0, 19.0)},
        source="ISO 4183 section pitch (SPZ 12 / SPA 15 / SPB 19)",
        askable=True,
        refine=True,
        coverage=[12.0, 15.0, 19.0],
    ),
    "groove_top_w": dict(
        desc="groove top width (section datum)",
        unit="mm",
        range={"easy": (9.0, 17.0), "medium": (9.0, 17.0), "hard": (9.0, 17.0)},
        source="ISO 4183 section (row-locked to pitch)",
        askable=True,
        refine=True,
    ),
    "groove_depth": dict(
        desc="groove depth below the outside diameter",
        unit="mm",
        range={"easy": (8.0, 15.0), "medium": (8.0, 15.0), "hard": (8.0, 15.0)},
        source="ISO 4183 section (row-locked to pitch)",
        askable=True,
        refine=True,
    ),
    "groove_angle": dict(
        desc="V-groove included angle (ISO 4183: 34 deg, 38 deg on large datum Ø)",
        unit="deg",
        range={"easy": (34.0, 38.0), "medium": (34.0, 38.0), "hard": (34.0, 38.0)},
        source="ISO 4183 groove angle (34/38 deg by datum diameter)",
        askable=True,
        refine=True,
    ),
    "width": dict(
        desc="pulley rim width B = 2E + (N-1)e (ISO 4183)",
        unit="mm",
        range={"easy": (16.0, 200.0), "medium": (16.0, 200.0), "hard": (16.0, 200.0)},
        source="ISO 4183 rim width B = 2E + (N-1)e (row-locked)",
        askable=True,
        refine=True,
    ),
    "bore_d": dict(
        desc="center bore diameter",
        unit="mm",
        range={"easy": (8.0, 40.0), "medium": (8.0, 60.0), "hard": (10.0, 80.0)},
        source="shaft-fit convention; bounded by the groove-root rim (refine + check)",
        askable=True,
        refine=True,
    ),
    "hub_d": dict(
        desc="hub outside diameter (0 = plain disc)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (18.0, 120.0), "hard": (18.0, 160.0)},
        source="catalog hub proportion",
        feature=True,
        refine=True,
    ),
    "hub_len": dict(
        desc="hub protrusion beyond the rim",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (8.0, 40.0), "hard": (8.0, 40.0)},
        source="proportion (~ 0.8-1.5 x pitch)",
        askable=True,
        refine=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    sec = _section(p["groove_top_w"], p["groove_depth"], p["groove_pitch"])
    if sec is None:
        bad.append("(groove_top_w, groove_depth, groove_pitch) is not an ISO 4183 section")
    # section not larger than the pulley can carry (min datum Ø)
    if p["groove_pitch"] in _MIN_DIA and p["outer_d"] < _MIN_DIA[p["groove_pitch"]]:
        bad.append("outer_d below the ISO 4183 minimum datum diameter for this section")
    if p["n_grooves"] < 1:
        bad.append("n_grooves < 1")
    # ISO rim width B = 2E + (N-1)e (exact, not a proportion)
    if sec is not None:
        exp_w = round(2.0 * sec[3] + (p["n_grooves"] - 1) * p["groove_pitch"], 1)
        if abs(p["width"] - exp_w) > 0.11:
            bad.append("width != 2E + (N-1)e: not the ISO 4183 rim width")
        # groove angle follows the ISO 34/38 datum-diameter step
        exp_ang = 34.0 if p["outer_d"] < sec[4] else 38.0
        if abs(p["groove_angle"] - exp_ang) > 1e-6:
            bad.append("groove_angle does not follow the ISO 34/38 datum-diameter step")
    # the groove is a real V-belt groove: 34/38 deg flanks + a flat bottom (not a point)
    if p["groove_angle"] not in (34.0, 38.0):
        bad.append("groove_angle is not the ISO 34 or 38 deg")
    half_bot = p["groove_top_w"] / 2.0 - p["groove_depth"] * math.tan(math.radians(p["groove_angle"] / 2.0))
    if half_bot <= 0.5:
        bad.append("groove bottoms out to a point: no trapezoidal flat (C <= 1 mm)")
    # grooves fit across the width, with a flange each side
    if p["width"] < (p["n_grooves"] - 1) * p["groove_pitch"] + p["groove_top_w"]:
        bad.append("width too small for the groove set")
    # a rim of material must remain between the groove roots and the bore
    root_r = p["outer_d"] / 2.0 - p["groove_depth"]
    if root_r - p["bore_d"] / 2.0 < 4.0:
        bad.append("< 4 mm rim between the groove root and the bore")
    if p["bore_d"] < 6.0:
        bad.append("bore_d < 6 mm: below practical shaft sizes")
    if p["hub_d"]:
        if p["hub_d"] < 1.55 * p["bore_d"]:
            bad.append("hub_d < 1.55*bore_d: hub wall too thin")
        if p["hub_d"] > 2.0 * root_r:
            bad.append("hub_d larger than the groove-root rim")
    return bad


# ── refine — pick a section that fits the diameter, then couple the rest ──────
def refine(p: dict, difficulty: str, rng) -> None:
    top_w, depth, pitch, edge, ang_step = _SECTIONS[int(rng.integers(len(_SECTIONS)))]
    if p["outer_d"] < _MIN_DIA[pitch]:
        raise Resample  # this section is too big for the drawn diameter
    p["groove_top_w"], p["groove_depth"], p["groove_pitch"] = top_w, depth, pitch

    # ISO groove angle: 34 deg, stepping to 38 deg above the section's datum step
    p["groove_angle"] = 34.0 if p["outer_d"] < ang_step else 38.0

    # ISO 4183 rim width B = 2E + (N-1)e (exact)
    n = p["n_grooves"]
    p["width"] = round(2.0 * edge + (n - 1) * pitch, 1)

    root_r = p["outer_d"] / 2.0 - depth
    b_lo, b_hi = PARAM_SPEC["bore_d"]["range"][difficulty]
    hi_b = min(0.9 * root_r, b_hi)
    lo_b = max(6.0, b_lo, 0.25 * root_r)
    if lo_b >= hi_b:
        raise Resample
    p["bore_d"] = round(float(rng.uniform(lo_b, hi_b)), 1)

    if difficulty in ("medium", "hard"):
        h_lo, h_hi = PARAM_SPEC["hub_d"]["range"][difficulty]
        hub_lo = max(1.7 * p["bore_d"], h_lo)
        hub_hi = min(1.8 * root_r, h_hi)
        if hub_lo >= hub_hi:
            raise Resample
        p["hub_d"] = round(float(rng.uniform(hub_lo, hub_hi)), 1)
        p["hub_len"] = round(pitch * float(rng.uniform(0.8, 1.5)), 1)
    else:
        p["hub_d"] = 0.0
        p["hub_len"] = 0.0
