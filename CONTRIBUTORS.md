# Contributors — the provenance board

**Auto-generated** by `.github/workflows/credits.yml` from the issues and PRs
themselves (SOP 📒 records) — do not edit by hand. Merged family ⇒ the row
below, named credit in the dataset card of the release that ships it, and
co-authorship on the BenchCAD 2.0 paper (see [CONTRIBUTING.md](CONTRIBUTING.md)).

| Family | Design author | Proposed | Implemented | Verified | Primary source |
|---|---|---|---|---|---|
| `banjo_bolt` | [@BenchCAD](https://github.com/BenchCAD) | [@BenchCAD](https://github.com/BenchCAD) · 2026-07-12 · #100 | [@BenchCAD](https://github.com/BenchCAD) · #116 | [@HaozheZhang6](https://github.com/HaozheZhang6) [@aqixiaoqi](https://github.com/aqixiaoqi) | DIN 7643 hollow-screw table (fasteners.eu): thread size, hex s, shank d3, bore d4, cross-hole d2, l1, t1, head height m, c1 (row-locked, M10x1..M26x1.5). ISO 261 fine pitch (1.0/1.5). Cross-drill count is a real single/double banjo variant. Reference: issue #100. |
| `duplex_sprocket` | [@HaozheZhang6](https://github.com/HaozheZhang6) | [@BenchCAD](https://github.com/BenchCAD) · 2026-07-06 · #1 | [@BenchCAD](https://github.com/BenchCAD) · #23 | [@HaozheZhang6](https://github.com/HaozheZhang6) | norelem 22253 datasheet (sprockets duplex 5/8" x 3/8" DIN ISO 606) |
| `example_tee_bracket` | [@BenchCAD](https://github.com/BenchCAD) | bootstrap (pre-SOP) | — | — | structural-bracket proportions |
| `extrusion_profile_4040` | [@BenchCAD](https://github.com/BenchCAD) | [@BenchCAD](https://github.com/BenchCAD) · 2026-07-06 · #17 | [@BenchCAD](https://github.com/BenchCAD) · #85 | [@HaozheZhang6](https://github.com/HaozheZhang6) | item Profile 8 40x40 (art. 0.0.026.03) |
| `flanged_bushing` | [@BenchCAD](https://github.com/BenchCAD) | [@BenchCAD](https://github.com/BenchCAD) · 2026-07-06 · #13 | [@BenchCAD](https://github.com/BenchCAD) · #52 | [@HaozheZhang6](https://github.com/HaozheZhang6) | norelem 23761 datasheet (plain bearing sintered bronze with collar, 61 articles over the bore series) |
| `hex_cap_bolt` | [@BenchCAD](https://github.com/BenchCAD) | [@BenchCAD](https://github.com/BenchCAD) · 2026-07-06 · #8 | [@BenchCAD](https://github.com/BenchCAD) · #55 | [@HaozheZhang6](https://github.com/HaozheZhang6) [@aqixiaoqi](https://github.com/aqixiaoqi) | ISO 4017 (hexagon head screws, full thread) |
| `lifting_eye_bolt` | [@BenchCAD](https://github.com/BenchCAD) | [@BenchCAD](https://github.com/BenchCAD) · 2026-07-09 · #76 | [@BenchCAD](https://github.com/BenchCAD) · #77 | — | DIN 580 dimension table (d2 eye inner, d3 eye outer, l thread length) per nominal thread size |
| `simplex_sprocket` | [@HaozheZhang6](https://github.com/HaozheZhang6) | [@BenchCAD](https://github.com/BenchCAD) · 2026-07-07 · #22 | — | — | norelem 22250 datasheet (single sprockets 5/8" x 3/8" DIN ISO 606, ready to install) |
| `socket_head_cap_screw` | [@BenchCAD](https://github.com/BenchCAD) | [@BenchCAD](https://github.com/BenchCAD) · 2026-07-09 · #66 | [@BenchCAD](https://github.com/BenchCAD) · #67 | [@HaozheZhang6](https://github.com/HaozheZhang6) [@miachen0401](https://github.com/miachen0401) | ISO 4762 head diameter dk, head height k, socket width s table |
| `v_belt_pulley` | [@BenchCAD](https://github.com/BenchCAD) | [@BenchCAD](https://github.com/BenchCAD) · 2026-07-06 · #5 | [@BenchCAD](https://github.com/BenchCAD) · #159 | — | ISO 4183 (narrow V-belt pulleys SPZ/SPA/SPB): groove datum widths/depths, pitch e, edge distance E, groove angle 34/38 deg by datum diameter, rim width B = 2E + (N-1)e, and minimum datum diameter per section (63/80/112 mm). The datum-line offset and ball-check ba offsets are simplified (proportion). |

*Proposed = family-issue author · Implemented = merged-PR author (who also
verified the issue's evidence at claim time, per CONTRIBUTING.md) · Verified =
approving [reviewer](REVIEWING.md).
"bootstrap (pre-SOP)" marks the reference designs that predate this workflow.*
