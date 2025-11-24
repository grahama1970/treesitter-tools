# treesitter-tools Context (Nov 24, 2025)

- **Location**: `/home/graham/workspace/experiments/treesitter-tools`
- **Purpose**: Tree-sitter CLI + Python API (`symbols`, `query`, `scan`) for extracting functions/classes or running queries on local code; commonly paired with bundle-files to summarize repos before bundling.
- **Current state**:
  - Supports ~30 languages via `tree_sitter_language_pack` (Python, JS/TS, C/C++/Obj-C, Rust, Go, Swift, C#, PHP, Ruby, Bash, Lua, JSON/YAML/TOML, etc.) with fallback node sets for everything else.
  - CLI commands:
    - `symbols <file>` → JSON list of functions/classes
    - `query <file> <tree-sitter-query>` → raw capture results
    - `scan <root>` → walk directories using include/exclude globs, emit JSON + optional Markdown outline (see README examples).
  - Tests live in `tests/test_core.py` and cover symbol extraction, querying, and directory scanning.
  - Install & validate with `uv pip install -e .` followed by `uv run pytest`.
- **Next steps**:
  1. Flesh out language-specific node tables (Ada, Zig, Nim, Elm, etc.) so signatures/docstrings are richer everywhere.
  2. Add streaming / incremental scan output (NDJSON or per-file events) for huge repos.
  3. Expose AST-based filtering (e.g., “only bundle functions named `foo`”) so bundle-files can optionally import these summaries.
  4. Evaluate swapping or augmenting `tree_sitter_language_pack` with `tree-sitter-languages` if we need grammars that pack doesn’t ship; document whichever bundle we standardize on.

Before hacking, skim `README.md` to confirm CLI behavior, then run `uv run pytest` to ensure the workspace is green. Keep README + CONTRACT updated with any new commands or behaviors.
