"""Machine gates for a contributed family — the same checks CI runs.

Gates (see docs/DESIGN_SPEC.md):
  1. family.json present, required keys, valid base_plane
  2. part.py exposes build(); spec.py exposes PARAM_SPEC + check(); every
     build() parameter is declared in PARAM_SPEC
  3. per difficulty x N seeds: the framework sampler draws params that pass
     check(); the DERIVED stand-alone program (derive.py) binds `result` and
     executes to a non-degenerate solid
  4. determinism: same seed => byte-identical derived program
  5. difficulty separation: the three difficulties aren't all identical
  6. geometry-hash duplicate report within the sampled batch
  7. assembly (multi-body) families: every body is a valid solid of positive
     volume, no two bodies interpenetrate, and the body count matches the
     `solids` / `components` BOM declared in family.json
"""

from __future__ import annotations

import hashlib
import inspect
import json
import tempfile
from pathlib import Path

from .derive import derive_program
from .loader import load_family
from .sampling import sample as sample_params

DIFFS = ("easy", "medium", "hard")
FAMILY_KEYS = ("family", "standard", "base_plane", "description", "contributor")
BASE_PLANES = {"XY", "XZ", "YZ"}
SPEC_REQUIRED = ("desc", "unit", "range", "source")


def _component_names(components, params) -> list[str]:
    """The BOM flattened to one name per body, for THIS instance.

    `quantity` is an int for a fixed component, or the name of the parameter
    that sets it (a ball or bolt count), so the expected body count follows the
    instance instead of being a constant the family cannot honour.
    """
    names: list[str] = []
    for c in components:
        qty = c.get("quantity", 1)
        if isinstance(qty, str):
            qty = int(params.get(qty, 0))
        names.extend([c.get("name", "component")] * max(0, int(qty)))
    return names


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

    body_counts: set[int] = set()
    body_gate_clean = [True]  # cleared by any per-body failure below

    # -- 1b. part.py must be clean source, not an editor scratch file --------
    # `bench2 edit` appends a PARAMS + show_object() block and removes it when
    # the editor closes; if the editor was killed the block survives. It is
    # harmless at import (show_object is stubbed) but it is not the family's
    # source of truth, so fail loudly rather than let it be committed.
    from .edit import has_scratch_block

    part_src = (fam_dir / "part.py").read_text() if (fam_dir / "part.py").exists() else ""
    if has_scratch_block(part_src):
        bad(f"part.py: still has a `bench2 edit` scratch block — "
            f"run `bench2 edit {fam_dir.name} --strip` (or delete the block) before committing")

    # -- 2. the pieces: part.build + spec.PARAM_SPEC/check -------------------
    try:
        part, spec = load_family(fam_dir)
    except Exception as e:  # noqa: BLE001
        bad(f"part.py/spec.py failed to import: {type(e).__name__}: {e}")
        return False, log
    missing_pieces = []
    if not callable(getattr(part, "build", None)):
        missing_pieces.append("part.py: build()")
    if not isinstance(getattr(spec, "PARAM_SPEC", None), dict):
        missing_pieces.append("spec.py: PARAM_SPEC")
    if not callable(getattr(spec, "check", None)):
        missing_pieces.append("spec.py: check()")
    if missing_pieces:
        bad(f"missing required piece(s): {missing_pieces}")
        return False, log

    argnames = list(inspect.signature(part.build).parameters)
    extra = [a for a in argnames if a not in spec.PARAM_SPEC]
    if extra:
        bad(f"part.build has parameter(s) not declared in PARAM_SPEC: {extra}")
        return False, log
    ok(f"pieces: build({len(argnames)} params) + PARAM_SPEC + check present")

    spec_param_names = set(spec.PARAM_SPEC)

    # -- 2b. assembly metadata: "solids" and the optional component BOM -------
    # An `_asm` family declares how many bodies it ships and what they are; the
    # geometry gates below then hold that declaration to the exported STEP,
    # instead of it being prose nobody can check.
    want_solids = meta.get("solids")
    components = meta.get("components") or []
    if want_solids is not None and (not isinstance(want_solids, int) or want_solids < 1):
        bad(f"family.json: solids must be a positive integer (got {want_solids!r})")
        want_solids = None
    if components and (not isinstance(components, list)
                       or not all(isinstance(c, dict) for c in components)):
        bad("family.json: components must be a list of {name, quantity, role} objects")
        components = []
    for c in components:
        qty, name = c.get("quantity", 1), c.get("name")
        if not name or not isinstance(name, str):
            bad(f"family.json: every component needs a name (got {c!r})")
        elif isinstance(qty, str):
            # a variable-count component (n balls, n bolts) names the parameter
            # that sets it, and is resolved per instance below
            if qty not in spec_param_names:
                bad(f"family.json: component {name!r} quantity {qty!r} is not a "
                    f"PARAM_SPEC parameter")
        elif not isinstance(qty, int) or qty < 1:
            bad(f"family.json: component {name!r} needs a positive integer "
                f"quantity, or the name of the parameter that sets it")
    if components and want_solids is not None:
        fixed = [c for c in components if not isinstance(c.get("quantity", 1), str)]
        if len(fixed) == len(components):
            total = sum(int(c.get("quantity", 1)) for c in components)
            if total != want_solids:
                bad(f"family.json: components sum to {total} bodies but "
                    f"solids={want_solids} — one row per real component, "
                    f"quantity for repeats")
            else:
                ok(f"family.json: components BOM sums to solids={want_solids}")
        else:
            bad("family.json: solids is a fixed count, but a component has a "
                "parametric quantity — drop solids and let the BOM set it")
    elif components:
        ok(f"family.json: components BOM declared ({len(components)} component types)")

    spec_bad = [
        f"{name}.{key}"
        for name, entry in spec.PARAM_SPEC.items()
        for key in SPEC_REQUIRED
        if key not in entry
    ]
    spec_bad += [
        f"{name}.range missing '{diff}'"
        for name, entry in spec.PARAM_SPEC.items()
        for diff in DIFFS
        if isinstance(entry.get("range"), dict) and diff not in entry["range"]
    ]
    if spec_bad:
        bad(f"PARAM_SPEC incomplete: {spec_bad[:6]}")
    else:
        ok(f"PARAM_SPEC: {len(spec.PARAM_SPEC)} params, all entries complete")

    # -- 3-6. sampling, determinism, execution, hashes -----------------------
    programs: dict[str, list[str]] = {diff: [] for diff in DIFFS}
    hashes: list[str] = []
    with tempfile.TemporaryDirectory() as td:
        for diff in DIFFS:
            n_ok = 0
            for seed in range(seeds):
                try:
                    p = sample_params(spec, diff, np.random.default_rng(seed))
                    violations = spec.check(p)
                    if violations:
                        bad(f"{diff}/seed{seed}: sample violates check: {violations[:2]}")
                        continue
                    # the declared spec is a contract: every sampled value must
                    # fall inside its own PARAM_SPEC range for this difficulty
                    oob = []
                    for name, entry in spec.PARAM_SPEC.items():
                        if name not in p:
                            oob.append(f"{name} missing from sample")
                            continue
                        lo, hi = entry["range"][diff]
                        if not (lo - 1e-9 <= p[name] <= hi + 1e-9):
                            oob.append(f"{name}={p[name]} outside declared ({lo}, {hi})")
                    if oob:
                        bad(f"{diff}/seed{seed}: sample breaks PARAM_SPEC contract: {oob[:2]}")
                        continue
                    # the framework derives the stand-alone instance program
                    # from build()'s source + params (derive.py) so the
                    # contributor never writes a code generator.
                    prog = derive_program(part, p)
                    if "result" not in prog:
                        bad(f"{diff}/seed{seed}: derived program binds no `result` — build() must assign `result`")
                        continue
                    # determinism: same seed => identical params => identical program
                    p2 = sample_params(spec, diff, np.random.default_rng(seed))
                    if derive_program(part, p2) != prog:
                        bad(f"{diff}/seed{seed}: NOT deterministic (same seed, different program)")
                        continue
                    programs[diff].append(prog)
                    if geometry:
                        step = Path(td) / f"{diff}_{seed}.step"
                        from .execute import execute_cq_to_step

                        execute_cq_to_step(prog, step)
                        hashes.append(_geom_hash(step))  # raises if degenerate
                        # per-body gates, on the EXPORTED solid — what the
                        # benchmark actually scores. A body can build fine
                        # in-process and still export inside-out or self-
                        # intersecting, and neither shows up in a render.
                        from .assembly import describe_pair, step_body_report

                        n_bodies, vols, pairs, invalid = step_body_report(step)
                        body_counts.add(n_bodies)
                        if invalid or pairs:
                            body_gate_clean[0] = False
                        for idx, vol, brep_ok in invalid:
                            why = "volume is not positive (solid is inside-out)" if vol <= 0 \
                                else "BRepCheck reports an invalid solid"
                            bad(f"{diff}/seed{seed}: body {idx} of {n_bodies}: {why} "
                                f"(volume {vol:.4g} mm³)")
                        names = _component_names(components, p)
                        for i, j, shared, thresh in pairs:
                            bad(f"{diff}/seed{seed}: components overlap — "
                                + describe_pair(i, j, shared, thresh, names))
                        # expected body count: the declared `solids`, or the BOM
                        # resolved against THIS instance (a ball/bolt count is a
                        # parameter, so the total is per-instance)
                        expect = len(names) if names else want_solids
                        if expect is not None and n_bodies != expect:
                            body_gate_clean[0] = False
                            how = (f"family.json declares solids={want_solids}" if not names
                                   else f"the components BOM resolves to {expect} for this instance")
                            bad(f"{diff}/seed{seed}: produced {n_bodies} solid(s) but {how}")
                    n_ok += 1
                except Exception as e:  # noqa: BLE001
                    bad(f"{diff}/seed{seed}: {type(e).__name__}: {str(e)[:120]}")
            if n_ok == seeds:
                ok(f"{diff}: {n_ok}/{seeds} seeds sample+check+build+execute clean")

    # coverage gate: params declaring `coverage: [...]` must produce every
    # declared value across a cheap large sampling pass (no geometry).
    cov_params = {n: e["coverage"] for n, e in spec.PARAM_SPEC.items() if "coverage" in e}
    if cov_params:
        seen: dict[str, set] = {n: set() for n in cov_params}
        for diff in DIFFS:
            for seed in range(40):
                try:
                    p = sample_params(spec, diff, np.random.default_rng(1000 + seed))
                except Exception:
                    continue
                for n in cov_params:
                    seen[n].add(round(float(p[n]), 6))
        for n, values in cov_params.items():
            missing = [v_ for v_ in values if not any(abs(v_ - s) < 1e-6 for s in seen[n])]
            if missing:
                bad(f"coverage: {n} never produced declared value(s) {missing} in 120 samples")
            else:
                ok(f"coverage: {n} reaches all {len(values)} declared values (standard table fully covered)")

    # geomlib declaration: names must exist in the registry AND be inlined in
    # the emitted (stand-alone) program.
    declared = meta.get("geomlib") or []
    if declared:
        from .geomlib import REGISTRY as _REG

        unknown = [n for n in declared if n not in _REG]
        first = next((pr for progs in programs.values() for pr in progs), None)
        if unknown:
            bad(f"family.json geomlib: unknown helper(s) {unknown} (have: {sorted(_REG)})")
        elif first and any(f"def {n}(" not in first for n in declared):
            bad("family.json geomlib: declared helpers are not inlined in the emitted program")
        elif first:
            ok(f"geomlib: {declared} registered + inlined (program stays stand-alone)")

    flat = [p for progs in programs.values() for p in progs]
    if flat:
        if len({min(progs) for progs in programs.values() if progs}) == 1 and len(
            [1 for progs in programs.values() if progs]
        ) == len(DIFFS):
            bad("difficulty separation: easy/medium/hard produced identical programs")
        else:
            ok("difficulty separation: difficulties produce distinct programs")
    if body_counts and body_gate_clean[0]:
        counts = sorted(body_counts)
        detail = str(counts[0]) if len(counts) == 1 else f"{counts[0]}-{counts[-1]}"
        note = f" (declares solids={want_solids})" if want_solids is not None else ""
        multi = counts[-1] > 1
        ok(f"bodies: {detail} solid(s) per instance, all valid"
           + (", no component overlap" if multi else "") + note)
    if hashes:
        dup = 1.0 - len(set(hashes)) / len(hashes)
        (ok if dup <= 0.5 else bad)(
            f"geometry novelty: {len(set(hashes))}/{len(hashes)} unique shapes "
            f"({dup:.0%} duplicate{' — too clone-heavy' if dup > 0.5 else ''})"
        )

    return all(passed for passed, _ in log), log
