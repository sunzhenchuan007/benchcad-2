"""simplex_sprocket — single-strand roller-chain sprocket, ISO 606 / DIN 8187.

REFERENCE design #2: demonstrates two patterns —
  * **table-driven parameters**: (pitch, roller_d, tooth_width) is a
    jointly-sampled row of the ISO 606 chain table, and the tooth form comes
    from the standard's equations;
  * **shared curve library**: the tooth profile comes from
    `bench2.geomlib.sprocket_profile`; `build()` embeds the helper's SOURCE in
    the emitted program (`inline_source`), so every generated CadQuery program
    stays fully stand-alone (imports only `math` + `cadquery`).

Heterogeneous variants in one family (catalog "Form" column):
  Form A — toothed disc + one-sided hub boss (medium/hard default),
  Form B — straight barrel hub through the disc, larger bores (up to 0.58·df,
           catalog row 22250-…1024).

Primary source: norelem 22250 datasheet (single sprockets 5/8" x 3/8" DIN ISO
606, ready to install) — dimension-symbol mapping in NOTES.md.

Tooth geometry (ISO 606:2015 §8.2; tip offset fitted to the catalog):
    dp = p / sin(pi/z)          pitch circle diameter   (== catalog D1, exact)
    da = dp + 0.68 * d1         tip circle diameter     (fits catalog D column)
    df = dp - 1.01 * d1         root circle diameter
"""

import math

from bench2.geomlib import inline_source, sprocket_profile  # noqa: F401 (used in build)

# ── standards tables ─────────────────────────────────────────────────────────
# ISO 606 / DIN 8187 B-series chains — (chain no., pitch p, roller d1, tooth width b1), mm
_ISO606 = [
    ("05B", 8.000, 5.00, 4.4),
    ("06B", 9.525, 6.35, 5.4),
    ("08B", 12.700, 8.51, 7.2),
    ("10B", 15.875, 10.16, 9.1),  # the 5/8" x 3/8" chain of the catalog part
    ("12B", 19.050, 11.91, 11.4),
    ("16B", 25.400, 15.88, 14.4),
]

# DIN 6885-1 Form A parallel keys — (bore_min, bore_max, key_width b, hub-seat depth t2), mm.
# t2 is the HUB-side keyway depth. The 5–12 mm key rows are cross-checked against
# the norelem 22250 datasheet T2 column (2,3 / 2,8 / 3,3).
_DIN6885A = [
    (6, 8, 2, 1.0), (8, 10, 3, 1.4), (10, 12, 4, 1.8), (12, 17, 5, 2.3),
    (17, 22, 6, 2.8), (22, 30, 8, 3.3), (30, 38, 10, 3.3), (38, 44, 12, 3.3),
    (44, 50, 14, 3.8), (50, 58, 16, 4.3), (58, 65, 18, 4.4), (65, 75, 20, 4.9),
]


def _keyway(bore_d):
    """(key width b, hub-side seat depth t2) per DIN 6885-1; proportional fallback."""
    for lo, hi, b, t2 in _DIN6885A:
        if lo <= bore_d < hi:
            return float(b), t2
    b = round(bore_d * 0.25, 0)
    return b, round(b * 0.4, 1)


def _derived(p):
    """ISO 606 §8.2 derived circles (see module docstring for the 0.68 fit)."""
    dp = p["pitch"] / math.sin(math.pi / p["n_teeth"])
    da = dp + 0.68 * p["roller_d"]
    df = dp - 1.01 * p["roller_d"]
    return dp, da, df


# ── 1. PARAM_SPEC ────────────────────────────────────────────────────────────
PARAM_SPEC = {
    # The chain row is sampled JOINTLY from _ISO606 — these three parameters are
    # one discrete choice, not independent uniforms.
    "pitch": dict(
        desc="chain pitch p (ISO 606 B-series row, sampled jointly with roller_d, tooth_width)",
        unit="mm",
        range={"easy": (8.0, 25.4), "medium": (8.0, 25.4), "hard": (8.0, 25.4)},
        source="ISO 606 Table 1 / DIN 8187 (discrete rows 05B–16B)",
        askable=True,
        # every chain row of the anchored table must be reachable by sampling
        coverage=[8.000, 9.525, 12.700, 15.875, 19.050, 25.400],
    ),
    "roller_d": dict(
        desc="chain roller diameter d1 (same table row as pitch)",
        unit="mm",
        range={"easy": (5.0, 15.88), "medium": (5.0, 15.88), "hard": (5.0, 15.88)},
        source="ISO 606 Table 1 (row-locked to pitch)",
        askable=True,
    ),
    "tooth_width": dict(
        desc="tooth width b1 (same table row as pitch)",
        unit="mm",
        range={"easy": (4.4, 14.4), "medium": (4.4, 14.4), "hard": (4.4, 14.4)},
        source="ISO 606 Table 1 (row-locked to pitch)",
        askable=True,
    ),
    "n_teeth": dict(
        desc="number of teeth z",
        unit="",
        range={"easy": (9, 18), "medium": (18, 36), "hard": (32, 60)},
        source="roller-chain practice: z >= 9 to limit chordal action; catalog range",
        askable=True,
    ),
    "bore_d": dict(
        desc="center bore diameter",
        unit="mm",
        range={"easy": (5.0, 30.0), "medium": (5.0, 45.0), "hard": (8.0, 60.0)},
        source="catalog D3 (H7); bounded by the root circle in check",
        askable=True,
    ),
    "form_b": dict(
        desc="hub form: 0 = Form A (one-sided hub boss), 1 = Form B (straight barrel hub)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        source="norelem 22250 'Form' column — heterogeneous catalog variants",
        feature=True,
    ),
    "hub_d": dict(
        desc="hub outside diameter (0 = flat plate sprocket)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (10.0, 120.0), "hard": (10.0, 160.0)},
        source="catalog D2 column",
        feature=True,
    ),
    "hub_len": dict(
        desc="hub length beyond the toothed disc",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (4.0, 36.0), "hard": (4.0, 36.0)},
        source="catalog L - B1 (= 1.7-2.3x tooth width)",
        askable=True,
    ),
    "has_keyway": dict(
        desc="DIN 6885A keyway in the bore (1 = yes; hard only)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 0), "hard": (1, 1)},
        source="DIN 6885 Form A key seats",
        feature=True,
    ),
}


# ── 2. check ─────────────────────────────────────────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    # z >= 9: below this, chordal action makes the drive unusable (chain practice)
    if p["n_teeth"] < 9:
        bad.append("n_teeth < 9: chordal action too severe for a roller-chain drive")
    # the (pitch, roller_d, tooth_width) triple must be an ISO 606 row, not free numbers
    if not any(
        abs(p["pitch"] - r[1]) < 1e-6 and abs(p["roller_d"] - r[2]) < 1e-6
        and abs(p["tooth_width"] - r[3]) < 1e-6
        for r in _ISO606
    ):
        bad.append("(pitch, roller_d, tooth_width) is not an ISO 606 B-series row")
    _, _, df = _derived(p)
    # rim between bore and root circle. Form A: 0.5*df; Form B barrel carries the
    # load in the hub, catalog reaches 0.58*df (row 22250-…1024: 24/41.11).
    bore_cap = 0.58 if p.get("form_b") else 0.50
    if p["bore_d"] > bore_cap * df:
        bad.append(f"bore_d > {bore_cap}*root_diameter: tooth rim too thin")
    if p["bore_d"] < 3.0:
        bad.append("bore_d < 3 mm: below practical shaft sizes")
    if p["form_b"] and not p["hub_d"]:
        bad.append("Form B requires a barrel hub (hub_d > 0)")
    if p["hub_d"]:
        # catalog hub proportions (norelem 22250: D2/D3 = 1.58-1.9, D2/df to 0.85)
        if p["hub_d"] < 1.55 * p["bore_d"]:
            bad.append("hub_d < 1.55*bore_d: hub wall too thin for a set screw / key")
        if p["hub_d"] > 0.87 * df:
            bad.append("hub_d > 0.87*root_diameter: hub would merge into the tooth rim")
        if p["hub_len"] < 0.5 * p["tooth_width"] or p["hub_len"] > 2.5 * p["tooth_width"]:
            bad.append("hub_len outside 0.5-2.5x tooth width: not a catalog proportion")
    if p["has_keyway"]:
        kw, _ = _keyway(p["bore_d"])
        if kw >= 0.5 * p["bore_d"]:
            bad.append("keyway width >= half the bore: DIN 6885 table misapplied")
        if not p["hub_d"]:
            bad.append("keyway without a hub: key seat needs hub material")
    return bad


# ── 3. sample ────────────────────────────────────────────────────────────────
def sample(difficulty: str, rng) -> dict:
    for _ in range(200):
        chain, pitch, d1, b1 = _ISO606[int(rng.integers(0, len(_ISO606)))]
        lo, hi = PARAM_SPEC["n_teeth"]["range"][difficulty]
        p = {
            "chain": chain,  # carried for the program header comment
            "pitch": pitch,
            "roller_d": d1,
            "tooth_width": b1,
            "n_teeth": int(rng.integers(lo, hi + 1)),
            "form_b": 0,
            "hub_d": 0.0,
            "hub_len": 0.0,
            "has_keyway": 0,
        }
        _, _, df = _derived(p)
        # bore: rim proportion (0.2-0.45 df) clamped to the DECLARED spec range —
        # the spec is the contract QA/edit derivation relies on.
        b_lo, b_hi = PARAM_SPEC["bore_d"]["range"][difficulty]
        hi_b = min(0.45 * df, b_hi)
        lo_b = max(3.0, b_lo, 0.2 * df)
        if lo_b >= hi_b:  # very large sprockets: the spec cap binds
            lo_b = 0.6 * hi_b
        p["bore_d"] = round(float(rng.uniform(lo_b, hi_b)), 1)
        if difficulty in ("medium", "hard"):
            p["form_b"] = int(rng.choice([0, 1]))
            h_lo, h_hi = PARAM_SPEC["hub_d"]["range"][difficulty]
            hub_lo = max(1.7 * p["bore_d"], h_lo)
            hub_hi = min(0.8 * df, h_hi)
            if hub_lo >= hub_hi:
                continue  # reject this draw; try a new chain row / tooth count
            p["hub_d"] = round(float(rng.uniform(hub_lo, hub_hi)), 1)
            # catalog hub protrusion: L - B1 = 1.7-2.3x tooth width (norelem 22250)
            p["hub_len"] = round(b1 * float(rng.uniform(1.5, 2.4)), 1)
        if difficulty == "hard":
            p["has_keyway"] = 1
        if not check(p):
            return p
    raise RuntimeError("no valid sample in 200 tries — ranges vs constraints too tight")


# ── 4. build ─────────────────────────────────────────────────────────────────
def build(p: dict) -> str:
    b1 = p["tooth_width"]
    ch = round(0.15 * b1, 2)  # deburr chamfer on the tooth-disc rims
    z = p["n_teeth"]
    # rotate so a tooth tip sits on +Y — the keyway (cut toward +Y) is then
    # tip-aligned ("keyway is aligned with the tooth tip", catalog note).
    phase = round(math.pi / 2 - math.pi / z, 6)
    form = "B" if p["form_b"] else "A"

    lines = [
        "import math",
        "import cadquery as cq",
        "",
        "",
        inline_source("sprocket_profile"),
        "",
        "",
        f"# ISO 606 simplex sprocket — chain {p['chain']} "
        f"(p={p['pitch']:.3f}, d1={p['roller_d']:.2f}), z={z}, Form {form}",
        f"pts = sprocket_profile({z}, {p['pitch']:.3f}, {p['roller_d']:.2f}, phase={phase})",
        f'disc = cq.Workplane("XY").polyline(pts).close().extrude({b1:.2f})',
        f'disc = disc.edges(">Z").chamfer({ch:.2f}).edges("<Z").chamfer({ch:.2f})',
        "result = disc",
    ]
    if p["hub_d"]:
        if p["form_b"]:
            # barrel protrudes symmetrically on BOTH faces (catalog drawing B)
            total = round(b1 + p["hub_len"], 2)
            z0 = round(-p["hub_len"] / 2, 2)
            lines += [
                "",
                "# Form B: straight barrel hub through the disc, symmetric overhang",
                f'result = result.union(cq.Workplane("XY").workplane(offset={z0:.2f})'
                f".circle({p['hub_d'] / 2:.2f}).extrude({total:.2f}))",
            ]
        else:
            lines += [
                "",
                "# Form A: one-sided hub boss",
                f'result = result.union(cq.Workplane("XY").workplane(offset={b1:.2f})'
                f".circle({p['hub_d'] / 2:.2f}).extrude({p['hub_len']:.2f}))",
            ]
    lines += [
        "",
        "# center bore",
        f'result = result.faces(">Z").workplane().hole({p["bore_d"]:.2f})',
    ]
    if p["has_keyway"]:
        kw, kd = _keyway(p["bore_d"])
        rect_h = round(kd + p["bore_d"] / 2, 2)
        lines += [
            "",
            "# DIN 6885A keyway (tip-aligned)",
            f'result = result.faces(">Z").workplane().center(0, {rect_h / 2:.2f})'
            f".rect({kw:.2f}, {rect_h:.2f}).cutThruAll()",
        ]
    return "\n".join(lines) + "\n"
