"""High-level API for programmatic use."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .core import CodeSymbol, extract_symbols, run_query


def list_symbols(path: Path, language: Optional[str] = None, max_chunk_size: Optional[int] = None) -> List[CodeSymbol]:
    """
    Extract functions and classes from a source file.
    
    Args:
        path: Path to the source file
        language: Optional language override (auto-detected from extension if not provided)
        max_chunk_size: Optional maximum size in characters for content chunks
    
    Returns:
        List of CodeSymbol objects
    """
    return extract_symbols(path, language, max_chunk_size)


def query_file(path: Path, query: str, language: Optional[str] = None):
    return run_query(path, query, language)


__all__ = ["list_symbols", "query_file", "CodeSymbol"]
