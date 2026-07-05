"""example_tee_bracket — REFERENCE design for the BenchCAD 2.0 four-piece interface.

A T-section mounting bracket: a flange plate with a central web standing on it,
optionally bolted through the flange, with a chamfered web top on hard parts.
Chosen as the reference because it exercises every part of the interface in a
part everyone can picture: continuous dimensions, an integer feature (bolt
holes), a hard-only feature (chamfer), and real engineering constraints
(plate proportions, bolt-hole edge distance).

This family is a TEACHING ARTIFACT — it does not enter the released dataset.
"""

# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
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


# ── 2. check — the engineering truth reviewers audit ─────────────────────────
def _hole_layout(p):
    """Shared geometry helpers: lateral hole offset and 4-hole axial offset."""
    y_off = (p["flange_w"] + p["web_t"]) / 4.0  # mid-line of each exposed flange strip
    x_off = p["length"] / 2.0 - max(2.0 * p["hole_d"], 8.0)  # end margin >= 2d (>=8 mm)
    return y_off, x_off


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
        y_off, x_off = _hole_layout(p)
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


# ── 3. sample — rejection-sample within PARAM_SPEC until check passes ────────
def sample(difficulty: str, rng) -> dict:
    for _ in range(200):
        p = {}
        for name in ("length", "flange_w", "flange_t", "web_h", "web_t", "hole_d"):
            lo, hi = PARAM_SPEC[name]["range"][difficulty]
            p[name] = round(float(rng.uniform(lo, hi)), 2)
        # discrete feature draws are explicit, not uniform floats:
        p["n_holes"] = {
            "easy": 0,
            "medium": int(rng.choice([0, 2])),
            "hard": int(rng.choice([2, 4])),
        }[difficulty]
        if difficulty == "hard":
            lo, hi = PARAM_SPEC["chamfer_c"]["range"]["hard"]
            p["chamfer_c"] = round(float(rng.uniform(lo, hi)), 2)
        else:
            p["chamfer_c"] = 0.0
        if not check(p):
            return p
    raise RuntimeError("no valid sample in 200 tries — ranges vs constraints too tight")


# ── 4. build — parameters -> deterministic CadQuery program ──────────────────
def build(p: dict) -> str:
    lines = [
        "import cadquery as cq",
        "",
        f"L, FW, FT = {p['length']:.2f}, {p['flange_w']:.2f}, {p['flange_t']:.2f}",
        f"WT, WH = {p['web_t']:.2f}, {p['web_h']:.2f}",
        "",
        "# flange plate on the XY plane, web standing on its centerline",
        'flange = cq.Workplane("XY").box(L, FW, FT, centered=(True, True, False))',
        'web = cq.Workplane("XY").workplane(offset=FT).box(L, WT, WH, centered=(True, True, False))',
        "result = flange.union(web)",
    ]
    if p["n_holes"]:
        y_off, x_off = _hole_layout(p)
        if p["n_holes"] == 2:
            pts = [(0.0, y_off), (0.0, -y_off)]
        else:
            pts = [(x, y) for x in (x_off, -x_off) for y in (y_off, -y_off)]
        pts_lit = ", ".join(f"({x:.2f}, {y:.2f})" for x, y in pts)
        lines += [
            "",
            f"# {p['n_holes']} bolt holes through the flange, clear of the web",
            f'result = result.faces("<Z").workplane().pushPoints([{pts_lit}]).hole({p["hole_d"]:.2f})',
        ]
    if p["chamfer_c"]:
        lines += [
            "",
            "# deburr chamfer on the web top edges",
            f'result = result.edges(">Z").chamfer({p["chamfer_c"]:.2f})',
        ]
    return "\n".join(lines) + "\n"
