# SK40 steep-taper shank — evidence and reconstruction notes

## Evidence hierarchy

1. **Source-locked interface:** KTA Spindle Toolings 2019 catalog p.101,
   “SK (DIN 69871) (DIN ISO 7388-1): Technical Information”, SK40 row.
2. **Cross-check named by Issue #187:** the independent ISO 7388-1 table agrees
   on shared columns `D`, `D1`, `D2`, `L1`, and `G`.
3. **Product-side reconstruction:** the user supplied a manually reconstructed
   `SK40.SLDPRT`, its exported `SK40.STEP`, and a generated CadQuery scaffold.
4. **OEM context only:** `SCHUNK-0263396 ER25 SK 40x100.sldprt` is the supplied
   manufacturer download. It stays outside the family package and is not read
   by `build()`.

The standard/interface dimensions override the manual SolidWorks geometry.
Undimensioned product-side controls use the honest source label `proportion`.

## Drawing symbols and code mapping

| Drawing | SK40 value | Code | Use |
|---|---:|---|---|
| `d` | 17 mm | `_ENTRY_BORE_D` | pull-stud entry counterbore |
| `D` | 44.45 mm | `_GAUGE_D` | 7:24 taper diameter at the gauge plane |
| `D1` | 63.55 mm | `_FLANGE_D` | maximum V-flange diameter |
| `D2 max.` | 50 mm | `_D2_MAX` / `check()` | product-side clearance envelope |
| `G` | M16 | `_THREAD_NOMINAL_D` | internal pull-stud thread |
| `L1` | 68.40 mm | `_TAPER_LENGTH` | small end to gauge plane |
| `L2` | 32 mm | `_THREAD_LENGTH` | pull-thread axial extent |
| `L3` | 8.2 mm | `_ENTRY_BORE_LENGTH` | entry counterbore length |
| `b` | 16.1 mm | `_DRIVE_SLOT_WIDTH` | flange drive-cut width scale |
| fixed | 3.2 / 11.10 / 15.90 mm | module constants | flange axial datums |
| `L4/L5/L6` | 22.8 / 25 / 18.5 mm | module constants | retained SK40 end-view landmarks |
| fixed | 4.60 / Ø10 mm | module constants | retained orientation-feature landmarks |

The catalog also lists `d1=4` and `e=27` for the optional AD/AF
through-flange coolant forms shown separately on p.101. This contribution
models the base form represented by the supplied reconstruction, so it does
not add those optional coolant passages.

## Equations and reconstructed controls

There are exactly **three independent build parameters**:

| Independent parameter | Baseline | What it changes |
|---|---:|---|
| `body_d` | 42.0 mm | diameter of the long cylindrical product body |
| `body_length` | 46.9 mm | straight length of that body |
| `nose_d` | 42.0 mm | overall scale of the ER25-style slotted end |

All remaining product-side dimensions are derived from baseline ratios measured
from the supplied human STEP:

```text
neck_d          = body_d × 33 / 42
neck_length     = body_d × 4.5 / 42
through_bore_d  = body_d × 18 / 42

nose_length      = nose_d × 25 / 42
collet_opening_d = nose_d × 19.0718 / 42
slot_width       = nose_d × 4.5 / 42
slot_depth       = nose_d × 3.2 / 42

edge_break = min(body_d, nose_d) × 0.5 / 42
```

The reconstructed body transition, nose bevel, and collet-seat half-angle are
fixed at 45°, 60°, and 8° respectively. They are not additional degrees of
freedom.

- The 7:24 taper is a **diametral** taper, so
  `small_diameter = _GAUGE_D - (7/24) * _TAPER_LENGTH`.
- The M16 coarse pitch is 2.0 mm (ISO metric coarse series). The internal basic
  minor diameter uses `D1 = D - 1.082532 P`, and a triangular cutter follows a
  true helix; the thread is not represented as smooth concentric rings.
- The body-to-neck and nose transitions retain the human modeler's intentional
  angle parameterization. Their axial runs are derived from radius change and
  the fixed angle instead of being independent arbitrary coordinates.
- Six product-end cutters are generated from `360 / _NUT_SLOT_COUNT`; their
  outward overshoot is construction-only and is not exposed as a parameter.
- The internal collet seat retains the approximately 8 degree half-angle
  measured from the supplied STEP. It is a fixed reconstruction proportion,
  not claimed as a DIN 6499 table value.

## Baseline comparison to the supplied STEP

The untracked reference STEP contains one valid solid with:

- bounding box: **63.50 × 63.50 × 168.25 mm**;
- volume: **179,506.814 mm³**;
- 156 faces: 51 cylinders, 42 cones, 43 planes, and 20 tori.

The final three-parameter baseline (`body_d=42`, `body_length=46.9`,
`nose_d=42`) is also one valid solid, with:

- bounding box: **63.55 × 63.55 × 168.40 mm**;
- volume: **179,291.972 mm³**;
- 121 faces.

This is +0.05 mm in each transverse envelope, +0.15 mm axially, and -0.120%
in volume relative to the supplied STEP. The remaining face-count difference
reflects the deliberately reconstructed finishing topology described below.

The generated converter scaffold has the same bounding box but volume
**180,855.422 mm³**, only 63 faces, and no toroidal faces because all nine
SolidWorks fillet/chamfer features were reported unsupported. The scaffold is
therefore a topology map, not the final acceptance geometry.

## Deliberate deviations

1. The OEM and reconstructed CAD files are not committed or loaded at runtime.
2. The three flange cutters preserve the manual STEP outline because the
   supplied evidence does not identify every local feature's function. Neutral
   names are used; no drive/locking purpose is invented for the third cut.
3. Undimensioned edge finishes are rebuilt as robust profile edge breaks,
   semantic circular-edge fillets at named axial landmarks, and conical
   transitions. Exact SolidWorks edge radii are unavailable from the converter
   log, so they are not presented as standard dimensions.
4. The three product-side parameter ranges vary around the manual
   reconstruction; every dependent dimension uses the disclosed ratios above.
   These are not claimed to be a SCHUNK catalog size ladder.
