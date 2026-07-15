"""DIN 6885-1 parallel-key seat dimensions (shared standard helper)."""


def keyway_dims(bore_d):
    """(key width b, hub-side seat depth t2) for a shaft bore of diameter
    `bore_d`, DIN 6885-1 Form A parallel keys.

    The full standard series is tabulated, 6 mm .. 500 mm of bore. The 6-75 mm
    rows are the ones the norelem 22250 datasheet prints (T2 column); the rows
    above 75 mm are the same series continued (roymech's BS 4235-1 table, whose
    b x h / t1 / t2 columns are identical to DIN 6885-1 -- both descend from
    ISO/R 773). A bore outside 6..500 mm raises: the old code fell back to
    b = 0.25*bore, t2 = 0.4*b there, which is not the standard and is silently
    wrong (bore 100 gave b=25, t2=10 where the series says a 28 x 16 key with
    t2 = 6.4). A benchmark part must not carry an invented key seat.

    Self-contained (table inlined, no imports) so it embeds verbatim in a
    generated program.
    """
    table = [
        (6, 8, 2, 1.0), (8, 10, 3, 1.4), (10, 12, 4, 1.8), (12, 17, 5, 2.3),
        (17, 22, 6, 2.8), (22, 30, 8, 3.3), (30, 38, 10, 3.3), (38, 44, 12, 3.3),
        (44, 50, 14, 3.8), (50, 58, 16, 4.3), (58, 65, 18, 4.4), (65, 75, 20, 4.9),
        (75, 85, 22, 5.4), (85, 95, 25, 5.4), (95, 110, 28, 6.4),
        (110, 130, 32, 7.4), (130, 150, 36, 8.4), (150, 170, 40, 9.4),
        (170, 200, 45, 10.4), (200, 230, 50, 11.4), (230, 260, 56, 12.4),
        (260, 290, 63, 12.4), (290, 330, 70, 14.4), (330, 380, 80, 15.4),
        (380, 440, 90, 17.4), (440, 500, 100, 19.5),
    ]
    for lo, hi, b, t2 in table:
        if lo <= bore_d < hi:
            return float(b), t2
    raise ValueError(
        "keyway_dims: bore %g mm is outside the DIN 6885-1 series (6..500 mm); "
        "a key seat cannot be invented for it" % bore_d
    )
