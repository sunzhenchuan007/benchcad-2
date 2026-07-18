"""knurled_thumb_screw_din464 — the benchmark generator spec.

The head trio + shank data (dk, ds, h, k, b) are the jointly-sampled DIN 464
row for the nominal thread size d; refine() draws a row and sets them from the
catalog table, plus a knurl depth scaled to the head. The shank length l is a
stock dimension drawn inside the size's DIN 464 availability band and the
knurl count is a proportion. check() audits that
the sampled data is a real DIN 464 row and that the geometry is consistent.

Anchor: DIN 464 knurled thumb screw, high type — head Ø dk, collar Ø ds, head
height h, knurl height k and thread length b per the standard; the coarse pitch
is ISO 261. Source: fasteners.eu DIN 464 datasheet table.
"""

# DIN 464 rows: nominal thread d -> (d, head Ø dk, collar Ø ds, head height h,
# knurl height k, thread length b, collar fillet r), mm — high type.
_ROWS = {
    "easy": [
        (1.0, 5.5, 2.8, 3.5, 1.5, 3.0, 0.5),
        (2.0, 9.0, 4.5, 5.3, 2.0, 6.0, 0.5),
        (3.0, 12.0, 6.0, 7.5, 2.5, 9.0, 0.5),
    ],
    "medium": [
        (4.0, 16.0, 8.0, 9.5, 3.5, 12.0, 0.5),
        (5.0, 20.0, 10.0, 11.5, 4.0, 15.0, 1.0),
        (6.0, 24.0, 12.0, 15.0, 5.0, 18.0, 1.0),
    ],
    "hard": [
        (8.0, 30.0, 16.0, 18.0, 6.0, 24.0, 2.0),
        (10.0, 36.0, 20.0, 23.0, 8.0, 30.0, 2.0),
    ],
}

# DIN 464 shank-length availability per size, read off the source page's l/mass
# matrix (l runs 2..40 nominal overall; each size ships a sub-band). Lower ends
# are lifted to b + 2 pitches so the plain neck under the collar survives.
_L_BANDS = {
    1: (3.6, 5.0), 2: (7.0, 10.0), 3: (10.2, 12.0), 4: (13.5, 16.0),
    5: (16.7, 20.0), 6: (20.1, 25.0), 8: (26.6, 40.0), 10: (33.1, 40.0),
}
_ALL_ROWS = [r for rows in _ROWS.values() for r in rows]

# ISO 261 coarse pitch by nominal thread diameter, mm (DIN 464 range M1..M10)
_PITCH = {1: 0.25, 2: 0.4, 3: 0.5, 4: 0.7, 5: 0.8, 6: 1.0, 8: 1.25, 10: 1.5}


# -- PARAM_SPEC ----------------------------------------------------------------
PARAM_SPEC = {
    "thread_dia_d": dict(
        desc="nominal metric thread diameter d (DIN 464 row)",
        unit="mm",
        range={"easy": (1.0, 3.0), "medium": (4.0, 6.0), "hard": (8.0, 10.0)},
        source="DIN 464 nominal thread size d",
        askable=True,
        refine=True,
        coverage=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0],
    ),
    "head_dia_dk": dict(
        desc="knurled head outer diameter dk (same DIN 464 row)",
        unit="mm",
        range={"easy": (5.0, 13.0), "medium": (15.0, 25.0), "hard": (29.0, 37.0)},
        source="DIN 464 head diameter dk (row-locked to d)",
        askable=True,
        refine=True,
    ),
    "collar_dia_ds": dict(
        desc="collar / raised shoulder diameter ds (same DIN 464 row)",
        unit="mm",
        range={"easy": (2.5, 6.5), "medium": (7.5, 12.5), "hard": (15.0, 21.0)},
        source="DIN 464 collar diameter ds (row-locked to d)",
        askable=True,
        refine=True,
    ),
    "head_h": dict(
        desc="total head height h — knurled disk plus collar (same DIN 464 row)",
        unit="mm",
        range={"easy": (3.0, 8.0), "medium": (9.0, 15.5), "hard": (17.0, 24.0)},
        source="DIN 464 head height h (row-locked to d)",
        askable=True,
        refine=True,
    ),
    "knurl_band_k": dict(
        desc="height of the knurled disk k (the knurl band; same DIN 464 row)",
        unit="mm",
        range={"easy": (1.0, 3.0), "medium": (3.0, 5.5), "hard": (5.5, 8.5)},
        source="DIN 464 knurl height k (row-locked to d)",
        askable=True,
        refine=True,
    ),
    "thread_len_b": dict(
        desc="threaded length b measured from the tip (same DIN 464 row)",
        unit="mm",
        range={"easy": (2.5, 9.5), "medium": (11.0, 18.5), "hard": (23.0, 30.5)},
        source="DIN 464 thread length b (row-locked to d)",
        askable=True,
        refine=True,
    ),
    "collar_fillet_r": dict(
        desc="fillet r where the collar meets the head-disk underside (drawing dim r)",
        unit="mm",
        range={"easy": (0.5, 0.5), "medium": (0.5, 1.0), "hard": (2.0, 2.0)},
        source="DIN 464 r column (row-locked to d)",
        askable=True,
        refine=True,
    ),
    "shank_len_l": dict(
        desc="shank length l under the collar (free stock length)",
        unit="mm",
        range={"easy": (3.6, 12.0), "medium": (13.5, 25.0), "hard": (26.6, 40.0)},
        source="DIN 464 length availability matrix (per-size band, l = 2..40 overall)",
        askable=True,
        refine=True,
    ),
    "n_knurls": dict(
        desc="number of straight-knurl flutes around the head rim",
        unit="count",
        range={"easy": (20, 28), "medium": (26, 36), "hard": (30, 40)},
        source="proportion (straight-knurl flute pitch)",
        askable=False,
        integer=True,
    ),
    "knurl_depth": dict(
        desc="radial depth of each knurl flute (shallow vs head_dia_dk)",
        unit="mm",
        range={"easy": (0.1, 0.7), "medium": (0.3, 1.3), "hard": (0.6, 1.95)},
        source="proportion (~3-4.5% of dk)",
        askable=False,
        refine=True,
    ),
}


# -- check — the engineering truth reviewers audit -----------------------------
def check(p: dict) -> list[str]:
    bad = []
    row = (p["thread_dia_d"], p["head_dia_dk"], p["collar_dia_ds"],
           p["head_h"], p["knurl_band_k"], p["thread_len_b"], p["collar_fillet_r"])
    if row not in _ALL_ROWS:
        bad.append("(d, dk, ds, h, k, b, r) is not a DIN 464 row")
    d, dk, ds = p["thread_dia_d"], p["head_dia_dk"], p["collar_dia_ds"]
    h, k, b, l = p["head_h"], p["knurl_band_k"], p["thread_len_b"], p["shank_len_l"]
    n, kd = int(round(p["n_knurls"])), p["knurl_depth"]
    if int(round(d)) not in _PITCH:
        bad.append("thread_dia_d has no ISO 261 coarse pitch")
    pitch = _PITCH.get(int(round(d)), 0.0)
    if not (d < ds < dk):
        bad.append("diameters must nest: thread_dia_d < collar_dia_ds < head_dia_dk")
    if k >= h:
        bad.append("knurl band k must be shorter than head height h (collar needs height)")
    if not (0.0 < kd < 0.1 * dk):
        bad.append("knurl_depth must be small and positive vs head_dia_dk")
    if b <= 3.0 * pitch:
        bad.append("thread_len_b must span more than ~3 pitches")
    if l <= b + 2.0 * pitch:
        bad.append("shank_len_l must exceed thread_len_b plus a plain relief")
    band = _L_BANDS.get(int(round(d)))
    if band and not (band[0] - 0.11 <= l <= band[1] + 0.11):
        bad.append("shank_len_l outside the DIN 464 per-size length availability")
    if not (16 <= n <= 44):
        bad.append("n_knurls outside a sane straight-knurl band (16..44)")
    return bad


# -- refine — draw the DIN 464 row + scale the knurl depth ---------------------
def refine(p: dict, difficulty: str, rng) -> None:
    d, dk, ds, h, k, b, r = _ROWS[difficulty][int(rng.integers(len(_ROWS[difficulty])))]
    p["thread_dia_d"] = d
    p["head_dia_dk"] = dk
    p["collar_dia_ds"] = ds
    p["head_h"] = h
    p["knurl_band_k"] = k
    p["thread_len_b"] = b
    p["collar_fillet_r"] = r
    lo, hi = _L_BANDS[int(round(d))]
    p["shank_len_l"] = round(float(rng.uniform(lo, hi)), 1)
    # knurl flutes scale with the head; small jitter keeps instances distinct
    p["knurl_depth"] = round(dk * float(rng.uniform(0.03, 0.045)), 2)
