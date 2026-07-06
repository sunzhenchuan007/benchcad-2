# Rules

One page. Rules replace meetings. If a situation isn't covered, open an issue —
the answer becomes a rule here.

1. **One family = one owner = one PR** = `designs/<family>/` (design.py,
   family.json, NOTES.md, preview.png). Nothing else in the diff.
2. **`bench2 validate` PASS = your code works.** That is the definition. It runs
   locally in minutes; CI just re-runs the same gates publicly.
3. **Review judges exactly two things**: are the constraints in
   `check()`/`PARAM_SPEC` *true*, and are the `family.json` labels correct.
   One review pass, verdict within days, comments limited to those two topics.
4. **Merged ≠ released.** Merge puts your design in `designs/`. Release
   qualification (instance saturation, frontier-model difficulty screen) is
   decided by the factory in batch before each dataset release, and the outcome
   is public in [STATUS.md](STATUS.md) — including the reason if a family is HELD.
5. **Pick work from [WANTED.md](WANTED.md).** On the list → claim it there and
   start. Not on the list → one-sentence issue first.
6. **No code? Still contribute.** Open an issue with the part name, a datasheet
   link, the parameter table, and the engineering constraints in plain words.
   A maintainer turns it into a design; both of you are credited.
7. **Everything happens in issues and PRs.** No DMs, no meetings, no status
   pings — [STATUS.md](STATUS.md) is regenerated automatically and is the
   single source of progress.
8. **Rule changes are PRs** to this file or DESIGN.md. Merge = in effect.
9. **Credit is automatic**: merged family → CONTRIBUTORS.md row + dataset-card
   credit + co-authorship on the BenchCAD 2.0 paper.
10. **The factory is a black box to contributors** (private seeds, held-out
    draws, packing). You never need it: local validate + preview is the whole
    contributor loop.
