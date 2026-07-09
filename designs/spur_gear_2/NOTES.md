# spur_gear_2 — source notes (datasheet → design mapping)

Primary input: **norelem 22400** — "Spur gears in steel, milled straight teeth,
module 1–6, 20° pressure angle".
[Datasheet / product family](https://www.norelem.com/en/Products/Product-overview/Drive-technology-and-standard-parts/22400-Spur-gears-in-steel-milled-straight-teeth.html)
The datasheet prints the module series, the 20° pressure angle and the two body
styles (A = hub, B = plain disc); the involute tooth profile itself is the
ISO 53 basic rack (a convention, realised by `geomlib.involute_gear_profile`).

Every geometric parameter traces to a datasheet symbol or an ISO 53 / ISO 54
relation. This file is the review evidence.

## Symbol mapping

| Datasheet | Meaning | Relation / standard | part.py / spec.py | Verified against catalog |
|---|---|---|---|---|
| `m` (Modul) | module (tooth size) | ISO 54 preferred series 1 | `module`, discrete draw in `refine` | m = 1, 1.25, 1.5, 2, 2.5, 3, 4, 5, 6 — catalog columns |
| `z` (Zähnezahl) | tooth count | catalog rows | `n_teeth`, discrete `choices` per tier | z = 12 … 90 (catalog sells z = 12 up) |
| **`d`** | pitch circle Ø dp | **dp = m·z** (ISO 53) | `_circles()` | m5: z12→**60**, z24→120, z48→240, z114→**570** — exact |
| **`da`** | tip circle Ø | **da = m·(z+2)** (ISO 53, addendum = m) | `_circles()` | m5: z12→**70**, z24→130, z48→250, z114→**580** — exact |
| `df` | root circle Ø | **df = m·(z−2.5)** (dedendum = 1.25 m) | `_circles()` | m5: z12→47.5, z24→107.5, z48→227.5, z114→557.5 |
| α | pressure angle | **20°** full-depth (ISO 53 basic rack) | `involute_gear_profile` | catalog 20° |
| `b` | face width | machine-design band **b = 6–11 m** | `face_width` (`check`: 5–15 m) | catalog b tracks module |
| Style **A** | hub boss (low z) | catalog: **z ≤ 30** | `hub_d`/`hub_len` set iff z ≤ 30 | hub Ø 1.7·bore … 0.78·df |
| Style **B** | plain disc (high z) | catalog: **z ≥ 32** | `hub_d = 0` iff z ≥ 32 | bore-only disc |
| bore + keyway | shaft fit | shaft-fit proportion + **DIN 6885 Form A** | `bore_d` (≤ 0.42 df), `keyway_dims()` | keyway on hub gears (hard tier) |

## da / df spot-check (module 5, against the catalog rows)

| z | dp = m·z | da = m·(z+2) | df = m·(z−2.5) | catalog dp / da |
|---|---|---|---|---|
| 12 | 60.0 | 70.0 | 47.5 | 60 / 70 ✓ |
| 24 | 120.0 | 130.0 | 107.5 | 120 / 130 ✓ |
| 48 | 240.0 | 250.0 | 227.5 | 240 / 250 ✓ |
| 114 | 570.0 | 580.0 | 557.5 | 570 / 580 ✓ |

dp and da land on the catalog's m = 5 rows exactly across the whole z range
(z = 12 → 60/70 … z = 114 → 570/580).

## Deliberate deviations

1. **Style A/B is keyed to z, not difficulty.** norelem 22400 is Style A (hub)
   up to z = 30 and Style B (plain disc) from z = 32; `refine()` sets the hub iff
   z ≤ 30, and `n_teeth` carries `coverage = [12, 30, 32, 90]` so both styles and
   both sides of the 30/32 boundary are always exercised. (Earlier the hub was
   tied to the difficulty tier, so high-z gears rendered with hubs — fixed.)
2. **z = 12 is admitted (catalog minimum), with root bridging.** A 20° full-depth
   tooth is interference-free only above z ≈ 2/sin²20° ≈ 17.1, so z = 12–17
   undercut. The catalog nonetheless sells z = 12, and `involute_gear_profile`
   bridges the root at low z rather than modelling the true undercut trochoid —
   an **approximation**, declared here (the earlier "z ≥ 14 limits undercut"
   floor both rejected the catalog's z = 12 and wrongly implied z = 14 is
   interference-free).
3. **Involute profile is the ISO 53 basic rack**, not a measured tooth trace —
   flanks are the true involute of the base circle r_b = (dp/2)·cos20°, tip and
   root truncated to da/df; fillet is a simple bridge, not the generating
   trochoid.
4. **bore / hub proportions are `proportion`** (bore ≤ 0.42 df, hub 1.7·bore …
   0.78 df): the catalog lists finished bores per article, not a formula, so
   these are declared conventions bounded by the root circle.
5. **Tooth-flank surface finish, profile shift (x), backlash and root fillet
   radius are not modelled** — geometry benchmark at the tooth-form level.
