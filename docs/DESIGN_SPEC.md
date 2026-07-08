# The Design Interface (part + spec)

A BenchCAD 2.0 family is one directory with two source files — the **part** you
draw, and the **spec** that varies it across the benchmark:

```
designs/<family>/
├── part.py       # the parametric part — a human writes this: build(<named params>)
├── spec.py       # the benchmark generator — PARAM_SPEC, check(), optional refine()
└── family.json   # labels: family, standard, base_plane, description, contributor
```

The split is deliberate. `part.py` reads like a part a person authored — named
parameters, ordinary CadQuery, no dictionaries and no code generation. `spec.py`
holds the machinery that turns one part into a difficulty-graded family; **the
framework does the sampling**, so you never hand-write a generator loop. The
reference implementations are
[`designs/example_tee_bracket/`](../designs/example_tee_bracket/) (no coupling)
and [`designs/simplex_sprocket/`](../designs/simplex_sprocket/) (table-driven +
coupled).

---

## `part.py` — `build(<named params>) -> cq.Workplane`

Write **plain parametric CadQuery**: named arguments, build the solid, bind it
to `result`, return it. This is the file a human reads.

```python
import cadquery as cq
import math
from bench2.geomlib import sprocket_profile     # shared curves — call them directly

def build(pitch, roller_d, tooth_width, n_teeth, bore_d, form_b=0):
    pts = sprocket_profile(n_teeth, pitch, roller_d)
    result = cq.Workplane("XY").polyline(pts).close().extrude(tooth_width)
    if form_b:                                   # branch on a feature param directly
        result = result.faces(">Z").workplane().circle(bore_d).extrude(tooth_width)
    result = result.faces(">Z").workplane().hole(bore_d)
    return result
```

You never format numbers into strings or emit code. For a concrete instance
`bench2` **derives** the stand-alone program a model is asked to produce
(`framework/bench2/derive.py`): each `build()` argument becomes a flat module
global (`n_teeth = 17`), and every helper the body calls — a geomlib curve, one
of your own `_local` functions, a module constant — is inlined, so the emitted
program imports only `cadquery` + `math`. The derivation is a pure text
transform (same params in ⇒ byte-identical program out), and `bench2 validate`
proves the derived program executes to the *same* solid as calling `build()`
directly — the final coding is machine-guaranteed consistent.

Rules:
- **named parameters** — every argument must be declared in `spec.py`'s `PARAM_SPEC`
- bind `result`; use only `cq` / `math` / geomlib helpers / your own module-level
  `_helpers` and constants (no I/O, no randomness, no other imports)
- deterministic: same arguments ⇒ same geometry, one non-degenerate solid, in
  the pinned environment (`cadquery==2.3.0`)
- a heterogeneous family branches on a `feature` param (`if form_b: …`) in
  ordinary `if`/`else` — the derived program keeps the branch, evaluated against
  that instance's values

---

## `spec.py` — the benchmark generator

### 1. `PARAM_SPEC: dict[str, dict]`

One entry per `build()` parameter. `desc/unit/range/source` are always
required; the remaining keys tell the framework **how to draw** the value:

| key | required | meaning |
|---|---|---|
| `desc` | ✓ | what the parameter physically is |
| `unit` | ✓ | `"mm"`, `"deg"`, `""` (counts/ratios) |
| `range` | ✓ | `{"easy": (lo, hi), "medium": (lo, hi), "hard": (lo, hi)}` — the contract every sampled value must satisfy; may widen with difficulty |
| `source` | ✓ | where the range comes from: a standard table (`"ISO 4014"`), an engineering rule, or `"proportion"` |
| `integer` | – | draw as an integer in `range` (default is a float, 2 dp) |
| `choices` | – | draw from a discrete set — `[0, 2, 4]`, or per-difficulty `{"easy": [0], "hard": [2, 4]}` |
| `refine` | – | **not drawn** by the framework — computed in `refine()` (a coupled parameter). Still declares a `range` for the contract |
| `askable` | – | `True` if a numeric QA question may target it |
| `feature` | – | `True` if it toggles an optional feature (drives edit derivation) |
| `coverage` | – | list of values sampling **must** be able to produce (e.g. every pitch row of the table); the validator fails if any never appears in ~120 draws |

Difficulty semantics: **easy** = core geometry, features off, tight ranges.
**medium** = features on, wider ranges. **hard** = all features, extreme-but-
valid ranges that exercise the constraint boundary.

### 2. `check(p: dict) -> list[str]`

Returns the list of violated constraints (empty = valid). This is the
engineering heart of the contribution and **the main thing humans review**.
Every constraint carries its reason — cite the rule or standard:

```python
def check(p):
    bad = []
    if p["web_t"] > p["web_h"] / 4:              # plate-like, not a block
        bad.append("web_t > web_h/4: web must be plate-like (structural convention)")
    return bad
```

The framework calls `check()` on every draw and rejects failures — you write the
constraints, not the loop.

### 3. `refine(p, difficulty, rng) -> None`  *(optional)*

Only needed when parameters are **coupled** — one value computed from others (a
bore bounded by a root circle, a hub sized off the bore) or drawn jointly (a
real table row, not free numbers). The framework draws every non-`refine`
parameter first, then calls `refine()` to fill the `refine=True` ones **in
place**. Write just the coupling — no rejection loop:

```python
from bench2 import Resample

def refine(p, difficulty, rng):
    _, pitch, d1, b1 = _ISO606[int(rng.integers(len(_ISO606)))]   # one real chain row
    p["pitch"], p["roller_d"], p["tooth_width"] = pitch, d1, b1
    df = _root_circle(pitch, p["n_teeth"], d1)
    lo, hi = PARAM_SPEC["bore_d"]["range"][difficulty]
    p["bore_d"] = round(float(rng.uniform(max(lo, 0.2 * df), min(hi, 0.45 * df))), 1)
    if min(hi, 0.45 * df) <= max(lo, 0.2 * df):
        raise Resample          # this base draw admits no valid bore — resample
```

Use only `rng` for randomness (same seed ⇒ same parameters). Raise
`bench2.Resample` to discard an infeasible base draw; the framework resamples.
Families with no coupling (like `example_tee_bracket`) omit `refine()` entirely.

---

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
`XY|XZ|YZ` is the natural sketch plane. A family that calls geomlib helpers adds
`"geomlib": ["sprocket_profile", "keyway_dims"]`.

## Shared standards: `bench2.geomlib` (don't copy-paste tooth math)

Reusable curve generators and standard tables (sprocket tooth profile, gear
involute, DIN 6885 keyway seat, …) live in `framework/bench2/geomlib/`. Import
and **call them directly** — in both `build()` (part.py) and any constraint
(spec.py). The deriver inlines the helper's source into each emitted program, so
it stays stand-alone (only `math` + `cadquery`):

```python
from bench2.geomlib import keyway_dims

def build(..., bore_d, has_keyway=0):
    if has_keyway:
        kw, kd = keyway_dims(bore_d)             # DIN 6885 seat — inlined on derive
        ...
```

- Declare what you use in `family.json`: `"geomlib": ["keyway_dims"]`. `bench2
  validate` checks the names against the registry and confirms they are inlined.
- A geomlib helper must be **self-contained** (only `math`/builtins, no module
  state, deterministic) so it runs verbatim inside an emitted program.
- Need a curve that doesn't exist yet? Add it to `geomlib/` in the same PR — the
  next family gets it for free.

**Part-specific** helper shared between `build()` and `check()` (a hole layout
used by both)? Put it in `part.py` and import it in `spec.py` with
`from part import _hole_layout` — spec may depend on the part, never the reverse.
One definition keeps build and check from drifting.

## Heterogeneous variants inside one family

Catalogs ship the same part in several forms (norelem 22250: Form A disc-with-
boss vs Form B barrel hub). Model them as ONE family with a `feature`-flagged
discrete parameter (`form_b: 0/1`, drawn via `choices`), branch in `build()`,
and give each variant its own constraints in `check()` (Form B legitimately
allows bores to 0.58·df where Form A stops at 0.50·df).

## What you do NOT write

No sampling loop (the framework samples from `PARAM_SPEC`), and no QA items or
edit pairs — those are derived downstream (`askable` params seed numeric QA;
`feature` params drive add/remove edits). Your jobs are `part.py`, `spec.py`,
and `family.json`.

## Machine gates (`bench2 validate`, same in CI)

1. `family.json` keys present and valid
2. `part.py:build` + `spec.py:PARAM_SPEC/check` exist; every `build()` parameter
   is declared in `PARAM_SPEC`
3. per difficulty × N seeds: the sampler draws params that pass `check`, the
   sampled value stays inside its declared `range` (the contract), and the
   derived program executes to a non-degenerate solid
4. determinism: same seed ⇒ byte-identical derived program
5. difficulty separation: the three difficulties don't produce identical programs
6. geometry-hash report: duplicate rate within the sample batch
7. coverage: every value in a `coverage=[...]` list appears across a 120-draw pass
8. geomlib: declared helpers exist in the registry and are inlined in the program

`bench2 preview <family>` renders three PNGs: `preview.png` (difficulty × seed
overview), `preview_views.png` (the four diagonal benchmark views — what the
model sees), and `preview_extremes.png` (smallest & largest sampled draw —
acceptance evidence that both ends of your declared ranges produce sane
geometry).
