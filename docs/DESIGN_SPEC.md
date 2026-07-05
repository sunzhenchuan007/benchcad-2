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

## 4. `build(p: dict) -> str`

Return a complete, deterministic CadQuery program as a string:

- starts with `import cadquery as cq`, ends with the solid bound to `result`
- all numbers formatted from `p` with fixed rounding (e.g. `f"{v:.2f}"`) —
  same `p` must yield a byte-identical program
- no randomness, no I/O, no imports beyond `cadquery`/`math`
- must execute in the pinned environment (`cadquery==2.3.0`) to a single
  non-degenerate solid

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

`bench2 preview <family>` renders difficulty × seed as one grid PNG — check
your part looks like what it claims to be before opening the PR.
