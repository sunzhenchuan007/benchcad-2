"""geomlib — shared parametric-curve generators for designs.

Designs may import these instead of copy-pasting curve math (tooth profiles,
involutes, ...). The generated CadQuery program must still be STAND-ALONE, so
`build()` embeds the *source code* of every helper it uses via
`inline_source(...)` — the emitted program imports only `math` and `cadquery`
and computes the curve itself.

Contract for library functions:
  - self-contained: may use only `math` and builtins (no imports of their own,
    no closures over module state) — they must run verbatim inside an emitted
    program;
  - deterministic: pure functions of their arguments, fixed rounding.

A family that uses geomlib declares it in family.json:
    "geomlib": ["sprocket_profile"]
`bench2 validate` checks the declaration against the registry and against the
emitted program text.
"""

from __future__ import annotations

import inspect

from .involute import involute_gear_profile
from .sprocket import sprocket_profile

REGISTRY = {
    "sprocket_profile": sprocket_profile,
    "involute_gear_profile": involute_gear_profile,
}


def inline_source(*names: str) -> str:
    """Return the verbatim source of the named helpers, ready to embed in a
    generated program (order preserved, deduplicated)."""
    seen, blocks = set(), []
    for n in names:
        if n in seen:
            continue
        if n not in REGISTRY:
            raise KeyError(f"geomlib has no helper named {n!r} (have: {sorted(REGISTRY)})")
        seen.add(n)
        blocks.append(inspect.getsource(REGISTRY[n]).rstrip())
    return "\n\n\n".join(blocks)
