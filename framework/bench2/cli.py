"""bench2 — the BenchCAD 2.0 contributor CLI.

    bench2 new <family>        scaffold designs/<family>/ from the template
    bench2 validate <family>   run every machine gate locally (same as CI)
    bench2 preview <family>    render a difficulty x seed grid PNG

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
    print(f"scaffolded designs/{family}/  (design.py + family.json)")
    print("next: fill in PARAM_SPEC / check / sample / build, then `bench2 validate`")
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


def cmd_preview(family: str, per_diff: int) -> int:
    import numpy as np

    from . import render
    from .execute import execute_cq_to_step
    from .validate import DIFFS, load_design

    fam_dir = _designs_root() / family
    if not fam_dir.is_dir():
        sys.exit(f"bench2: designs/{family}/ not found")
    d = load_design(fam_dir)
    rows, labels = [], []
    with tempfile.TemporaryDirectory() as td:
        for diff in DIFFS:
            row = []
            for seed in range(per_diff):
                p = d.sample(diff, np.random.default_rng(seed))
                step = Path(td) / f"{diff}_{seed}.step"
                execute_cq_to_step(d.build(p), step)
                verts, tris = render.step_to_normalized_mesh(step)
                row.append(render.render_iso(verts, tris))
                print(f"  rendered {diff}/seed{seed}")
            rows.append(row)
            labels.append(diff)
    out = render.compose_grid(rows, labels, fam_dir / "preview.png")
    print(f"preview → {out}")
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(prog="bench2", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p_new = sub.add_parser("new", help="scaffold a new family")
    p_new.add_argument("family")
    p_val = sub.add_parser("validate", help="run all machine gates")
    p_val.add_argument("family")
    p_val.add_argument("--seeds", type=int, default=4, help="seeds per difficulty (default 4)")
    p_val.add_argument("--fast", action="store_true", help="skip geometry execution (syntax-only)")
    p_pre = sub.add_parser("preview", help="render a difficulty x seed grid")
    p_pre.add_argument("family")
    p_pre.add_argument("--per-diff", type=int, default=3, help="seeds per difficulty row")
    a = ap.parse_args()
    if a.cmd == "new":
        sys.exit(cmd_new(a.family))
    if a.cmd == "validate":
        sys.exit(cmd_validate(a.family, a.seeds, a.fast))
    if a.cmd == "preview":
        sys.exit(cmd_preview(a.family, a.per_diff))
