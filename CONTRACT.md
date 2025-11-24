# treesitter-tools Contract

1. **Tree-sitter first** – the package must rely on upstream grammars (via `tree_sitter_language_pack`) and never ship custom parsers generated at runtime without review.
2. **Local-only** – no network access is required after install; grammars are embedded in the dependency. CLI should operate entirely on local files/stdin.
3. **Deterministic output** – given the same source file and options, the tool must emit identical JSON/text so downstream automation can diff results.
4. **Composable API** – expose the same functionality via Python modules and the CLI so SciLLM or other agents can call whichever interface is easier.
5. **Safe defaults** – refuse to parse binary files, surface errors with actionable messages, and fall back gracefully when a language grammar is missing.
6. **Documented behaviors** – whenever commands or outputs change, update `README.md` and the CLI `--help` text to match.
