"""bench2 debug — build a family and open it in a GUI for interactive debugging.

    uv run python tools/debug_family.py <family> [--gui] [--strip]
                                        [--diff easy|medium|hard] [--seed N] [key=value ...]

Examples:
    uv run python tools/debug_family.py v_belt_pulley --gui      # edit part.py in CQ-editor
    uv run python tools/debug_family.py v_belt_pulley --strip    # remove the debug block
    uv run python tools/debug_family.py v_belt_pulley --diff hard

`--gui` opens the family's **part.py itself** in CQ-editor so you edit `build()`
directly (F5 to re-render). It appends a small DEBUG block (a sampled `PARAMS` +
`show_object`) to the bottom of `designs/<family>/part.py`; edit the geometry,
press F5, iterate. **Run `--strip` (or delete the block) before committing** —
bench2 needs a clean `build()`.

CQ-editor is a stand-alone app kept in its own env (it brings cadquery 2.8, which
can't share the repo's pinned cadquery 2.3, so it is NOT a repo dependency; this
script just launches it):  `uv tool install cq-editor`  (one-time).
(A family that imports from bench2 may not resolve in CQ-editor's env — for those
use ocp-vscode instead, below.)

Without `--gui`: shows via ocp-vscode if installed (`uv add --dev ocp-vscode`, live
in the VS Code "OCP CAD Viewer" panel — works for every family), else writes a STEP.
"""
import importlib.util
import os
import sys

import numpy as np

sys.path.insert(0, "framework")
from bench2 import sampling                       # noqa: E402
from bench2.render import _ocp_hashcode_fix       # noqa: E402

_ocp_hashcode_fix()

_MARK = "# ─── DEBUG (bench2 debug --gui)"
# Appended to the family's part.py so CQ-editor renders it on F5. The try/except
# keeps a normal `import part` (and bench2) safe when the block is present —
# show_object only exists inside CQ-editor.
_DEBUG_BLOCK = '''

{mark} — DELETE, or run `--strip`, BEFORE COMMITTING ───────
PARAMS = dict(
    {params}
)
try:
    show_object(build(**PARAMS), name="{family}")   # F5 in CQ-editor
except NameError:
    pass
'''


def _load(mod, path):
    spec = importlib.util.spec_from_file_location(mod, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _strip(part_path):
    src = open(part_path).read()
    idx = src.find(_MARK)
    if idx < 0:
        print("no debug block to strip")
        return
    open(part_path, "w").write(src[:idx].rstrip() + "\n")
    print(f"stripped the debug block from {part_path}")


def _open_in_cq_editor(family, p):
    import shutil
    import subprocess
    part_path = f"designs/{family}/part.py"
    src = open(part_path).read()
    if _MARK not in src:
        params_src = ",\n    ".join(f"{k}={v!r}" for k, v in p.items())
        with open(part_path, "a") as f:
            f.write(_DEBUG_BLOCK.format(mark=_MARK, params=params_src, family=family))
    cqed = shutil.which("cq-editor") or os.path.expanduser("~/.local/bin/cq-editor")
    if not (os.path.exists(cqed) or shutil.which("cq-editor")):
        print("view      : CQ-editor not installed. One-time:  uv tool install cq-editor")
        print(f"            then: cq-editor {part_path}")
        return
    # detached so it outlives this script and doesn't block the shell
    subprocess.Popen([cqed, part_path], start_new_session=True,
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"view      : opened {part_path} in CQ-editor — edit build()/PARAMS, press F5.")
    print(f"            ⚠️ appended a DEBUG block; run `--strip {family}` before committing.")


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    family = argv[0]
    diff, seed, gui, strip, overrides = "medium", 0, False, False, {}
    i = 1
    while i < len(argv):
        a = argv[i]
        if a == "--diff":
            diff = argv[i + 1]; i += 2
        elif a == "--seed":
            seed = int(argv[i + 1]); i += 2
        elif a == "--gui":
            gui = True; i += 1
        elif a == "--strip":
            strip = True; i += 1
        elif "=" in a:
            k, v = a.split("=", 1)
            overrides[k] = v; i += 1
        else:
            print(f"ignoring arg {a!r}"); i += 1

    if not os.path.isdir(f"designs/{family}"):
        print(f"no such family: designs/{family}/  (run from the repo root)")
        return 2
    if strip:
        _strip(f"designs/{family}/part.py")
        return 0

    part = _load("part", f"designs/{family}/part.py")
    spec = _load("spec", f"designs/{family}/spec.py")
    p = sampling.sample(spec, diff, np.random.default_rng(seed))
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

    if gui:
        _open_in_cq_editor(family, p)
        return 0
    try:
        from ocp_vscode import show
        show(obj, name=family)
        print("view      : shown in the OCP CAD Viewer (VS Code)")
    except ImportError:
        import cadquery as cq
        out = f"{family}_debug.step"
        cq.exporters.export(val, out)
        print(f"view      : no viewer — wrote {out} (FreeCAD), or pass --gui for CQ-editor.")
        print("            live viewers:  uv tool install cq-editor   |   uv add --dev ocp-vscode")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
