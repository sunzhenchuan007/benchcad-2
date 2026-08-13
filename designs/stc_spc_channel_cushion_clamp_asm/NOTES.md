# STC / SPC geometry notes

The catalogue rows are atomic: `catalog_row` selects D1, B, C, D, E and the
UNC thread together. No interpolation is used. The two steel halves, elastomer
cushion and lock nut are separate named assembly components.

The catalogue does not dimension strap depth, cushion wall, slit width, hook
reach, stud length or nut proportions. Those values are deterministic
proportions of the printed B/E/thread envelope. The bottom lips represent the
inward engagement interface of a 41.3 mm SCS channel; the rail itself is not
emitted.

The standard-component demo was reviewed for its reusable construction
patterns. Its public nut/stud helpers are ISO metric M3--M16 only, while this
catalogue explicitly selects 1/4-20, 5/16-18, or 3/8-16 UNC. Mapping those
sizes to M6/M8/M10 would be false. Instead, the same reviewed 60-degree helical
construction is specialized locally with the actual catalogue pitches:
1/4-20 = 1.270 mm, 5/16-18 = 1.411 mm, and 3/8-16 = 1.5875 mm. The exposed
stud end has a modeled external thread, and the double-chamfered lock nut has
the matching modeled internal groove. The nylon locking insert remains
intentionally omitted; the unmarked nut AF/height and stud length are still
labelled `proportion`.

Heldout migration: family name uses the required assembly suffix `stc_spc_channel_cushion_clamp_asm`; linked Issue is #343.
