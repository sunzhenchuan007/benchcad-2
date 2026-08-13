"""Catalogue-row sampling contract for STAUFF SRF bushings."""

from bench2 import Resample

SOURCE = "STAUFF Catalogue 1 - STAUFF Clamps, English, 06/2026, p. 175"
PROPORTION = "proportion (unmarked profile details identified in Issue #89)"

# D1 tube, D2 flange OD, H1 total height, H2 flange height, D3 mounting bore
ROWS = (
    (6,18,22,4,10),(8,20,22,4,12),(10,22,22,4,14),(12,24,22,4,16),
    (14,26,22,4,18),(15,28,22,4,20),(16,28,22,4,20),(18,30,22,4,22),
    (20,32,22,4,24),(22,34,22,4,26),(25,38,22,4,30),(28,41,22,4,33),
    (30,43,22,4,34),(35,48,22,4,40),(38,51,22,4,43),(42,55,22,4,47),
)


def _ranges(column):
    values = [float(row[column]) for row in ROWS]
    bounds = (min(values), max(values))
    return {"easy": bounds, "medium": bounds, "hard": bounds}


PARAM_SPEC = {
    "catalog_row": dict(desc="zero-based key for one complete SRF catalogue row", unit="",
        range={"easy":(0,5),"medium":(0,11),"hard":(0,15)}, source=f"{SOURCE}; complete rows",
        integer=True, choices={"easy":list(range(6)),"medium":list(range(12)),"hard":list(range(16))},
        coverage=[0,5,6,15]),
    "material_code": dict(desc="0=PP natural polypropylene, 1=SA87 black elastomer", unit="",
        range={"easy":(0,0),"medium":(0,1),"hard":(0,1)}, source=f"{SOURCE}; printed material codes",
        integer=True, choices={"easy":[0],"medium":[0,1],"hard":[0,1]}, coverage=[0,1]),
    "tube_od": dict(desc="nominal tube diameter D1",unit="mm",range=_ranges(0),source=f"{SOURCE}; D1 by row",refine=True),
    "flange_od": dict(desc="retaining flange outside diameter D2",unit="mm",range=_ranges(1),source=f"{SOURCE}; D2 by row",refine=True),
    "body_height": dict(desc="overall axial height H1",unit="mm",range=_ranges(2),source=f"{SOURCE}; H1 by row",refine=True),
    "flange_height": dict(desc="retaining flange axial height H2",unit="mm",range=_ranges(3),source=f"{SOURCE}; H2 by row",refine=True),
    "mounting_bore": dict(desc="compatible mounting bore D3",unit="mm",range=_ranges(4),source=f"{SOURCE}; D3 by row",refine=True),
}


def refine(p, difficulty, rng):
    del difficulty, rng
    try:
        row = ROWS[int(p["catalog_row"])]
    except (IndexError, TypeError, ValueError):
        raise Resample from None
    (p["tube_od"], p["flange_od"], p["body_height"],
     p["flange_height"], p["mounting_bore"]) = row


def check(p):
    bad = []
    i = p.get("catalog_row")
    if not isinstance(i, int) or isinstance(i, bool) or not 0 <= i < len(ROWS):
        bad.append(f"catalog_row={i!r}: must select one complete row from {SOURCE}")
        return bad
    actual = (p["tube_od"],p["flange_od"],p["body_height"],p["flange_height"],p["mounting_bore"])
    if actual != ROWS[i]:
        bad.append(f"D1/D2/H1/H2/D3 do not match catalogue row {i} ({SOURCE})")
    if p["material_code"] not in (0,1):
        bad.append(f"material_code must encode PP or SA87 ({SOURCE})")
    if p["mounting_bore"] <= p["tube_od"] + 0.4:
        bad.append(f"D3 leaves no positive bushing wall ({SOURCE}; {PROPORTION})")
    if p["flange_od"] <= p["mounting_bore"]:
        bad.append(f"D2 must retain outside D3 mounting bore ({SOURCE})")
    if p["body_height"] <= p["flange_height"]:
        bad.append(f"H1 must exceed H2 ({SOURCE})")
    return bad
