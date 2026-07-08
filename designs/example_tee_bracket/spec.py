"""example_tee_bracket — the benchmark generator spec.

PARAM_SPEC declares every parameter (unit, per-difficulty range, source);
check() is the engineering truth reviewers audit. The framework samples from
this declaration (bench2.sampling) — there is no hand-written generator loop.
n_holes uses `choices` (a discrete 0/2/4 set per difficulty); every other
parameter is a plain range the sampler draws uniformly, so this family needs no
refine() hook.
"""

from part import _hole_layout


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "length": dict(
        desc="overall bracket length (X)",
        unit="mm",
        range={"easy": (40.0, 80.0), "medium": (40.0, 120.0), "hard": (30.0, 160.0)},
        source="proportion (typical machine-bracket envelope)",
        askable=True,
    ),
    "flange_w": dict(
        desc="flange (base plate) width (Y)",
        unit="mm",
        range={"easy": (24.0, 40.0), "medium": (20.0, 50.0), "hard": (16.0, 60.0)},
        source="proportion",
        askable=True,
    ),
    "flange_t": dict(
        desc="flange thickness (Z)",
        unit="mm",
        range={"easy": (4.0, 8.0), "medium": (3.0, 10.0), "hard": (3.0, 12.0)},
        source="proportion (plate stock gauges)",
        askable=True,
    ),
    "web_h": dict(
        desc="web (upright plate) height above the flange",
        unit="mm",
        range={"easy": (20.0, 40.0), "medium": (16.0, 60.0), "hard": (12.0, 80.0)},
        source="proportion",
        askable=True,
    ),
    "web_t": dict(
        desc="web thickness (Y)",
        unit="mm",
        range={"easy": (4.0, 8.0), "medium": (3.0, 10.0), "hard": (3.0, 12.0)},
        source="proportion (plate stock gauges)",
    ),
    "n_holes": dict(
        desc="bolt holes through the flange (0 / 2 / 4, symmetric about the web)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 2), "hard": (2, 4)},
        choices={"easy": [0], "medium": [0, 2], "hard": [2, 4]},
        source="mounting convention (pairs, symmetric)",
        askable=True,
        feature=True,  # toggles a feature -> drives add/remove edit derivation
    ),
    "hole_d": dict(
        desc="bolt hole diameter",
        unit="mm",
        range={"easy": (4.0, 6.0), "medium": (4.0, 9.0), "hard": (4.0, 11.0)},
        source="M4–M10 clearance holes",
        askable=True,
    ),
    "chamfer_c": dict(
        desc="chamfer on the web top edges (0 = none; hard only)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (0.0, 0.0), "hard": (0.6, 1.5)},
        source="deburr/handling chamfer convention",
        feature=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    # plates must stay plate-like, not blocks (structural-plate convention)
    if p["web_t"] > p["web_h"] / 4.0:
        bad.append("web_t > web_h/4: web must be plate-like")
    if p["flange_t"] > p["flange_w"] / 4.0:
        bad.append("flange_t > flange_w/4: flange must be plate-like")
    # a very tall web on a narrow base tips over / can't be welded square
    if p["web_h"] > 3.0 * p["flange_w"]:
        bad.append("web_h > 3*flange_w: unstable proportion")
    if p["n_holes"]:
        y_off, x_off = _hole_layout(p["flange_w"], p["web_t"], p["length"], p["hole_d"])
        # bolt-hole edge distance >= 1.5 d (machinery-handbook tear-out rule)
        if p["flange_w"] / 2.0 - y_off < 1.5 * p["hole_d"]:
            bad.append("hole center < 1.5d from flange edge: tear-out risk")
        # drill clearance between hole wall and the web face
        if y_off - p["web_t"] / 2.0 - p["hole_d"] / 2.0 < 1.0:
            bad.append("hole wall < 1 mm from web face: drill clearance")
        if p["n_holes"] == 4:
            # end distance >= 1.5 d and hole-pair spacing >= 3 d (bolt-pattern rule)
            if x_off < 1.5 * p["hole_d"]:
                bad.append("4-hole: end distance < 1.5d")
            if 2.0 * x_off < 3.0 * p["hole_d"]:
                bad.append("4-hole: hole spacing < 3d")
    # a chamfer that consumes half the plate thickness is no longer a chamfer
    if p["chamfer_c"] and p["chamfer_c"] >= p["web_t"] / 2.0:
        bad.append("chamfer_c >= web_t/2: chamfer would gut the web edge")
    return bad
