# treesitter-tools Contract

1. **Pure AST extraction** – this tool focuses solely on parsing and extracting structured information from code using Tree-sitter. No semantic search, embeddings, or vector databases. Other tools handle search/indexing; we provide the parsed data.
2. **Tree-sitter first** – the package must rely on upstream grammars (via `tree_sitter_language_pack`) and never ship custom parsers generated at runtime without review.
3. **Local-only** – no network access is required after install; grammars are embedded in the dependency. CLI should operate entirely on local files/stdin.
4. **Deterministic output** – given the same source file and options, the tool must emit identical JSON/text so downstream automation can diff results.
5. **Composable API** – expose the same functionality via Python modules and the CLI so SciLLM or other agents can call whichever interface is easier.
6. **Safe defaults** – refuse to parse binary files, surface errors with actionable messages, and fall back gracefully when a language grammar is missing.
7. **Documented behaviors** – whenever commands or outputs change, update `README.md` and the CLI `--help` text to match.
