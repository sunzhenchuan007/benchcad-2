"""toggle_latch_base_plate — the benchmark generator spec.

The eight size dimensions are ONE jointly-sampled row of the Ganter GN 832 table
(sizes 55 / 150 / 200) — not eight free numbers. refine() draws the row and sets
those parameters; check() re-asserts that the eight together are a real catalog
row (row-lock). The remaining dimensions (sheet thickness, corner round, ear
thickness, fold fillet) are honest `"proportion"`s the framework draws freely to
give the family its novelty, bounded by check() so the stamping stays sane.

Primary source: Ganter GN 832 toggle latches (steel / stainless steel), catalog
size table — sizes 55 / 150 / 200. Symbol -> parameter map is in NOTES.md and in
part.py's docstring. The lever, U-bolt hook and catch bracket are mating parts
(their b4/b5/b6/l1/l3/r/FH columns are out of scope for this base-plate family).
"""

from part import _brk_len, _clevis_cx, _mount_hole_x, _nose_len, _pin_z

# Ganter GN 832 size table — one row = (size, l2, b1, d2, d1, h1, b2, b3, d3), mm
#   l2 plate length · b1 plate width · d2 mounting-hole Ø · d1 pivot-pin Ø
#   h1 overall height · b2 clevis width · b3 keeper-nose width · d3 cotter bore Ø
_GN832 = [
    (55, 60.0, 23.0, 3.2, 2.0, 11.0, 17.0, 14.0, 2.6),
    (150, 86.0, 34.0, 4.1, 3.0, 12.5, 23.0, 20.0, 3.1),
    (200, 111.0, 43.0, 5.3, 4.0, 19.0, 30.0, 26.0, 5.3),
]

_GN = "Ganter GN 832 toggle-latch size table (sizes 55/150/200)"


# ── PARAM_SPEC ───────────────────────────────────────────────────────────────
PARAM_SPEC = {
    # -- row-locked catalog dimensions (jointly sampled by refine as one row) --
    "plate_l": dict(
        desc="base-plate length l2 (X), left end to pivot axis",
        unit="mm",
        range={"easy": (60.0, 111.0), "medium": (60.0, 111.0), "hard": (60.0, 111.0)},
        source=_GN + " — l2 column (row-locked)",
        askable=True,
        refine=True,
    ),
    "plate_w": dict(
        desc="base-plate width b1 (Y)",
        unit="mm",
        range={"easy": (23.0, 43.0), "medium": (23.0, 43.0), "hard": (23.0, 43.0)},
        source=_GN + " — b1 column (row-locked)",
        askable=True,
        refine=True,
        coverage=[23.0, 34.0, 43.0],
    ),
    "mount_hole_d": dict(
        desc="mounting-hole diameter d2 (two holes)",
        unit="mm",
        range={"easy": (3.2, 5.3), "medium": (3.2, 5.3), "hard": (3.2, 5.3)},
        source=_GN + " — d2 column (row-locked)",
        askable=True,
        refine=True,
    ),
    "pin_d": dict(
        desc="pivot pin-hole diameter d1 (through both clevis ears)",
        unit="mm",
        range={"easy": (2.0, 4.0), "medium": (2.0, 4.0), "hard": (2.0, 4.0)},
        source=_GN + " — d1 column (row-locked)",
        askable=True,
        refine=True,
    ),
    "brk_h": dict(
        desc="overall height h1 (plate underside to clevis top)",
        unit="mm",
        range={"easy": (11.0, 19.0), "medium": (11.0, 19.0), "hard": (11.0, 19.0)},
        source=_GN + " — h1 column (row-locked)",
        askable=True,
        refine=True,
    ),
    "brk_w": dict(
        desc="clevis outer width b2 (Y)",
        unit="mm",
        range={"easy": (17.0, 30.0), "medium": (17.0, 30.0), "hard": (17.0, 30.0)},
        source=_GN + " — b2 column (row-locked)",
        askable=True,
        refine=True,
    ),
    "nose_w": dict(
        desc="keeper-nose tab width b3 (Y); used only when has_nose",
        unit="mm",
        range={"easy": (14.0, 26.0), "medium": (14.0, 26.0), "hard": (14.0, 26.0)},
        source=_GN + " — b3 column (row-locked)",
        askable=True,
        refine=True,
    ),
    "cotter_d": dict(
        desc="spring-cotter-pin bore diameter d3; used only when has_nose",
        unit="mm",
        range={"easy": (2.6, 5.3), "medium": (2.6, 5.3), "hard": (2.6, 5.3)},
        source=_GN + " — d3 column (row-locked)",
        askable=True,
        refine=True,
    ),
    # -- free proportions (drawn by the framework — the family's novelty) -----
    "plate_t": dict(
        desc="stamped sheet / plate thickness s (Z)",
        unit="mm",
        range={"easy": (1.6, 2.2), "medium": (1.3, 2.7), "hard": (1.0, 3.0)},
        source="proportion (steel sheet stock; GN 832 base is not thickness-tabulated)",
        askable=True,
    ),
    "corner_r": dict(
        desc="rounded plate-corner radius (formed/stamped corner rounds)",
        unit="mm",
        range={"easy": (1.5, 2.5), "medium": (1.2, 3.2), "hard": (1.0, 4.0)},
        source="proportion (stamped-corner break; NOT drawing symbol r = U-bolt reach)",
        askable=True,
    ),
    "wall_t": dict(
        desc="clevis wall (ear) thickness",
        unit="mm",
        range={"easy": (1.4, 2.0), "medium": (1.2, 2.4), "hard": (1.0, 3.0)},
        source="proportion (formed from the same sheet class as the base)",
    ),
    "fold_r": dict(
        desc="base<->clevis fold fillet radius (formed bend)",
        unit="mm",
        range={"easy": (0.6, 1.2), "medium": (0.6, 1.8), "hard": (0.5, 2.5)},
        source="proportion (sheet-metal bend radius)",
    ),
    # -- feature toggle -------------------------------------------------------
    "has_nose": dict(
        desc="keeper-nose tab + spring-cotter-pin bore at the left end (0/1)",
        unit="",
        range={"easy": (0, 0), "medium": (0, 1), "hard": (1, 1)},
        choices={"easy": [0], "medium": [0, 1], "hard": [1]},
        source="GN 832 keeper-tab variant (feature)",
        askable=True,
        feature=True,
    ),
}


# ── check — the engineering truth reviewers audit ────────────────────────────
def check(p: dict) -> list[str]:
    bad = []

    # (1) row-lock: the eight size dims must together be one real GN 832 row
    row = next(
        (
            r for r in _GN832
            if abs(p["plate_l"] - r[1]) < 1e-6 and abs(p["plate_w"] - r[2]) < 1e-6
            and abs(p["mount_hole_d"] - r[3]) < 1e-6 and abs(p["pin_d"] - r[4]) < 1e-6
            and abs(p["brk_h"] - r[5]) < 1e-6 and abs(p["brk_w"] - r[6]) < 1e-6
            and abs(p["nose_w"] - r[7]) < 1e-6 and abs(p["cotter_d"] - r[8]) < 1e-6
        ),
        None,
    )
    if row is None:
        bad.append("(plate_l,plate_w,mount_hole_d,pin_d,brk_h,brk_w,nose_w,cotter_d) "
                    "is not one GN 832 catalog row")

    # (2) base stays a stamped plate, not a block
    if p["plate_t"] > 0.15 * p["plate_w"]:
        bad.append("plate_t > 0.15*plate_w: base is a block, not stamped sheet")
    if p["plate_t"] < 0.8:
        bad.append("plate_t < 0.8 mm: below usable sheet stock")

    # (3) clevis fits within the plate and keeps a real slot for the lever eye
    if p["brk_w"] >= p["plate_w"]:
        bad.append("brk_w >= plate_w: clevis wider than the base plate")
    if p["wall_t"] < 0.8:
        bad.append("wall_t < 0.8 mm: ear thinner than usable sheet stock")
    if p["brk_w"] - 2.0 * p["wall_t"] < p["pin_d"]:
        bad.append("clevis slot (brk_w-2*wall_t) < pin_d: lever eye / pin won't fit")

    # (4) pivot hole sits inside the ears: >=0.5 mm of ear above and clear of the plate
    zc = _pin_z(p["plate_t"], p["brk_h"])
    if zc + p["pin_d"] / 2.0 > p["brk_h"] - 0.5:
        bad.append("pin hole < 0.5 mm below the clevis top: would break out")
    if zc - p["pin_d"] / 2.0 < p["plate_t"] + 0.5:
        bad.append("pin hole < 0.5 mm above the plate: fouls the base")

    # (5) two mounting holes: on the plate, tear-out edge distance >=1.5 d, clear
    #     of the nose step and of the clevis base (machinery-handbook 1.5d rule)
    xf, xn = _mount_hole_x(p["plate_l"], p["has_nose"])
    e = 1.5 * p["mount_hole_d"]
    left = _nose_len(p["plate_l"]) if p["has_nose"] else 0.0
    clevis_left = _clevis_cx(p["plate_l"]) - _brk_len(p["plate_l"]) / 2.0
    if p["plate_w"] / 2.0 - p["mount_hole_d"] / 2.0 < e:
        bad.append("mounting hole < 1.5d from the long plate edge: tear-out risk")
    if xf - p["mount_hole_d"] / 2.0 < left + 0.5:
        bad.append("far mounting hole runs off the plate / into the nose step")
    if xn + p["mount_hole_d"] / 2.0 > clevis_left - 2.0:
        bad.append("near mounting hole fouls the clevis base")

    # (6) fold fillet is a fold, not a takeover of the ear / plate
    if p["fold_r"] > (p["brk_h"] - p["plate_t"]) / 2.0:
        bad.append("fold_r > half the ear height: not a fold radius")
    if p["fold_r"] > 0.45 * _brk_len(p["plate_l"]):
        bad.append("fold_r > 0.45*clevis length: fillet swamps the fold")

    # (7) corner round + cotter bore stay within their features
    if p["corner_r"] > p["plate_w"] / 2.0 - 1.0:
        bad.append("corner_r too large for the plate half-width")
    if p["has_nose"] and p["cotter_d"] > 0.5 * p["nose_w"]:
        bad.append("cotter_d > 0.5*nose_w: bore too big for the keeper tab")

    return bad


# ── refine — draw one GN 832 size row (the only coupling) ────────────────────
def refine(p: dict, difficulty: str, rng) -> None:
    """Pick one catalog size and set the eight row-locked dimensions together —
    they are a real GN 832 row, not eight free numbers. Everything else was
    drawn by the framework from PARAM_SPEC; check() re-asserts the row-lock."""
    _, l2, b1, d2, d1, h1, b2, b3, d3 = _GN832[int(rng.integers(len(_GN832)))]
    p["plate_l"] = l2
    p["plate_w"] = b1
    p["mount_hole_d"] = d2
    p["pin_d"] = d1
    p["brk_h"] = h1
    p["brk_w"] = b2
    p["nose_w"] = b3
    p["cotter_d"] = d3
