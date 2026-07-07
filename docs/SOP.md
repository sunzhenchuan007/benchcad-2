# SOP: a family's full lifecycle — from nothing to released

One family = one issue = one PR (RULES.md #1). **The issue is the family's
dossier**: every stage leaves its evidence there, so the whole history is
readable in one place. Ten stations; 📌 marks what lands in the issue,
📒 marks the record the credits board reads (who did what, when).

```
0 propose → 1 triage → 2 claim → 3 build → 4 PR → 5 CI → 6 review → 7 merge → 8 dossier → 9 factory/release
```

**Where do I start?**
Propose a part → *Family request* form · know parts but not GitHub → *Expert
contribution* form ([guide EN](GETTING_STARTED.md)/[中文](GETTING_STARTED.zh.md))
· found a bug → *Bug report* · framework idea → *Feature request* · want to
build → pick a [`triaged` family issue](../../../issues?q=is%3Aissue+is%3Aopen+label%3Atriaged)
· want to review → [REVIEWING.md](../REVIEWING.md).

## 0. Propose (anyone, ~15 min) — the evidence package

Open a **Family request** issue (form). Three mandatory pieces (worked
example: [#1 duplex_sprocket](../../../issues/1); how to obtain them:
[SOP_REFERENCE_IMAGES.md](SOP_REFERENCE_IMAGES.md)):

- 📌 **anchoring standard/catalog** (link)
- 📌 **dimensioned drawing** (symbols D, D1, B1 … — stored in
  `docs/assets/refs/`, embedded via raw URL)
- 📌 **dimension table** with the **min and max rows explicit** + full
  datasheet link + implementer notes (derived relations, coverage hint)

**No render images at this stage** — nothing has been implemented yet. The
only images in a fresh issue are the *datasheet's* drawing/photo. Our renders
(4-views, extremes) arrive at station 8, as a comment.
📒 Issue author + timestamp = the **proposer**.

## 1. Triage (a maintainer or any non-author, ~5 min)

Run the [TRIAGE.md](TRIAGE.md) check: three pieces present, source real, two
numbers spot-checked, parametrizable, no duplicate. Move the label:
`needs-triage` → `triaged` (or `needs-evidence` + one comment naming the gap).
📌 One-line verdict comment. 📒 The `triaged` label event = the **triager**.
Completing someone else's evidence package is itself credited (RULES.md #6).

## 2. Claim

📌 Self-assign the issue (or comment "I'll take it" and a maintainer assigns).
Assignee visible on the issue = nobody else starts it. Only `triaged` issues
are worth claiming.

## 3. Build (locally; guide: [GETTING_STARTED](GETTING_STARTED.md))

`bench2 new <family>` → fill the four pieces (+ `NOTES.md` symbol mapping for
any equation-driven family) → iterate until:
- `bench2 validate <family>` = **PASS** (incl. spec-contract, geomlib,
  **coverage** against the station-0 table)
- `bench2 preview <family>` → three PNGs: overview, **benchmark 4-views**,
  **extremes** — compare against the drawing and the table's min/max rows
  yourself first.

## 4. PR

One PR, only `designs/<family>/`, description contains `Closes #<issue>`.
**CI enforces the link** (`require-issue-link.yml`): a designs PR without a
valid open-issue link goes red — edit the PR description to fix, no new push
needed. 📌 GitHub auto-links the PR in the issue timeline.
📒 PR author = the **implementer**.

## 5. CI (automatic)

Re-runs the same gates publicly. Red = fix locally, push again (same PR).

## 6. Review (one person, not the author — RULES.md #3)

Order in [REVIEWING.md](../REVIEWING.md): renders vs drawing → extremes vs
min/max rows → coverage → **equations (3 layers: formula vs standard, numbers
vs catalog, deviations declared)** → `check()` audit → `PARAM_SPEC` →
`family.json` → scope. Verdict = approve with the three-line evidence comment,
or request changes. 📒 The approving review = the **verifier**.

## 7. Merge

📌 Issue auto-closes (`Closes #N`); the category tracking list ticks itself;
STATUS.md flips the family to MERGED on the next board refresh.

## 8. Dossier close-out (automatic)

📌 On merge, CI posts a **close-out comment on the issue**: the three preview
images + the validate summary (workflow: `.github/workflows/dossier.yml`).
The issue now reads end-to-end — proposal evidence at the top, acceptance
evidence at the bottom. 📒 The credits workflow regenerates
[CONTRIBUTORS.md](../CONTRIBUTORS.md): one provenance row per family —
proposed by / triaged by / implemented in / reviewed by.

## 9. Factory & release (maintainers, batch)

Before each dataset release the private factory runs saturation sampling,
QA/edit derivation, and the frontier difficulty screen; outcomes appear in
[STATUS.md](../STATUS.md) (GENERATED → QUALIFIED / HELD-with-reason →
RELEASED). 📌 On release, a maintainer comments the dataset tag (e.g.
`released in v2.0-lite`) on the issue — the dossier's final line.

---

**Total human touch-points**: propose (once), one triage pass, claim (a
click), build, one review, one release note. Everything else — link
enforcement, gates, close-out, boards, credits — is automated, and every
stage is visible in the issue.
