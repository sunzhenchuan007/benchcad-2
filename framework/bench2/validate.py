"""Machine gates for a contributed design — the same checks CI runs.

Gates (see docs/DESIGN_SPEC.md):
  1. family.json present, required keys, valid base_plane
  2. design.py exposes the four pieces with the right shapes
  3. per difficulty x N seeds: sample() passes check(); build() returns a
     program; the program executes to a non-degenerate solid
  4. determinism: same seed => byte-identical program
  5. difficulty separation: the three difficulties aren't all identical
  6. geometry-hash duplicate report within the sampled batch
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

DIFFS = ("easy", "medium", "hard")
FAMILY_KEYS = ("family", "standard", "base_plane", "description", "contributor")
BASE_PLANES = {"XY", "XZ", "YZ"}
SPEC_REQUIRED = ("desc", "unit", "range", "source")


def load_design(fam_dir: Path):
    spec = importlib.util.spec_from_file_location(f"design_{fam_dir.name}", fam_dir / "design.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _geom_hash(step_path: Path) -> str:
    from . import render

    verts, tris = render.step_to_normalized_mesh(step_path)  # raises if degenerate
    h = hashlib.sha256()
    h.update(verts.round(3).tobytes())
    h.update(tris.tobytes())
    return h.hexdigest()[:16]


def validate_family(fam_dir: Path, seeds: int = 4, geometry: bool = True):
    """Returns (ok, log) where log is a list of (passed, message)."""
    import numpy as np

    log: list[tuple[bool, str]] = []

    def ok(msg):
        log.append((True, msg))

    def bad(msg):
        log.append((False, msg))

    # -- 1. family.json ------------------------------------------------------
    fj = fam_dir / "family.json"
    if not fj.exists():
        bad("family.json: missing")
        return False, log
    meta = json.loads(fj.read_text())
    missing = [k for k in FAMILY_KEYS if k not in meta]
    if missing:
        bad(f"family.json: missing keys {missing}")
    elif meta["base_plane"] not in BASE_PLANES:
        bad(f"family.json: base_plane must be one of {sorted(BASE_PLANES)}")
    else:
        ok("family.json: keys + base_plane valid")

    # -- 2. the four pieces --------------------------------------------------
    try:
        d = load_design(fam_dir)
    except Exception as e:  # noqa: BLE001
        bad(f"design.py failed to import: {type(e).__name__}: {e}")
        return False, log
    for piece in ("PARAM_SPEC", "check", "sample", "build"):
        if not hasattr(d, piece):
            bad(f"design.py: missing `{piece}`")
    if not all(passed for passed, _ in log[-4:]):
        return False, log
    spec_bad = [
        f"{name}.{key}"
        for name, entry in d.PARAM_SPEC.items()
        for key in SPEC_REQUIRED
        if key not in entry
    ]
    spec_bad += [
        f"{name}.range missing '{diff}'"
        for name, entry in d.PARAM_SPEC.items()
        for diff in DIFFS
        if isinstance(entry.get("range"), dict) and diff not in entry["range"]
    ]
    if spec_bad:
        bad(f"PARAM_SPEC incomplete: {spec_bad[:6]}")
    else:
        ok(f"PARAM_SPEC: {len(d.PARAM_SPEC)} params, all entries complete")

    # -- 3-6. sampling, determinism, execution, hashes -----------------------
    programs: dict[str, list[str]] = {diff: [] for diff in DIFFS}
    hashes: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        for diff in DIFFS:
            n_ok = 0
            for seed in range(seeds):
                try:
                    p = d.sample(diff, np.random.default_rng(seed))
                    violations = d.check(p)
                    if violations:
                        bad(f"{diff}/seed{seed}: sample violates check: {violations[:2]}")
                        continue
                    prog = d.build(p)
                    if not isinstance(prog, str) or "result" not in prog:
                        bad(f"{diff}/seed{seed}: build() must return a program binding `result`")
                        continue
                    # determinism: same seed => identical params and program
                    p2 = d.sample(diff, np.random.default_rng(seed))
                    if d.build(p2) != prog:
                        bad(f"{diff}/seed{seed}: NOT deterministic (same seed, different program)")
                        continue
                    programs[diff].append(prog)
                    if geometry:
                        step = Path(td) / f"{diff}_{seed}.step"
                        from .execute import execute_cq_to_step

                        execute_cq_to_step(prog, step)
                        hashes.append(_geom_hash(step))  # raises if degenerate
                    n_ok += 1
                except Exception as e:  # noqa: BLE001
                    bad(f"{diff}/seed{seed}: {type(e).__name__}: {str(e)[:120]}")
            if n_ok == seeds:
                ok(f"{diff}: {n_ok}/{seeds} seeds sample+check+build+execute clean")

    flat = [p for progs in programs.values() for p in progs]
    if flat:
        if len({min(progs) for progs in programs.values() if progs}) == 1 and len(
            [1 for progs in programs.values() if progs]
        ) == len(DIFFS):
            bad("difficulty separation: easy/medium/hard produced identical programs")
        else:
            ok("difficulty separation: difficulties produce distinct programs")
    if hashes:
        dup = 1.0 - len(set(hashes)) / len(hashes)
        (ok if dup <= 0.5 else bad)(
            f"geometry novelty: {len(set(hashes))}/{len(hashes)} unique shapes "
            f"({dup:.0%} duplicate{' — too clone-heavy' if dup > 0.5 else ''})"
        )

    return all(passed for passed, _ in log), log
