"""extrusion_profile_4040 — the benchmark generator spec.

The 40x40 Profile-8 cross-section is one fixed webbed hollow section (central
boss + four diagonal webs to the corners + four face T-slots whose chambers are
the hollow cells), so the section is fixed; the variable axes are the cut length,
the central ∅6.8 core bore and the rounded outer corners (R4) — the dimensions
that actually vary across the 40x40 range. Pairing a 40x40 body with the
Profile-5/6 slot series (those are the 20x20 / 30x30 products) is dropped.

Anchor: item Profile 8 40x40 (art. 0.0.026.03). item publishes the cross-section
but not a full ortho dim table, so the chamber width/depth, the boss (12) and the
web (4.5) are catalog-approximate (`proportion`); the slot opening (8), lip (4.5),
core bore (∅6.8) and corner (R4) are the catalog values.
"""


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "length": dict(
        desc="cut length of the extrusion (along the axis)",
        unit="mm",
        range={"easy": (40.0, 120.0), "medium": (120.0, 300.0), "hard": (300.0, 500.0)},
        source="cut-to-length stock (proportion)",
        askable=True,
    ),
    "core_bore": dict(
        desc="central core bore ∅6.8, tapped M8 for end fastening (0 = light/solid)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (6.8, 6.8), "hard": (6.8, 6.8)},
        choices={"easy": [0.0], "medium": [6.8], "hard": [6.8]},
        source="item 40x40 core bore ∅6.8",
        feature=True,
        coverage=[0.0, 6.8],
    ),
    "corner_r": dict(
        desc="rounded outer corner radius R4 (0 = sharp corners)",
        unit="mm",
        range={"easy": (0.0, 0.0), "medium": (0.0, 4.0), "hard": (4.0, 4.0)},
        choices={"easy": [0.0], "medium": [0.0, 4.0], "hard": [4.0]},
        source="item 40x40 rounded-corner variant (R4)",
        feature=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []
    if p["length"] < 20.0:
        bad.append("length < 20 mm: below a usable cut length")
    # the two variable features must be the item catalog values when present
    if p["core_bore"] and abs(p["core_bore"] - 6.8) > 1e-6:
        bad.append("core_bore is not the item ∅6.8")
    if p["corner_r"] and abs(p["corner_r"] - 4.0) > 1e-6:
        bad.append("corner_r is not the item R4")
    # ∅6.8 must sit inside the central boss (12 mm across flats) leaving a wall
    if p["core_bore"] > 12.0 - 2.0 * 2.0:
        bad.append("core_bore breaks out of the central boss wall")
    return bad
