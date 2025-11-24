"""Core Tree-sitter helpers used by the CLI and Python API."""

from __future__ import annotations

import json
import os
import fnmatch
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

from tree_sitter import Language, Node, Parser, Query, QueryCursor
import tree_sitter_language_pack as tlp

LANGUAGE_MAPPINGS = {
    # Scripting & shells
    "py": "python",
    "python": "python",
    "pyi": "python",
    "rb": "ruby",
    "php": "php",
    "pl": "perl",
    "ps1": "powershell",
    "psm1": "powershell",
    "sh": "bash",
    "bash": "bash",
    "zsh": "bash",
    "lua": "lua",
    "r": "r",
    # Web & frontend
    "js": "javascript",
    "jsx": "javascript",
    "ts": "typescript",
    "tsx": "typescript",
    "css": "css",
    "scss": "scss",
    "html": "html",
    # Systems / compiled
    "c": "c",
    "h": "c",
    "cpp": "cpp",
    "cxx": "cpp",
    "cc": "cpp",
    "hpp": "cpp",
    "hh": "cpp",
    "m": "objc",
    "mm": "objc",
    "rs": "rust",
    "go": "go",
    "swift": "swift",
    "cs": "csharp",
    "nim": "nim",
    "zig": "zig",
    "asm": "asm",
    # JVM / functional
    "java": "java",
    "kt": "kotlin",
    "kts": "kotlin",
    "scala": "scala",
    "clj": "clojure",
    "ml": "ocaml",
    "mli": "ocaml_interface",
    "hs": "haskell",
    # Data / markup / configuration
    "json": "json",
    "yml": "yaml",
    "yaml": "yaml",
    "toml": "toml",
    "ini": "ini",
    "md": "markdown",
    "xml": "xml",
    "sql": "sql",
    # Misc
    "dart": "dart",
    "elm": "elm",
    "erlang": "erlang",
    "f90": "fortran",
    "fs": "fsharp",
    "jl": "julia",
    "tex": "latex",
    "s": "asm",
    "ada": "ada",
    "ino": "arduino",
}

DEFAULT_FUNCTION_NODE_TYPES = {
    "function_definition",
    "function_declaration",
    "method_definition",
    "method_declaration",
    "generator_function_declaration",
    "impl_item",
}

FUNCTION_NODE_TYPES = {
    "python": {"function_definition", "async_function_definition", "decorated_definition"},
    "javascript": {"function_declaration", "method_definition", "arrow_function"},
    "typescript": {"function_declaration", "method_definition", "generator_function_declaration"},
    "go": {"function_declaration", "method_declaration"},
    "rust": {"function_item"},  # Removed impl_item to avoid duplication with classes
    "java": {"method_declaration"},
    "kotlin": {"function_declaration"},
    "php": {"function_definition", "method_declaration"},
    "c": {"function_definition"},
    "cpp": {"function_definition", "function_declarator", "method_definition"},
    "objc": {"function_definition", "method_definition"},
    "csharp": {"method_declaration"},
    "scala": {"function_definition", "method_declaration"},
    "haskell": {"function_declaration"},
    "dart": {"function_signature"},
}

CLASS_NODE_TYPES = {
    "python": {"class_definition", "decorated_definition"},
    "javascript": {"class_declaration"},
    "typescript": {"class_declaration", "interface_declaration"},
    "java": {"class_declaration", "interface_declaration"},
    "kotlin": {"class_declaration"},
    "php": {"class_declaration"},
    "go": {"type_spec"},  # Captures type Foo struct { ... }
    "c": {"struct_specifier"},  # Note: C structs are data-only, no methods
    "rust": {"struct_item", "impl_item"},
    "cpp": {"class_specifier", "struct_specifier"},
    "objc": {"class_declaration"},
    "csharp": {"class_declaration", "interface_declaration"},
    "scala": {"class_definition", "trait_definition"},
}

NAME_NODE_TYPES = {"identifier", "name", "property_identifier", "type_identifier"}


def is_binary_file(path: Path) -> bool:
    """Check if file is binary by looking for NUL bytes in first 8KB."""
    try:
        with path.open("rb") as f:
            chunk = f.read(8192)
            return b"\x00" in chunk
    except OSError:
        return False
@dataclass
class CodeSymbol:
    kind: str
    name: str
    start_line: int
    end_line: int
    signature: Optional[str]
    docstring: Optional[str]
    content: Optional[str] = None
    # Chunking fields
    chunk_index: Optional[int] = None
    chunk_count: Optional[int] = None
    parent_symbol: Optional[str] = None
    overflow: Optional[bool] = None

    def to_dict(self) -> dict:
        data = {
            "kind": self.kind,
            "name": self.name,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "signature": self.signature,
            "docstring": self.docstring,
            "content": self.content,
        }
        if self.overflow:
            data.update({
                "chunk_index": self.chunk_index,
                "chunk_count": self.chunk_count,
                "parent_symbol": self.parent_symbol,
                "overflow": self.overflow,
            })
        return data


def detect_language(path: Path, override: Optional[str] = None) -> Optional[str]:
    if override:
        return override
    ext = path.suffix.lstrip(".").lower()
    return LANGUAGE_MAPPINGS.get(ext)
PARSER_CACHE = {}

def load_language(language: str) -> Language:
    try:
        return tlp.get_language(language)
    except Exception as exc:  # pragma: no cover - pass through message
        raise RuntimeError(f"Tree-sitter grammar for '{language}' is unavailable: {exc}") from exc


def parse_source(source: bytes, language: str) -> Node:
    if language not in PARSER_CACHE:
        parser = Parser()
        parser.language = load_language(language)
        PARSER_CACHE[language] = parser
    else:
        parser = PARSER_CACHE[language]
    
    tree = parser.parse(source)
    return tree.root_node


def _node_text(node: Node, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", "replace")


def _identifier_from(node: Node, source: bytes) -> Optional[str]:
    field = node.child_by_field_name("name")
    if field is not None:
        return _node_text(field, source)
    if node.type in NAME_NODE_TYPES:
        return _node_text(node, source)
    for child in node.children:
        name = _identifier_from(child, source)
        if name:
            return name
    return None


def _python_docstring(node: Node, source: bytes) -> Optional[str]:
    if not node.children:
        return None
    for child in node.children:
        if child.type == "block" and child.child_count:
            first = child.children[0]
            if first.type == "expression_statement" and first.child_count:
                expr = first.children[0]
                if expr.type in {"string", "string_literal"}:
                    text = _node_text(expr, source)
                    return text.strip("\"' ")
    return None


def _signature_snippet(node: Node, source: bytes) -> str:
    lines = _node_text(node, source).splitlines()
    if not lines:
        return ""
    first = lines[0]
    if len(lines) > 1:
        first += " ..."
    return first.strip()


def extract_symbols(path: Path, language: Optional[str] = None, max_chunk_size: Optional[int] = None) -> List[CodeSymbol]:
    path = Path(path)
    if is_binary_file(path):
        raise ValueError(f"Refusing to parse binary file: {path}")

    language = detect_language(path, language)
    if not language:
        raise ValueError(f"Cannot detect Tree-sitter language for {path}")
    source = path.read_bytes()
    root = parse_source(source, language)
    symbols: List[CodeSymbol] = []
    func_nodes = FUNCTION_NODE_TYPES.get(language, DEFAULT_FUNCTION_NODE_TYPES)
    class_nodes = CLASS_NODE_TYPES.get(language, set())

    # Track visited nodes to avoid duplicates (e.g. decorated function inside decorated_definition)
    visited_nodes = set()

    def visit(node: Node) -> None:
        if node.id in visited_nodes:
            return

        # Special handling for Python decorators
        if language == "python" and node.type == "decorated_definition":
            # The decorated_definition contains the function/class definition as a child
            # We want to capture the whole decorated node as the content
            # But we need to check if it's a function or class
            body = node.child_by_field_name("definition")
            if body:
                if body.type in func_nodes:
                    process_node(node, "function", body)
                    visited_nodes.add(body.id) # Don't process the inner definition again
                elif body.type in class_nodes:
                    process_node(node, "class", body)
                    visited_nodes.add(body.id)
            visited_nodes.add(node.id)
            return

        # Special handling for Go type_spec (only structs/interfaces)
        if language == "go" and node.type == "type_spec":
            # Check if it's a struct or interface
            type_node = node.child_by_field_name("type")
            if type_node and type_node.type in {"struct_type", "interface_type"}:
                process_node(node, "class")
            visited_nodes.add(node.id)
            return

        if node.type in func_nodes:
            process_node(node, "function")
        elif node.type in class_nodes:
            process_node(node, "class")
        
        visited_nodes.add(node.id)
        for child in node.children:
            visit(child)

    def process_node(node: Node, kind: str, name_source_node: Optional[Node] = None) -> None:
        # For C structs, try to find name more robustly
        if language == "c" and node.type == "struct_specifier":
            name_node = node.child_by_field_name("name")
            if name_node:
                name = _node_text(name_node, source)
            else:
                name = "<anonymous>"
        else:
            # Use the node itself or a specific child for name extraction
            target = name_source_node or node
            name = _identifier_from(target, source) or "<anonymous>"
        
        doc = _python_docstring(node, source) if language == "python" else None
        content = _node_text(node, source)
        signature = _signature_snippet(node, source)
        start_line = node.start_point[0] + 1
        end_line = node.end_point[0] + 1

        # Chunking logic
        if max_chunk_size and len(content) > max_chunk_size:
            chunks = []
            current_pos = 0
            total_len = len(content)
            
            while current_pos < total_len:
                # Determine chunk end
                chunk_end = min(current_pos + max_chunk_size, total_len)
                
                # If not the last chunk, try to align to newline
                if chunk_end < total_len:
                    # Look for newline up to 100 chars back to avoid breaking lines mid-statement if possible
                    # But simpler: just look forward for next newline if it's close?
                    # Design decision: Hard split at max_chunk_size is safer for strict limits,
                    # but line splitting is better for LLMs.
                    # Let's try to find the *last* newline within the chunk limit
                    last_newline = content.rfind('\n', current_pos, chunk_end)
                    if last_newline != -1 and last_newline > current_pos:
                        chunk_end = last_newline + 1 # Include the newline
                    # Else: no newline found, hard split (rare for code)
                
                chunk_text = content[current_pos:chunk_end]
                
                # Calculate line numbers for this chunk
                # Relative to the start of the function
                prefix = content[:current_pos]
                chunk_start_line_offset = prefix.count('\n')
                chunk_lines_count = chunk_text.count('\n')
                
                chunk_start_line = start_line + chunk_start_line_offset
                chunk_end_line = chunk_start_line + chunk_lines_count
                
                chunks.append({
                    "content": chunk_text,
                    "start_line": chunk_start_line,
                    "end_line": chunk_end_line
                })
                
                current_pos = chunk_end
            
            # Create symbols for chunks
            for i, chunk in enumerate(chunks):
                symbols.append(
                    CodeSymbol(
                        kind=kind,
                        name=name, # Keep same name
                        start_line=chunk["start_line"],
                        end_line=chunk["end_line"],
                        signature=signature, # Copy signature to all chunks
                        docstring=doc, # Copy docstring to all chunks
                        content=chunk["content"],
                        chunk_index=i,
                        chunk_count=len(chunks),
                        parent_symbol=name,
                        overflow=True
                    )
                )
        else:
            # No chunking needed
            symbols.append(
                CodeSymbol(
                    kind=kind,
                    name=name,
                    start_line=start_line,
                    end_line=end_line,
                    signature=signature,
                    docstring=doc,
                    content=content,
                )
            )

    visit(root)
    return symbols


def run_query(path: Path, query: str, language: Optional[str] = None) -> List[dict]:
    path = Path(path)
    language = detect_language(path, language)
    if not language:
        raise ValueError(f"Cannot detect Tree-sitter language for {path}")
    source = path.read_bytes()
    language_obj = load_language(language)
    root = parse_source(source, language)
    ts_query = Query(language_obj, query)
    cursor = QueryCursor(ts_query)
    results: List[dict] = []
    for pattern_index, captures in cursor.matches(root):
        capture_items = []
        for name, nodes in captures.items():
            for node in nodes:
                capture_items.append(
                    {
                        "name": name,
                        "text": _node_text(node, source),
                        "start_line": node.start_point[0] + 1,
                        "end_line": node.end_point[0] + 1,
                    }
                )
        results.append({"pattern_index": pattern_index, "captures": capture_items})
    return results


def symbols_to_json(symbols: Iterable[CodeSymbol]) -> str:
    return json.dumps([sym.to_dict() for sym in symbols], indent=2)


def _match_any(patterns: Sequence[str], rel_path: str) -> bool:
    rel_path = rel_path.replace("\\", "/")
    for pattern in patterns:
        pattern = pattern.replace("\\", "/")
        candidates = [pattern]
        if pattern.startswith("**/"):
            candidates.append(pattern[3:])
        for candidate in candidates:
            if fnmatch.fnmatch(rel_path, candidate):
                return True
    return False


def scan_directory(
    root: Path,
    include: Sequence[str] | None = None,
    exclude: Sequence[str] | None = None,
    max_chunk_size: Optional[int] = None,
) -> List[FileSymbols]:
    root = root.resolve()
    include = include or ["**/*"]
    exclude = exclude or []
    reports: List[FileSymbols] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if not _match_any(include, rel):
            continue
        if exclude and _match_any(exclude, rel):
            continue
        
        try:
            symbols = extract_symbols(path, max_chunk_size=max_chunk_size)
            language = detect_language(path) or "unknown"
            if symbols:
                reports.append(FileSymbols(path=path, language=language, symbols=symbols))
        except Exception as exc:
            # Capture error in the report
            reports.append(FileSymbols(path=path, language="unknown", symbols=[], error=str(exc)))
            continue
            
    return reports


def outline_markdown(reports: Iterable[FileSymbols]) -> str:
    lines: List[str] = []
    for report in reports:
        lines.append(f"## {report.path.as_posix()} ({report.language})")
        for sym in report.symbols:
            lines.append(f"- {sym.kind}: {sym.name} (lines {sym.start_line}-{sym.end_line})")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


__all__ = [
    "LANGUAGE_MAPPINGS",
    "CodeSymbol",
    "FileSymbols",
    "extract_symbols",
    "run_query",
    "scan_directory",
    "outline_markdown",
    "symbols_to_json",
]
@dataclass
class FileSymbols:
    path: Path
    language: str
    symbols: List[CodeSymbol]
    error: Optional[str] = None

    def to_dict(self) -> dict:
        data = {
            "path": self.path.as_posix(),
            "language": self.language,
            "symbols": [sym.to_dict() for sym in self.symbols],
        }
        if self.error:
            data["error"] = self.error
        return data
