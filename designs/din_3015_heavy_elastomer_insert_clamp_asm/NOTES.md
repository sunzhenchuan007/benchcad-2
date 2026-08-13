# Source and proportion map

The dimensional anchor is STAUFF Catalogue 1 - STAUFF Clamps, English,
version 06/2026, page 42 (DIN 3015 Part 2, Heavy Series, type RI). The official
drawing and product image show two separate clamp-body halves and **one**
elastomer insert made from two semicircular lobes joined by a visible film
hinge. The model therefore returns exactly three named solids; the insert is a
connected component, not two loose rings or a merely slit cylinder.

| Model quantity / feature | Source boundary |
|---|---|
| D, D1, L1, L2, H, B and group | printed page-42 table |
| PP-R / PA-R body material codes | printed page-42 ordering key; metadata only |
| SA73 for 4S-6S; E70 for 8S-10S | printed page-42 insert-material entries; metadata only |
| two insert lobes and visible film hinge | official page-42 drawing/product image |
| small retention bands | visible official insert detail; count/size unmarked |
| annular cavity seating grooves | visible official clamp detail; depth/width unmarked |
| split gap | `proportion`: `clamp(0.010 H, 0.25 mm, 0.80 mm)` |
| insert radial clearance | `proportion`: `max(0.20 mm, 0.006 D1)` |
| insert axial end clearance | `proportion`: `0.08 B` at each end |
| seating-groove radial depth | `proportion`: 150% of radial clearance |
| seating-groove axial width | `proportion`: `0.09 B` |
| mounting passage diameter | `proportion`: `min(0.24 B, 0.28 (L1-L2))` |
| counterbore diameter | `proportion`: `min(1.65 passage_d, 0.46 B)` |
| counterbore depth | `proportion`: 12% of one clamp-half height |
| outside corner radius | `proportion`: `min(0.09 B, 0.06 H)` |
| hinge radial thickness | `proportion`: `min(0.30 insert_wall, 0.12 D1)` |
| hinge overlap into each lobe | `proportion`: `max(0.50 mm, 0.015 D1)` |
| retention-band radial height | `proportion`: 125% of radial clearance |
| retention-band axial width | `proportion`: `0.06 B` |

`CATALOG_ROWS` contains 40 complete, sampleable rows: 4S, 5S, 6S, 8S, 9S
and 10S. The following eight printed 7S rows are retained explicitly in
`HELD_7S_ROWS`, but are not sampled because page 42 does not assign their
insert material:

| Group | D values (mm) | D1 / L1 / L2 / H / B (mm) | Status |
|---|---|---|---|
| 7S | 55, 57, 60, 63.5, 65, 70, 72, 76 | 88 / 154 / 122 / 120 / 60 | held: insert-material gap |

The assembly is a fixed catalog pose. Polymer names remain categorical
metadata: geometry does not model stiffness, compression, friction, ageing or
the film hinge's motion. The supported pipe/tube/hose and mounting hardware
are context, not shipped component bodies.

## Reuse boundary with Issue #355

The local `_half_blank`, `_mounting_points`, mounting through-hole cutter and
outside counterbore cutter intentionally follow the same signatures and duties
as the adjacent DIN 3015 implementation. Those generic rectangular-half and
mounting-cut primitives can later be promoted to `bench2.geomlib`. Catalog
rows, material rules, cavity/insert profiles, the connected film-hinged insert
and its retention details remain family-specific. No Issue #355 annular
profile relief was copied; the only bands here are source-visible details on
the elastomer insert.
