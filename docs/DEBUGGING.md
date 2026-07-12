# Debugging a family in a 3D GUI

`bench2 preview` gives you PNGs. To *rotate, section, and tweak* a part live, use a
3D viewer. Two ways, pick one.

## A. `tools/debug_family.py` (recommended — one command)

```bash
uv run python tools/debug_family.py v_belt_pulley               # a medium sample
uv run python tools/debug_family.py v_belt_pulley --diff hard --seed 3
uv run python tools/debug_family.py v_belt_pulley outer_d=80 n_grooves=2 hub_d=52
```

It samples a valid parameter set (honouring `spec.check`), applies any `key=value`
overrides, builds, prints `params / check / solids / bbox`, and shows the model.

**Overrides are raw** — they don't re-run `spec.refine()`, so a derived field
(e.g. `width = 2E+(N-1)e`) won't auto-update and `check` will flag it. That's the
point when hunting a bug; override the derived field too, or just pick a clean
sample with `--seed`.

### Make the view live (one-time)

```bash
uv add --dev ocp-vscode
```
Then in VS Code install the **"OCP CAD Viewer"** extension, click its plug icon to
start the viewer, and re-run the command — the part renders in a panel you can
orbit/section, and it re-renders each run. Runs in the repo env, so it works for
**every** family (including ones that `import` from `bench2`). Without ocp-vscode
the tool writes a `*.step` you can open in FreeCAD.

## B. CQ-editor (edit-and-see live in a GUI window)

`part.py` stays a clean `build()` — **no debug block** (bench2 derives a
stand-alone program from it, so it must not carry `__main__`/`show_object` code).
To render it in CadQuery's GUI editor, drive it from a tiny wrapper — CQ-editor
draws whatever you `show_object`:

```python
# view.py — put next to a copy of the family's part.py; open THIS in cq-editor
import importlib, sys
sys.path.insert(0, ".")            # the folder holding part.py
import part
importlib.reload(part)             # re-read part.py on every F5
PARAMS = dict(outer_d=80.0, width=28.0, n_grooves=2, groove_pitch=12.0,
              groove_top_w=9.7, groove_depth=9.0, groove_angle=34.0,
              bore_d=32.0, hub_d=52.0, hub_len=14.0)
show_object(part.build(**PARAMS), name="v_belt_pulley")
```

```bash
uv tool install cq-editor          # one-time — isolated env, brings its own cadquery
cq-editor view.py
```

- Tweak an instance: edit `PARAMS`, press **F5** — the 3D re-renders.
- Change the geometry: edit `part.py`, Ctrl+S, back to `view.py`, **F5**
  (`importlib.reload` picks up the saved part.py).
- Edits live in the editor buffer; Ctrl+S writes back to the file.

(part.py imports only `cadquery`, so cq-editor's own cadquery builds it. For a
family that imports from `bench2`, use path A — the ocp-vscode tool.)

## Hand-writing a new family

```bash
bench2 new my_family          # scaffolds designs/my_family/{part,spec,family}.py
# write build() in part.py — keep it clean; drive it from a view.py wrapper (§B)
uv run python tools/debug_family.py my_family        # eyeball it in 3D
bench2 validate my_family                            # the machine gates
```

## Reading a `part.py` fast

The parts are commented for exactly this. Look for:
- the **header docstring** — what the part is, the coordinate frame (`z=0` is …),
  and a **dimension glossary** mapping drawing symbols → code params;
- **inline comments** on each solid step (rim / hub / bore …).

Copy a known-good instance from the family's issue dimension table (or a `view.py`
wrapper's `PARAMS`), nudge one number, re-run, see what moved.
