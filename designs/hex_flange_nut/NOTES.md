# hex_flange_nut - source notes (DIN 6923 / ISO 4161 mapping)

Primary inputs are the DIN 6923 / ISO 4161 dimension table and the drawing
attached to [family issue #150](https://github.com/BenchCAD-org/benchcad-2-heldout/issues/150).
The table rows were cross-checked against the DIN 6923 tables published by
fasteners.eu and Fuller Fasteners. Metric coarse pitch follows ISO 261; the
basic internal-thread geometry follows ISO 68-1 and ISO 965.

All catalog dimensions are sampled as one locked row. Dimensions not tabulated
by DIN 6923 are identified below as geometric construction or proportion.

## Symbol mapping

| Drawing / table | Meaning | Relation / source | `part.py` / `spec.py` | Verified row |
|---|---|---|---|---|
| `d` | nominal thread diameter | DIN 6923 / ISO 4161 row | `thread_dia_d` | M12: 12 mm |
| `P` | metric coarse pitch | ISO 261 | `_PITCH[d]` | M12: 1.75 mm |
| `s` | width across flats | DIN 6923 / ISO 4161 row | `hex_s` | M12: 18 mm |
| `e` | width across corners | hex construction: `e = s / cos(30 deg)` | local `e` | M12: 20.785 mm |
| `dc` | flange outside diameter | DIN 6923 / ISO 4161 row | `flange_dia_dc` | M12: 26 mm |
| `m` | total nut height | DIN 6923 / ISO 4161 row | `total_h_m` | M12: 12 mm |
| `c` | flange edge thickness | DIN 6923 / ISO 4161 row | `flange_thk_c` | M12: 1.8 mm |
| `D1` | basic internal minor diameter | `D1 = d - 1.0825 P`, ISO metric basic profile | `r_min = D1 / 2` | M12: 10.106 mm |
| 60 deg | internal thread profile angle | ISO 68-1 metric basic profile | swept triangular helical groove | one start, pitch 1.75 mm at M12 |
| 15 deg | upper hex face chamfer | issue #150 drawing | conical envelope intersected with the hex prism | M12 chamfer height: 0.373 mm |
| 90-120 deg | upper thread-entry included angle | issue #150 drawing | fixed at the permitted 120 deg value | M12 entry depth: 0.729 mm |
| - | flange cone height | proportion; not tabulated by DIN 6923 | `flange_seat_h = 0.30-0.48 m` | M12 sampled range: 3.60-5.76 mm |
| - | locking serration count and depth | proportion; serrated DIN 6923 variant | `serrations`, depth `0.4 c` | plain or 12-22 directional ramps |

The M12 face-chamfer check uses
`h = (e/2 - s/2) tan(15 deg) = 0.373 mm`. The M12 entry chamfer uses the
120-degree included angle selected from the drawing allowance and evaluates to
0.729 mm with the modeled entry radii.

## Deliberate deviations

1. The thread is a true single-start swept helix, but crest/root truncation,
   tolerance class, and manufacturing runout are simplified. The groove
   reaches the basic major and minor radii and overruns both faces to leave an
   open thread.
2. The drawing permits a 90-120 degree thread-entry chamfer; the model uses the
   120-degree endpoint for every catalog row. Entry radii are proportional
   because the table does not dimension them.
3. The 15-degree upper chamfer is modeled as a rotational conical envelope
   tangent to the wrenching flats. It removes all six upper corners and leaves
   a circular top land; the table does not give a separate land diameter.
4. Serrations are directional triangular ramps. DIN 6923 identifies the
   serrated variant but the cited table does not specify tooth count or tooth
   depth, so both are declared proportions rather than catalog dimensions.
5. Surface finish, coatings, material, markings, and thread tolerance class
   are outside the geometry benchmark.
