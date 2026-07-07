# Triage: checking an issue before anyone spends time on it

Every new issue arrives labeled `needs-triage`. A maintainer (or any
contributor who is not the author) runs the check below and moves the label:

```
needs-triage ──ok──────────→ triaged          (ready to claim / to fix)
             ──incomplete──→ needs-evidence   (+ one comment: what's missing)
             ──out of scope→ closed           (+ one sentence why)
```

The triage verdict is **one short comment** ("triage OK: standard verified,
table rows spot-checked" — or what's missing). The label event + comment are
the permanent record of *who* checked *what* *when*; the credits board reads
them. Budget: ~5 minutes.

## Family request (`[family]`) — the evidence check

1. **Three pieces present?** Anchoring standard/catalog **link**, a
   **dimensioned drawing** (symbols D, B1, …), a **dimension table with the
   min and max rows**. Missing any → `needs-evidence`, name the gap.
   (How to obtain them: [SOP_REFERENCE_IMAGES.md](SOP_REFERENCE_IMAGES.md).)
2. **Source is real?** Open the link. The standard number / catalog article
   must actually exist. You are not verifying the full standard text — just
   that the anchor is genuine. Dead link or invented standard → `needs-evidence`.
3. **Spot-check two numbers.** Pick two table cells and check them against the
   linked datasheet (or against the standard's defining equation if there is
   one — e.g. a sprocket's D1 column must equal p/sin(π/z)). A table that
   fails a spot-check is not review-ready.
4. **Parametrizable & buildable?** ≥ 4 real parameters, visible difficulty
   headroom (what makes an easy vs a hard variant?), geometry within CadQuery
   reach (prismatic/revolved solids + profiles + booleans — no free-form
   sculpting).
5. **Not a duplicate?** Search `designs/` and open `family` issues.

Pass → remove `needs-triage`, add `triaged`, comment one line. The issue is
now claimable (SOP station 2).

## Bug report — the reproduction check

1. Reproduce it (command + output in the issue should be enough — if not,
   `needs-evidence`).
2. Confirm it is a bug, not a documented behavior or a local-env problem.
3. For a *design* bug: the report must contain an **engineering reason**
   ("root Ø exceeds catalog df by 2 mm"), not just "looks wrong".

Pass → `triaged` (+ `good first issue` if the fix is contained).

## Feature request — the fit check

1. Does it already exist (docs, CLI `--help`, a config knob)?
2. Does it belong to a roadmap workstream? If yes, comment a pointer and move
   the discussion to that `[tracking]` issue; close the duplicate.
3. Is the scope one PR? Bigger → suggest splitting, or park it on the roadmap.

Pass → `triaged`.

## Who may triage

Anyone except the issue author; maintainers resolve disagreements. Completing
a `needs-evidence` package yourself (finding the datasheet, filling the table)
is a credited contribution (RULES.md #6) — the credits board records the
triager per family.
