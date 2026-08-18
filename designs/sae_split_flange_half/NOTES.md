# SAE split-flange half — source notes

Primary source: [Anfield Industries, *Flange Catalog / Split Flanges*, Rev. C](https://anfieldind.com/wp-content/uploads/2026/04/01_Anfield-Flange-general-Catalog_Rev.C.pdf), p. 1, “Code 61 Split Flange”. Cross-check: [Anchor Fluid Power, *Flange Catalog*](https://onehydraulicsdata.s3.amazonaws.com/DATASHEETS/AnchorFlangeCatalog.pdf), printed pp. 83–84.

Anchor states that its split-flange connections are manufactured to SAE J518-1/-2 and ISO 6162-1/-2. The implemented family is Code 61 only (SAE J518-1 / ISO 6162-1), nominal sizes 1/2–5 in.

Rev. C also lists `-H` high-pressure catalog variants at 1-1/4, 1-1/2 and
2 in. Those repeat the same A-G/I/K envelope and change H plus the catalog
working-pressure rating. This family follows issue #254's one baseline Code 61
row per nominal size; it does not claim to model the separate `-H` product
suffix.

## Symbol mapping

| Drawing | Meaning | `part.py` / `spec.py` | Evidence |
|---|---|---|---|
| A | flange-head counterbore diameter | `counterbore_d` | Anfield p. 1 table |
| B | smaller through bore behind the shoulder | `bore_d` | Anfield p. 1 table |
| C | bolt-hole centre spacing within one half | `bolt_spacing` | Anchor p. 84 three-decimal values through 4 in; Anfield for 5 in |
| D | overall end-to-end length | `overall_length` | Anfield p. 1 table |
| E | pattern centreline to bolt centre | `split_to_bolt` | Anfield p. 1 table |
| F | half width / forged outline | `half_width` | Anfield Rev. C p. 1 table |
| G | maximum crown thickness | `overall_thickness` | Anfield p. 1 table |
| H | bolt-ear plate thickness | `plate_thickness` | Anfield p. 1 table |
| I | stepped-bore lip depth | `lip_depth` | Anfield p. 1 table |
| K | bolt clearance-hole diameter | `bolt_hole_d` | Anfield p. 1 table |
| 0.039–0.060 | split-face setback from pattern centreline | `split_setback` | Anfield p. 1 drawing note |

All table dimensions are stored in inches and converted to millimetres by
`25.4 mm/in`. Each sample selects one complete row. In particular, the model
does **not** assume `G = H + I`; the catalog disproves that relation for several
sizes.

## Evidence checks

- Anfield 1/2 in row: A = 1.22, B = 0.96, C = 1.50, D = 2.13 in. Anchor gives the corresponding standard bolt spacing as C = **1.500** in.
- Anfield 1 in row prints C = 2.06 in; Anchor’s three-decimal Code 61 value is **2.062** in. The implementation uses the latter.
- Anfield 5 in row supplies the declared maxima A = 6.43, B = 5.53, C = 6.00, D = 7.24 in.

Anchor's p. 84 letters are not the same schema as Anfield's: for example,
Anchor F/G/H correspond approximately to Anfield A/B/I, while Anchor B is
the overall length. Anchor also stops its split-half table at 4 in and differs
slightly on manufacturer-specific forging and clearance values (for example
1/2 in F/G = 1.219/.955 and J = .350). Those columns are cross-checks only;
the model keeps Anfield as its coherent primary row and substitutes only the
more precise standard bolt spacing C.

## Deliberate geometric interpretation

The Rev. C side view shows the entire bridge block bulging outward from ear
thickness H to maximum thickness G, but it does not dimension the generating
radius. The outer kidney/bridge profile and local transition into the bolt
pads are therefore modeled as honest proportions constrained by B, D, E, F,
G and H. They are not attributed to SAE/ISO tolerances. Threads, surface
texture, plating and the mating bolts/O-ring are outside this single-part
family.

The preview uses a smooth symmetric spline across the bridge width: both
radial edges return to H and the middle reaches G, so the block is an outward
convex cap rather than an inward cut. The transition stays at H through the
bolt-ear circle, begins at `E + 1.00*(D-C)/2`, and reaches the full G crown at
`E + 1.25*(D-C)/2`. A hidden 0.50 mm overlap into the H plate only stabilizes
the solid boolean and does not change the exposed H/G envelope. These are
explicit visual proportions for the undimensioned forging transition, not
additional catalog dimensions.
