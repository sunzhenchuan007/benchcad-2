"""extrusion_profile_4040 — the benchmark generator spec.

The 40x40 Profile-8 cross-section is one fixed webbed hollow section (central
boss + four diagonal webs to the corners + four face T-slots whose chambers are
the hollow cells), so the section is fixed; the variable axes are the cut length,
and the central ∅6.8 core bore — the dimensions that vary; the outer corners
are always the catalog R4 (the profile has no sharp corners). Pairing a 40x40 body with the
Profile-5/6 slot series (those are the 20x20 / 30x30 products) is dropped.

Anchor: item Profile 8 40x40 (art. 0.0.026.03). Published on the drawing and used
as published: overall 40, slot opening 8, lip 4.5, core bore ∅6.8, corner R4, and
the chamber width — the drawing's 12.25 is measured from the chamber wall to the
far face, so 20 - 12.25 = 7.75 per side and the chamber is 15.5 wide. An earlier
revision carried 15.3 and called it "catalog-approximate"; the value is on the
drawing.

item does not publish a full ortho dim table, so four numbers remain genuine
proportions and are named as such in part.py: the boss radius, where the chamber
wall leaves the straight, the radius of the curve into the boss, and the angle
each void stops short of the diagonal (which is what gives the web its width).
They are set together so the section comes out 51.62 % solid against the ~52.1 %
measured off the reference raster.
"""


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    "length": dict(
        desc="cut length of the extrusion (along the axis)",
        unit="mm",
        range={"easy": (40.0, 120.0), "medium": (120.0, 300.0), "hard": (300.0, 500.0)},
        source="cut-to-length stock (proportion)",
    ),
    "core_bore": dict(
        desc="central core bore ∅6.8, tapped M8 for end fastening (standard item feature)",
        unit="mm",
        range={"easy": (6.8, 6.8), "medium": (6.8, 6.8), "hard": (6.8, 6.8)},
        choices={"easy": [6.8], "medium": [6.8], "hard": [6.8]},
        source="item 40x40 core bore ∅6.8",
                coverage=[6.8],
    ),
    "corner_r": dict(
        # the real item Profile 8 is ALWAYS rounded R4 — the reference has no
        # sharp corners, so this is fixed at 4.0 on every tier (not a variable)
        desc="rounded outer corner radius (fixed R4 — Profile 8 has no sharp corners)",
        unit="mm",
        range={"easy": (4.0, 4.0), "medium": (4.0, 4.0), "hard": (4.0, 4.0)},
        source="item 40x40 corner radius R4 (catalog value, always present)",
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
    if abs(p["corner_r"] - 4.0) > 1e-6:
        bad.append("corner_r must be R4: the item Profile 8 has no sharp corners")
    # ∅6.8 must sit inside the central boss (12 mm across flats) leaving a wall
    if p["core_bore"] > 12.0 - 2.0 * 2.0:
        bad.append("core_bore breaks out of the central boss wall")
    return bad
