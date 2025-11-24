The key difference: osgrep is a semantic search tool (embeddings + vector DB), while treesitter-tools is a pure AST extraction library. For AST parsing specifically, we're at parity.

Recommended Next Steps:
Documentation - Update README with content extraction examples
GitHub Push - Still blocked on gh auth login - you'll need to authenticate
Optional Enhancements:
Add --with-content to scan command (not just 
symbols
)
Add chunking strategies (max-size splitting for large functions)
Performance benchmarks on large repos
Add more language-specific node mappings (Go structs as classes, etc.)
