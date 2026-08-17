# Source and STEP anchor

The dimensional table is STAUFF *Catalogue 1 - STAUFF Clamps*, English,
06/2026, page 42 (DIN 3015 Part 2, Heavy Series, type RI).  The supplied
official `1110008634.STEP` identifies its product geometry as `4006_PPR` and
anchors the unmarked local features for the Group-4 / D=6 mm row.

The STEP contains exactly three solids and has a 70 x 46.5 x 30.5 mm envelope:
two molded body halves and one connected stepped annular insert.  It does not
contain a split or film-hinged two-lobe insert.

## Catalogue and STEP mapping

| Quantity / feature | Evidence |
|---|---|
| D, D1, L1, L2, H, B and group | printed page-42 table |
| PP-R / PA-R body material codes | printed page-42 ordering key; metadata only |
| SA73 for 4S-6S; E70 for 8S-10S | printed page-42 insert-material entries; metadata only |
| two body halves plus one insert | `1110008634.STEP`, three valid solids |
| Group-4 insert core | STEP: OD 25, ID 6, full width 30.5 mm |
| Group-4 central insert band | STEP: OD 31.5, axial width 15.25 mm |
| Group-4 split gap / axial clearance | STEP: zero in the fixed closed pose |
| Group-4 mounting passage | STEP cylindrical surface: diameter 10.4 mm |
| Group-4 outside counterbore | STEP: diameter 18 mm, floor 9 mm from outside |
| Group-4 plan corner radius | STEP cylindrical surface: radius 8 mm |
| outside molded lattice | STEP: perimeter wall, centre/cross ribs and circular lands |

The STEP-observed Group-4 proportions are applied deterministically to the
other printed rows:

- central-band radial height and matching body groove depth: `0.13 D1`;
- central-band and matching groove width: `0.50 B`;
- mounting passage: the minimum of `0.341 B`, `0.416 (L1-L2)`, and the
  positive-clearance limit beside the insert cavity;
- outside counterbore: `min(0.590 B, 0.720 (L1-L2))`;
- counterbore depth: `0.387` of one body-half height;
- plan corner radius: `0.262 B`;
- simplified molded outside relief depth: `0.408` of one body-half height,
  volume-calibrated against the supplied STEP's deeper drafted pockets.

The assembly uses the source STEP axes: X is L1, Y is H, and Z is B.  Fine
molding draft, product lettering and tiny local radii are omitted, but the
main envelope, three-solid topology, stepped insert, mounting interfaces and
deep ribbed cavities are retained.

## Sampled rows

`CATALOG_ROWS` contains 40 material-complete rows: 4S, 5S, 6S, 8S, 9S and
10S.  The catalogue's eight Group-7S dimensional rows remain explicit in
`HELD_7S_ROWS` but are not sampled because page 42 does not assign their insert
material.

The supported pipe/tube/hose and mounting hardware are context, not shipped
component bodies.  Material codes do not simulate stiffness, compression,
friction, ageing or tolerances.

## Reuse boundary with Issue #355

The half blank, mounting-point layout, through-hole cutter and outside
counterbore cutter keep the same narrow duties as the adjacent DIN 3015
family.  The RI stepped insert, matching central groove and molded relief
remain family-specific.
