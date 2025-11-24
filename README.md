# treesitter-tools

`treesitter-tools` is a lightweight Python CLI + library that wraps Tree-sitter so agents can inspect local source code the same way osgrep does. It currently auto-detects 30+ grammars (Python, JS/TS, C/C++, Obj-C, Rust, Go, Java/Kotlin/Scala, Swift, C#, PHP, Ruby, Bash, Lua, JSON/YAML/TOML, etc.) thanks to `tree_sitter_language_pack`, and it can:

- detect a file's language automatically
- parse code with `tree_sitter_language_pack`
- walk the AST to list top-level functions/classes with signatures, docstrings, and locations
- run Tree-sitter queries for ad-hoc inspection

The goal is to keep analyses local (no MCP server needed) while exposing a CLI (`treesitter-tools symbols ...`) that other automation can shell into.

## Quick start

```bash
# install locally
uv pip install -e .

# list functions/classes in a file
treesitter-tools symbols path/to/file.py

# save JSON elsewhere and override the language
treesitter-tools symbols app/component.tsx --language typescript --output ast.json

# run a query (same syntax as `tree-sitter query`)
treesitter-tools query app/component.tsx '(function_declaration name: (identifier) @name)'

# walk an entire repo and get JSON + Markdown outline
treesitter-tools scan . --include "src/**/*.py" --outline outline.md --output symbols.json
```

Programmatic use mirrors the CLI:

```python
from pathlib import Path
from treesitter_tools import api

symbols = api.list_symbols(Path("src/main.py"))
for sym in symbols:
    print(sym.name, sym.start_line, sym.kind)

outline = treesitter_tools.core.outline_markdown(
    treesitter_tools.core.scan_directory(Path("src"), include=["**/*.py"])
)
```
