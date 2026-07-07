# SOP: the evidence package of a family issue

Every family issue carries a complete evidence package — **all three are
mandatory** (worked example: [issue #1](../../../issues/1), norelem 22253):

1. **One anchoring standard/catalog** (link; e.g. ISO 606 via norelem 22253)
2. **A dimensioned drawing** — the engineering drawing with dimension symbols
   (D, D1, B1, …). A product photo is a nice extra, never a substitute.
3. **A dimension table** — the standard's rows (markdown table in the issue;
   include the **min and max rows** explicitly, link the full datasheet)

Acceptance later checks against exactly these: `preview_views.png` vs the
drawing, the `coverage` gate vs the table, and `preview_extremes.png` (the
smallest and largest generated part) vs the table's min/max rows.

## Where images live

**Never** drag images into the issue by hand — store them in the repo so they
are versioned and the issue survives CDN changes:

```
docs/assets/refs/<family>_photo.png      product photo
docs/assets/refs/<family>_drawing.png    dimensioned drawing (preferred!)
```

Referenced in the issue via
`https://raw.githubusercontent.com/BenchCAD-org/benchcad-2/main/docs/assets/refs/<file>`.

## Path A — pull the original image from a catalog page (best quality)

1. **Find the product page**: search `norelem <part> DIN ISO` (also good:
   Misumi, McMaster, TraceParts). Prefer pages that anchor a standard.
2. **Open it in the browser**; on the cookie banner choose *Deny /
   necessary-only*.
3. **Extract the original image URLs** from the DOM (one line in the console —
   don't screenshot the page, the CDN original is sharper):
   ```js
   [...document.querySelectorAll('img')].map(i=>i.src)
     .filter(s=>/Zoom|product|media/i.test(s))
   ```
   norelem convention: `Zoom-Default-<article>-….png` = product photo,
   `Zoom-Default-Z<article>.png` = **dimensioned drawing** (the prize).
4. **Download** with curl (browser UA), drop into `docs/assets/refs/`,
   `file *.png` to sanity-check.

## Path B — datasheet PDF (when the page is JS-hostile)

norelem datasheets have stable static URLs:
`norelem.com/xs_db/DOKUMENT_DB/www/NORELEM/DataSheet/en/<NN>/<article>_Datasheet_…--en.pdf`
Download, convert the first page (`sips`/`pdftoppm`), crop the photo/drawing
regions.

## Path C — screenshot (last resort)

Browser zoom-screenshot of the image region. Lowest quality; only when A and B
fail.

## Attach to the issue (fixed format)

Append to the issue body:

```markdown
## Reference images

| Product | Dimensioned drawing |
|---|---|
| ![photo](<raw-url>_photo.png) | ![drawing](<raw-url>_drawing.png) |

*Source: [<vendor> <article> — <title>](<product-page-url>) · [datasheet PDF](<pdf-url>).
Drawing symbols (D, D1, …) map to design parameters — see the simplex NOTES.md
for the pattern.*
```

Then append the **dimension table** section: symbols legend + markdown table
with at least the min row, 3–4 representative rows, and the max row; link the
full datasheet. Add an implementer note (coverage declaration, any derived
relations you spotted, e.g. "B2 = b1 + pt, constant").

Rules: always name the **source with a link** (catalog images are used as
review reference with attribution); the drawing is mandatory — its dimension
symbols become the family's parameter names; the photo is optional garnish.
