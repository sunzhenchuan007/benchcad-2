# BenchCAD 2.0 — Agent Guide

Guide for AI agents (and humans working with them) contributing to this repo.
Most contributors draft designs with an AI assistant — that's expected and
welcome. These are the rules that make agent-drafted contributions mergeable.

## What this repo is

The home of BenchCAD 2.0: a parametric CAD benchmark built from **explicit
parametric designs** (200 part families target). A contribution is one
`designs/<family>/design.py` exposing four pieces — `PARAM_SPEC`, `check`,
`sample`, `build` — plus a `family.json`. Read `docs/DESIGN_SPEC.md` first;
copy the shape of `designs/example_tee_bracket/design.py`.

```
DESIGN.md          decision record — why things are the way they are
docs/DESIGN_SPEC.md the four-piece interface (the contract you implement)
CONTRIBUTING.md    contributor loop
REVIEWING.md       what human review checks
framework/bench2/  the CLI: new / validate / preview
designs/           one directory per family
```

## Workflow

```bash
uv sync
uv run bench2 new <family>        # scaffold
uv run bench2 validate <family>   # every machine gate — must PASS before PR
uv run bench2 preview <family>    # render the grid — a human must look at it
```

## Hard rules for agent-drafted designs

1. **Never fabricate a source.** Every `PARAM_SPEC` range and every `check()`
   constraint cites where it comes from (a standard table, a handbook rule, a
   shop convention, or honest `"proportion"`). If you don't know a real rule,
   write `"proportion"` — do not invent an ISO number. Fabricated citations
   are the fastest way to get a PR rejected and flagged.
2. **Constraints must be engineering-true, not validator-appeasing.** Never
   weaken `check()` to make `sample()` pass. If sampling fails, the ranges
   and constraints disagree — fix the ranges.
3. **Determinism is absolute.** Randomness only through the `rng` argument;
   numbers formatted with fixed rounding in `build`. Same seed ⇒ byte-identical
   program. `bench2 validate` enforces this.
4. **A human must run `bench2 preview` and look at the image** before the PR
   is opened. Geometry that executes can still be nonsense; the render is the
   sanity check machines can't do.
5. **Don't touch anything outside `designs/<your-family>/`** in a family PR.
   One PR = one family.
6. Commits are DCO-signed (`git commit -s`) by the human contributor.

## What review will do with your output

Machines re-run everything `bench2 validate` checks. Humans audit exactly two
things: whether the constraints in `check()`/`PARAM_SPEC` are *true*, and
whether `family.json` labels are correct. Optimize for an auditable design:
short, cited, physically-motivated constraints beat clever code.
