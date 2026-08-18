# Engineering notes

Source: *STAUFF Catalogue 1 - STAUFF Clamps*, English, 06/2026,
pages 114-117, type MLC with standard smooth inside surface (`HV`).

The supplied `6100246250.STEP` is the 2-line Group-1 physical anchor. It
contains two valid solids and has an approximately 60.86 x 27 x 30 mm
envelope. The 30 mm body depth, rounded plan corners, outside perimeter wall,
fastener bosses, molded relief pockets, and longitudinal/cross-rib topology
are taken from that STEP. Fine molding draft and tiny local radii are omitted.

## Catalogue mapping and coupling

| Symbol | Build parameter | Meaning |
|---|---|---|
| D | `tube_od` | Common pipe/tube outside diameter |
| L1 | `length` | Overall body length |
| L2 | `pitch` | Adjacent tube-axis pitch |
| L3 | `span` | Fastener-passage pattern spacing |
| H | `height` | Total height including the split |
| B | `fastener_passage_count` | Through-fastener interface count |

The twelve `(line_count, group)` rows, expressed as L1/L2/L3/H/B in mm, are:

| Lines | Group 1 | Group 2 | Group 3 |
|---:|---|---|---|
| 2 | 60.5/20/40/27/2 | 78.5/29/58/33/2 | 92.5/36/72/37/2 |
| 3 | 56/20/20/27/2 | 85/29/29/33/2 | 106/36/36/37/2 |
| 4 | 76/20/40/27/2 | 114/29/58/33/2 | 142/36/72/37/2 |
| 6 | 116/20/40/27/3 | 172/29/58/33/3 | 214/36/72/37/3 |

`refine()` copies the complete selected topology/group row, then selects D
only from that group's published D list. Cross-group D/geometry combinations
are therefore impossible. Coverage includes the catalogue minimum 6, maximum
25.4, and overlapping values 15 and 18 mm.

## Unmarked dimensions (`source = "proportion"`)

| Group | `body_depth` | upper `passage_d` | lower tapped hole | `counterbore_d` | `counterbore_depth` |
|---:|---:|---:|---:|---:|---:|
| 1 | 30.0 | 4.5 | M4 x 0.7 | 8.0 | 3.0 |
| 2 | 30.0 | 6.0 | M6 x 1.0 | 12.0 | 4.0 |
| 3 | 30.0 | 8.0 | M8 x 1.25 | 16.0 | 5.0 |

The split is fixed at the drawing's nominal 1.0 mm. `check()` preserves the
passage/counterbore hierarchy, passage-to-seat clearance, surrounding wall,
and usable half height. The catalogue drawing specifies hole count and shows
outside-face counterbores but does not publish a thread callout. Per the user
request, only the lower half is tapped; M4/M6/M8 selection by group is an
explicit `proportion`, while the corresponding coarse pitches are ISO 261.
The upper half remains a clearance passage so a screw can clamp the split.

## Worked catalogue-row check

For 6-line/group-3/D=25.4: L1=214, L2=36, L3=72, H=37, B=3. The six seat
axes are `[-90,-54,-18,18,54,90]` mm and the three passage axes are
`[-72,0,72]` mm. Passage-to-seat clearance is
`L2/2 - D/2 - passage_d/2 = 18 - 12.7 - 4 = 1.3 mm`. Each half is
`(H-1)/2 = 18 mm` high, at Z `[-18.5,-0.5]` and `[0.5,18.5]`, giving the
specified 1.0 mm split and exact H=37 envelope.

## Deliberate deviations

- The STEP-visible outside pocket/rib/boss topology is retained. Pocket depth,
  wall/rib widths, boss margin, and plan-corner radius are documented
  proportions scaled across catalogue rows; fine draft and tiny radii remain
  simplified.
- Bolts, plates, and supported tubes are omitted. The upper half retains a
  smooth clearance passage; the lower half now contains a visible modeled
  internal metric thread after its outside counterbore. Thread size selection
  is a requested proportion, not a catalogue claim.
- PP, PA, and PA-VO material codes do not change nominal geometry; shrinkage
  and tolerances are not modelled.
- Request-only profiled seats and mixed-diameter bodies are excluded; all seats
  use the standard HV smooth equal-D form.

Heldout migration: family name uses the required assembly suffix `multi_line_pipe_clamp_body_asm`; linked Issue is #342.
