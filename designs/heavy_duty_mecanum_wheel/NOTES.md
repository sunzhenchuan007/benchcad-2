# NEXUS NM heavy-duty mecanum-wheel modeling notes

## Evidence boundary

The five manufacturer STEP files are measurement/reference evidence only and
are never imported by `part.py`. The submitted geometry is independently
rebuilt with CadQuery. Do not commit or redistribute the STEP or ZIP files.

Published catalog coupling retained by `spec.py`:

| model | wheel diameter | plate outer-face width | published set load |
|---|---:|---:|---:|
| NM127A | 127 mm | 66 mm | 200 kg |
| NM152A | 152.4 mm | 80 mm | 300 kg |
| NM203A | 203 mm | 105 mm | 600 kg |
| NM254A | 254 mm | 128 mm | 1500 kg |
| NM305A | 304.8 mm | 156 mm | 3000 kg |

The loads apply to a complete four-wheel set; no per-wheel rating is invented.

## STEP measurements used by the reconstruction

| model | plate OD / thickness | hub OD / bore | bolt count / PCD / hole | roller max D / axis length | pin D |
|---|---:|---:|---:|---:|---:|
| NM127A | 120 / 12 | 50 / 17 | 8 / 40 / 4.2 | 28 / 63 | 5 |
| NM152A | 144 / 14 | 68 / 30 | 8 / 58 / 4.2 | 33 / 77 | 6* |
| NM203A | 192 / 17 | 68 / 30 | 8 / 58 / 4.2 | 43 / 105 | 8 |
| NM254AL | 240 / 20 | 98 / 35 | 8 / 80 / 6.8 | 56 / 130 | 10 |
| NM305A | 288 / 25 | 120 / 45 | 8 / 100 / 8.5 | 68.5 / 160 | 12 |

All dimensions are millimetres. `*` NM152A pin diameter is inferred from the
coaxial seat/bore geometry because the STEP assembly does not expose the same
separable pin body as the other rows. The plate-side through/counterbore pairs
measured 5/9, 5/9, 5/9, 8/15 and 10/18 mm respectively. Bolt count is fixed
topology because all five STEP models contain eight equally spaced holes;
PCD, hole diameter and the 0 or 22.5 degree phase are catalog-derived values.

The roller loft uses symmetric diameter samples measured at axial fractions
0, 0.20, 0.30, 0.40, 0.45 and 0.50. This reproduces the visibly crowned middle,
narrowed ends and short end land more faithfully than an ellipsoid. The five
half-profile diameter sets are stored in `CATALOG_DETAILS` in `part.py`.

Final whole-assembly bounding-box comparison (representative left hand):

| model | official STEP bbox | rebuilt bbox | maximum absolute delta |
|---|---:|---:|---:|
| NM127A | 127.000 x 127.000 x 68.741 | 126.994 x 126.994 x 68.740 | 0.006 |
| NM152A | 152.400 x 152.400 x 80.000 | 152.377 x 152.377 x 80.000 | 0.023 |
| NM203A | 203.200 x 203.200 x 106.700 | 202.989 x 203.000 x 106.700 | 0.211 |
| NM254AL | 254.000 x 254.000 x 132.249 | 253.974 x 253.987 x 132.250 | 0.026 |
| NM305A | 304.800 x 304.800 x 160.048 | 304.783 x 304.783 x 160.050 | 0.017 |

The NM203A catalog/drawing row publishes a 203.0 mm nominal wheel diameter,
while its STEP envelope measures 203.2 mm. `wheel_d` intentionally retains the
published 203.0 mm sourced value; the 0.2 mm nominal-versus-STEP difference is
not presented as a modeling tolerance. For all rows, published `overall_width`
is the side-plate outer-face width, while the larger STEP/rebuilt Z envelope
includes protruding axle-end hardware.

## Topology and handedness

The STEP assemblies show two mostly closed circular plates separated along the
wheel axis. Each plate has a broad shallow face recess, a central hub opening,
an eight-hole bolt circle, and eight local axle-seat ears that extend beyond
the nominal plate OD but remain inside the roller-defined wheel envelope. No
large spoke windows or independent bridge rods are present. The reconstruction
therefore uses two closed plate extrusions with locally cut roller-envelope
pockets and short integral mounting ears, one continuous stepped hub, eight
rollers and eight coaxial pins: 19 solids in total.

Roller centers are indexed every 45 degrees. Every local axis is the
circumferential tangent with the same 45-degree axial skew. `handedness=0`
matches the common skew direction seen in the official NM254AL left-hand STEP;
`handedness=1` reverses only that axial component. Thus all eight rollers on a
wheel remain consistent and the two hands are exact axial mirrors.

## Proportion assumptions and omissions

- Face-recess depth/radius, keyway width/depth, local seat wall thickness,
  small counterbore depth and unmeasured transition radii are explicit
  proportions derived from the corresponding catalog row.
- The modeled pins reproduce the visible STEP assembly envelope; published
  `overall_width` remains the distance between plate outer faces.
- Hidden bearings, seals, threads, washers, grease, branding and small
  manufacturing fillets are omitted.
- External nut/bolt-head shapes and the exact cast/forged edge-seat blends are
  simplified into axisymmetric pin ends and smooth integral ears. The ears do
  reproduce the STEP's repeated outer-edge lobes and axle-seat silhouette.
