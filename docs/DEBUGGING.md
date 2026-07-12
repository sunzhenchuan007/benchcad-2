# Debugging a family in a 3D GUI

`bench2 preview` gives you PNGs. To *rotate, section, and tweak* a part live, use a
3D viewer. Two ways, pick one.

## A. `tools/debug_family.py` (recommended — one command)

```bash
uv run python tools/debug_family.py v_belt_pulley               # a medium sample
uv run python tools/debug_family.py v_belt_pulley --diff hard --seed 3
uv run python tools/debug_family.py v_belt_pulley outer_d=80 n_grooves=2 hub_d=52
uv run python tools/debug_family.py v_belt_pulley --gui         # edit part.py live in CQ-editor
uv run python tools/debug_family.py v_belt_pulley --strip       # remove the debug block again
```

It samples a valid parameter set (honouring `spec.check`), applies any `key=value`
overrides, builds, prints `params / check / solids / bbox`, and shows the model.

**Overrides are raw** — they don't re-run `spec.refine()`, so a derived field
(e.g. `width = 2E+(N-1)e`) won't auto-update and `check` will flag it. That's the
point when hunting a bug; override the derived field too, or just pick a clean
sample with `--seed`.

### Edit the geometry live — `--gui` (CQ-editor)

`--gui` opens the family's **part.py itself** in CQ-editor so you edit `build()`
and press **F5** to re-render:

```bash
uv tool install cq-editor                                    # one-time (isolated env)
uv run python tools/debug_family.py v_belt_pulley --gui       # opens part.py in CQ-editor
#   … edit build()/PARAMS, press F5, iterate …
uv run python tools/debug_family.py v_belt_pulley --strip     # strip the block before committing
```

It appends a small **DEBUG block** (a sampled `PARAMS` + `show_object`) to the
bottom of `designs/<family>/part.py`, then launches CQ-editor on it — so you edit
the real `build()`, not a wrapper. The block is guarded (`try/except NameError`)
so a normal `import part` / `bench2` still works while it's there, but **run
`--strip` (or delete it) before you commit** — bench2 needs a clean `build()`.

(CQ-editor brings its own cadquery 2.8, so it is **not** a repo dependency — the
tool just shells out to the isolated install, like calling `git`. A family that
`import`s from `bench2` may not resolve in CQ-editor's env; for those use
ocp-vscode below.)

### Or a docked panel in VS Code — ocp-vscode (one-time)

```bash
uv add --dev ocp-vscode
```
Then in VS Code install the **"OCP CAD Viewer"** extension, click its plug icon to
start the viewer, and re-run the command **without** `--gui` — the part renders in
a panel you can orbit/section, and it re-renders each run. Runs in the repo env, so
it works for **every** family (including ones that `import` from `bench2`). Without
either viewer the tool writes a `*.step` you can open in FreeCAD.

## Hand-writing a new family

```bash
bench2 new my_family          # scaffolds designs/my_family/{part,spec,family}.py
# write build() in part.py — keep it clean; iterate on it live with --gui (§A)
uv run python tools/debug_family.py my_family --gui   # edit build() in CQ-editor, F5
uv run python tools/debug_family.py my_family         # or eyeball a sample in 3D
bench2 validate my_family                            # the machine gates
```

## Reading a `part.py` fast

The parts are commented for exactly this. Look for:
- the **header docstring** — what the part is, the coordinate frame (`z=0` is …),
  and a **dimension glossary** mapping drawing symbols → code params;
- **inline comments** on each solid step (rim / hub / bore …).

Copy a known-good instance from the family's issue dimension table (or the
`--gui` DEBUG block's `PARAMS`), nudge one number, re-run, see what moved.
