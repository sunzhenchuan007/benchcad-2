"""Derive a stand-alone CadQuery program from a parameterized `build(p)`.

The contributor writes an ordinary parameterized function:

    import cadquery as cq
    import math
    from bench2.geomlib import sprocket_profile

    def build(p):
        z = p["n_teeth"]
        pts = sprocket_profile(z, p["pitch"], p["roller_d"])
        result = cq.Workplane("XY").polyline(pts).close().extrude(p["tooth_width"])
        return result

For a concrete instance we DERIVE the stand-alone source that a model is asked
to produce (style B — flat variables):

    import cadquery as cq
    import math

    def sprocket_profile(...):   # inlined: build's dependencies travel with it
        ...

    # parameters (this instance)
    n_teeth = 17
    pitch = 15.875
    roller_d = 10.16
    tooth_width = 9.1

    z = n_teeth
    pts = sprocket_profile(z, pitch, roller_d)
    result = cq.Workplane("XY").polyline(pts).close().extrude(tooth_width)

The derivation is a pure text transform: same params in => byte-identical
program out. Because the emitted body IS the contributor's body with the
params bound as module globals, executing the derived program is equivalent to
calling build(p) — the machine guarantees the final coding is consistent, the
contributor never writes a code generator.
"""

from __future__ import annotations

import ast
import builtins
import inspect
import re
import textwrap

_BUILTINS = set(dir(builtins))
_PARAM_RE = re.compile(r"""\bp\[\s*(['"])(\w+)\1\s*\]""")


def _func_body_source(func) -> str:
    """The body of `func` as source text (docstring + trailing `return`
    stripped), dedented to column 0, comments preserved."""
    src = textwrap.dedent(inspect.getsource(func))
    fn = ast.parse(src).body[0]
    stmts = list(fn.body)
    if (
        stmts
        and isinstance(stmts[0], ast.Expr)
        and isinstance(stmts[0].value, ast.Constant)
        and isinstance(stmts[0].value.value, str)
    ):
        stmts = stmts[1:]  # drop docstring
    if stmts and isinstance(stmts[-1], ast.Return):
        stmts = stmts[:-1]  # drop `return result`
    if not stmts:
        return ""
    lines = src.splitlines()
    start, end = stmts[0].lineno, stmts[-1].end_lineno
    return textwrap.dedent("\n".join(lines[start - 1 : end])).rstrip()


def _free_names(code_text: str) -> set[str]:
    """Names read but not bound in `code_text` (a module-level snippet)."""
    tree = ast.parse(code_text)
    bound, loaded = set(), set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            (bound if isinstance(node.ctx, ast.Store) else loaded).add(node.id)
        elif isinstance(node, ast.arg):
            bound.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bound.add(node.name)
    return loaded - bound - _BUILTINS


def _collect(name, design, acc, seen):
    """Recursively gather what a free `name` needs to become stand-alone."""
    if name in seen or name in acc["params"]:
        return
    seen.add(name)
    val = getattr(design, name, None)
    if inspect.ismodule(val):
        acc["imports"][name] = val.__name__
    elif inspect.isfunction(val):
        fsrc = textwrap.dedent(inspect.getsource(val)).rstrip()
        acc["funcs"][name] = fsrc
        for dep in _free_names(fsrc):
            _collect(dep, design, acc, seen)
    elif val is not None:  # a module-level constant (table/number/str)
        acc["consts"][name] = f"{name} = {val!r}"
    # else: unknown free name (a param handled elsewhere, or a builtin miss)


def derive_program(design, params: dict) -> str:
    """Return the stand-alone CadQuery source for one instance of `design`."""
    body = _rewritten_body(design)
    free = _free_names(body)

    acc = {"imports": {}, "consts": {}, "funcs": {}, "params": {}}
    # params first, so _collect skips them
    for name in free:
        if name in params:
            acc["params"][name] = params[name]
    seen = set(acc["params"])
    for name in sorted(free):
        if name not in acc["params"]:
            _collect(name, design, acc, seen)

    out: list[str] = []
    for alias in sorted(acc["imports"]):
        mod = acc["imports"][alias]
        out.append(f"import {mod}" if mod == alias else f"import {mod} as {alias}")
    out.append("")
    if acc["consts"]:
        for name in sorted(acc["consts"]):
            out.append(acc["consts"][name])
        out.append("")
    for name in sorted(acc["funcs"]):
        out.append(acc["funcs"][name])
        out.append("")
        out.append("")
    if acc["params"]:
        out.append("# parameters (this instance)")
        for name in sorted(acc["params"]):
            out.append(f"{name} = {acc['params'][name]!r}")
        out.append("")
    out.append(body)
    return "\n".join(out).rstrip() + "\n"


def _rewritten_body(design) -> str:
    """build()'s body with p["x"] rewritten to flat `x`."""
    return _PARAM_RE.sub(r"\2", _func_body_source(design.build))


def declared_helpers(design, params: dict) -> set[str]:
    """geomlib helper names the derived program actually inlines (for the
    validate cross-check against family.json)."""
    body = _rewritten_body(design)
    acc = {"imports": {}, "consts": {}, "funcs": {}, "params": dict.fromkeys(
        n for n in _free_names(body) if n in params)}
    seen = set(acc["params"])
    for name in sorted(_free_names(body)):
        if name not in acc["params"]:
            _collect(name, design, acc, seen)
    return set(acc["funcs"])
