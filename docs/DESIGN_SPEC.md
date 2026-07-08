# The Design Interface (four pieces)

A BenchCAD 2.0 family is one directory:

```
designs/<family>/
├── design.py      # the contribution — everything below lives here
└── family.json    # labels: family, standard, base_plane, description, contributor
```

`design.py` must expose exactly four things. The reference implementation
[`designs/example_tee_bracket/design.py`](../designs/example_tee_bracket/design.py)
shows all of them in ~150 commented lines.

## 1. `PARAM_SPEC: dict[str, dict]`

One entry per parameter:

| key | required | meaning |
|---|---|---|
| `desc` | ✓ | what the parameter physically is |
| `unit` | ✓ | `"mm"`, `"deg"`, `""` (counts/ratios) |
| `range` | ✓ | `{"easy": (lo, hi), "medium": (lo, hi), "hard": (lo, hi)}` — ranges may widen with difficulty; integers use `int` bounds |
| `source` | ✓ | where the range comes from: a standard table (`"ISO 4014"`), an engineering rule (`"AISC edge-distance rule"`), or `"proportion"` for conventional ratios |
| `askable` | – | `True` if a numeric QA question may target it (visible or derivable from the part) |
| `feature` | – | `True` if this parameter toggles an optional feature (drives T2/T4 edit derivation) |
| `coverage` | – | list of discrete values sampling **must** be able to produce (e.g. every pitch row of the anchored table). The validator samples ~120 draws and fails if any declared value never appears |

Difficulty semantics: **easy** = core geometry, optional features off, tight
conventional ranges. **medium** = optional features on, wider ranges.
**hard** = all features, extreme-but-valid ranges exercising the constraint
boundary.

## 2. `check(p: dict) -> list[str]`

Returns the list of violated constraints (empty = valid). This is the
engineering heart of the contribution and **the main thing humans review**.
Every constraint carries its reason:

```python
def check(p):
    bad = []
    # thin-walled plate, not a block (structural-plate convention)
    if p["web_t"] > p["web_h"] / 4:
        bad.append("web_t > web_h/4: web must be plate-like, not a block")
    # bolt-hole edge distance ≥ 1.5·d (machinery-handbook rule)
    if p["n_holes"] and p["hole_edge"] < 1.5 * p["hole_d"]:
        bad.append("hole edge distance < 1.5·d: risk of tear-out")
    return bad
```

Write constraints for: manufacturability ratios, feature clearances,
standard-table relations, and anything an engineer would reject on sight.
Cite the rule or standard in the message or a comment.

## 3. `sample(difficulty: str, rng) -> dict`

Draw a parameter set from `PARAM_SPEC[<difficulty>]` ranges that **passes
`check`** (rejection-sample internally). `rng` is a `numpy.random.Generator`;
use only `rng` for randomness — same seed must give the same parameters.

## 4. `build(p) -> cq.Workplane`

Write **plain parameterized CadQuery** — ordinary code a human reads, *not* a
code generator. Read parameters as `p["name"]`, bind the finished solid to
`result`, and `return result`:

```python
import cadquery as cq
import math
from bench2.geomlib import sprocket_profile   # optional shared curves

def build(p):
    z = p["n_teeth"]
    pts = sprocket_profile(z, p["pitch"], p["roller_d"])
    result = cq.Workplane("XY").polyline(pts).close().extrude(p["tooth_width"])
    if p["bore_d"]:                       # branch on feature params directly
        result = result.faces(">Z").workplane().hole(p["bore_d"])
    return result
```

You never format numbers into strings or emit code. `bench2` **derives** each
instance's stand-alone program from this function automatically
(`framework/bench2/derive.py`): the params it reads become module globals
(flat variables — `n_teeth = 17`), and any helper it calls (geomlib curves,
your own `_local` functions, module constants) is inlined, so the emitted
program imports only `cadquery` + `math`. The derivation is a pure text
transform — same `p` in ⇒ byte-identical program out — and `bench2 validate`
proves the derived program executes to the *same* solid as calling `build(p)`
directly, so the final coding is machine-guaranteed consistent.

Rules:
- bind `result`; use only `cq` / `math` / geomlib helpers / your own
  module-level `_helpers` and constants (no I/O, no randomness, no other imports)
- deterministic: same `p` ⇒ same geometry
- executes in the pinned environment (`cadquery==2.3.0`) to a single
  non-degenerate solid
- a heterogeneous family branches on a `feature` param (`if p["form_b"]: …`)
  in ordinary `if`/`else` — the derived program keeps the branch, evaluated
  against that instance's values

## `family.json`

```json
{
  "family": "tee_bracket",
  "standard": null,
  "base_plane": "XY",
  "description": "T-section mounting bracket: flange plate + central web, optional bolt holes.",
  "source": "structural-bracket proportions; AISC edge-distance rule for holes",
  "contributor": "your-github-handle"
}
```

`standard` is the anchoring spec (`"ISO 4014"`) or `null`; `base_plane` ∈
`XY|XZ|YZ` is the natural sketch plane of the part.

## Shared curves: `bench2.geomlib` (don't copy-paste tooth math)

Standard curve generators (sprocket tooth profile, gear involute, …) live in
`framework/bench2/geomlib/`. If your part needs one:

```python
from bench2.geomlib import inline_source, sprocket_profile

def build(p):
    lines = [
        "import math", "import cadquery as cq", "", "",
        inline_source("sprocket_profile"),   # embeds the helper's SOURCE
        "",
        f"pts = sprocket_profile({p['n_teeth']}, {p['pitch']:.3f}, ...)",
        ...
    ]
```

- The emitted program stays **stand-alone** — it carries the helper's source
  and imports only `math` + `cadquery`. Never make a generated program import
  benchcad code.
- Declare what you use in `family.json`: `"geomlib": ["sprocket_profile"]`.
  `bench2 validate` checks the declaration against the registry and confirms
  the helper is actually inlined.
- Need a curve that doesn't exist yet? Add it to `geomlib/` in the same PR
  (self-contained function, `math`-only, deterministic) — the next family
  gets it for free. See `designs/simplex_sprocket/` for the working example.

## Heterogeneous variants inside one family

Catalogs often ship the same part in several structural forms (norelem 22250:
Form A disc-with-boss vs Form B barrel hub). Model them as ONE family with a
`feature`-flagged discrete parameter (`form_b: 0/1`), branch in `build()`, and
give each variant its own constraint set in `check()` (Form B legitimately
allows bores to 0.58·df where Form A stops at 0.50·df). One family, several
stand-alone parameterized cases.

## What you do NOT write

QA items and edit pairs are derived downstream: QA templates instantiate over
`askable` parameters; edits perturb numeric parameters (T1/T3) and toggle
`feature` parameters (T2/T4). Your only jobs are the four pieces + labels.

## Machine gates (`bench2 validate`, same in CI)

1. `family.json` keys present and valid
2. the four pieces exist with the right signatures
3. per difficulty × N seeds: `sample` passes `check`; `build` executes to a
   non-degenerate solid (volume > 0)
4. determinism: same seed ⇒ byte-identical program
5. difficulty separation: the three difficulties don't produce identical programs
6. geometry-hash report: duplicate rate within the sample batch
7. coverage: every value declared in a `coverage=[...]` list is produced at
   least once across a cheap 120-draw pass — proof the standard table is
   fully covered, not just one row

`bench2 preview <family>` renders three PNGs: `preview.png` (difficulty × seed
overview), `preview_views.png` (the benchmark's four diagonal views — what the
model will actually see), and `preview_extremes.png` (the smallest and largest
sampled draw — acceptance evidence that both ends of your declared ranges
produce sane geometry; compare against the min/max rows of the dimension table
in your family issue).
