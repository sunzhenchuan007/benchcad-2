# knurled_thumb_screw_din464 — source notes (DIN 464 → design mapping)

## Symbol mapping

| DIN 464 | Meaning | part.py / spec.py |
|---|---|---|
| d / P | thread nominal / ISO 261 coarse pitch | `thread_dia_d`, `_PITCH` |
| dk / h / k | head Ø / head height / knurl band | `head_dia_dk` / `head_h` / `knurl_band_k` |
| ds | collar (shoulder) Ø | `collar_dia_ds` |
| b | thread length from the tip | `thread_len_b` (rings; last crest ≤ b) |
| l | shank length | `shank_len_l` — drawn inside the per-size availability band |
| r | collar → head-disk blend | `collar_fillet_r` (row-locked 0.5 / 1 / 2) |
| c | disk rim chamfer | applied to BOTH disk rims as min(0.15·k, 0.1·dk) |
| n | knurl pitch band | knurl approximated as straight flutes (count = proportion) |

## Length availability (page l/mass matrix → _L_BANDS)

The source page lists l = 2…40 with a per-size mass matrix; empty cells =
not available. Bands used (lower ends lifted to b + 2·P so the plain neck
under the collar survives): M1 3.6–5, M2 7–10, M3 10.2–12, M4 13.5–16,
M5 16.7–20, M6 20.1–25, M8 26.6–40, M10 33.1–40. Two cells of the matrix are
ambiguous in the crawl (collapsed empty columns around the bracketed M3.5
size); the bands stay inside the unambiguous span.

## Deliberate deviations

1. Thread = revolved 60° V-rings (the swept helix silently no-ops on the M6
   and M8 rows); same flanks / depth / 0.25·P overcut.
2. c is a proportional chamfer (min(0.15·k, 0.1·dk)) applied to both rims —
   the page's c row exists but its column mapping is ambiguous in the crawl.
3. Straight knurl approximated by axial flutes (count 16–44, proportion);
   DIN 82 knurl pitch not modelled tooth-accurately.
