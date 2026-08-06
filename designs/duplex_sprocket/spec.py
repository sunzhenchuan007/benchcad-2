"""duplex_sprocket — the benchmark generator spec.

Same table-driven + coupled pattern as simplex_sprocket, extended by the duplex
column: the chain row is (pitch p, roller d1, tooth width b1, transverse pitch
pt), and the groove wall between bore and inter-row cylinder adds one more bore
bound. The framework samples from PARAM_SPEC; refine() holds the joint row draw
and the bore/hub coupling — no rejection loop.

Primary source: norelem 22253 datasheet (sprockets duplex 5/8" x 3/8" DIN ISO
606) — symbol mapping in NOTES.md. pt column cross-checked against the Renold
DIN 8187 duplex tables ("Transverse Pitch"); 10B-2 = 16,59 confirmed by norelem
22253 B2 = 25,5.
"""

from bench2 import Resample
from bench2.geomlib import keyway_dims
from part import _circles

# ISO 606 / DIN 8187 B-series duplex chains —
# (chain no., pitch p, roller d1, tooth width b1, transverse pitch pt), mm.
_ISO606_2 = [
    ("05B-2", 8.000, 5.00, 4.4, 5.64),
    ("06B-2", 9.525, 6.35, 5.4, 10.24),
    ("08B-2", 12.700, 8.51, 7.2, 13.92),
    ("10B-2", 15.875, 10.16, 9.1, 16.59),  # the 5/8" x 3/8" chain of norelem 22253
    ("12B-2", 19.050, 11.91, 11.4, 19.46),
    ("16B-2", 25.400, 15.88, 14.4, 31.88),
]


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    # (pitch, roller_d, tooth_width, trans_pitch) is ONE discrete choice — a row
    # of _ISO606_2 — drawn jointly in refine().
    "pitch": dict(
        desc="chain pitch p (ISO 606 B-series duplex row, jointly with roller_d, "
             "tooth_width, trans_pitch)",
        unit="mm",
        range={"easy": (8.0, 25.4), "medium": (8.0, 25.4), "hard": (8.0, 25.4)},
        source="ISO 606 Table 1 / DIN 8187 (discrete rows 05B-2 – 16B-2)",
        refine=True,
        coverage=[8.000, 9.525, 12.700, 15.875, 19.050, 25.400],
    ),
    "roller_d": dict(
        desc="chain roller diameter d1 (same table row as pitch)",
        unit="mm",
        range={"easy": (5.0, 15.88), "medium": (5.0, 15.88), "hard": (5.0, 15.88)},
        source="ISO 606 Table 1 (row-locked to pitch)",
        refine=True,
    ),
    "tooth_width": dict(
        desc="single-row tooth width b1 (same table row as pitch; catalog B1)",
        unit="mm",
        range={"easy": (4.4, 14.4), "medium": (4.4, 14.4), "hard": (4.4, 14.4)},
        source="ISO 606 Table 1 (row-locked to pitch)",
        refine=True,
    ),
    "trans_pitch": dict(
        desc="transverse pitch pt — center distance of the two tooth rows "
             "(same table row as pitch; catalog B2 = tooth_width + pt)",
        unit="mm",
        range={"easy": (5.64, 31.88), "medium": (5.64, 31.88), "hard": (5.64, 31.88)},
        source="ISO 606 / DIN 8187 duplex 'Transverse Pitch' column (Renold "
               "tables; 10B-2 = 16,59 confirmed by norelem 22253 B2 = 25,5)",
        refine=True,
    ),
    "n_teeth": dict(
        desc="number of teeth z (both rows identical, in phase)",
        unit="",
        range={"easy": (9, 18), "medium": (18, 36), "hard": (32, 60)},
        source="roller-chain practice: z >= 9 to limit chordal action; catalog range",
        integer=True,
    ),
    "bore_d": dict(
        desc="center bore diameter",
        unit="mm",
        range={"easy": (5.0, 30.0), "medium": (5.0, 45.0), "hard": (8.0, 60.0)},
        source="catalog D3 (H7); bounded by root circle and groove wall (refine + check)",
        refine=True,
    ),
    "hub_d": dict(
        desc="hub outside diameter (0 = flat double disc, no hub)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (10.0, 120.0), "hard": (10.0, 160.0)},
        source="catalog D2 column",
        feature=True,
        refine=True,
    ),
    "hub_len": dict(
        desc="hub length beyond the outer tooth disc (catalog L - B2)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (4.0, 36.0), "hard": (4.0, 36.0)},
        source="catalog L - B2 (= 1.6-3.7x tooth width across the 22253 rows)",
        refine=True,
    ),
    "has_keyway": dict(
        desc="DIN 6885A keyway in the bore (1 = yes; hard only)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 0), "hard": (1, 1)},
        choices={"easy": [0], "medium": [0], "hard": [1]},
        source="DIN 6885 Form A key seats",
        feature=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    # z >= 9: below this, chordal action makes the drive unusable (chain practice)
    if p["n_teeth"] < 9:
        bad.append("n_teeth < 9: chordal action too severe for a roller-chain drive")
    # the (pitch, roller_d, tooth_width, trans_pitch) quadruple must be an
    # ISO 606 duplex row, not free numbers
    if not any(
        abs(p["pitch"] - r[1]) < 1e-6 and abs(p["roller_d"] - r[2]) < 1e-6
        and abs(p["tooth_width"] - r[3]) < 1e-6 and abs(p["trans_pitch"] - r[4]) < 1e-6
        for r in _ISO606_2
    ):
        bad.append("(pitch, roller_d, tooth_width, trans_pitch) is not an ISO 606 duplex row")
    # rows must not overlap: the groove segment needs positive length
    if p["trans_pitch"] <= p["tooth_width"]:
        bad.append("trans_pitch <= tooth_width: tooth rows would overlap (no groove left)")
    _, _, df, groove_d = _circles(p["pitch"], p["n_teeth"], p["roller_d"])
    if p["bore_d"] > 0.50 * df:
        bad.append("bore_d > 0.50*root_diameter: tooth rim too thin")
    # the groove cylinder is the only material joining the two rows — it must
    # keep a hub-like wall around the bore to transmit the torque
    if 1.55 * p["bore_d"] > groove_d:
        bad.append("bore_d > groove_d/1.55: wall between bore and groove too thin")
    if p["bore_d"] < 3.0:
        bad.append("bore_d < 3 mm: below practical shaft sizes")
    if p["hub_d"]:
        # catalog hub proportions (norelem 22253: D2/D3 = 1.9-2.8, D2/df up to
        # 0.906 — z=17 D2=69, z=25 D2=105 — the hub still sits inside the root circle)
        if p["hub_d"] < 1.55 * p["bore_d"]:
            bad.append("hub_d < 1.55*bore_d: hub wall too thin for a set screw / key")
        if p["hub_d"] > 0.91 * df:
            bad.append("hub_d > 0.91*root_diameter: hub would merge into the tooth rim")
        if p["hub_len"] < 0.5 * p["tooth_width"] or p["hub_len"] > 4.0 * p["tooth_width"]:
            bad.append("hub_len outside 0.5-4.0x tooth width: not a catalog proportion")
    if p["has_keyway"]:
        kw, _ = keyway_dims(p["bore_d"])
        if kw >= 0.5 * p["bore_d"]:
            bad.append("keyway width >= half the bore: DIN 6885 table misapplied")
        if not p["hub_d"]:
            bad.append("keyway without a hub: key seat needs hub material")
    return bad


# ── refine — the joint row draw + bore/hub coupling (no rejection loop) ───────
def refine(p: dict, difficulty: str, rng) -> None:
    """Fill the coupled parameters after the framework's base draw. Raises
    Resample when no hub fits the drawn chain+tooth count."""
    # (pitch, roller_d, tooth_width, trans_pitch) is ONE discrete choice
    _, pitch, d1, b1, pt = _ISO606_2[int(rng.integers(len(_ISO606_2)))]
    p["pitch"], p["roller_d"], p["tooth_width"], p["trans_pitch"] = pitch, d1, b1, pt
    _, _, df, groove_d = _circles(pitch, p["n_teeth"], d1)

    # bore: rim proportion clamped to the DECLARED spec range AND the
    # groove-wall rule (the spec is the contract QA/edit derivation uses)
    b_lo, b_hi = PARAM_SPEC["bore_d"]["range"][difficulty]
    hi_b = min(0.45 * df, groove_d / 1.6, b_hi)
    lo_b = max(3.0, b_lo, 0.2 * df)
    if lo_b >= hi_b:  # very large sprockets: the spec cap binds
        lo_b = 0.6 * hi_b
    p["bore_d"] = round(float(rng.uniform(lo_b, hi_b)), 1)

    # one-sided hub boss on medium/hard, sized off the bore and root circle
    if difficulty in ("medium", "hard"):
        h_lo, h_hi = PARAM_SPEC["hub_d"]["range"][difficulty]
        hub_lo = max(1.7 * p["bore_d"], h_lo)
        hub_hi = min(0.90 * df, h_hi)  # reach the catalog's large high-z hubs (D2/df up to 0.906)
        if hub_lo >= hub_hi:
            raise Resample  # no hub fits this chain/tooth draw — resample
        p["hub_d"] = round(float(rng.uniform(hub_lo, hub_hi)), 1)
        # catalog hub protrusion: L - B2 = 1.6-3.7x tooth width (norelem 22253)
        h_len_hi = PARAM_SPEC["hub_len"]["range"][difficulty][1]
        p["hub_len"] = round(min(b1 * float(rng.uniform(1.6, 3.6)), h_len_hi), 1)
    else:
        p["hub_d"] = 0.0
        p["hub_len"] = 0.0
