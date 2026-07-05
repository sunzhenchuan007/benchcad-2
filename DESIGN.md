# BenchCAD 2.0 — Design Blueprint

Decision record for BenchCAD 2.0. Everything here was settled before the first
line of code; change it by PR, not by drift.

## 1. What 2.0 is

A community-grounded parametric CAD benchmark: **200 part families**, each
defined by an auditable *parametric design* whose engineering constraints are
written and reviewed by people who know the domain — not guessed by an LLM.

**Positioning: eval-first.** BenchCAD 2.0 is an evaluation benchmark. We do not
ship an official train split. Our own 1.0 experiments are the reason: training
on BenchCAD families lifts in-distribution scores dramatically (0.76 IoU) while
generalization to unseen families stays poor — training teaches a model *these
families*, not CAD. Anyone who wants training data can sample it themselves
from the public designs (see §4); the official evaluation instances and the
held-out split are drawn privately and stay clean.

## 2. Composition: families are inherited on audit; instances are never inherited

- **Family level — audit-and-promote.** The 106 BenchCAD 1.0 families do not
  enter 2.0 automatically. Each is upgraded to the explicit-parameter design
  interface (§3), its numeric ranges re-grounded against standards tables and
  engineering rules, and only then promoted. Weak families are repaired or
  dropped. Community contributions take the roster to 200.
- **Instance level — full regeneration.** No 1.0 data row is copied. Every 2.0
  instance is freshly sampled: corrected parameters require re-rendering
  anyway, and one year of public exposure means 1.0 instances must be assumed
  to be in training corpora.
- **BenchCAD 1.0 is frozen forever.** Repo, dataset, and leaderboard stay
  archived and reproducible (it is cited in published system cards). 2.0 scores
  are not comparable to 1.0 scores, by construction.

## 3. The contribution unit: an explicit parametric design ("four-piece" interface)

A family is one `design.py` exposing:

| Piece | What it is | Why it exists |
|---|---|---|
| `PARAM_SPEC` | every parameter: meaning, unit, per-difficulty range, source (standard table / engineering rule), `askable` flag | the knowledge is *inspectable*, not buried in code |
| `check(p)` | inter-parameter engineering constraints, each with its reason | **this is what humans review** — the grounding |
| `sample(difficulty, rng)` | draws a parameter set satisfying `check` | reproducible sampling |
| `build(p)` | parameters → executable CadQuery program (deterministic) | geometry |

Contributors submit **only** `design.py` + `family.json`. QA items and edit
pairs are **derived, not hand-written**: question templates instantiate over
`askable` parameters; edit pairs perturb parameters (T1/T3) and toggle optional
features (T2/T4). Derivation runs in the private factory (§4).

Machine gates (CI, same command locally): samples at every difficulty pass
`check`, programs execute to non-degenerate solids, same seed ⇒ byte-identical
program, difficulties are distinguishable, geometry hashes don't collide with
released parts. Humans review exactly two things: the constraints in
`check`/`PARAM_SPEC` (engineering truth) and the labels in `family.json`.

## 4. Public / private boundary

| Public | Private |
|---|---|
| this repo: framework, specs, **all 200 designs** (ours + community's) | the factory: rendering, QA template engine, edit derivation, ingest |
| released dataset versions on HF | unreleased families & unreleased renders |
| leaderboard + validation CI | **held-out split: private parameter draws + answers** |

All 200 designs are public and auditable — the benchmark's trust story. The
moat is not design secrecy; it is the leaderboard's authority, the private
held-out draws, and the factory. Anyone may sample public designs to make
their own training data; official eval instances are private draws, so
self-trained models still face unseen parameters.

## 5. Sampling: to geometric saturation, not to a quota

1.0 used a flat ~169 instances/family; simple families were redundant, complex
ones under-sampled. 2.0 samples each family until the **novel-geometry rate**
(fresh geometry hash per new sample) drops below threshold. Simple families
saturate around ~30–50 instances, complex ones support ~200–300. Instance
count per family is a measured property of its parameter space, not a quota.

## 6. Release artifacts

| Artifact | Size (est.) | Role |
|---|---|---|
| `full` pool | ~12–18k | complete eval pool, error analysis; **not a train set** |
| `eval` subset | ~1.5–2k (stratified: family × difficulty) | **the leaderboard metric** — affordable for everyone |
| held-out | ~1–2k, never released | anti-gaming audit; rotated if contamination is suspected |

## 7. Versioning

- Fixes merge anytime (public designs by PR; 1.0-era families via errata), but
  **released data is immutable**. Data changes accumulate into the next tagged
  release (v2.1, …) — release-train, never drip-patching, because leaderboard
  scores must stay comparable within a version.
- Every leaderboard row records the dataset version it was scored on.

## 8. Community mechanics (adopted from Terminal-Bench)

- Merged family ⇒ named credit + **co-authorship on the BenchCAD 2.0 paper**.
- Proposal-first: a family PR must link an approved Family Proposal issue
  (one-line CI check), so effort lands where the wanted-list needs it.
- DCO sign-off on every commit; repo is MIT — contributed designs can be
  absorbed and evolved by the private factory, with credit preserved.
- Contributor loop is friction-free by construction: `bench2 new` scaffolds,
  `bench2 validate` runs every machine gate locally, `bench2 preview` renders
  the part grid — the same three commands CI runs.

## 9. Repo layout (this repo) and its siblings

```
benchcad-2.0/        this repo — the 2.0 home: framework, specs, designs, CI, leaderboard
benchcad-main        the scoring engine (voxel IoU, QA scoring) — stable, shared
(private factory)    rendering, QA/edit derivation, held-out draws, HF ingest
HF: BenchCAD/*       released, versioned data artifacts
```

## 10. Roadmap — adopted from Terminal-Bench 3, deliberately deferred

TB-3's review machinery is the mature form of what §8 starts. We adopt the
shape now (AGENTS/CLAUDE/REVIEWING docs, PR + proposal templates, validate
report auto-posted on PRs, label state machine) and defer the heavy pieces
until contribution volume justifies them:

- **LLM rubric review** (`rubrics/design-review.toml` + a `bench2 check --llm`)
  grading constraint quality and citation plausibility — TB-3's `harbor check`.
- **Known-bad regression designs** (`ci_checks/test-designs/`): intentionally
  broken designs that must FAIL validation, testing the validator itself.
- **Difficulty trials** (TB-3's `/run`): sample instances, run a reference
  model, report solve rates on the PR — evidence the family isn't trivial.
- **Reviewer pool + auto-assignment** once there is more than one reviewer.
- **Public dashboard** (proposals / PRs / coverage vs the wanted-200 list),
  reading only public state.

