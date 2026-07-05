# CLAUDE.md

Read [`AGENTS.md`](AGENTS.md) — it is the agent guide for this repo (rules for
drafting designs, the workflow, and the hard rules on sources, determinism,
and scope). `docs/DESIGN_SPEC.md` is the interface contract;
`designs/example_tee_bracket/` is the reference implementation.

Repo-specific reminders:

- Run commands from the repo root with `uv run` (`uv run bench2 validate <family>`).
- The environment is pinned (`cadquery==2.3.0`, `numpy==1.26.4`); don't bump pins.
- `bench2 validate` must PASS and a human must have looked at
  `bench2 preview` output before any PR.
- Never fabricate standards citations in `PARAM_SPEC.source` or `check()`
  messages; use `"proportion"` when no real rule is known.
