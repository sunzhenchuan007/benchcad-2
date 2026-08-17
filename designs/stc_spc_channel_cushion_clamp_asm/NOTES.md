# STC / SPC geometry notes

The catalogue rows are atomic: `catalog_row` selects D1, B, C, D, E and the
UNC thread together. No interpolation is used. The assembly has four real,
named components: one continuous steel strut clamp, one D-shaped elastomer
insert, one transverse cross-bolt, and one lock nut.

The catalogue does not dimension clamp depth, cushion overhang, service-slit
width, channel-hook reach, bolt-head proportions, nut AF/height, or thread
projection. Those values are deterministic proportions of the printed
B/E/thread envelope. The channel-facing lips point toward global -Z and
represent the engagement interface of a 41.3 mm SCS channel; the rail itself is
not emitted.

The reusable standard-component library was reviewed, but its public threaded
fasteners are ISO metric M3--M16. This catalogue explicitly selects 1/4-20,
5/16-18, or 3/8-16 UNC, so substituting M6/M8/M10 would be false. The local
60-degree helical construction uses the actual catalogue pitches: 1/4-20 =
1.270 mm, 5/16-18 = 1.411 mm, and 3/8-16 = 1.5875 mm. The nut's internal
thread is cut by the exact mating bolt geometry, which preserves the modeled
thread while preventing shared volume. The nylon locking insert is omitted.

Heldout migration: the family uses the required assembly suffix
`stc_spc_channel_cushion_clamp_asm`; the linked Issue is #343.

## Homologous topology reference

The otherwise-unmarked construction was studied against Reliance Worldwide
Corporation / HoldRite model `HR100100-4-555`, downloaded from the official
[3D CAD publisher page](https://bim.rwc.com/cadpublisher/100-304ss-series-strut-mount-cushion-clamp/hr100100-4-555-1?Partid=117565&ViewId=67475&plpver=20&uomval=Imperial&vwNm=3D&rfxid=20&RestOfPartIds=118087&IsEmbedded=true).
The file is an AP242 STEP exported by TraceParts. It is a homologous 1-inch
strut-mounted clamp, not a STAUFF catalogue model, so none of its dimensions
replace a printed STAUFF D1/B/C/D/E/thread value.

The AP242 file stores one fused `MANIFOLD_SOLID_BREP`, not an assembly tree.
An exact geometric partition nevertheless recovers four non-overlapping
logical bodies whose union reproduces the source: `steel_strut_clamp`,
`cushion_insert`, `cross_bolt`, and `lock_nut`. Component names and material
semantics additionally rely on the product specification and visible fastening
arrangement; they are not claimed as STEP assembly metadata.

Reference axes and recovered relations:

- pipe/bore axis: global Y;
- tightening bolt axis: global X;
- rail-facing/down direction: global -Z;
- cushion depth: Y=-19.05..19.05 mm;
- steel width: Y=-15.875..15.875 mm, leaving 3.175 mm cushion overhang per end.

## Contact construction

The model derives every mating pair from a shared datum rather than positioning
independently generated shapes afterward:

1. The steel cavity is cut with the same unperforated D blank used to build the
   cushion. This gives coincident cylindrical/planar side contacts with zero
   shared volume. Two reduced-depth seats touch the cushion's flat underside.
2. The cross-bolt plain shank and steel lug hole use the same nominal radius.
   The bolt-head bearing face is the +X lug face.
3. The nut begins on the -X lug face, so its bearing face is exactly coincident
   with the steel face.
4. The nut bore is cut by the actual external thread of the same cross-bolt.
   This guarantees coaxial mating and zero thread interference.
5. The cushion has no nominal contact with either bolt or nut.

The recovered HoldRite reference has the same contact graph. Its measured
nominal shared areas are 2459.106 mm2 (steel/cushion), 272.235 mm2
(steel/bolt), 76.500 mm2 (steel/nut), and 116.543 mm2 (bolt/nut). Areas in the
parametric STAUFF family vary with the catalogue row; the graph and zero-volume
interference are invariant.
