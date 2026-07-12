# BenchCAD 2.0 <sub>(in preparation)</sub>

**The agentic generation of BenchCAD: tool use, execution feedback, and
multi-turn refinement over community-grounded parametric CAD — 300 industrial
part families, every one an auditable parametric design (dataset v2.0).**

[![Discord](https://img.shields.io/badge/Discord-join%20the%20community-5865F2?logo=discord&logoColor=white)](https://discord.gg/be9AtvrDyK)

BenchCAD 2.0 is the successor to
[BenchCAD](https://github.com/BenchCAD/BenchCAD-main) (17,900 parts / 106
families, used in frontier-model system cards). Where 1.0's parameter ranges
were largely machine-chosen, every 2.0 family is an explicit **parametric
design**: a parameter table with units, ranges and sources, plus the
inter-parameter engineering constraints that make a part *manufacturable* —
written and reviewed by people who know the domain.

**Three documents cover everything:**

- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — rules, the full lifecycle, how to
  claim & verify an issue, bugs/features. *(Contributors start here; merged
  family ⇒ co-authorship — see the [provenance board](CONTRIBUTORS.md).)*
- **[`REVIEWING.md`](REVIEWING.md)** — how to verify a family PR (renders vs
  drawing, extremes vs table, three-layer equation check).
- **[`docs/DESIGN_SPEC.md`](docs/DESIGN_SPEC.md)** — the part + spec interface;
  copy [`designs/simplex_sprocket/`](designs/simplex_sprocket/) (table-driven reference).

Roadmap → [#21](../../issues/21) · progress → [`STATUS.md`](STATUS.md) · claim a family → [open family issues](../../issues?q=is%3Aissue+is%3Aopen+label%3Afamily) ([`good first issue`](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) = easiest) · **illustrated tutorial** [EN](docs/WALKTHROUGH.md)/[中文](docs/WALKTHROUGH.zh.md) · deep dive: [decision record](DESIGN.md) · scoring engine → [BenchCAD-main](https://github.com/BenchCAD/BenchCAD-main)

> **🧑‍🔧 New here / not a GitHub person?** Step-by-step guide for engineers:
> **[English](docs/GETTING_STARTED.md) · [中文](docs/GETTING_STARTED.zh.md)** —
> including a zero-code path: bring a datasheet, we write the code, you get credit.

## The 60-second contributor loop

```bash
uv sync                          # once: Python 3.11 env (pinned CadQuery)

uv run bench2 new corner_bracket        # scaffold designs/corner_bracket/
# ... fill part.py (build) + spec.py (PARAM_SPEC, check, optional refine) ...
uv run bench2 validate corner_bracket   # every machine gate, locally
uv run bench2 preview corner_bracket    # render a 3×3 grid (difficulty × seed)
uv run python tools/debug_family.py corner_bracket --gui   # edit part.py live in a 3D GUI (docs/DEBUGGING.md)
# open a PR — CI runs the same two commands and posts the preview
```

You write **two files of engineering knowledge** (`part.py` + `spec.py`); rendering, QA
generation, and edit-pair derivation are done downstream by the maintainers'
pipeline. Reviewers audit exactly two things: your constraints and your labels.

## Status

🚧 Framework + reference design stage. The wanted-families list, proposal
process, and contribution drive open with the public launch.

## License

MIT (code & designs). Released datasets: CC BY 4.0 on Hugging Face.
