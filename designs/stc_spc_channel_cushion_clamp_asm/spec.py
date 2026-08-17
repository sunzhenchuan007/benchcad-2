"""Catalogue-row sampling contract for STAUFF STC/SPC channel clamps."""

from bench2 import Resample

SOURCE = "STAUFF Catalogue 1 - STAUFF Clamps, English, 06/2026, pp. 172-173"
PROPORTION = "proportion (unmarked dimensions identified in Issue #88)"

# code, D1, Bmin, C, D, E, thread (0=1/4-20, 1=5/16-18, 2=3/8-16)
ROWS = (
    ("STC-025",6.4,15.7,5.6,28.2,2.0,0),("STC-037",8.0,19.1,7.1,31.5,2.0,0),
    ("STC-050",12.7,22.1,8.6,34.5,2.0,0),("SPC-025",13.5,23.1,9.1,35.8,2.0,0),
    ("STC-062",16.0,25.4,10.4,38.1,2.0,0),("SPC-037",17.2,27.2,11.4,40.4,2.0,0),
    ("STC-075",19.0,33.8,13.5,45.2,2.0,0),("SPC-050",21.3,36.8,15.0,48.5,2.0,0),
    ("STC-087",22.2,36.8,14.7,48.5,2.0,0),("STC-100",25.4,42.2,16.8,51.6,2.8,0),
    ("SPC-075",26.9,45.5,18.3,54.9,2.8,0),("STC-125",32.0,48.8,19.8,58.4,2.8,0),
    ("SPC-100",33.7,56.4,23.1,69.9,3.0,1),("STC-150",38.0,56.4,23.1,69.9,3.0,1),
    ("SPC-125",42.0,62.7,26.2,77.0,3.0,1),("SPC-150",48.3,62.7,29.5,83.3,3.0,1),
    ("STC-200",50.8,69.1,29.5,83.3,3.0,1),("SPC-200",60.3,69.1,35.8,96.0,3.0,1),
    ("STC-250",63.5,88.1,38.9,102.4,3.0,1),("STC-262",66.7,88.1,38.9,102.4,3.0,1),
    ("SPC-250",73.0,94.5,42.2,108.5,3.0,1),("STC-300",76.2,100.8,45.2,114.8,3.0,1),
    ("SPC-300",88.9,110.7,50.0,124.7,3.0,2),("SPC-350",102.0,126.2,57.9,140.5,3.0,2),
    ("SPC-400",114.0,138.9,64.3,153.2,3.0,2),("SPC-500",140.0,164.3,77.0,178.6,3.6,2),
    ("SPC-600",168.0,189.7,89.7,204.0,3.6,2),
)


def _ranges(column):
    values = [float(row[column]) for row in ROWS]
    bounds = (min(values), max(values))
    return {"easy": bounds, "medium": bounds, "hard": bounds}


PARAM_SPEC = {
    "catalog_row": dict(desc="zero-based key for one complete printed STC/SPC row", unit="",
        range={"easy":(0,8),"medium":(0,21),"hard":(0,26)},
        source=f"{SOURCE}; complete row labels, no interpolation", integer=True,
        choices={"easy":list(range(9)),"medium":list(range(22)),"hard":list(range(27))},
        coverage=[0,3,12,26]),
    "material_code": dict(desc="0=W32 zinc steel, 1=W4 AISI 304, 2=W5 AISI 316", unit="",
        range={"easy":(0,0),"medium":(0,1),"hard":(0,2)},
        source=f"{SOURCE}; W32/W4/W5 ordering options", integer=True,
        choices={"easy":[0],"medium":[0,1],"hard":[0,1,2]}, coverage=[0,1,2]),
    "tube_od": dict(desc="tube outside diameter D1",unit="mm",range=_ranges(1),source=f"{SOURCE}; D1 coupled to row",refine=True),
    "install_width_min": dict(desc="minimum installation width B",unit="mm",range=_ranges(2),source=f"{SOURCE}; B min coupled to row",refine=True),
    "c": dict(desc="tube-axis height C",unit="mm",range=_ranges(3),source=f"{SOURCE}; C coupled to row",refine=True),
    "height_d": dict(desc="overall height D",unit="mm",range=_ranges(4),source=f"{SOURCE}; D coupled to row",refine=True),
    "edge_e": dict(desc="catalogued clamp-edge thickness E",unit="mm",range=_ranges(5),source=f"{SOURCE}; E coupled to row",refine=True),
    "thread_code": dict(desc="0=1/4-20, 1=5/16-18, 2=3/8-16 UNC",unit="",
        range={"easy":(0,2),"medium":(0,2),"hard":(0,2)},source=f"{SOURCE}; G coupled to row",integer=True,refine=True),
}


def refine(p, difficulty, rng):
    del difficulty, rng
    try:
        row = ROWS[int(p["catalog_row"])]
    except (IndexError, TypeError, ValueError):
        raise Resample from None
    (p["tube_od"], p["install_width_min"], p["c"], p["height_d"],
     p["edge_e"], p["thread_code"]) = row[1:]


def check(p):
    bad = []
    i = p.get("catalog_row")
    if not isinstance(i, int) or isinstance(i, bool) or not 0 <= i < len(ROWS):
        bad.append(f"catalog_row={i!r}: must select one complete row from {SOURCE}")
        return bad
    expected = ROWS[i][1:]
    actual = (p["tube_od"],p["install_width_min"],p["c"],p["height_d"],p["edge_e"],p["thread_code"])
    if actual != expected:
        bad.append(f"D1/B/C/D/E/thread do not match complete row {ROWS[i][0]} ({SOURCE})")
    if p["material_code"] not in (0,1,2):
        bad.append(f"material_code must be W32/W4/W5 encoded 0/1/2 ({SOURCE})")
    if p["install_width_min"] <= p["tube_od"] + 2.0*p["edge_e"] + 0.7:
        bad.append(f"B leaves no positive cushion wall/clearance ({PROPORTION})")
    if p["c"] <= p["tube_od"]/2.0 + 0.5:
        bad.append(f"C leaves no positive cushion wall below the tube bore ({SOURCE}; {PROPORTION})")
    if p["height_d"] <= p["c"] + p["install_width_min"]/2.0:
        bad.append(f"D must clear wrapped profile and stud ear ({SOURCE}; {PROPORTION})")
    return bad
