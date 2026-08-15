"""BenchCAD parameter specification for the complete GN 832 latch."""


_SOURCE = (
    "Ganter GN 832 official catalog table, sizes 55/150/200; "
    "Step-1 supplied STEP references for Size 55 and Size 200"
)

PARAM_SPEC = {
    "catalog_index": dict(
        desc="complete official GN 832 row: 0=Size 55, 1=Size 150, 2=Size 200",
        unit="",
        range={"easy": (0, 0), "medium": (1, 1), "hard": (2, 2)},
        choices={"easy": [0], "medium": [1], "hard": [2]},
        source=_SOURCE,
        integer=True,
        askable=True,
        coverage=[0, 1, 2],
    ),
    "sheet_t": dict(
        desc="unlisted stamped-sheet thickness used by body lip and catch",
        unit="mm",
        range={
            "easy": (0.90, 1.20),
            "medium": (1.20, 1.65),
            "hard": (1.65, 2.20),
        },
        source="proportion; bounded against official wire diameter d1",
        askable=True,
    ),
}


def check(p: dict) -> list[str]:
    bad = []
    idx = int(p["catalog_index"])
    if idx not in (0, 1, 2) or abs(p["catalog_index"] - idx) > 1e-9:
        bad.append("catalog_index must be exactly 0, 1, or 2")
        return bad

    wire_d = (2.0, 3.0, 4.0)[idx]
    if p["sheet_t"] < 0.40 * wire_d:
        bad.append("sheet_t < 0.40*d1: formed sheet is implausibly thin")
    if p["sheet_t"] > 0.65 * wire_d:
        bad.append("sheet_t > 0.65*d1: formed sheet is implausibly thick")
    return bad
