# Contributing

Everything you need is on this one page. A contribution is **two files of
engineering knowledge**: a parametric design whose ranges and constraints are
true. Merged family ⇒ your row on the [provenance board](CONTRIBUTORS.md),
named credit in the dataset card, co-authorship on the BenchCAD 2.0 paper.

Questions / want to say hi → [Discord](https://discord.gg/be9AtvrDyK).
Not a GitHub person? → step-by-step guide
[EN](docs/GETTING_STARTED.md)/[中文](docs/GETTING_STARTED.zh.md) (zero-code
path included). Want a worked example first? → illustrated tutorial
[EN](docs/WALKTHROUGH.md)/[中文](docs/WALKTHROUGH.zh.md).

## The 60-second loop

```bash
uv sync                              # once
uv run bench2 new <family>           # scaffold designs/<family>/
# fill part.py + spec.py (docs/DESIGN_SPEC.md; copy designs/simplex_sprocket/)
uv run bench2 validate <family>      # every machine gate, locally
uv run bench2 preview <family>       # LOOK at the three images yourself
# open a PR with `Closes #<issue>` — CI re-runs the same gates
```

## The rules (ten, memorize-able)

1. **One family = one issue = one PR**, touching only `designs/<family>/`,
   with `Closes #<issue>` in the description (CI enforces the link).
2. **`bench2 validate` PASS = your code works.** CI just re-runs it publicly.
3. **Review = one person who is not the author**, following
   [REVIEWING.md](REVIEWING.md). One pass, verdict within days.
4. **Merged ≠ released.** Release qualification (saturation sampling,
   difficulty screen) runs in the private factory per release batch; outcomes
   are public on [STATUS.md](STATUS.md), including HELD reasons.
5. **Pick work from the [family issues](../../issues?q=is%3Aissue+is%3Aopen+label%3Afamily)**
   (easiest: [`good first issue`](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)).
   No issue for your part? Open a *Family request* first.
6. **No code? Still credited.** File a *Part proposal (no code)* issue (datasheet
   + table + constraints in plain words); a maintainer implements; both of you
   land on the provenance board.
7. **Work lives in issues and PRs.** [Discord](https://discord.gg/be9AtvrDyK)
   is for questions and chatter — decisions land back in the issue. No
   meetings;
   [STATUS.md](STATUS.md) and [CONTRIBUTORS.md](CONTRIBUTORS.md) regenerate
   themselves.
8. **Rule changes are PRs** to this file. Merge = in effect.
9. **Credit is automatic** — the provenance board is generated from the
   issues/PRs themselves (who proposed / implemented / verified each family).
10. **The factory is a black box to contributors** (private seeds, held-out
    draws). You never need it: local validate + preview is the whole loop.

## The lifecycle (who does what, and what gets recorded)

| # | Station | Who | What happens |
|---|---|---|---|
| 0 | **Propose** | anyone | *Family request* form: standard link + dimensioned drawing + dimension table **with min/max rows**. **No render images** — those arrive at station 7. 📒 issue author = *proposer* |
| 1 | **Claim & verify** | implementer | Self-assign, then **check the evidence before coding** (below). Gaps → fill them yourself (credited) or label `needs-evidence` + one comment naming what's missing |
| 2 | **Build** | implementer | The 60-second loop, plus `NOTES.md` symbol mapping for any equation-driven family. Compare the previews against the drawing and the table's min/max rows yourself first |
| 3 | **PR** | implementer | `Closes #N`; CI enforces the link. 📒 PR author = *implementer* |
| 4 | **CI** | robot | Same gates, public. Red = fix and push again |
| 5 | **Review** | one non-author | [REVIEWING.md](REVIEWING.md): renders vs drawing → extremes vs min/max → coverage → equations (3 layers) → constraints. 📒 approver = *verifier* |
| 6 | **Merge** | maintainer | Issue auto-closes; tracking list ticks itself |
| 7 | **Dossier** | robot | Acceptance renders + validate summary posted back to the issue; [CONTRIBUTORS.md](CONTRIBUTORS.md) refreshes. The issue now reads end-to-end |
| 8 | **Factory & release** | maintainers | Batch generation + difficulty screen; [STATUS.md](STATUS.md) flips stages; on release the dataset tag is commented on the issue |

## Claiming an issue = you verify it (5 minutes, before writing code)

The implementer is the triager — nobody else pre-checks issues for you:

1. **Three pieces present?** Standard/catalog link · dimensioned drawing
   (symbols D, B1, …) · dimension table with min & max rows.
2. **Source real?** Open the link; the standard number / catalog article must
   exist. Dead or invented anchor → `needs-evidence`.
3. **Spot-check two numbers** against the datasheet — or against the defining
   equation if there is one (a sprocket's D1 column must equal p/sin(π/z)).
4. **Buildable?** ≥ 4 real parameters, visible easy→hard headroom, geometry
   within CadQuery reach (prismatic/revolved + profiles + booleans).
5. **Not a duplicate?** The welcome bot already ran a name check against
   [`registry.json`](registry.json) (601+ known names: merged + proposed +
   wanted) when the issue opened — read its comment. Same part type as
   BenchCAD 1.0 is fine, the *name* must be unique.

Getting the reference images: norelem product pages expose CDN originals
(`Zoom-Default-<article>.png` = photo, `Zoom-Default-Z<article>.png` =
dimensioned drawing — extract with `[...document.querySelectorAll('img')].map(i=>i.src)`);
datasheet PDFs live at stable URLs (`norelem.com/xs_db/DOKUMENT_DB/...`).
Store images in `docs/assets/refs/<family>_{photo,drawing}.png` — never
drag-and-drop into the issue — and embed via SHA-pinned blob URLs with
`?raw=true` (`https://github.com/BenchCAD-org/benchcad-2-heldout/blob/<commit>/docs/assets/refs/<file>.png?raw=true`);
these render for repo members while the repo is private, where anonymous
raw.githubusercontent URLs 404. Always name the source with a link.

## Issue taxonomy — the title prefix says what it is

| Title pattern | What it is | Who opens it | Labels |
|---|---|---|---|
| `[roadmap] BenchCAD 2.0 — <quarter>` | the quarterly plan; pinned; one per quarter | maintainers | `roadmap` |
| `[workstream] <name>` | one roadmap line: goals, task list, all its discussion | maintainers | `workstream` |
| `[category] <name>` | a part-family category: live checklist of its families | maintainers | `category`, `cat:*` |
| `[family] <snake_case_name>` | one part-family proposal (the evidence package) | **anyone** (form) | `family`, `cat:*` |
| `[family-assembly] <name>_asm` | a family whose real product is a multi-part **assembly**. Family name carries the **`_asm` suffix** in `designs/`. Model = `cq.Compound`, every real component its own solid, zero interference; PR adds `preview_parts.png` (each part isolated beside the assembly) | **anyone** (form) | `family`, `family-assembly`, `cat:*` |
| `[proposal] <part name>` | zero-code part proposal — we write the code | **anyone** (form) | `family`, `proposal` |
| `[bug] <short description>` | something broken (design / framework / CI / docs) | **anyone** (form) | `bug` |
| `[fix] <the correction> (<family>)` | a defect in a **merged** family + its correction — prefix first, family in trailing parens; the fix PR carries the same title | **anyone** | `bug` |
| `[feat] <short description>` | framework improvement | **anyone** (form) | `enhancement` |

Hierarchy (GitHub sub-issues, visible as a tree on each issue):
`[roadmap]` ⊃ `[workstream]` / `[category]` ⊃ `[family]` / `[bug]` / `[feat]`.
The forms set prefixes and labels for you — just don't delete them. Status is
one extra label only: `needs-evidence` (plus `good first issue` as an
invitation).

## Bugs, features, everything else

- **Bug** → *Bug report* form (command + output; for a design bug, an
  engineering reason). Fix PRs link the issue with `Closes #N`.
- **Defect in a merged family** → `[fix] <the correction> (<family>)` issue —
  the wrong relation vs the catalog/standard one, with before/after renders;
  the fix PR reuses the same title and links it with `Closes #N` (e.g. #158/#159).
- **Framework feature** → *Feature request* form; big ideas belong to an
  existing `[workstream]` issue on the
  [roadmap](https://github.com/BenchCAD-org/benchcad-2-heldout/issues/21).
- **Review** → verify a family PR per [REVIEWING.md](REVIEWING.md); the
  approving reviewer is credited as that family's verifier.
- **Errata against released 1.0 data** → issue with the record id + the
  engineering reason; fixes land in the next dataset version (released data is
  immutable).

## Fine print

- Every commit DCO-signed (`git commit -s`).
- MIT: merged designs may be evolved by the maintainers' pipeline (held-out
  draws, future tiers) with your credit preserved.
- Instances, QA, edits, and the held-out split are generated privately;
  released data is versioned on Hugging Face.
- (If AI-assisted) you reviewed every line and stand behind the constraints.
