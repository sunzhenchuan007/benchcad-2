# Reviewing a family PR

Every design PR must pass the automated gates and one maintainer review.
Machines already proved the design *runs*; your job is to judge whether it is
*true*. Budget: ~15 minutes per family.

## What is already machine-checked (don't re-do it)

`bench2 validate` in CI: file structure, the four pieces exist, every
difficulty × seed samples within constraints, programs execute to
non-degenerate solids, same seed ⇒ byte-identical program, difficulties are
distinct, geometry-novelty report. If CI is red, stop — back to the author.

## Review order

1. **Look at the preview** (CI artifact, or run `bench2 preview <family>`).
   Does the part look like what `family.json` says it is? Are easy/medium/hard
   visually plausible tiers of the same part — not three different parts, not
   identical clones?
2. **Audit `check()` — the heart of the review.** For every constraint:
   - Is it *engineering-true*? (Would a machinist/designer agree?)
   - Is the cited rule real? Spot-check any standard number the author cites.
     **Fabricated citations ⇒ reject the PR**, not just the line.
   - What's *missing*? Think about how this part fails in the real world
     (tear-out, thin walls, tool clearance, unstable proportions) and check
     whether those failure modes are constrained.
3. **Audit `PARAM_SPEC`.** Ranges physically sensible per tier; `source`
   fields specific (a table, a rule, or honest `"proportion"`); `askable`
   only on parameters actually visible/derivable from the part; `feature`
   on the optional-feature toggles.
4. **Check `family.json`.** Family name accurate, `standard` correct or null,
   `base_plane` matches the build, description honest.
5. Scope: PR touches only `designs/<family>/`; commits DCO-signed.

## Labels

`new design` (auto on open) → `waiting on reviewer` (CI green) →
`waiting on author` (changes requested) → merge when approved.

## After merge

Add the contributor to the credit roll (dataset card + paper author list per
CONTRIBUTING.md). Ingest into the private factory happens on the maintainer
side; the public design directory is the record of the contribution.
