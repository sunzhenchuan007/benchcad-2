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

## B. CQ-editor (paste-and-run a single part)

For a self-contained `part.py` (imports only `cadquery`), open it straight in
CadQuery's GUI editor:

```bash
uv run --with cq-editor cq-editor designs/v_belt_pulley/part.py
```

Every `part.py` ends with a debug block:

```python
PARAMS = dict(outer_d=80.0, width=28.0, n_grooves=2, ...)   # edit these
if __name__ == "__main__":
    show_object(build(**PARAMS))     # CQ-editor draws it; F5 to re-run
```

Edit `PARAMS`, press **F5**, orbit the model. (If a family imports from `bench2`,
use path A instead — CQ-editor runs in its own env.)

## Hand-writing a new family

```bash
bench2 new my_family          # scaffolds designs/my_family/{part,spec,family}.py
# write build() in part.py; add a PARAMS dict + the show_object debug block
uv run python tools/debug_family.py my_family        # eyeball it in 3D
bench2 validate my_family                            # the machine gates
```

## Reading a `part.py` fast

The parts are commented for exactly this. Look for:
- the **header docstring** — what the part is, the coordinate frame (`z=0` is …),
  and a **dimension glossary** mapping drawing symbols → code params;
- **inline comments** on each solid step (rim / hub / bore …);
- the **`PARAMS` debug block** at the bottom — a known-good instance to start from.

Nudge one number in `PARAMS`, re-run, see what moved.
