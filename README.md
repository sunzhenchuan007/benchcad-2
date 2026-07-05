# BenchCAD 2.0 <sub>(in preparation)</sub>

**A community-grounded parametric CAD benchmark — 200 industrial part
families, every one defined by an auditable parametric design.**

BenchCAD 2.0 is the successor to
[BenchCAD](https://github.com/BenchCAD/BenchCAD-main) (17,900 parts / 106
families, used in frontier-model system cards). Where 1.0's parameter ranges
were largely machine-chosen, every 2.0 family is an explicit **parametric
design**: a parameter table with units, ranges and sources, plus the
inter-parameter engineering constraints that make a part *manufacturable* —
written and reviewed by people who know the domain.

- **Design blueprint / decision record** → [`DESIGN.md`](DESIGN.md)
- **End-to-end walkthrough** (datasheet → merged family, on a real example) → [`docs/WALKTHROUGH.md`](docs/WALKTHROUGH.md)
- **The interface** → [`docs/DESIGN_SPEC.md`](docs/DESIGN_SPEC.md); references: [`designs/example_tee_bracket/`](designs/example_tee_bracket/) (proportions) · [`designs/simplex_sprocket/`](designs/simplex_sprocket/) (table-driven, from the norelem 22250 datasheet)
- **Contributing** (merged family ⇒ co-authorship, [`CONTRIBUTORS.md`](CONTRIBUTORS.md)) → [`CONTRIBUTING.md`](CONTRIBUTING.md)
- Scoring engine (shared with 1.0) → [BenchCAD-main](https://github.com/BenchCAD/BenchCAD-main)

## The 60-second contributor loop

```bash
uv sync                          # once: Python 3.11 env (pinned CadQuery)

uv run bench2 new corner_bracket        # scaffold designs/corner_bracket/
# ... fill in PARAM_SPEC, check(), sample(), build() ...
uv run bench2 validate corner_bracket   # every machine gate, locally
uv run bench2 preview corner_bracket    # render a 3×3 grid (difficulty × seed)
# open a PR — CI runs the same two commands and posts the preview
```

You write **one file of engineering knowledge** (`design.py`); rendering, QA
generation, and edit-pair derivation are done downstream by the maintainers'
pipeline. Reviewers audit exactly two things: your constraints and your labels.

## Status

🚧 Framework + reference design stage. The wanted-families list, proposal
process, and contribution drive open with the public launch.

## License

MIT (code & designs). Released datasets: CC BY 4.0 on Hugging Face.
