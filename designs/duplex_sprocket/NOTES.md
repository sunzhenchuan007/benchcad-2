# duplex_sprocket — source notes (datasheet → design mapping)

Primary input: **norelem 22253 datasheet** — "Sprockets duplex 5/8" × 3/8"
DIN ISO 606" (10B-2 chain, z = 9–95).
[Datasheet PDF](https://www.norelem.com/xs_db/DOKUMENT_DB/www/NORELEM/DataSheet/en/22/22253_Datasheet_22066_Sprockets_duplex_5_8_x_3_8_DIN_ISO_606--en.pdf)
· Transverse-pitch column for all six chain rows cross-checked against the
[Renold chain tables](https://www.renold.com/media/228840/renold-brand-chain-tables.pdf)
(European BS Standard — Duplex, "Transverse Pitch" K column).

Every design parameter traces to a datasheet symbol or a standard equation.
This file is the review evidence: a reviewer can check any row against the
datasheet (the dimension table with min/max rows is in the family issue, #1).

## Symbol mapping

| Datasheet | Meaning | Relation / standard | part.py / spec.py | Verified against catalog |
|---|---|---|---|---|
| Pitch `5/8 × 3/8` | chain pitch × inner width (10B-2) | ISO 606 Table 1 row | `pitch`, jointly-sampled `_ISO606_2` row | 15,875 × 9,65 = our 10B-2 row |
| `z` (No. of teeth) | tooth count (both rows, in phase) | — | `n_teeth` | catalog sells z = 9–95 |
| **`D1`** | pitch circle Ø dp | **dp = p / sin(π/z)** (ISO 606 §8.2) | `_circles()` | z=9: 46.415 vs **46,42** · z=12: 61.336 vs **61,34** · z=17: 86.395 vs **86,39** · z=25: 126.66 vs **126,66** · z=45: 227.58 vs **227,58** — exact |
| `D` | tip circle Ø da | ISO band; offset fitted: **da = dp + 0.68·d1** | `_circles()` | Δ(D−D1) = 6,86–6,94 for z=9–25; 0.68·10.16 = 6.91 ✓ (z=45/95 see deviations) |
| — (implied) | root circle Ø df | df = dp − 1.01·d1 (ri = 0.505·d1) | `_circles()` | basis for bore/hub/groove limits |
| **pt** (implied by `B2`) | transverse pitch — row center distance | ISO 606 / DIN 8187 duplex table: 5.64 / 10.24 / 13.92 / **16.59** / 19.46 / 31.88 | `trans_pitch` (5th column of `_ISO606_2`) | **B2 = B1 + pt**: 9 + 16.59 = 25.59 ≈ catalog constant **25,5** ✓ |
| `B1` | single-row tooth width bf1 | ISO 606 (≈0.95 × inner width) | `tooth_width` | catalog **9** vs ISO 10B **9,1** (see deviations) |
| `B2` | overall double-row width | **= B1 + pt** (constant per chain) | `tooth_width + trans_pitch` (derived, not a free param) | constant **25,5** across all z ✓ |
| — (between rows) | intermediate groove Ø | proportion: **df − 1.5·d1** — groove must clear the inner link plates; Renold plate height 10B = **14,60** ≈ 1.44·d1, sunk half below the root | `_circles()` groove_d; `check`: groove wall ≥ 1.55·bore | not tabulated in 22253 (visible in the drawing between the rows) |
| `D2` | hub outside Ø | catalog proportion: 2.5–4.8 × D3max, ≤ 0.83 × df | `hub_d` (+ `check` bounds 1.55·bore … 0.87·df) | 30–145 across z=9–95 |
| `D3 max` | pilot bore max | — | `bore_d` is the FINISHED bore (rim cap 0.50·df), same convention as simplex | 12–30 |
| `L` | overall length = B2 + hub protrusion | — | `tooth_width + trans_pitch + hub_len` | L−B2 = 14,5–33,5 = **1.6–3.7 × b1** → sample range |
| keyway | DIN 6885 key seat | **DIN 6885-1 Form A** (same `keyway_dims()` table as simplex, T2 cross-checked there) | `keyway_dims()`; tip-aligned via profile `phase` | — |
| `C`, `R` | tooth side chamfer / radius | manufacturer finish | outer-rim chamfer `0.15·b1` only | — |
| material notes | C45, teeth hardened | — | out of scope (geometry benchmark) | — |

## Deliberate deviations

1. **B1 = 9,1 (ISO) vs 9 (catalog)** — norelem grinds duplex teeth 0.1 mm
   narrower than the ISO simplex width. We keep the ISO Table 1 value so the
   row is shared with simplex_sprocket; B2 comes out 25.69 vs catalog 25,5
   (+0.7%).
2. **Tip Ø fit 0.68·d1** is exact for the catalog's z = 9–25 rows; at z = 45/95
   the catalog picks a higher point inside the ISO tip band (Δ ≈ 8.4 vs our
   6.9 mm, −0.6% of D). Kept at 0.68 for consistency with simplex_sprocket —
   both values are legal ISO 606 tip positions.
3. **Groove Ø is a proportion** (df − 1.5·d1): 22253 draws but does not
   tabulate it. The rule keeps the groove ~0.75·d1 below the root radius, just
   clearing the chain plate half-height (14,60/2 = 7,3 < 7,6 mm for 10B).
4. **Inner rims are not chamfered** — the catalog's C/R finish applies per
   row; inside faces meet the groove cylinder, where a chamfer would be
   machining detail invisible at benchmark resolution.
5. **Grub screws / retaining features not modeled** (sub-mm), as in simplex.
