# Contributing a family to BenchCAD 2.0

A contribution is **one file of engineering knowledge**: a parametric design
whose ranges and constraints are true. You do not write QA items, edit pairs,
or rendering code — those are derived downstream from your design.

**Merged family ⇒ your row in [CONTRIBUTORS.md](CONTRIBUTORS.md), named credit
in the dataset card + co-authorship on the BenchCAD 2.0 paper.**

**Start here → [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md)** — the full
workflow demonstrated on a real family (`simplex_sprocket`, built from the
norelem 22250 datasheet), including all three verification layers.

## The loop

```bash
uv sync                              # once
uv run bench2 new <family>           # scaffold designs/<family>/
# fill in the four pieces (see docs/DESIGN_SPEC.md and designs/example_tee_bracket/)
uv run bench2 validate <family>      # every machine gate, locally
uv run bench2 preview <family>       # look at your part before anyone else does
# open a PR — CI runs the same validate + posts your preview
```

## What review looks at

Machines already checked structure, determinism, executability, and geometry.
A maintainer reviews exactly two things:

1. **`check()` + `PARAM_SPEC`** — are the constraints and ranges *true*?
   Cite your sources (standard tables, handbook rules, shop conventions).
2. **`family.json`** — are the family / standard / base-plane labels correct?

## Rules

- One PR = one family. `design.py` + `family.json` only.
- Every commit is DCO-signed (`git commit -s`).
- The repo is MIT: merged designs may be evolved by the maintainers' pipeline
  (held-out draws, future tiers) with your credit preserved.
- Instances, QA, edits, and the held-out split are generated privately by the
  maintainers; released data is versioned on Hugging Face.

## What else you can contribute

- **Bugs** — *Bug report* form (a design, the CLI, CI, or docs); a fix PR
  links the issue with `Closes #N`, same flow as families.
- **Framework features** — *Feature request* form; big ideas belong to a
  [roadmap](https://github.com/BenchCAD-org/benchcad-2/issues/21) workstream's
  `[tracking]` issue.
- **Triage** — run the [evidence check](docs/TRIAGE.md) on `needs-triage`
  issues, or complete a `needs-evidence` package; both are recorded on the
  [provenance board](CONTRIBUTORS.md).
- **Review** — verify a family PR per [REVIEWING.md](REVIEWING.md); the
  approving reviewer is credited as the family's verifier.
- **Errata against released 1.0 data** — the 1.0 generators are private, so
  file an issue with the record id + the engineering reason; fixes land in the
  next dataset version.

Every issue starts `needs-triage`; after the [TRIAGE.md](docs/TRIAGE.md) check
it becomes `triaged` (claimable) or `needs-evidence` (needs your help). The
full station-by-station lifecycle — including exactly where each role is
recorded — is [docs/SOP.md](docs/SOP.md).
