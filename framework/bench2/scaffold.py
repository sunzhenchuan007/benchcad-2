"""`bench2 new` — write a TODO-annotated four-piece skeleton."""

from __future__ import annotations

import json
from pathlib import Path

_TEMPLATES = Path(__file__).parent / "templates"


def create(fam_dir: Path, family: str) -> None:
    fam_dir.mkdir(parents=True)
    design = (_TEMPLATES / "design.py.tmpl").read_text().replace("__FAMILY__", family)
    (fam_dir / "design.py").write_text(design)
    meta = {
        "family": family,
        "standard": None,
        "base_plane": "XY",
        "description": "TODO: one sentence — what the part is and its main features",
        "source": "TODO: standard table / engineering rule / proportion convention",
        "contributor": "TODO: your-github-handle",
    }
    (fam_dir / "family.json").write_text(json.dumps(meta, indent=2) + "\n")
