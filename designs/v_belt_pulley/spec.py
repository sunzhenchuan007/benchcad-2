"""v_belt_pulley — the benchmark generator spec (norelem 22070 / DIN 2211, Form J).

Form J = a **multi-groove** narrow-V sheave (N = 2 or 3) for a **taper clamping
bush**: grooved rim + one-sided hub boss (D5) + a conical taper bore (no keyway).
The framework draws the outside diameter and groove count; refine() picks the ISO
4183 belt section (SPZ/SPA/SPB), sets the ISO rim width B = 2E + (N-1)e and the
34/38 deg groove angle, then couples the taper-bush bore and the hub boss D5 to
the diameter the way the catalogue does (D5 ≈ 0.68·D).

Anchor: norelem 22070 "V-belt pulleys, grey cast iron for taper clamping bushes"
(DIN 2211) — Form J rows; ISO 4183 groove section constants; D5/D ≈ 0.56-0.81
(mean 0.68) across the real Form J table.
"""

import math

from bench2 import Resample

# ISO 4183 sections: (groove_top_w lg, groove_depth, groove_pitch e = E1,
#                     edge distance E, datum-Ø step above which angle = 38 deg), mm
_SECTIONS = [
    (9.7, 9.0, 12.0, 8.0, 80.0),      # SPZ
    (12.7, 11.0, 15.0, 10.0, 118.0),  # SPA
    (16.3, 14.0, 19.0, 12.5, 190.0),  # SPB
]
_MIN_DIA = {12.0: 63.0, 15.0: 80.0, 19.0: 112.0}   # ISO 4183 min datum Ø per section


def _section(top_w, depth, pitch):
    for s in _SECTIONS:
        if (s[0], s[1], s[2]) == (top_w, depth, pitch):
            return s
    return None


PARAM_SPEC = {
    "outer_d": dict(
        desc="pulley outside diameter D",
        unit="mm",
        range={"easy": (63.0, 90.0), "medium": (80.0, 140.0), "hard": (112.0, 224.0)},
        source="norelem 22070 Form J datum-diameter range",
        askable=True,
    ),
    "n_grooves": dict(
        desc="number of V-grooves (Form J: 2 or 3)",
        unit="",
        range={"easy": (2, 2), "medium": (2, 3), "hard": (2, 3)},
        source="norelem 22070 Form J (multi-groove)",
        askable=True,
        integer=True,
    ),
    "groove_pitch": dict(
        desc="groove pitch e (ISO 4183 section spacing)",
        unit="mm",
        range={"easy": (12.0, 19.0), "medium": (12.0, 19.0), "hard": (12.0, 19.0)},
        source="ISO 4183 section pitch (SPZ 12 / SPA 15 / SPB 19)",
        askable=True, refine=True, coverage=[12.0, 15.0, 19.0],
    ),
    "groove_top_w": dict(
        desc="groove top width (section datum)", unit="mm",
        range={"easy": (9.0, 17.0), "medium": (9.0, 17.0), "hard": (9.0, 17.0)},
        source="ISO 4183 section (row-locked to pitch)", askable=True, refine=True,
    ),
    "groove_depth": dict(
        desc="groove depth below the outside diameter", unit="mm",
        range={"easy": (8.0, 15.0), "medium": (8.0, 15.0), "hard": (8.0, 15.0)},
        source="ISO 4183 section (row-locked to pitch)", askable=True, refine=True,
    ),
    "groove_angle": dict(
        desc="V-groove included angle (ISO 4183: 34 deg, 38 deg on large datum Ø)",
        unit="deg",
        range={"easy": (34.0, 38.0), "medium": (34.0, 38.0), "hard": (34.0, 38.0)},
        source="ISO 4183 groove angle (34/38 deg by datum diameter)",
        askable=True, refine=True,
    ),
    "width": dict(
        desc="rim width B = 2E + (N-1)e (ISO 4183)", unit="mm",
        range={"easy": (16.0, 200.0), "medium": (16.0, 200.0), "hard": (16.0, 200.0)},
        source="ISO 4183 rim width B = 2E + (N-1)e (row-locked)", askable=True, refine=True,
    ),
    "bore_d": dict(
        desc="conical taper-bush bore diameter (small/front end)", unit="mm",
        range={"easy": (14.0, 42.0), "medium": (18.0, 55.0), "hard": (24.0, 80.0)},
        source="taper clamping bush seat (~0.6*D5); bounded by the groove-root rim",
        askable=True, refine=True,
    ),
    "hub_d": dict(
        desc="hub-boss diameter D5 (Form J: ~0.68*D)", unit="mm",
        range={"easy": (34.0, 62.0), "medium": (48.0, 100.0), "hard": (70.0, 170.0)},
        source="norelem 22070 Form J D5 (D5/D ~ 0.56-0.81, mean 0.68)",
        askable=True, refine=True,
    ),
    "hub_len": dict(
        desc="hub-boss protrusion past the back rim face", unit="mm",
        range={"easy": (8.0, 20.0), "medium": (8.0, 24.0), "hard": (10.0, 30.0)},
        source="proportion (~0.15*D)", askable=True, refine=True,
    ),
}


def check(p: dict) -> list[str]:
    bad = []
    sec = _section(p["groove_top_w"], p["groove_depth"], p["groove_pitch"])
    if sec is None:
        bad.append("(groove_top_w, groove_depth, groove_pitch) is not an ISO 4183 section")
    if p["groove_pitch"] in _MIN_DIA and p["outer_d"] < _MIN_DIA[p["groove_pitch"]]:
        bad.append("outer_d below the ISO 4183 minimum datum diameter for this section")
    if p["n_grooves"] < 2:
        bad.append("Form J is multi-groove: n_grooves must be >= 2")
    if sec is not None:
        exp_w = round(2.0 * sec[3] + (p["n_grooves"] - 1) * p["groove_pitch"], 1)
        if abs(p["width"] - exp_w) > 0.11:
            bad.append("width != 2E + (N-1)e: not the ISO 4183 rim width")
        exp_ang = 34.0 if p["outer_d"] < sec[4] else 38.0
        if abs(p["groove_angle"] - exp_ang) > 1e-6:
            bad.append("groove_angle does not follow the ISO 34/38 datum-diameter step")
    if p["groove_angle"] not in (34.0, 38.0):
        bad.append("groove_angle is not the ISO 34 or 38 deg")
    half_bot = p["groove_top_w"] / 2.0 - p["groove_depth"] * math.tan(math.radians(p["groove_angle"] / 2.0))
    if half_bot <= 0.5:
        bad.append("groove bottoms out to a point: no trapezoidal flat (C <= 1 mm)")
    root_r = p["outer_d"] / 2.0 - p["groove_depth"]
    # Form J always has a hub boss D5, and a taper bore inside it
    if not p["hub_d"]:
        bad.append("Form J always has a hub boss: hub_d must be > 0")
    else:
        if p["hub_d"] <= p["bore_d"] + 6.0:
            bad.append("hub_d too close to the bore: no hub wall for the taper bush")
        if p["hub_d"] > 2.0 * root_r:
            bad.append("hub_d (D5) larger than the groove-root rim")
    if p["bore_d"] < 10.0:
        bad.append("bore_d < 10 mm: below practical taper-bush sizes")
    if root_r - p["bore_d"] / 2.0 < 4.0:
        bad.append("< 4 mm rim between the groove root and the bore")
    return bad


def refine(p: dict, difficulty: str, rng) -> None:
    top_w, depth, pitch, edge, ang_step = _SECTIONS[int(rng.integers(len(_SECTIONS)))]
    if p["outer_d"] < _MIN_DIA[pitch]:
        raise Resample  # this section is too big for the drawn diameter
    p["groove_top_w"], p["groove_depth"], p["groove_pitch"] = top_w, depth, pitch
    p["groove_angle"] = 34.0 if p["outer_d"] < ang_step else 38.0

    n = p["n_grooves"]
    p["width"] = round(2.0 * edge + (n - 1) * pitch, 1)   # ISO 4183 rim width (exact)

    root_r = p["outer_d"] / 2.0 - depth
    # hub boss D5 ~ 0.68*D (catalogue), clamped below the groove-root rim
    hub = 0.68 * p["outer_d"] * float(rng.uniform(0.94, 1.06))
    p["hub_d"] = round(min(hub, 1.9 * root_r), 1)
    p["hub_len"] = round(0.15 * p["outer_d"] * float(rng.uniform(0.85, 1.15)), 1)

    # conical taper-bush bore ~ 0.6*D5, leaving >=4 mm rim to the groove root
    bore = 0.6 * p["hub_d"] * float(rng.uniform(0.9, 1.1))
    hi_b = min(bore, 2.0 * (root_r - 4.0), p["hub_d"] - 6.0)
    lo_b = 10.0
    if hi_b <= lo_b:
        raise Resample
    p["bore_d"] = round(float(rng.uniform(max(lo_b, 0.85 * hi_b), hi_b)), 1)
