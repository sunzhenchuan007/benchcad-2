# NAS6203–NAS6220 close-tolerance bolt — source notes

Primary anchor: **NAS6203 THRU NAS6220, Revision 10 (20 Dec 2013)**,
“Bolt, tension, hex head, close tolerance, alloy steel, short thread, reduced
major thread dia., self-locking and nonlocking, 160 KSI Ftu”. The issue's
dimensioned Figure 1 and Table I/II transcription are the review evidence.

Cross-checks:

- [Jet-Tek NAS6203–NAS6210 Table I/II transcription](https://jet-tek.com/nas-bolts/nas6203-nas6210.php)
- [Fastener Dimensions NAS6203–NAS6220 series summary](https://www.fastenerdimensions.com/upload/documentgroups/mainfiles/NAS6203%20thru%20NAS6220.pdf)

## Modeled configuration

The geometry is the baseline undrilled, nonlocking, non-repair bolt. Optional
head/thread drilling, locking patches and plating codes do not change the core
Table I envelope and are intentionally omitted. Repair codes X/Y are also
omitted: the cited reproduction says “sheet 1 of 7” but does not provide sheet
7, so no repair-bolt dimensions are invented.

## Table mapping

| NAS symbol | Meaning | Parameter / relation |
|---|---|---|
| C | hex width across flats | `head_af`, midpoint of C min/max |
| D | close-tolerance plain shank | `shank_d`, midpoint of D min/max |
| E | under-head bearing diameter | `bearing_d`, published minimum |
| H | nominal head height | `head_height` |
| Thread UNJF-3A | nominal diameter and TPI | `thread_pitch`; modeled crest diameter is an explicit 0.99 proportion |
| GRIP | cylindrical plain length | `grip_length`, Table II dash ladder |
| (T) | fixed short-thread allowance | `thread_length` |
| LENGTH | under-head total length | exactly `grip_length + thread_length` in `part.py` |

Table II has 66 published grip entries: dash 1–32 followed by even numbers
34–100. The grip is dash/16 inch converted to the table's three decimals.

## Spot checks

- NAS6203: C = .376/.367, D = .1895/.1885, E min = .335,
  H = .110 in. Dash 6 gives grip .375 and length .698, so T = .323 in.
- NAS6220: C = 1.814/1.801, D = 1.2490/1.2475, E min = 1.772,
  H = .625 in. Table II gives T = 1.083 in.

The exact reduced-major and repair-bolt tolerance geometry is not available in
the issue evidence. The modeled thread crest is therefore honestly labeled a
`proportion`; it is not presented as an invented NAS tolerance.
