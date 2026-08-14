# toggle_latch_base_plate — Step 2 reconstruction notes

This implementation replaces the earlier base-plate-only abstraction with the
complete visible GN 832 latch shown by the supplied Step-1 extreme files.

Official sources:

- [Ganter GN 832 product page](https://www.ganternorm.com/en/products/product-family/Stainless-Steel-Quality-Class-2/GN-832-Toggle-latches-Steel-Stainless-Steel)
- [GN 832 dimension drawing](https://live-katalog.ganternorm.com/pdf/ganter/en/832.pdf?dispositiontype=attachment)

## Catalog row lock

`catalog_index` selects one entire official row. No dimensions are independently
mixed across sizes.

| index | size | FH (N) | b1 | b2 | b3 | b4 | b5 | b6 | d1 | d2 | d3 | h1 | h2 | l1 | l2 | l3 | m1 | m2 | m3 | m4 | r |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 55 | 550 | 23 | 17 | 14 | 44 | 13 | 30 | 2 | 3.2 | 2.6 | 11 | 9 | 102 | 60 | 34 | 9.5 | 12.5 | 5 | 12 | 26 |
| 1 | 150 | 1500 | 34 | 23 | 20 | 70 | 19 | 43 | 3 | 4.1 | 3.1 | 12.5 | 11 | 140 | 86 | 38 | 13 | 22.5 | 8 | 20 | 30 |
| 2 | 200 | 2000 | 43 | 30 | 26 | 90 | 27 | 66 | 4 | 5.3 | 5.3 | 19 | 15 | 191 | 111 | 57.5 | 10 | 31.5 | 15 | 25.5 | 36 |

## Visible modeled structure

- rectangular formed latch body with upturned operating lip;
- open clevis relief and transverse pivot pin;
- continuous U-shaped elastic latch wire at diameter `d1`;
- included catch bracket at `b6 × b5`, two `d2` holes using `m3/m4`;
- raised formed catch nose and the body safety-pin drilling `d3`.

## Honest Step-2 simplifications

The model returns one compound containing five visible, non-degenerate bodies:
formed latch body, separate operating lip, transverse pivot pin, elastic
U-wire, and catch bracket. The catch is placed in the closed/contact pose so
the U-wire bears on its raised nose. No hidden connector is added, and the
separate bodies are not claimed to be welded.

The official table does not provide sheet thickness or every stamped transition
radius. `sheet_t`, the operating-lip curve, catch-nose bend and small edge breaks
are explicitly proportional. Hidden mechanisms, manufacturing embossing,
textures and threads are omitted.

The Size 55 / Size 200 STEP reference envelopes are respectively
`105.813 × 11.941 × 22.636 mm` and `191.045 × 20.353 × 47.657 mm`. The CQ
extremes preserve the official `l1` layout and match the two measured Y/Z
cross-section envelopes; their X extents are `101.895 mm` and `190.805 mm`
(3.918 mm and 0.240 mm shorter than the STEP bounding boxes because the imported
STEP includes un-dimensioned formed end allowances beyond the catalog datum).
