# Agent Instructions — treesitter-tools

This repo packages Tree-sitter helpers (CLI + Python API). Follow these guardrails whenever you touch it.

## 1. Bootstrapping
- Always read `CONTEXT.md` and `README.md` at the start of a session; they outline supported commands (`symbols`, `query`, `scan`) and current priorities.
- Use `uv` for everything (install, lock, test). No `pip`/`poetry`/`conda` substitutions.
- Before editing, ensure grammars are available by running `uv pip install -e .` (installs `tree_sitter_language_pack`).

## 2. Development Flow
- Keep shared logic inside `treesitter_tools/core.py`; CLI modules should stay thin wrappers around those helpers.
- When adding languages, update both `LANGUAGE_MAPPINGS` and the node-type dictionaries so symbols remain meaningful.
- Directory scanning must respect include/exclude globs and stay deterministic; avoid random ordering.
- Any new behavior (flags, API helpers) must be documented in README + CLI `--help`.

## 3. Testing & Verification
- Run `uv run pytest` after code changes; tests already cover extraction, queries, and scans—extend them when expanding features.
- For CLI-only tweaks, add smoke tests under `tests/` that import the core helpers; we avoid spawning subprocesses in tests.

## 4. Safety & Output
- CLI commands output JSON to stdout by default; never emit extra chatter unless the user requests `--output`/`--outline` files.
- When walking directories, skip binary/unrecognized files silently and continue (errors should not abort the entire scan).

## 5. Handoff Expectations
- Update `CONTEXT.md` whenever you add noteworthy capabilities or TODOs.
- Include concise reproduction steps (command + expected artifact) in PR descriptions or handoffs so the next agent can resume quickly.

Stick to these guardrails and the tool stays predictable for bundle-files and other agents.
