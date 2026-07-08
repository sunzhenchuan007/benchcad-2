# simplex_sprocket — source notes (datasheet → design mapping)

Primary input: **norelem 22250 datasheet** — "Sprockets single 5/8" × 3/8"
DIN ISO 606, ready to install" (10B-1 chain, Form A/B, z = 10–25).
[Datasheet PDF](https://www.norelem.com/xs_db/DOKUMENT_DB/www/NORELEM/DataSheet/en/22/22250_Datasheet_17671_Sprockets_single_5_8_x_3_8_DIN_ISO_606_ready_to_install--en.pdf)
· Material: steel C45, teeth inductively hardened ~HRC 50. Keyway per
DIN 6885 / BS 4235, **aligned with the tooth tip**; two grub screws (one on
the keyway centre, one at 90°).

Every design parameter traces to a datasheet symbol or a standard equation.
This file is the review evidence: a reviewer can check any row against the
datasheet.

## Symbol mapping

| Datasheet | Meaning | Relation / standard | part.py / spec.py | Verified against catalog |
|---|---|---|---|---|
| Pitch `5/8 × 3/8` | chain pitch × inner width (10B-1) | ISO 606 Table 1 row | `pitch`, jointly-sampled `_ISO606` row | 15,875 × 9,65 = our 10B row |
| `z` (No. of teeth) | tooth count | — | `n_teeth` | catalog sells z = 10–25 |
| **`D1`** | pitch circle Ø dp | **dp = p / sin(π/z)** (ISO 606 §8.2) | `_circles()` | z=10: 51.372 vs **51,37** · z=13: 66.335 vs **66,32** · z=25: 126.66 vs **126,66** — exact |
| `D` | tip circle Ø da | ISO band; offset fitted: **da = dp + 0.68·d1** | `_circles()` | Δ(D−D1) = 6,86–6,94 across z=10–25; 0.68·10.16 = 6.91 ✓ |
| — (implied) | root circle Ø df | df = dp − 1.01·d1 (ri = 0.505·d1) | `_circles()` | basis for bore/hub limits |
| `B1` | tooth width bf1 | ISO 606 (≈0.95 × inner width) | `tooth_width` | catalog **9,1** = our 10B b1 |
| `D2` | hub outside Ø | catalog proportion: 1.58–1.9 × D3, ≤0.85 × df | `hub_d` (+ `check` bounds 1.55·bore … 0.87·df) | 35–80 |
| `D3` H7 | finished bore | — | `bore_d` (rim cap: 0.50·df Form A, 0.58·df Form B) | 15–42 |
| `L` | overall length = B1 + hub protrusion | — | `tooth_width + hub_len`; sample 1.5–2.4 × b1 | L−B1 = 15,9 / 20,9 ≈ 1.75 / 2.3 × b1 |
| `B3` H9 | keyway width b | **DIN 6885-1 Form A** | `keyway_dims()` width | bore 16→**5**, 19→**6**, 25→**8**, 32→**10**, 40→**12** — all match |
| `T2` | keyway hub-seat depth t2 | DIN 6885-1 t2 (hub side) | `keyway_dims()` depth (true t2 table) | catalog **2,3 / 2,8 / 3,3** = DIN t2 for b = 5/6/8+ |
| keyway note | "aligned with the tooth tip" | catalog convention | `build()` rotates profile so a tip sits on +Y over the keyway | — |
| `D4` | grub-screw threads (M4–M10, one on keyway centre, one at 90°) | — | **not modeled** (sub-mm features) | — |
| `C`, `R` | tooth side chamfer / side radius | manufacturer finish | approximated by rim chamfer `0.15·b1` | C = 1,6 · R = 16 (constant) |
| `Form A / B` | A = disc + one-sided hub; B = straight barrel hub | — | `form_b` variant param: build() branches; check() allows Form B bores to 0.58·df (row …1024: 24/41,11 = 0.584) | both modeled |
| material notes | C45, HRC 50, bright | — | out of scope (geometry benchmark) | — |

## Deliberate deviations

1. **Tip Ø uses a fitted 0.68·d1 offset**, not the ISO band edges — reproduces
   this catalog; other manufacturers pick other values inside the band.
2. **Grub screws are not modeled** — sub-mm thread features add little
   geometric signal for the benchmark. (Form B *is* modeled, as the `form_b`
   heterogeneous variant.)
3. **`C`/`R` tooth side finishing** approximated by a rim chamfer.
4. **bore rim caps are per-variant**: 0.50·df for Form A, 0.58·df for Form B
   (the catalog's own …1024 row).
