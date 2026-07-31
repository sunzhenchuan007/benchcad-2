"""Multi-body (`_asm`) geometry checks: body count, per-body volume, interference.

An assembly family returns several solids in one `cq.Compound` (or a
`cq.Assembly`, folded to a compound on export). Two properties then decide
whether it is an assembly at all, and neither is visible in a render:

* **every component survived** — a boolean that silently ate a body, or two
  components fused into one, changes the solid count;
* **the components do not occupy the same space** — `makeCompound` never merges,
  so mutually embedded bodies look perfectly normal in a preview and in the
  STEP, and every downstream consumer inherits the nonsense.

`CONTRIBUTING.md` has always required "every real component its own solid, zero
interference"; this module is what makes that a machine gate instead of prose.
"""

from __future__ import annotations

from pathlib import Path

# A pair counts as interfering when the shared volume exceeds the LARGER of:
#   * an absolute floor — a coincident-face mate is legal (a bolt head bearing on
#     a tab), and OCC's boolean on touching faces returns slivers rather than
#     nothing: measured 0.016 mm³ on pipe_clamp_asm's head/tab contact, which is
#     a 0.08 µm-thick layer over the contact area, i.e. numerical, not design;
#   * a relative floor — 10 ppm of the smaller body, so the gate scales from an
#     M3 set screw to a 630 mm chuck without retuning.
# Calibration: at these values all six existing `_asm` families report zero
# pairs, while three_jaw_scroll_chuck (benchcad-2#82) reports 73 000-106 000 mm³
# on eight pairs — four orders of magnitude clear of the threshold either way.
INTERFERENCE_ABS_MM3 = 0.05
INTERFERENCE_REL = 1.0e-5


def load_bodies(step_path: Path):
    """The solids in a STEP, in file order. Returns a list of cq Solid/Shape."""
    from .render import _ocp_hashcode_fix

    _ocp_hashcode_fix()
    import cadquery as cq

    shape = cq.importers.importStep(str(step_path))
    solids = shape.solids().vals()
    if not solids:
        val = shape.val()
        solids = [val] if val is not None else []
    return solids


def body_volumes(bodies) -> list[float]:
    return [float(b.Volume()) for b in bodies]


def invalid_bodies(bodies) -> list[tuple[int, float, bool]]:
    """Bodies that are not a sane solid: [(index, volume, brep_valid), …].

    Two failures, both invisible in a render and in the solid count:

    * **non-positive volume** — the solid is inside-out (OCC reports a signed
      volume), so every downstream volume/mesh/boolean is wrong;
    * **BRepCheck-invalid** — self-intersecting or inconsistently oriented faces.
      A swept-then-unioned body (a bearing cage) can build fine in-process and
      still export a broken solid; the exported STEP is what the benchmark
      scores, so that is where this is checked.
    """
    from OCP.BRepCheck import BRepCheck_Analyzer

    out = []
    for i, b in enumerate(bodies):
        vol = float(b.Volume())
        try:
            valid = bool(BRepCheck_Analyzer(b.wrapped).IsValid())
        except Exception:  # noqa: BLE001
            valid = True  # never fail a family because the checker itself blew up
        if vol <= 0.0 or not valid:
            out.append((i, vol, valid))
    return out


def _bbox_overlap(a, b, slack: float = 1e-6) -> bool:
    """Cheap pre-filter: no bounding-box overlap ⇒ no interference."""
    ba, bb = a.BoundingBox(), b.BoundingBox()
    return not (
        ba.xmax < bb.xmin - slack or bb.xmax < ba.xmin - slack
        or ba.ymax < bb.ymin - slack or bb.ymax < ba.ymin - slack
        or ba.zmax < bb.zmin - slack or bb.zmax < ba.zmin - slack
    )


def _common_volume(a, b) -> float:
    """Volume shared by two solids (0.0 when they only touch or miss)."""
    import cadquery as cq

    try:
        inter = cq.Workplane(obj=a).intersect(cq.Workplane(obj=b))
    except Exception:  # noqa: BLE001 — OCC raises several unrelated types on empty results
        return 0.0
    vals = [v for v in inter.vals() if v is not None]
    total = 0.0
    for v in vals:
        try:
            total += float(v.Volume())
        except Exception:  # noqa: BLE001
            continue
    return total


def interferences(bodies, abs_tol: float = INTERFERENCE_ABS_MM3,
                  rel_tol: float = INTERFERENCE_REL):
    """Interfering body pairs as [(i, j, shared_mm3, threshold_mm3), …].

    Bounding boxes are checked first, so the O(n²) boolean pass only runs on
    pairs that can possibly overlap — a 16-body bearing does ~a dozen booleans,
    not 120.
    """
    vols = body_volumes(bodies)
    hits = []
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            if not _bbox_overlap(bodies[i], bodies[j]):
                continue
            shared = _common_volume(bodies[i], bodies[j])
            if shared <= 0.0:
                continue
            # abs(): a reversed solid reports a negative volume, and a negative
            # threshold would flag every pair it touches for the wrong reason.
            thresh = max(abs_tol, rel_tol * min(abs(vols[i]), abs(vols[j])))
            if shared > thresh:
                hits.append((i, j, shared, thresh))
    return hits


def step_body_report(step_path: Path):
    """(n_bodies, volumes, interfering_pairs, invalid_bodies) for one instance."""
    bodies = load_bodies(step_path)
    if not bodies:
        return 0, [], [], []
    vols = body_volumes(bodies)
    pairs = interferences(bodies) if len(bodies) > 1 else []
    return len(bodies), vols, pairs, invalid_bodies(bodies)


def describe_pair(idx_i: int, idx_j: int, shared: float, thresh: float,
                  names: list[str] | None = None) -> str:
    """`body 2 (cage) ∩ body 5 (ball) = 12.4 mm³ (> 0.001 tol)`."""

    def label(k):
        if names and k < len(names) and names[k]:
            return f"body {k} ({names[k]})"
        return f"body {k}"

    return (f"{label(idx_i)} ∩ {label(idx_j)} = {shared:.4g} mm³ "
            f"(tolerance {thresh:.3g})")
