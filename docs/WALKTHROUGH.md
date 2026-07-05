# Walkthrough: contributing a family, end to end

This is the complete workflow, demonstrated on a real family —
[`designs/simplex_sprocket/`](../designs/simplex_sprocket/) — built from a real
manufacturer datasheet. Follow it step by step for your own part; every file it
mentions exists in this repo as a working example.

```
input (datasheet/standard) → proposal → scaffold → four pieces → VERIFY → sign → PR → credit
```

## 0. Input: start from something real

A family starts from a **real engineering source**, not imagination:

- a manufacturer datasheet (our example: *norelem 22250 — sprockets single
  5/8" × 3/8" DIN ISO 606, ready to install*),
- a standard's table/equations (ISO 606 Table 1 + §8.2), and/or
- a shop rule you can cite.

From the source you extract three things:
1. **the parameter list** — what varies across the catalog (tooth count, bore,
   hub Ø, …),
2. **the relations** — formulas tying them together (dp = p/sin(π/z)),
3. **the limits** — what combinations the catalog/standard never sells
   (these become `check()`).

Record the mapping as you go — it becomes your family's `NOTES.md`
([example](../designs/simplex_sprocket/NOTES.md)): one table, datasheet symbol
→ meaning → formula → your parameter. That file is what makes review fast.

## 1. Propose (before you build)

Open a **Family Proposal** issue (template provided): part, why it adds
coverage, parameter sketch, the 2–3 constraints you already know, source.
Wait for the `approved` label — it protects you from building something
duplicate or out of scope.

## 2. Scaffold

```bash
uv sync
uv run bench2 new my_family        # designs/my_family/{design.py, family.json}
```

## 3. Fill the four pieces (copy the reference's shape)

Two references show the two source patterns — copy whichever matches yours:

| | [`example_tee_bracket`](../designs/example_tee_bracket/design.py) | [`simplex_sprocket`](../designs/simplex_sprocket/design.py) |
|---|---|---|
| pattern | free proportions | **table-driven** (standards rows) |
| PARAM_SPEC | independent ranges | jointly-sampled table row + free params |
| check() | proportion rules (1.5·d edge distance…) | row-membership + z ≥ 9 + rim/hub walls |
| build() | box/hole/chamfer | standard's tooth equations → polyline |

Rules that make review painless (details in [DESIGN_SPEC.md](DESIGN_SPEC.md)):
- every `PARAM_SPEC.source` and `check()` message cites the table/rule — or
  honestly says `"proportion"`; **never invent a citation**
- randomness only through `rng`; numbers formatted with fixed rounding
- `askable=True` on parameters QA may target; `feature=True` on toggles

## 4. VERIFY — three layers, all before the PR

**Layer 1 — machine gates** (same command CI runs):
```bash
uv run bench2 validate my_family
```
```
✓ family.json: keys + base_plane valid
✓ PARAM_SPEC: 8 params, all entries complete
✓ easy/medium/hard: 4/4 seeds sample+check+build+execute clean
✓ difficulty separation: difficulties produce distinct programs
✓ geometry novelty: 12/12 unique shapes (0% duplicate)
PASS
```
What each gate proves: constraints and ranges agree (sampling converges);
**every sampled value stays inside its own declared `PARAM_SPEC` range** (the
spec is a contract — downstream QA/edit derivation relies on it; this gate
caught a real bug in this very reference, where proportional bore sampling
escaped the declared range on large sprockets); programs execute to
non-degenerate solids; same seed ⇒ byte-identical program (determinism);
tiers differ; you're not cloning one shape.

**Layer 2 — your eyes**:
```bash
uv run bench2 preview my_family    # difficulty × seed grid PNG
```
Machines can't tell a sprocket from a starfish. Look at the grid: is it the
part? Are easy/medium/hard plausible tiers of the *same* part?

**Layer 3 — numbers vs the source** (the step that catches wrong formulas):
pick 2–3 catalog rows and check your derived values against them by hand.
From our example (norelem D1 column vs `dp = p/sin(π/z)`):

| z | formula | catalog D1 |
|---|---|---|
| 10 | 51.372 | 51,37 ✓ |
| 13 | 66.335 | 66,32 ✓ |
| 25 | 126.66 | 126,66 ✓ |

Same for the DIN 6885 keyway rows (bore 16→5, 19→6, 25→8 — all match).
Put these spot-checks in `NOTES.md`: they are the strongest evidence your
design is *true*, not just runnable.

## 5. Sign your work

- `family.json` → `"contributor": "your-github-handle"`
- add your row to [`CONTRIBUTORS.md`](../CONTRIBUTORS.md)
- commit with DCO: `git commit -s`

## 6. PR

One PR = one family = `designs/my_family/` only (`design.py`, `family.json`,
`NOTES.md`, `preview.png`). The PR template checklist mirrors everything
above. CI re-runs the machine gates and posts the report + preview on the PR;
a maintainer then reviews exactly two things (see [REVIEWING.md](../REVIEWING.md)):
are your constraints **true**, and are your labels correct.

## 7. After merge

Your row in CONTRIBUTORS.md is permanent; the release that ships your family
credits you in the dataset card, and merged-family contributors are invited as
co-authors on the BenchCAD 2.0 paper. Instance generation (rendering, QA,
edits, held-out draws) happens downstream in the maintainers' pipeline — your
design is the contribution.
