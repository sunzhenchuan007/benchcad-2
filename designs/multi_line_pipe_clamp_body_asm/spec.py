"""Joint catalogue-row sampling for the STAUFF MLC family."""

from bench2 import Resample


_ROWS = {
    (2, 1): (60.5, 20.0, 40.0, 27.0, 2), (2, 2): (78.5, 29.0, 58.0, 33.0, 2),
    (2, 3): (92.5, 36.0, 72.0, 37.0, 2), (3, 1): (56.0, 20.0, 20.0, 27.0, 2),
    (3, 2): (85.0, 29.0, 29.0, 33.0, 2), (3, 3): (106.0, 36.0, 36.0, 37.0, 2),
    (4, 1): (76.0, 20.0, 40.0, 27.0, 2), (4, 2): (114.0, 29.0, 58.0, 33.0, 2),
    (4, 3): (142.0, 36.0, 72.0, 37.0, 2), (6, 1): (116.0, 20.0, 40.0, 27.0, 3),
    (6, 2): (172.0, 29.0, 58.0, 33.0, 3), (6, 3): (214.0, 36.0, 72.0, 37.0, 3),
}
_DS = {1: (6.0, 6.4, 8.0, 9.5, 10.0, 12.0),
       2: (10.0, 12.0, 12.7, 13.5, 14.0, 15.0, 16.0, 17.2, 18.0),
       3: (15.0, 16.0, 17.2, 18.0, 19.0, 20.0, 21.3, 22.0, 23.0, 25.0, 25.4)}
_CAT = "STAUFF Catalogue 1 - STAUFF Clamps, 06/2026, pp. 114-117"


def _r(easy, medium, hard):
    return {"easy": easy, "medium": medium, "hard": hard}


PARAM_SPEC = {
    "line_count": {"desc": "Number of equal-diameter tube seats", "unit": "", "range": _r((2, 4), (2, 6), (2, 6)), "source": _CAT, "integer": True, "choices": _r([2, 3, 4], [2, 3, 4, 6], [2, 3, 4, 6]), "coverage": [2, 3, 4, 6]},
    "group": {"desc": "STAUFF group selecting one coupled dimensional row", "unit": "", "range": _r((1, 2), (1, 3), (1, 3)), "source": _CAT, "integer": True, "choices": _r([1, 2], [1, 2, 3], [1, 2, 3]), "coverage": [1, 2, 3]},
    "tube_od": {"desc": "Common pipe/tube outside diameter D", "unit": "mm", "range": _r((6.0, 18.0), (6.0, 25.4), (6.0, 25.4)), "source": _CAT, "refine": True, "coverage": [6.0, 15.0, 18.0, 25.4]},
    "length": {"desc": "Overall body length L1", "unit": "mm", "range": _r((56.0, 114.0), (56.0, 214.0), (56.0, 214.0)), "source": _CAT, "refine": True},
    "pitch": {"desc": "Adjacent tube-axis pitch L2", "unit": "mm", "range": _r((20.0, 29.0), (20.0, 36.0), (20.0, 36.0)), "source": _CAT, "refine": True},
    "span": {"desc": "Fastener passage spacing L3", "unit": "mm", "range": _r((20.0, 58.0), (20.0, 72.0), (20.0, 72.0)), "source": _CAT, "refine": True},
    "height": {"desc": "Total assembled height H", "unit": "mm", "range": _r((27.0, 33.0), (27.0, 37.0), (27.0, 37.0)), "source": _CAT, "refine": True},
    "fastener_passage_count": {"desc": "Through-fastener interfaces B", "unit": "", "range": _r((2, 2), (2, 3), (2, 3)), "source": _CAT, "integer": True, "refine": True},
    "body_depth": {"desc": "Unmarked body extrusion depth", "unit": "mm", "range": _r((16.0, 23.2), (16.0, 28.8), (16.0, 28.8)), "source": "proportion", "refine": True},
    "passage_d": {"desc": "Unmarked smooth fastener passage diameter", "unit": "mm", "range": _r((4.5, 6.0), (4.5, 8.0), (4.5, 8.0)), "source": "proportion", "refine": True},
    "counterbore_d": {"desc": "Unmarked outside-face counterbore diameter", "unit": "mm", "range": _r((8.0, 12.0), (8.0, 16.0), (8.0, 16.0)), "source": "proportion", "refine": True},
    "counterbore_depth": {"desc": "Unmarked counterbore depth", "unit": "mm", "range": _r((3.0, 4.0), (3.0, 5.0), (3.0, 5.0)), "source": "proportion", "refine": True},
    "thread_nominal_d": {"desc": "Proportion-selected lower-half tapped-hole nominal diameter (M4/M6/M8)", "unit": "mm", "range": _r((4.0, 6.0), (4.0, 8.0), (4.0, 8.0)), "source": "proportion; ISO 261 coarse metric size", "refine": True},
    "thread_pitch": {"desc": "ISO 261 coarse pitch coupled to M4/M6/M8 tapped-hole size", "unit": "mm", "range": _r((0.7, 1.0), (0.7, 1.25), (0.7, 1.25)), "source": "ISO 261 coarse series", "refine": True},
    "tension_clearance": {"desc": "Visible split-plane tension clearance", "unit": "mm", "range": _r((1.0, 1.0), (1.0, 1.0), (1.0, 1.0)), "source": "STAUFF pp. 114-117 drawing nominal 1 mm", "refine": True},
}


def refine(p, difficulty, rng):
    del difficulty
    key = (int(p["line_count"]), int(p["group"]))
    if key not in _ROWS:
        raise Resample
    p["length"], p["pitch"], p["span"], p["height"], p["fastener_passage_count"] = _ROWS[key]
    ds = _DS[key[1]]
    # Make catalogue extremes and overlapping cross-group diameters auditable
    # while retaining row-coupled variation for the intermediate topologies.
    required_d = {(2, 1): 6.0, (2, 2): 18.0, (2, 3): 15.0,
                  (6, 1): 12.0, (6, 2): 10.0, (6, 3): 25.4}
    p["tube_od"] = required_d.get(key, float(ds[int(rng.integers(0, len(ds)))]))
    p["body_depth"] = {1: 16.0, 2: 23.2, 3: 28.8}[key[1]]
    p["passage_d"] = {1: 4.5, 2: 6.0, 3: 8.0}[key[1]]
    p["counterbore_d"] = {1: 8.0, 2: 12.0, 3: 16.0}[key[1]]
    p["counterbore_depth"] = {1: 3.0, 2: 4.0, 3: 5.0}[key[1]]
    p["thread_nominal_d"] = {1: 4.0, 2: 6.0, 3: 8.0}[key[1]]
    p["thread_pitch"] = {1: 0.7, 2: 1.0, 3: 1.25}[key[1]]
    p["tension_clearance"] = 1.0


def check(p):
    bad = []
    key = (int(p["line_count"]), int(p["group"]))
    expected = _ROWS.get(key)
    if expected is None:
        return ["line_count/group is not a catalogue MLC row (STAUFF pp. 114-117)"]
    for name, actual, required in zip(("L1", "L2", "L3", "H", "B"), (p["length"], p["pitch"], p["span"], p["height"], p["fastener_passage_count"]), expected):
        if actual != required:
            bad.append(f"{name} is not the selected catalogue row (STAUFF pp. 114-117)")
    if p["tube_od"] not in _DS[key[1]]:
        bad.append("tube_od is not listed for selected group (STAUFF pp. 114-117)")
    if p["tube_od"] >= p["pitch"]:
        bad.append("tube_od >= L2: adjacent seats overlap (catalogue geometry)")
    # Passage axes sit midway between neighbouring seats in all four drawings.
    # Keep the through interface outside the smooth seat even at maximum D.
    if p["tube_od"] / 2.0 + p["passage_d"] / 2.0 >= p["pitch"] / 2.0:
        bad.append("fastener through passage breaks into tube seat (catalogue layout/proportion)")
    if not p["passage_d"] < p["counterbore_d"] < p["pitch"]:
        bad.append("passage/counterbore hierarchy invades adjacent seat (proportion)")
    if p["body_depth"] <= p["counterbore_d"]:
        bad.append("body_depth lacks counterbore material (proportion)")
    expected_thread = {1: (4.0, 0.7), 2: (6.0, 1.0), 3: (8.0, 1.25)}[key[1]]
    if (p["thread_nominal_d"], p["thread_pitch"]) != expected_thread:
        bad.append("tapped-hole M size/pitch does not match group proportion and ISO 261")
    if p["thread_nominal_d"] > p["passage_d"]:
        bad.append("lower tapped-hole nominal exceeds upper clearance passage (proportion)")
    if 2 * p["counterbore_depth"] >= p["height"] - p["tension_clearance"]:
        bad.append("counterbores consume half-height (proportion)")
    if p["tension_clearance"] != 1.0:
        bad.append("clearance is not drawing nominal 1 mm (STAUFF pp. 114-117)")
    return bad
