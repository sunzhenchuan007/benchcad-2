# Reviewing a family PR

Every design PR must pass the automated gates and one human review by someone
who is not the author (CONTRIBUTING.md rule 3). Machines already proved the
design *runs*; your job is to judge whether it is *true*. Budget: ~15 minutes.

## What is already machine-checked (don't re-do it)

`bench2 validate` in CI: file structure, `part.py` + `spec.py` exist, every
difficulty × seed samples within constraints **and within the declared
PARAM_SPEC ranges** (spec-contract), programs execute to non-degenerate
solids, same seed ⇒ byte-identical program, difficulties distinct, geometry
novelty, table `coverage`, geomlib declared + inlined. For an assembly
family, three more, taken from the exported STEP: the body count equals
`family.json` `"solids"`, every body has positive volume and passes
`BRepCheck`, and no two bodies share volume. CI red = stop, back to the
author. CI green = start here.

Note what that last one does **not** cover: bodies that do not overlap can
still be wrong together — floating unretained, mating on the wrong face,
teeth that never mesh. Non-overlap is now machine-checked; *fit* is still
yours (direction 4 below).

## The six directions a review judges

Both when writing a family PR and when reviewing one, judge these six
directions (the "Review order" below is the step-by-step how-to):

1. **Table & parameterization.** The dimension table is real and traceable —
   standard + page, consistent with the drawing attached next to it, columns
   named physical-quantity + symbol (`height_G`, not `G`), untabulated values
   honestly `"proportion"`, nothing fabricated. The spec uses the table
   correctly: rows locked (no cross-row mixes), `coverage` reaches the whole
   table, discrete catalog ladders never sampled continuously.
2. **Review material.** The issue carries a true 2D orthographic drawing + a
   product photo; the PR re-embeds them and ships the renders regenerated at
   the current head; an assembly adds `preview_parts.png`. The four benchmark
   views must suffice to reconstruct the geometry — no "solid outside,
   structure inside": fully enclosed internals are either not scored bodies
   or get a cutaway view. The code reads against the drawing: variables carry
   the drawing symbol, the drawing's relations appear as code, equation-heavy
   families ship `NOTES.md`.
3. **Geometry vs table/drawing.** Recompute at least one row; measure the
   built bbox against the declared envelope (collapsed or protruding geometry
   still passes validate); match the drawing's profiles feature by feature;
   eyeball the min/max extremes — many failures only appear at the ends of
   the size range.
4. **Real function & fit.** Every functional interface must work
   geometrically: gears mesh with real tooth profiles, threads are modelled,
   mates touch without fusing, nothing floats unretained. Validate now proves
   assembly bodies do not share volume; it cannot tell you they engage.
   Operating-state parameters (opening / travel / tilt) must stay
   interference-free across the whole range, not just the sampled position.
5. **Detail geometry.** Small features on the drawing survive: fillets,
   chamfers, thread run-outs — the reference usually has no sharp corners, so
   sharp corners in a render are a smell. Curved surfaces are real arcs, not
   polyline approximations. Like features are treated consistently across the
   family.
6. **Process.** One family = one issue = one PR, `Closes #N`, the full file
   package, renders **and the PR body** updated at the current head after any
   geometry change, DCO-signed commits.

## Review order

0. **Is the issue's evidence real?** The implementer verified it when
   claiming (CONTRIBUTING.md "Claiming an issue = you verify it") — you are
   the only other pair of eyes. Glance: standard link live, dimension table
   has min/max rows, no obvious mismatch with the PR. Thin evidence = request
   changes on the issue, not the code.
1. **Renders vs the source pictures.** Put `preview_views.png` (the four
   diagonal views exactly as the model will see them) next to the dimensioned
   drawing in the family issue: is it the same part? Are easy/medium/hard
   plausible tiers of one part — not three parts, not clones? For an assembly,
   open `preview_parts.png` too — every component is panelled individually, so
   check each one against the drawing, not just the assembled silhouette.
   Then ask: could the four benchmark views alone reconstruct this geometry?
   Internals invisible in all four views are either not scored bodies or need
   a cutaway.
2. **Extremes vs the table.** `preview_extremes.png` shows the globally
   smallest and largest draw. Hold them against the min/max rows of the
   dimension table in the issue: sane proportions at the small end, correct
   features at the large end?
3. **Coverage.** Table-driven family ⇒ validate must print
   `coverage: <param> reaches all N declared values`. No coverage line on a
   table-anchored family? Request a `coverage=[...]` declaration.
4. **Verify the equations — NOTES.md, three layers.** Any family that derives
   geometry from equations (gear involute, sprocket tooth form, thread helix)
   must ship a `NOTES.md` mapping datasheet symbols → parameters → formulas.
   Check the three layers in order:
   - **(a) Formula vs standard.** Every derived quantity in `part.py`/`spec.py` must
     trace to a cited clause or be declared a fit/proportion. Examples of
     what "correct" looks like: sprocket pitch Ø `dp = p / sin(π/z)`
     (ISO 606 §8.2 — exact, no tolerance); involute function
     `inv α = tan α − α` and tip Ø `da = m·(z+2)` for standard proportions
     (ISO 21771); keyway width/depth from the DIN 6885-1 table, never a
     ratio. A formula with no source and no `proportion` declaration is a
     review comment.
   - **(b) Numbers vs catalog.** Recompute **at least one row yourself**:
     take a catalog row from the issue's dimension table, push it through the
     design's formula, compare against the printed column (expect ≲ 0.5 % or
     a deviation the author explains). The author's own evidence is the
     "Verified against catalog" column in NOTES.md — your job is to spot-check
     it, e.g. duplex z=17: 15.875/sin(π/17) = 86.395 vs catalog 86,39 ✓.
   - **(c) Deviations declared.** Where the design intentionally departs from
     the catalog (fitted constants, unmodeled sub-mm features, simplified
     finishes), NOTES.md must say so under "Deliberate deviations". An
     undeclared mismatch you find in (b) is either a bug or a missing
     deviation entry — both are review comments.
4b. **Physical & functional validity — build one and measure.** Don't read
   this off the render. For an assembly, `bench2 validate` now proves the body
   count matches `"solids"`, that each body is a valid positive-volume solid,
   and that no two bodies share volume — do not re-do those. What it cannot
   prove, and you must:
   - **The envelope.** Build an instance and compare its bbox with the declared
     envelope. A revolve about the wrong axis collapses a part to a lamina, and
     an unclipped helper solid protrudes past the outline; both still pass
     validate.
   - **Engagement.** Not overlapping is not the same as fitting. Gear teeth
     must actually mesh, threads must exist rather than be smooth holes, mates
     must touch on the face the drawing says, and no component may float
     unretained — zero shared volume is equally true of a correctly seated bolt
     and of one hovering 5 mm above its hole.
   - **The whole operating range.** If a parameter opens, travels or tilts the
     assembly, the sampled position being clear says nothing about the rest of
     the range — check the ends.
   Mating dimensions belong in `check()` like any other constraint; a clearance
   that exists only inside `part.py` is invisible to review.
5. **Audit `check()` — the heart of the review.** For every constraint: is it
   engineering-true (would a machinist agree)? Is the cited rule real —
   spot-check any standard number (**fabricated citation ⇒ reject the PR**)?
   What's *missing* — think tear-out, thin walls, tool clearance, unstable
   proportions, and check those failure modes are constrained.
6. **Audit `PARAM_SPEC`.** Ranges sensible per tier; `source` fields specific
   (a table, a rule, or honest `"proportion"`); `askable` only on parameters
   visible/derivable from the part; `feature` on optional-feature toggles;
   `coverage` on the table-driving parameter.
7. **`family.json`.** Name accurate, `standard` correct or null, `base_plane`
   matches the build, `geomlib` lists exactly the helpers used, description
   honest, `contributor` is the actual author.
8. **Scope.** PR touches only `designs/<family>/`; description has
   `Closes #N` (CI enforces); commits DCO-signed.

## The verdict

Approve with a three-line comment so the dossier is self-explaining (the
credits board records you as the verifier):

```
views ✓ (against the 22253 drawing)
equations ✓ (recomputed D1 @ z=17; pt column vs Renold table)
constraints ✓ (bore/groove wall rule is sound; no missing failure mode found)
```

Or request changes, comments limited to the topics above. One pass, verdict
within days.

## Labels

Only one matters: `needs-evidence` on an issue whose package is incomplete.
PRs need no labels — CI status + GitHub review states (approve / request
changes) are the workflow.

## After merge — all automatic

`dossier.yml` posts the acceptance evidence back to the family issue;
STATUS.md flips the family to MERGED; the credits workflow adds the full
provenance row (proposed / implemented / verified) to
CONTRIBUTORS.md. You do nothing.
