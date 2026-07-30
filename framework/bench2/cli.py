"""bench2 — the BenchCAD 2.0 contributor CLI.

    bench2 new <family>        scaffold designs/<family>/ from the template
    bench2 edit <family>       open part.py in CQ-editor (live 3D, F5 to re-render)
    bench2 validate <family>   run every machine gate locally (same as CI)
    bench2 preview <family>    render a difficulty x seed grid PNG
    bench2 status              regenerate STATUS.md (the progress board)

Run from the repo root (the directory containing designs/).
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path


def _designs_root() -> Path:
    root = Path.cwd() / "designs"
    if not root.is_dir():
        sys.exit("bench2: run from the repo root (no designs/ directory here)")
    return root


def cmd_new(family: str) -> int:
    from . import scaffold

    fam_dir = _designs_root() / family
    if fam_dir.exists():
        sys.exit(f"bench2: designs/{family}/ already exists")
    scaffold.create(fam_dir, family)
    print(f"scaffolded designs/{family}/  (part.py + spec.py + family.json)")
    print("next: write build() in part.py + PARAM_SPEC/check in spec.py, then `bench2 validate`")
    return 0


def cmd_validate(family: str, seeds: int, fast: bool) -> int:
    from .validate import validate_family

    fam_dir = _designs_root() / family
    if not fam_dir.is_dir():
        sys.exit(f"bench2: designs/{family}/ not found")
    passed, log = validate_family(fam_dir, seeds=seeds, geometry=not fast)
    for okay, msg in log:
        print(("  ✓ " if okay else "  ✗ ") + msg)
    print(("PASS — " if passed else "FAIL — ") + f"designs/{family}")
    return 0 if passed else 1


def _param_caption(spec, p) -> str:
    """Compact `name=value` summary of the meaningful params (~2 per line) for a
    preview row label — lets a reviewer map the rendered part to its numbers and
    to the source drawing. Covers askable dimensions plus feature params (a hub
    diameter, a keyway toggle) so every catalog symbol is legible."""
    parts = [f"{k}={p[k]}" for k, e in spec.PARAM_SPEC.items()
             if (e.get("askable") or e.get("feature")) and k in p]
    return "\n".join(", ".join(parts[i:i + 2]) for i in range(0, len(parts), 2))


def cmd_preview(family: str, per_diff: int) -> int:
    import numpy as np

    from . import render
    from .derive import derive_program
    from .execute import execute_cq_to_step
    from .loader import load_family
    from .sampling import sample as sample_params
    from .validate import DIFFS

    fam_dir = _designs_root() / family
    if not fam_dir.is_dir():
        sys.exit(f"bench2: designs/{family}/ not found")
    part, spec = load_family(fam_dir)
    rows, labels, view_rows, view_labels = [], [], [], []
    with tempfile.TemporaryDirectory() as td:
        for diff in DIFFS:
            row = []
            for seed in range(per_diff):
                p = sample_params(spec, diff, np.random.default_rng(seed))
                step = Path(td) / f"{diff}_{seed}.step"
                execute_cq_to_step(derive_program(part, p), step)
                verts, tris = render.step_to_normalized_mesh(step)
                row.append(render.render_iso(verts, tris))
                if seed == 0:  # what the MODEL will see: the 4 benchmark views
                    view_rows.append(render.render_bench_views(verts, tris))
                    # label the row with this instance's numbers so a reviewer can
                    # map the rendered part to its parameters and the source drawing
                    view_labels.append(f"{diff}\n{_param_caption(spec, p)}")
                print(f"  rendered {diff}/seed{seed}")
            rows.append(row)
            labels.append(diff)
    out = render.compose_grid(rows, labels, fam_dir / "preview.png")
    out2 = render.compose_grid(view_rows, view_labels, fam_dir / "preview_views.png")

    # extremes: scan cheap samples across all difficulties, pick the overall
    # smallest / largest parameter draw (mean of range-normalized numeric
    # params), render each in the 4 benchmark views — acceptance evidence
    # that BOTH ends of the declared ranges produce sane geometry.
    # normalize against the GLOBAL range (union across difficulties) so the
    # absolute-largest part (e.g. hard-tier max) wins, not a per-tier extreme
    glob = {}
    for name, entry in spec.PARAM_SPEC.items():
        los, his = zip(*(entry["range"][diff] for diff in DIFFS))
        glob[name] = (min(los), max(his))
    cands = []
    for diff in DIFFS:
        for seed in range(100, 130):
            try:
                p = sample_params(spec, diff, np.random.default_rng(seed))
            except Exception:
                continue
            scores = []
            for name, (lo, hi) in glob.items():
                v = p.get(name)
                if isinstance(v, (int, float)) and hi > lo:
                    scores.append((float(v) - lo) / (hi - lo))
            if scores:
                cands.append((sum(scores) / len(scores), diff, p))
    ex_rows, ex_labels = [], []
    with tempfile.TemporaryDirectory() as td:
        for tag, (s, diff, p) in (("min", min(cands, key=lambda c: c[0])),
                                  ("max", max(cands, key=lambda c: c[0]))):
            step = Path(td) / f"ex_{tag}.step"
            execute_cq_to_step(derive_program(part, p), step)
            verts, tris = render.step_to_normalized_mesh(step)
            ex_rows.append(render.render_bench_views(verts, tris))
            ex_labels.append(f"{tag} ({diff})\n{_param_caption(spec, p)}")
            print(f"  extreme {tag} [{diff}]: "
                  + ", ".join(f"{k}={p[k]}" for k, e in spec.PARAM_SPEC.items()
                              if e.get("askable") and k in p))
    out3 = render.compose_grid(ex_rows, ex_labels, fam_dir / "preview_extremes.png")
    print(f"preview → {out}")
    print(f"benchmark views (what the model sees) → {out2}")
    print(f"extremes (smallest & largest draw) → {out3}")

    # multi-body family: one panel per component (highlighted in place) plus the
    # assembled and exploded views. `CONTRIBUTING.md` requires this sheet for an
    # `_asm` family; producing it here means it is reproducible and refreshes
    # with the geometry, instead of being hand-made once per PR.
    out4 = _render_parts_sheet(fam_dir, family, part, spec)
    if out4:
        print(f"components (each part in place, + exploded) → {out4}")
    return 0


def _render_parts_sheet(fam_dir, family, part, spec):
    """`preview_parts.png` for a multi-body family; None for a single solid."""
    import json

    import numpy as np

    from . import render
    from .derive import derive_program
    from .execute import execute_cq_to_step
    from .sampling import sample as sample_params

    p = sample_params(spec, "medium", np.random.default_rng(0))
    with tempfile.TemporaryDirectory() as td:
        step = Path(td) / "parts.step"
        execute_cq_to_step(derive_program(part, p), step)
        bodies = render.step_to_body_meshes(step)
    if len(bodies) < 2:
        return None

    meta = {}
    fj = fam_dir / "family.json"
    if fj.exists():
        try:
            meta = json.loads(fj.read_text())
        except ValueError:
            meta = {}
    from .validate import _component_names

    # same BOM flattening validate uses, so a parametric quantity (n balls,
    # n bolts) labels the panels of THIS instance
    names = _component_names(meta.get("components") or [], p)

    rows, labels = [], []
    rows.append([render.render_bodies(bodies, front=f) for f in render.BENCH_FRONTS])
    labels.append(f"assembled — {len(bodies)} bodies\n{_param_caption(spec, p)}")
    rows.append([render.render_bodies(bodies, front=f, explode=0.55)
                 for f in render.BENCH_FRONTS])
    labels.append("exploded (presentation only —\nnot the exported geometry)")
    # one row per DISTINCT component: a bearing with 11 balls needs one ball
    # panel, not eleven. The first body of each name is the one highlighted.
    seen: dict[str, int] = {}
    for i in range(len(bodies)):
        who = names[i] if i < len(names) else f"body {i}"
        seen.setdefault(who, i)
    for who, i in seen.items():
        rows.append([render.render_bodies(bodies, front=f, highlight=i)
                     for f in render.BENCH_FRONTS])
        n_same = sum(1 for k in range(len(bodies))
                     if (names[k] if k < len(names) else f"body {k}") == who)
        count = f" x{n_same} (first shown)" if n_same > 1 else ""
        labels.append(f"{who}{count}\n(body {i} of {len(bodies)}, in place)")
    return render.compose_grid(rows, labels, fam_dir / "preview_parts.png", label_w=340)


def cmd_status() -> int:
    from pathlib import Path as _P

    from .status import main as status_main

    root = _P.cwd()
    if not (root / "designs").is_dir():
        sys.exit("bench2: run from the repo root (no designs/ directory here)")
    print(f"status → {status_main(root)}")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(prog="bench2", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_new = sub.add_parser("new", help="scaffold a new family")
    p_new.add_argument("family")
    p_edit = sub.add_parser("edit", help="open a family's part.py in CQ-editor (live 3D)")
    p_edit.add_argument("family", nargs="?", help="family name (designs/<family>/part.py)")
    p_edit.add_argument("set", nargs="*", metavar="k=v",
                        help="override sampled parameters, e.g. outer_d=80")
    p_edit.add_argument("--file", help="open this part.py instead of a family name")
    p_edit.add_argument("--diff", default="medium", choices=["easy", "medium", "hard"],
                        help="difficulty tier to sample the preview instance from")
    p_edit.add_argument("--seed", type=int, default=0, help="sampling seed (default 0)")
    p_edit.add_argument("--strip", action="store_true",
                        help="only remove a leftover scratch block, don't open the editor")
    p_val = sub.add_parser("validate", help="run all machine gates")
    p_val.add_argument("family")
    p_val.add_argument("--seeds", type=int, default=4, help="seeds per difficulty (default 4)")
    p_val.add_argument("--fast", action="store_true", help="skip geometry execution (syntax-only)")
    p_pre = sub.add_parser("preview", help="render a difficulty x seed grid")
    p_pre.add_argument("family")
    p_pre.add_argument("--per-diff", type=int, default=3, help="seeds per difficulty row")
    sub.add_parser("status", help="regenerate STATUS.md")
    a = ap.parse_args()
    if a.cmd == "new":
        sys.exit(cmd_new(a.family))
    if a.cmd == "edit":
        from .edit import cmd_edit

        sys.exit(cmd_edit(a.family, a.file, a.diff, a.seed, a.set, a.strip))
    if a.cmd == "validate":
        sys.exit(cmd_validate(a.family, a.seeds, a.fast))
    if a.cmd == "preview":
        sys.exit(cmd_preview(a.family, a.per_diff))
    if a.cmd == "status":
        sys.exit(cmd_status())
