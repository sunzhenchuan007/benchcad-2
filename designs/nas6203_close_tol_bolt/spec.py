"""NAS6203-NAS6220 Rev. 10 table-driven close-tolerance bolts.

Table I locks thread designation, head C, close-tolerance shank D, bearing E,
head height H and short-thread length T to one of all 13 basic numbers. Table II
defines grip dash numbers in 1/16-inch increments and LENGTH = GRIP + T.
Replacement oversize X/Y data are intentionally absent because source sheet 7
is missing from the issue evidence.
"""


_MM_PER_IN = 25.4


def _mm(value):
    return round(value * _MM_PER_IN, 4)


# (basic, nominal thread d, TPI, Cmax, Cmin, Dmax, Dmin, Emin, H, T), inches.
# NAS6203-NAS6220 Rev. 10, Tables I-II. T is the constant LENGTH-GRIP column.
_ROWS_IN = [
    (6203, 0.1900, 32, 0.376, 0.367, 0.1895, 0.1885, 0.335, 0.110, 0.323),
    (6204, 0.2500, 28, 0.439, 0.429, 0.2495, 0.2485, 0.398, 0.125, 0.370),
    (6205, 0.3125, 24, 0.502, 0.492, 0.3120, 0.3110, 0.460, 0.156, 0.438),
    (6206, 0.3750, 24, 0.564, 0.554, 0.3745, 0.3735, 0.523, 0.188, 0.454),
    (6207, 0.4375, 20, 0.690, 0.678, 0.4370, 0.4360, 0.648, 0.219, 0.528),
    (6208, 0.5000, 20, 0.752, 0.741, 0.4995, 0.4985, 0.710, 0.250, 0.528),
    (6209, 0.5625, 18, 0.877, 0.865, 0.5615, 0.5605, 0.835, 0.281, 0.594),
    (6210, 0.6250, 18, 0.940, 0.928, 0.6240, 0.6230, 0.898, 0.312, 0.626),
    (6212, 0.7500, 16, 1.065, 1.052, 0.7490, 0.7480, 1.023, 0.375, 0.666),
    (6214, 0.8750, 14, 1.252, 1.239, 0.8740, 0.8730, 1.210, 0.438, 0.759),
    (6216, 1.0000, 12, 1.440, 1.427, 0.9990, 0.9980, 1.398, 0.500, 0.895),
    (6218, 1.1250, 12, 1.627, 1.614, 1.1240, 1.1225, 1.585, 0.562, 0.989),
    (6220, 1.2500, 12, 1.814, 1.801, 1.2490, 1.2475, 1.772, 0.625, 1.083),
]

_TIER_ROWS = {
    "easy": _ROWS_IN[:4],
    "medium": _ROWS_IN[4:9],
    "hard": _ROWS_IN[9:],
}

# Table II contains 66 real grip rows: 1-32, then even dash numbers 34-100.
_ALL_DASHES = list(range(1, 33)) + list(range(34, 101, 2))
_TIER_DASHES = {
    "easy": list(range(2, 17)),
    "medium": list(range(2, 33)),
    "hard": _ALL_DASHES,
}


def _grip_in(dash):
    # Table II converts the 1/16-in ladder to three decimal places.
    return round(dash / 16.0, 3)


def _row_values(row):
    _, nominal_d, tpi, cmax, cmin, dmax, dmin, emin, head_h, thread_len = row
    shank = 0.5 * (dmax + dmin)
    return (
        _mm(0.5 * (cmax + cmin)),
        _mm(head_h),
        _mm(emin),
        _mm(shank),
        _mm(0.99 * nominal_d),
        _mm(1.0 / tpi),
        _mm(thread_len),
    )


def _row_range(index):
    return {
        difficulty: (
            min(_row_values(row)[index] for row in rows),
            max(_row_values(row)[index] for row in rows),
        )
        for difficulty, rows in _TIER_ROWS.items()
    }


_NAS = "NAS6203-NAS6220 Rev. 10 Table I"

PARAM_SPEC = {
    "head_af": dict(
        desc="hex-head width across flats C (mid-tolerance)",
        unit="mm",
        range=_row_range(0),
        source=f"{_NAS}, C max/min",
        refine=True,
    ),
    "head_height": dict(
        desc="hex-head nominal height H",
        unit="mm",
        range=_row_range(1),
        source=f"{_NAS}, H +.015/-.000",
        refine=True,
    ),
    "bearing_d": dict(
        desc="minimum under-head bearing diameter E",
        unit="mm",
        range=_row_range(2),
        source=f"{_NAS}, E min",
        refine=True,
    ),
    "shank_d": dict(
        desc="close-tolerance plain-grip diameter D (mid-tolerance)",
        unit="mm",
        range=_row_range(3),
        source=f"{_NAS}, D max/min",
        refine=True,
        coverage=[_row_values(row)[3] for row in _ROWS_IN],
    ),
    "thread_major_d": dict(
        desc="reduced external thread major diameter used for geometry",
        unit="mm",
        range=_row_range(4),
        source="proportion (0.99 nominal UNJF diameter; exact repair X/Y tolerances omitted)",
        refine=True,
    ),
    "thread_pitch": dict(
        desc="UNJF thread pitch from the basic-number thread designation",
        unit="mm",
        range=_row_range(5),
        source=f"{_NAS}, UNJF-3A thread designation",
        refine=True,
    ),
    "grip_length": dict(
        desc="plain cylindrical grip from Table II dash number",
        unit="mm",
        range={
            difficulty: (
                _mm(min(_grip_in(dash) for dash in dashes)),
                _mm(max(_grip_in(dash) for dash in dashes)),
            )
            for difficulty, dashes in _TIER_DASHES.items()
        },
        source="NAS6203-NAS6220 Rev. 10 Table II, 66-entry 1/16-in grip ladder",
        refine=True,
    ),
    "thread_length": dict(
        desc="short-thread dimension T, so under-head LENGTH = GRIP + T",
        unit="mm",
        range=_row_range(6),
        source="NAS6203-NAS6220 Rev. 10 Table II (constant LENGTH-GRIP by basic number)",
        refine=True,
    ),
}


def _is_basic_row(p):
    return any(
        all(
            abs(p[column] - values[index]) < 1e-6
            for index, column in enumerate(
                (
                    "head_af",
                    "head_height",
                    "bearing_d",
                    "shank_d",
                    "thread_major_d",
                    "thread_pitch",
                    "thread_length",
                )
            )
        )
        for row in _ROWS_IN
        for values in (_row_values(row),)
    )


def _is_grip_value(value):
    return any(abs(value - _mm(_grip_in(dash))) < 1e-6 for dash in _ALL_DASHES)


def check(p: dict) -> list[str]:
    bad = []
    if not _is_basic_row(p):
        bad.append("head/shank/thread dimensions are not one NAS6203-NAS6220 Table I row")
    if not _is_grip_value(p["grip_length"]):
        bad.append("grip_length is not on the 66-entry NAS Table II dash ladder")
    if p["thread_major_d"] >= p["shank_d"]:
        bad.append("thread major diameter is not reduced below close-tolerance D")
    if p["bearing_d"] <= p["shank_d"]:
        bad.append("E <= D: no under-head bearing land around the close-tolerance shank")
    if p["head_af"] <= p["bearing_d"]:
        bad.append("C <= E: bearing land would exceed the hex across flats")
    if p["thread_length"] < 5.0 * p["thread_pitch"]:
        bad.append("T < five thread pitches: below NAS Figure 1 minimum engagement region X")
    return bad


def refine(p: dict, difficulty: str, rng) -> None:
    rows = _TIER_ROWS[difficulty]
    row = rows[int(rng.integers(len(rows)))]
    values = _row_values(row)
    for index, column in enumerate(
        (
            "head_af",
            "head_height",
            "bearing_d",
            "shank_d",
            "thread_major_d",
            "thread_pitch",
            "thread_length",
        )
    ):
        p[column] = values[index]

    dashes = _TIER_DASHES[difficulty]
    dash = dashes[int(rng.integers(len(dashes)))]
    p["grip_length"] = _mm(_grip_in(dash))
