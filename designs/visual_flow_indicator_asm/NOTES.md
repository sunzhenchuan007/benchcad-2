# HVF geometry notes

## Source mapping

The ELESA `HVF` datasheet, revision 10/2025, pages 1-2 contains 15 complete
rows: five nominal sizes across brass BSPP, AISI 316 BSPP, and brass NPT
executions where offered. `catalog_row` selects an indivisible printed row.

| Size | H | L | B / plan | h1 | s | End layout |
|---|---:|---:|---:|---:|---:|---|
| 1/4 | 66 | 44 | 27 | 22 | 20 | two-rod lozenge |
| 3/8, 1/2 | 92 | 60 | 40 | 36 | 28 | two-rod lozenge |
| 3/4, 1 | 114 | 70 | 70 square | 46 | 46 | four-rod square |

Female BSPP major diameters and pitches follow ISO 228-1; NPT major diameters
and pitches follow ASME B1.20.1. Each boss has a continuous minor bore, a
major-diameter entrance, and three major/minor relief bands. NPT relief bands
shrink with the 1:16 diameter taper. BSPP and NPT use their respective
approximate diametral thread depths. The reliefs show thread presence and form,
but are not a helical manufacturing thread.

## Assembly relations

- Both bosses, end-body passages, the glass-tube bore, rotor, and axle share
  the global Z flow axis, so inlet and outlet form one connected passage.
- The glass tube bears on the two inner end faces. Separate packing rings sit
  in annular recesses outside the glass wall.
- The annular rotor hub clears the axle. Two blades are pitched about their
  local span axes and remain inside the glass bore for the full pose range.
- Small catalog rows use two tie rods; large rows use four. Each hollow tie rod
  is clamped between the end bodies by a separate through screw and lower nut,
  matching the vendor's distinct `TIE RODS` and `SCREWS AND NUTS` callouts.
- `rod_count` therefore drives three BOM quantities. The family intentionally
  omits a fixed `solids` value and resolves to 15 bodies for small rows and 21
  bodies for large rows.

## Deliberate deviations

The vendor STEP is measurement evidence only and is not imported. It exports a
single fused solid and does not preserve the functional assembly decomposition.
Unpublished glass wall, end plate/boss split, boss hex width, thread entrance
and relief lengths, tie-rod/screw/nut dimensions, rotor blade pitch and section,
axle, seal section, fillets, and clearances are documented `proportion`
reconstructions. The simplified CAD does not claim pressure, flow-rate,
temperature, viscosity, sealing, or material performance.
