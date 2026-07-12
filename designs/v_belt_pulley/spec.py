"""v_belt_pulley — the benchmark generator spec (norelem 22070 / DIN 2211, Form J).

Form J = a multi-groove (N = 2/3) taper-bush sheave: grooved rim + a narrower
solid hub boss centred in it + a conical taper bore (no keyway). Params carry
their norelem/DIN drawing symbol (see part.py glossary): outer_dia_D (D),
rim_width_B (B), hub_dia_D5 (D5), hub_width_L (L), bore_dia_d1, with L + L1 = B.

Anchor: norelem 22070 (DIN 2211) Form J rows; ISO 4183 groove sections; from the
real table D5/D ~= 0.68 and the hub width L ~= 0.28*D (the taper-bush length),
so L1 = B - L grows with the groove count N.
"""

import math

from bench2 import Resample

# ISO 4183 sections: (groove_top lg, groove_depth T, groove_pitch e = E1,
#                     edge distance E, datum-Ø step above which angle = 38 deg)
_SECTIONS = [
    (9.7, 9.0, 12.0, 8.0, 80.0),      # SPZ
    (12.7, 11.0, 15.0, 10.0, 118.0),  # SPA
    (16.3, 14.0, 19.0, 12.5, 190.0),  # SPB
]
_MIN_DIA = {12.0: 63.0, 15.0: 80.0, 19.0: 112.0}


def _section(lg, depth, pitch):
    for s in _SECTIONS:
        if (s[0], s[1], s[2]) == (lg, depth, pitch):
            return s
    return None


PARAM_SPEC = {
    "outer_dia_D": dict(
        desc="pulley outside diameter D",
        unit="mm",
        range={"easy": (63.0, 90.0), "medium": (80.0, 140.0), "hard": (112.0, 224.0)},
        source="norelem 22070 Form J datum-diameter range",
        askable=True,
    ),
    "rim_width_B": dict(
        desc="rim width B = 2E + (N-1)e (ISO 4183)", unit="mm",
        range={"easy": (16.0, 200.0), "medium": (16.0, 200.0), "hard": (16.0, 200.0)},
        source="ISO 4183 rim width B = 2E + (N-1)e (row-locked)", askable=True, refine=True,
    ),
    "n_grooves": dict(
        desc="number of V-grooves N (Form J: 2 or 3)", unit="",
        range={"easy": (2, 2), "medium": (2, 3), "hard": (2, 3)},
        source="norelem 22070 Form J (multi-groove)", askable=True, integer=True,
    ),
    "groove_pitch_e": dict(
        desc="groove pitch e (ISO 4183 section spacing)", unit="mm",
        range={"easy": (12.0, 19.0), "medium": (12.0, 19.0), "hard": (12.0, 19.0)},
        source="ISO 4183 section pitch (SPZ 12 / SPA 15 / SPB 19)",
        askable=True, refine=True, coverage=[12.0, 15.0, 19.0],
    ),
    "groove_top_lg": dict(
        desc="groove top width lg (section datum)", unit="mm",
        range={"easy": (9.0, 17.0), "medium": (9.0, 17.0), "hard": (9.0, 17.0)},
        source="ISO 4183 section (row-locked to pitch)", askable=True, refine=True,
    ),
    "groove_depth_T": dict(
        desc="groove depth T below the outside diameter", unit="mm",
        range={"easy": (8.0, 15.0), "medium": (8.0, 15.0), "hard": (8.0, 15.0)},
        source="ISO 4183 section (row-locked to pitch)", askable=True, refine=True,
    ),
    "groove_angle_a": dict(
        desc="V-groove included angle α (ISO 4183: 34 deg, 38 deg on large datum Ø)",
        unit="deg",
        range={"easy": (34.0, 38.0), "medium": (34.0, 38.0), "hard": (34.0, 38.0)},
        source="ISO 4183 groove angle (34/38 deg by datum diameter)",
        askable=True, refine=True,
    ),
    "hub_dia_D5": dict(
        desc="hub-boss diameter D5 (Form J: ~0.68*D)", unit="mm",
        range={"easy": (34.0, 62.0), "medium": (48.0, 100.0), "hard": (70.0, 170.0)},
        source="norelem 22070 Form J D5 (D5/D ~ 0.56-0.81, mean 0.68)",
        askable=True, refine=True,
    ),
    "hub_width_L": dict(
        desc="hub-boss width L (taper-bush length; centred in B, so L1 = B-L)", unit="mm",
        range={"easy": (16.0, 40.0), "medium": (18.0, 45.0), "hard": (20.0, 55.0)},
        source="norelem 22070 Form J L (~0.28*D, the taper-bush length)",
        askable=True, refine=True,
    ),
    "shaft_bore_D2": dict(
        desc="taper-bush SHAFT bore D2; the pulley seat front Ø = 2*D2 (< back 0.8*D5)", unit="mm",
        range={"easy": (14.0, 42.0), "medium": (18.0, 60.0), "hard": (24.0, 90.0)},
        source="taper clamping bush seat (~0.6*D5); bounded by the hub wall",
        askable=True, refine=True,
    ),
}


def check(p: dict) -> list[str]:
    bad = []
    sec = _section(p["groove_top_lg"], p["groove_depth_T"], p["groove_pitch_e"])
    if sec is None:
        bad.append("(groove_top_lg, groove_depth_T, groove_pitch_e) is not an ISO 4183 section")
    if p["groove_pitch_e"] in _MIN_DIA and p["outer_dia_D"] < _MIN_DIA[p["groove_pitch_e"]]:
        bad.append("outer_dia_D below the ISO 4183 minimum datum diameter for this section")
    if p["n_grooves"] < 2:
        bad.append("Form J is multi-groove: n_grooves must be >= 2")
    if sec is not None:
        exp_B = round(p["n_grooves"] * p["groove_pitch_e"], 1)
        if abs(p["rim_width_B"] - exp_B) > 0.11:
            bad.append("rim_width_B != N*e: edges are not half-teeth")
        exp_a = 34.0 if p["outer_dia_D"] < sec[4] else 38.0
        if abs(p["groove_angle_a"] - exp_a) > 1e-6:
            bad.append("groove_angle_a does not follow the ISO 34/38 datum-diameter step")
    if p["groove_angle_a"] not in (34.0, 38.0):
        bad.append("groove_angle_a is not the ISO 34 or 38 deg")
    half_bot = p["groove_top_lg"] / 2.0 - p["groove_depth_T"] * math.tan(math.radians(p["groove_angle_a"] / 2.0))
    if half_bot <= 0.5:
        bad.append("groove bottoms out to a point: no trapezoidal flat")
    root_r = p["outer_dia_D"] / 2.0 - p["groove_depth_T"]
    # the hub boss is narrower than the rim (L < B, so L1 = B - L > 0) and fits the rim
    if p["hub_width_L"] >= p["rim_width_B"]:
        bad.append("hub_width_L >= rim_width_B: no rim overhang (L1 = B - L must be > 0)")
    if p["hub_dia_D5"] > 2.0 * root_r:
        bad.append("hub_dia_D5 larger than the groove-root rim")
    if p["hub_dia_D5"] <= p["shaft_bore_D2"] + 6.0:
        bad.append("hub_dia_D5 too close to the bore: no hub wall for the taper bush")
    if p["shaft_bore_D2"] < 10.0:
        bad.append("bore_dia_d1 < 10 mm: below practical taper-bush sizes")
    if root_r - p["shaft_bore_D2"] / 2.0 < 4.0:
        bad.append("< 4 mm rim between the groove root and the bore")
    return bad


def refine(p: dict, difficulty: str, rng) -> None:
    lg, depth, pitch, edge, ang_step = _SECTIONS[int(rng.integers(len(_SECTIONS)))]
    if p["outer_dia_D"] < _MIN_DIA[pitch]:
        raise Resample
    p["groove_top_lg"], p["groove_depth_T"], p["groove_pitch_e"] = lg, depth, pitch
    p["groove_angle_a"] = 34.0 if p["outer_dia_D"] < ang_step else 38.0

    n = p["n_grooves"]
    # rim width B = N*e → the first groove sits at e/2 from each edge, so the two
    # rim edges are HALF teeth and the N-1 lands between grooves are full teeth
    p["rim_width_B"] = round(n * pitch, 1)

    root_r = p["outer_dia_D"] / 2.0 - depth
    # hub boss D5 ~ 0.68*D, clamped below the groove-root rim
    p["hub_dia_D5"] = round(min(0.68 * p["outer_dia_D"] * float(rng.uniform(0.94, 1.06)),
                                1.9 * root_r), 1)
    # hub width L ~ the taper-bush length (~0.28*D), kept < B so the rim overhangs (L1 > 0)
    p["hub_width_L"] = round(min(0.28 * p["outer_dia_D"], 0.85 * p["rim_width_B"]), 1)

    # conical taper-bush bore ~ 0.6*D5, leaving a hub wall and a rim to the groove root
    bore = 0.3 * p["hub_dia_D5"] * float(rng.uniform(0.9, 1.1))   # D2; 2*D2 (~0.6*D5) < back 0.8*D5 → frustum
    hi_b = min(bore, p["hub_dia_D5"] - 6.0, 2.0 * (root_r - 4.0))
    lo_b = 10.0
    if hi_b <= lo_b:
        raise Resample
    p["shaft_bore_D2"] = round(float(rng.uniform(max(lo_b, 0.85 * hi_b), hi_b)), 1)
