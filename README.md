# treesitter-tools

`treesitter-tools` is a **pure AST extraction library** for Python that uses Tree-sitter to parse and extract structured information from source code. Unlike semantic search tools (embeddings, vector DBs), this focuses solely on parsing code into queryable structures.

It auto-detects 30+ languages (Python, JS/TS, C/C++, Obj-C, Rust, Go, Java/Kotlin/Scala, Swift, C#, PHP, Ruby, Bash, Lua, JSON/YAML/TOML, etc.) via `tree_sitter_language_pack` and provides:

- **Automatic language detection** from file extensions
- **Function/class extraction** with signatures, docstrings, line numbers, and full source content
- **Tree-sitter query execution** for advanced AST inspection  
- **Directory scanning** with glob pattern filtering

**Use cases:** Code analysis, documentation generation, static analysis tools, LLM context preparation, code search indexing.

## Quick start

```bash
# install locally
uv pip install -e .

# list functions/classes in a file (metadata only)
treesitter-tools symbols path/to/file.py

# extract full source code of functions/classes
treesitter-tools symbols path/to/file.py --content

# save JSON elsewhere and override the language
treesitter-tools symbols app/component.tsx --language typescript --output ast.json

# run a query (same syntax as `tree-sitter query`)
treesitter-tools query app/component.tsx '(function_declaration name: (identifier) @name)'

# walk an entire repo and get JSON + Markdown outline
treesitter-tools scan . --include "src/**/*.py" --outline outline.md --output symbols.json
```

### Content Extraction

The `--content` flag extracts the full source code of each function/class, not just metadata. This is essential for:
- **LLM context preparation** - feed complete function bodies to language models
- **Code chunking** - split large files into semantic units (functions) for embedding/indexing
- **Documentation generation** - include full implementation in generated docs

```bash
# Extract full function bodies for embedding pipeline
treesitter-tools symbols src/
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
