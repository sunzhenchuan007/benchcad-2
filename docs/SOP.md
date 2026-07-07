# SOP: a family's full lifecycle — from nothing to released

One family = one issue = one PR (RULES.md #1). **The issue is the family's
dossier**: every stage leaves its evidence there, so the whole history is
readable in one place. Eight stations; what lands in the issue is marked 📌.

```
0 propose → 1 claim → 2 build → 3 PR → 4 CI → 5 review → 6 merge → 7 dossier close-out → 8 factory/release
```

## 0. Propose (anyone, ~15 min) — the evidence package

Open a **Family request** issue (form provided). Three mandatory pieces
(worked example: [#1 duplex_sprocket](../../../issues/1); how to obtain them:
[SOP_REFERENCE_IMAGES.md](SOP_REFERENCE_IMAGES.md)):

- 📌 **anchoring standard/catalog** (link)
- 📌 **dimensioned drawing** (symbols D, D1, B1 … — stored in
  `docs/assets/refs/`, embedded via raw URL)
- 📌 **dimension table** with the **min and max rows explicit** + full
  datasheet link + implementer notes (derived relations, coverage hint)

An issue without the package is labeled `expert-input` until someone completes
it — completing the package is itself a credited contribution (RULES.md #6).

## 1. Claim

📌 Self-assign the issue (or comment "I'll take it" and a maintainer assigns).
Assignee visible on the issue = nobody else starts it.

## 2. Build (locally; guide: GETTING_STARTED [EN](GETTING_STARTED.md)/[中文](GETTING_STARTED.zh.md))

`bench2 new <family>` → fill the four pieces → iterate until:
- `bench2 validate <family>` = **PASS** (incl. spec-contract, geomlib,
  **coverage** against the table from station 0)
- `bench2 preview <family>` → three PNGs: overview, **benchmark 4-views**,
  **extremes (smallest & largest draw)** — compare against the drawing and the
  table's min/max rows yourself first.

## 3. PR

One PR, only `designs/<family>/`, description contains `Closes #<issue>`.
📌 GitHub auto-links the PR in the issue timeline.

## 4. CI (automatic)

Re-runs the same gates publicly; posts the validate report + previews on the
PR. Red = fix locally, push again (same PR).

## 5. Review (one person, not the author — RULES.md #3)

Order in [REVIEWING.md](../REVIEWING.md): 4-views vs the drawing → extremes vs
the table's min/max rows → coverage gate → constraints true? → labels right?
Verdict as accept / request-changes, comments limited to those topics.

## 6. Merge

📌 Issue auto-closes (`Closes #N`); the category tracking list ticks itself;
STATUS.md flips the family to MERGED on the next board refresh.

## 7. Dossier close-out (automatic)

📌 On merge, CI posts a **close-out comment on the issue**: the three preview
images + the validate summary. The issue now reads end-to-end — proposal
evidence at the top, acceptance evidence at the bottom. (Workflow:
`.github/workflows/dossier.yml`.)

## 8. Factory & release (maintainers, batch)

Before each dataset release the private factory runs saturation sampling, QA/
edit derivation, and the frontier difficulty screen; outcomes appear in
[STATUS.md](../STATUS.md) (GENERATED → QUALIFIED / HELD-with-reason →
RELEASED). 📌 On release, a maintainer comments the dataset tag (e.g.
`released in v2.0`) on the issue — the dossier's final line.

---

**Total human touch-points**: propose (once), claim (a click), build, one
review, one release note. Everything else is automated, and every stage is
visible in the issue.
