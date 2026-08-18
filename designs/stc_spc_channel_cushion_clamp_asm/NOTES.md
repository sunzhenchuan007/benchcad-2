# STC / SPC geometry notes

The catalogue rows are atomic: `catalog_row` selects D1, B, C, D, E and the
UNC thread together. No interpolation is used. The assembly has five real,
named components: two separated left/right steel strut-clamp halves, one
D-shaped elastomer insert, one transverse cross-bolt, and one lock nut. The
steel halves remain separated by a visible centre gap through the crown.

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
Its recoverable contact arrangement informs the fastener and cushion mating
surfaces, but its continuous steel topology is not transferred to the STAUFF
model. The STAUFF catalogue drawing and product photograph show the top-centred
fastener between separately terminated left/right clamp halves. Component names
and material semantics rely on that product evidence, not on STEP assembly
metadata.

Reference axes and recovered relations:

- pipe/bore axis: global Y;
- tightening bolt axis: global X;
- rail-facing/down direction: global -Z;
- cushion depth: Y=-19.05..19.05 mm;
- steel width: Y=-15.875..15.875 mm, leaving 3.175 mm cushion overhang per end.

## Contact construction

The model derives every mating pair from a shared datum rather than positioning
independently generated shapes afterward:

1. Both steel halves are cut from the same unperforated D blank used to build
   the cushion. This gives coincident cylindrical/planar side contacts with zero
   shared volume. Two reduced-depth seats touch the cushion's flat underside.
2. The cross-bolt plain shank and both top-ear holes use the same nominal
   radius. The shank crosses the visible centre gap, and the bolt-head bearing
   face is the +X outer-ear face.
3. The nut begins on the -X outer-ear face, so its bearing face is exactly
   coincident with the left steel half.
4. The nut bore is cut by the actual external thread of the same cross-bolt.
   This guarantees coaxial mating and zero thread interference.
5. The cushion has no nominal contact with either bolt or nut.

The recovered HoldRite reference supports these mating-interface types, but not
the count or continuity of the STAUFF steel parts. Areas in the parametric
STAUFF family vary with the catalogue row; the zero-volume interference rule is
invariant.
