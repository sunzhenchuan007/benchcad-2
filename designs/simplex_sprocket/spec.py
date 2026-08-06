"""simplex_sprocket — the benchmark generator spec.

Demonstrates the two patterns that make a family more than a box:
  * table-driven parameters — (pitch, roller_d, tooth_width) is one jointly
    sampled row of the ISO 606 chain table, not three free numbers;
  * coupled parameters — the bore is bounded by the computed root circle and
    the hub is sized off the bore, so refine() fills them after the base draw.

The framework samples from PARAM_SPEC (bench2.sampling); refine() is the only
hand-written sampling code, and it holds just the coupling — no rejection loop.

Primary source: norelem 22250 datasheet (single sprockets 5/8" x 3/8" DIN ISO
606) — dimension-symbol mapping in NOTES.md.

Tooth geometry (ISO 606:2015 §8.2; tip offset fitted to the catalog):
    dp = p / sin(pi/z)          pitch circle diameter   (== catalog D1, exact)
    da = dp + 0.68 * d1         tip circle diameter     (fits catalog D column)
    df = dp - 1.01 * d1         root circle diameter
"""

import math

from bench2 import Resample
from bench2.geomlib import keyway_dims

# ISO 606 / DIN 8187 B-series chains — (chain no., pitch p, roller d1, tooth width b1), mm
_ISO606 = [
    ("05B", 8.000, 5.00, 4.4),
    ("06B", 9.525, 6.35, 5.4),
    ("08B", 12.700, 8.51, 7.2),
    ("10B", 15.875, 10.16, 9.1),  # the 5/8" x 3/8" chain of the catalog part
    ("12B", 19.050, 11.91, 11.4),
    ("16B", 25.400, 15.88, 14.4),
]


def _circles(pitch, n_teeth, roller_d):
    """ISO 606 §8.2 derived circles (pitch / tip / root diameters); see the
    module docstring for the 0.68 tip fit."""
    dp = pitch / math.sin(math.pi / n_teeth)
    da = dp + 0.68 * roller_d
    df = dp - 1.01 * roller_d
    return dp, da, df


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    # The chain row is one discrete choice (refine draws it jointly from _ISO606).
    "pitch": dict(
        desc="chain pitch p (ISO 606 B-series row, jointly with roller_d, tooth_width)",
        unit="mm",
        range={"easy": (8.0, 25.4), "medium": (8.0, 25.4), "hard": (8.0, 25.4)},
        source="ISO 606 Table 1 / DIN 8187 (discrete rows 05B–16B)",
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
        desc="tooth width b1 (same table row as pitch)",
        unit="mm",
        range={"easy": (4.4, 14.4), "medium": (4.4, 14.4), "hard": (4.4, 14.4)},
        source="ISO 606 Table 1 (row-locked to pitch)",
        refine=True,
    ),
    "n_teeth": dict(
        desc="number of teeth z",
        unit="",
        range={"easy": (9, 18), "medium": (18, 36), "hard": (32, 60)},
        source="roller-chain practice: z >= 9 to limit chordal action; catalog range",
        integer=True,
    ),
    "bore_d": dict(
        desc="center bore diameter",
        unit="mm",
        range={"easy": (5.0, 30.0), "medium": (5.0, 45.0), "hard": (8.0, 60.0)},
        source="catalog D3 (H7); bounded by the root circle (refine + check)",
        refine=True,
    ),
    "form_b": dict(
        desc="hub form: 0 = Form A (one-sided hub boss), 1 = Form B (straight barrel hub)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (0, 1)},
        choices={"easy": [0], "medium": [0, 1], "hard": [0, 1]},
        source="norelem 22250 'Form' column — heterogeneous catalog variants",
        feature=True,
    ),
    "hub_d": dict(
        desc="hub outside diameter (0 = flat plate sprocket)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (10.0, 120.0), "hard": (10.0, 160.0)},
        source="catalog D2 column",
        feature=True,
        refine=True,
    ),
    "hub_len": dict(
        desc="hub length beyond the toothed disc",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (4.0, 36.0), "hard": (4.0, 36.0)},
        source="catalog L - B1 (= 1.7-2.3x tooth width)",
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
    # the (pitch, roller_d, tooth_width) triple must be an ISO 606 row, not free numbers
    if not any(
        abs(p["pitch"] - r[1]) < 1e-6 and abs(p["roller_d"] - r[2]) < 1e-6
        and abs(p["tooth_width"] - r[3]) < 1e-6
        for r in _ISO606
    ):
        bad.append("(pitch, roller_d, tooth_width) is not an ISO 606 B-series row")
    _, _, df = _circles(p["pitch"], p["n_teeth"], p["roller_d"])
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
        kw, _ = keyway_dims(p["bore_d"])
        if kw >= 0.5 * p["bore_d"]:
            bad.append("keyway width >= half the bore: DIN 6885 table misapplied")
        if not p["hub_d"]:
            bad.append("keyway without a hub: key seat needs hub material")
    return bad


# ── refine — the coupling, and only the coupling (no rejection loop) ──────────
def refine(p: dict, difficulty: str, rng) -> None:
    """Fill the coupled parameters after the framework has drawn the base ones.

    Sets the jointly-sampled chain row and the size-dependent bore / hub. Raises
    Resample when a hub can't fit the drawn chain+tooth count, so the framework
    discards the draw and tries again — the escape the old loop wrote as
    `continue`.
    """
    # (pitch, roller_d, tooth_width) is ONE discrete choice — a real chain row
    _, pitch, d1, b1 = _ISO606[int(rng.integers(len(_ISO606)))]
    p["pitch"], p["roller_d"], p["tooth_width"] = pitch, d1, b1
    _, _, df = _circles(pitch, p["n_teeth"], d1)

    # bore: rim proportion (0.2-0.45 df) clamped to the DECLARED spec range —
    # the spec is the contract QA/edit derivation relies on.
    b_lo, b_hi = PARAM_SPEC["bore_d"]["range"][difficulty]
    hi_b = min(0.45 * df, b_hi)
    lo_b = max(3.0, b_lo, 0.2 * df)
    if lo_b >= hi_b:  # very large sprockets: the spec cap binds
        lo_b = 0.6 * hi_b
    p["bore_d"] = round(float(rng.uniform(lo_b, hi_b)), 1)

    # hub only on medium/hard; sized off the bore and the root circle
    if difficulty in ("medium", "hard"):
        h_lo, h_hi = PARAM_SPEC["hub_d"]["range"][difficulty]
        hub_lo = max(1.7 * p["bore_d"], h_lo)
        hub_hi = min(0.8 * df, h_hi)
        if hub_lo >= hub_hi:
            raise Resample  # no hub fits this chain/tooth draw — resample
        p["hub_d"] = round(float(rng.uniform(hub_lo, hub_hi)), 1)
        # catalog hub protrusion: L - B1 = 1.7-2.3x tooth width (norelem 22250)
        p["hub_len"] = round(b1 * float(rng.uniform(1.5, 2.4)), 1)
    else:
        p["hub_d"] = 0.0
        p["hub_len"] = 0.0
