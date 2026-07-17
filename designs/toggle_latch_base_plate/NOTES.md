# toggle_latch_base_plate — source notes (drawing → design mapping)

Primary input: **Ganter GN 832 toggle latches** (steel / stainless steel) —
dimensioned catalog sketch + product photo, sizes **55 / 150 / 200**.
Product page: <https://www.ganternorm.com/en/products/2.4-Tensioning-with-clamping-mechanisms/Toggle-latches/GN-832-Toggle-latches-Steel-Stainless-Steel>

The GN 832 assembly is: a stamped **base plate** with a formed **U-clevis** that
pivots the toggle **lever**, whose **U-bolt hook** draws down onto a separate
**catch bracket**. This family models the **base plate + clevis + holes** only —
the prismatic, size-scalable sub-part named by the family. The lever, U-bolt and
catch bracket are the mating pieces and are **out of scope**; their table columns
(b4, b5, b6, l1, l3, m*, r, FH) are therefore not consumed here.

Every geometry variable is named after its GN 832 drawing symbol. Eight are
**row-locked** to one catalog size (refine() sets the row, check() re-asserts the
whole row is real); four are honest **`"proportion"`s** that give the family its
geometric novelty and are bounded by check().

## Symbol → parameter → formula

| GN 832 symbol | meaning | part.py / spec.py | status | value(s) 55 / 150 / 200 |
|---|---|---|---|---|
| `l2` | plate length, left end → pivot axis | `plate_l` | row-locked | 60 / 86 / 111 |
| `b1` | plate width | `plate_w` (coverage) | row-locked | 23 / 34 / 43 |
| `d2` | mounting-hole Ø (×2) | `mount_hole_d` | row-locked | 3.2 / 4.1 / 5.3 |
| `d1` | pivot pin-hole Ø | `pin_d` | row-locked | 2 / 3 / 4 |
| `h1` | overall height (base → clevis top) | `brk_h` | row-locked | 11 / 12.5 / 19 |
| `b2` | clevis outer width | `brk_w` | row-locked | 17 / 23 / 30 |
| `b3` | keeper-nose tab width | `nose_w` (feature) | row-locked | 14 / 20 / 26 |
| `d3` | spring-cotter-pin bore Ø | `cotter_d` (feature) | row-locked | 2.6 / 3.1 / 5.3 |
| `s` | stamped sheet thickness | `plate_t` | **proportion** | 1.0–3.0 mm, ≤ 0.15·b1 |
| — | rounded plate-corner radius | `corner_r` | **proportion** | 1.0–4.0 mm |
| — | clevis ear thickness | `wall_t` | **proportion** | 1.0–3.0 mm |
| — | base↔clevis fold fillet | `fold_r` | **proportion** | 0.5–2.5 mm |
| `r` | **U-bolt reach** (lever) | *not modeled* | — | 26 / 30 / 36 |

Internal construction proportions (fixed fractions of `plate_l` / `brk_h`, shared
by build() and check() via `part._helpers` so they never drift):

| helper | formula | role |
|---|---|---|
| `_brk_len` | `0.20·l2` | clevis length along X |
| `_nose_len` | `0.14·l2` | keeper-nose tab length along X |
| `_clevis_cx` | `l2 − 0.06·l2 − _brk_len/2` | pivot-axis X (clevis set against right end) |
| `_mount_hole_x` | left + {0.24, 0.66}·span | the two mounting-hole X positions |
| `_pin_z` | `s + 0.60·(h1 − s)` | pivot-pin axis height |

## Row-lock

`refine()` draws one index into `_GN832` and sets all eight locked dims from that
row; `check()` constraint (1) fails unless the eight together match a catalog row
(`abs(... ) < 1e-6`). So `plate_w = 34` can only ever occur with
`plate_l = 86, mount_hole_d = 4.1, …` — a size can never be mixed across rows.
`coverage=[23,34,43]` on `plate_w` forces the validator to confirm all three
sizes are reachable.

## Deliberate deviations / interpretations

1. **Base plate + clevis only.** The articulated lever + U-bolt hook (pose-
   dependent, non-prismatic) and the separate catch bracket are mating parts,
   modeled elsewhere in the assembly family set. This part is the stamped base.
2. **`corner_r` is a modeled proportion, not the drawing's `r`.** Drawing `r`
   (26/30/36) is the U-bolt reach of the lever; it is *not* a plate-corner
   radius and is deliberately **not** reused as one (that would be a fabricated
   dimension). Plate corner rounds are an honest `"proportion"`.
3. **Sheet thickness `s` is a proportion.** GN 832's base-plate stock thickness
   is not a tabulated column, so `plate_t` is a `"proportion"` bounded plate-like
   (`≤ 0.15·b1`, `≥ 0.8 mm`), i.e. a stamping not a machined block.
4. **Mounting-hole X positions are proportions** of the flat span between the
   left/nose end and the clevis (the catalog `m*` pitch columns render
   inconsistently on the source page, so they are not row-locked); hole Ø `d2`,
   count (2) and the 1.5·d tear-out edge distance are enforced.
5. **Clevis = two separate ears (open clevis)** carrying `d1`, unioned to the
   plate and clipped inside the `l2 × b1 × h1` envelope; the outer bend line of
   each ear gets the `fold_r` fillet (the visible formed fold), the inner base
   inside the lever slot stays sharp.
6. **Cotter bore modeled as a vertical through-hole** in the keeper-nose tab
   (the catalog shows it in the formed lever-tail curl); diameter `d3` and
   `≤ 0.5·b3` clearance are honored.

## Envelope

Declared envelope = `plate_l × plate_w × brk_h` (= l2 × b1 × h1). Probed bbox
equals it exactly for all three rows × both feature states (x∈[0,l2],
y∈[−b1/2, b1/2], z∈[0, h1]); the clevis (`b2 < b1`) and nose (`b3 < b1`) sit
inside the width and nothing protrudes.
