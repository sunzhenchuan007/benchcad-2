"""bench2 debug — build a family and open it in a GUI for interactive debugging.

    uv run python tools/debug_family.py <family> [--diff easy|medium|hard]
                                        [--seed N] [key=value ...]

Examples:
    uv run python tools/debug_family.py v_belt_pulley
    uv run python tools/debug_family.py v_belt_pulley --diff hard
    uv run python tools/debug_family.py v_belt_pulley outer_d=80 n_grooves=2 hub_d=52

It samples a valid parameter set for the family (respecting spec.check), applies
any `key=value` overrides you pass, builds the part, prints the params + solid
count + bounding box, and shows it in a 3D viewer:

  • if `ocp-vscode` is installed  → live view in the VS Code "OCP CAD Viewer"
    panel (recommended — runs in the repo env, so it works for every family,
    including ones that import from bench2). One-time setup:
        uv add --dev ocp-vscode
        # + install the "OCP CAD Viewer" extension in VS Code, then click its
        #   plug icon to start the viewer, and run this script.

  • otherwise → writes a STEP file you can open in FreeCAD / any CAD viewer.

To hand-tune a single instance, either pass key=value overrides here, or open the
family's part.py directly in CQ-editor and edit its PARAMS block (see
docs/DEBUGGING.md).
"""
import importlib.util
import sys

import numpy as np

sys.path.insert(0, "framework")
from bench2 import sampling                       # noqa: E402
from bench2.render import _ocp_hashcode_fix       # noqa: E402

_ocp_hashcode_fix()


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    family = argv[0]
    diff, seed, overrides = "medium", 0, {}
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--diff":
            diff = argv[i + 1]; i += 2
        elif a == "--seed":
            seed = int(argv[i + 1]); i += 2
        elif "=" in a:
            k, v = a.split("=", 1)
            overrides[k] = v; i += 1
        else:
            print(f"ignoring arg {a!r}"); i += 1

    import os
    if not os.path.isdir(f"designs/{family}"):
        print(f"no such family: designs/{family}/  (run from the repo root)")
        return 2
    part = _load("part", f"designs/{family}/part.py")
    spec = _load("spec", f"designs/{family}/spec.py")
    p = sampling.sample(spec, diff, np.random.default_rng(seed))

    # apply overrides, coercing to the type the PARAM_SPEC declares (int vs float).
    # NOTE: overrides are RAW — they do NOT re-run spec.refine(), so derived fields
    # (e.g. width = 2E+(N-1)e) won't auto-update; check() will flag the mismatch,
    # which is exactly what you want when hunting a geometry bug. Override the
    # derived field too, or just use --seed/--diff to pick a clean sample.
    ints = {k for k, d in spec.PARAM_SPEC.items() if d.get("integer")}
    for k, v in overrides.items():
        p[k] = int(round(float(v))) if k in ints else float(v)

    bad = spec.check(p)
    print("family    :", family)
    print("params    :", {k: (round(v, 2) if isinstance(v, float) else v) for k, v in p.items()})
    print("check     :", "clean" if not bad else bad)
    obj = part.build(**p)
    val = obj.val() if hasattr(obj, "val") else obj
    bb = val.BoundingBox()
    print("solids    :", len(val.Solids()))
    print("bbox (mm) : X %.1f  Y %.1f  Z %.1f" % (bb.xlen, bb.ylen, bb.zlen))

    try:
        from ocp_vscode import show
        show(obj, name=family)
        print("view      : shown in the OCP CAD Viewer (VS Code)")
    except ImportError:
        import cadquery as cq
        out = f"{family}_debug.step"
        cq.exporters.export(val, out)
        print(f"view      : no ocp-vscode installed — wrote {out} (open in FreeCAD).")
        print("            install a viewer:  uv add --dev ocp-vscode   (see docs/DEBUGGING.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
