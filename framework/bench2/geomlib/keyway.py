"""DIN 6885-1 parallel-key seat dimensions (shared standard helper)."""


def keyway_dims(bore_d):
    """(key width b, hub-side seat depth t2) for a shaft bore of diameter
    `bore_d`, DIN 6885-1 Form A parallel keys.

    The 5-20 mm key rows are cross-checked against the norelem 22250 datasheet
    T2 column. Outside the tabulated bore range a proportional fallback keeps
    the seat sane. Self-contained (table inlined, no imports) so it embeds
    verbatim in a generated program.
    """
    table = [
        (6, 8, 2, 1.0), (8, 10, 3, 1.4), (10, 12, 4, 1.8), (12, 17, 5, 2.3),
        (17, 22, 6, 2.8), (22, 30, 8, 3.3), (30, 38, 10, 3.3), (38, 44, 12, 3.3),
        (44, 50, 14, 3.8), (50, 58, 16, 4.3), (58, 65, 18, 4.4), (65, 75, 20, 4.9),
    ]
    for lo, hi, b, t2 in table:
        if lo <= bore_d < hi:
            return float(b), t2
    b = round(bore_d * 0.25, 0)
    return b, round(b * 0.4, 1)
