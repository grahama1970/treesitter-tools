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

## Usage

### List Symbols in a File

```bash
# Auto-detect language
treesitter-tools symbols src/core.py

# Explicit language
treesitter-tools symbols script.txt --language python

# Include full content (useful for LLM context)
treesitter-tools symbols src/core.py --content
```

### Scan a Directory

```bash
# Scan current directory recursively
treesitter-tools scan .

# Filter by glob pattern
treesitter-tools scan src --include "**/*.py"

# Generate markdown outline
treesitter-tools scan src --outline OUTLINE.md

# Verbose mode (show errors and skipped files)
treesitter-tools scan src --verbose
```

### Query with Tree-sitter S-expressions

```bash
treesitter-tools query src/core.py "(function_definition) @func"
```

## Troubleshooting

### Common Errors

**"Cannot detect Tree-sitter language"**
- The file extension is unknown (e.g., `.txt`).
- **Fix:** Use the `--language` flag to specify it manually:
  ```bash
  treesitter-tools symbols myscript.txt --language python
  ```

**"Refusing to parse binary file"**
- The file appears to be binary (contains NUL bytes).
- **Fix:** `treesitter-tools` only supports text source code.

**"Tree-sitter grammar for 'xyz' is unavailable"**
- The requested language grammar is not installed in the environment.
- **Fix:** Ensure `tree-sitter-language-pack` supports the language.

**"No symbols found"**
- The file was parsed, but no functions or classes were found.
- **Fix:** Check if the file contains code, or if the language mapping supports the constructs you expect.

## Development

### Running Tests

```bash
uv run pytest
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
