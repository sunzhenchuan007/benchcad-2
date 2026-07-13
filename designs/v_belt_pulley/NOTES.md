# v_belt_pulley — source notes (datasheet → design mapping)

Primary input: **ISO 4183** — "Belt drives — Classical and narrow V-belts —
Grooved pulleys (system based on datum width)", narrow sections **SPZ / SPA / SPB**.
The groove geometry (top width, depth, pitch `e`, edge distance `E`, angle) and
the minimum datum diameter per section trace to ISO 4183; the rim width is the
ISO relation, not a proportion.

## Symbol mapping

| ISO 4183 | Meaning | Relation / value | part.py / spec.py | Section values (SPZ / SPA / SPB) |
|---|---|---|---|---|
| section | narrow V-belt profile | SPZ / SPA / SPB | `_SECTIONS`, drawn in `refine` | — |
| `e` (E1) | groove pitch (centre-to-centre) | ISO 4183 | `groove_pitch` (coverage) | 12 / 15 / 19 |
| `E` | edge distance (outer groove centre → face) | ISO 4183 | `_SECTIONS[.][3]` | 8 / 10 / 12.5 |
| `lg` | groove top width | ISO 4183 datum | `groove_top_w` | 9.7 / 12.7 / 16.3 |
| depth | groove depth below OD | ISO 4183 | `groove_depth` | 9 / 11 / 14 |
| **α** | **groove angle** | **34°, → 38° above the datum step** | `groove_angle` (refine) | 34/38 by datum Ø |
| **B** | **rim width** | **B = 2E + (N−1)e** (exact) | `width` (refine, `check`) | SPZ N1=16 N2=28 · SPA N1=20 · SPB N2=44 |
| C | groove flat-bottom width | `lg − 2·depth·tan(α/2)` | trapezoid bottom in part.py | > 1 mm enforced (`check`) |
| dd min | minimum datum diameter | ISO 4183 | `_MIN_DIA` | 63 / 80 / 112 |

## Spot check — ISO rim width B = 2E + (N−1)e

| section | E | e | N | B = 2E + (N−1)e |
|---|---|---|---|---|
| SPZ | 8 | 12 | 1 | 16 |
| SPZ | 8 | 12 | 2 | 28 |
| SPA | 10 | 15 | 1 | 20 |
| SPB | 12.5 | 19 | 2 | 44 |

These land on the ISO 4183 rim widths exactly (SPZ N1 16 / N2 28, SPA N1 20,
SPB N2 44).

## Deliberate deviations

1. **Groove angle stepped 34° → 38° by datum diameter** (per section: SPZ > 80,
   SPA > 118, SPB > 190 mm), a simplification of ISO 4183's finer angle bands
   (32/34/36/38°). `outer_d` is used as a proxy for the datum diameter dd (the
   datum line sits a few mm below the OD).
2. **Groove is a trapezoid**: flanks at α, stopping at a flat bottom
   C = lg − 2·depth·tan(α/2), so a belt seats on the flanks and never bottoms —
   not the sharp V-to-a-point of the earlier model. Root radius / ball-check `ba`
   offsets are not modelled.
3. **Bore / hub are `proportion`** (bore ≤ 0.9·root-rim, hub 1.7·bore … 1.8·root),
   bounded by the groove-root rim — the catalog lists finished bores per article,
   not a formula.
4. **Belt datum-line offset, keyway and set-screw are not modelled** — geometry
   benchmark at the groove-profile level.
