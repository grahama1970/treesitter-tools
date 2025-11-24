"""High-level API for programmatic use."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from .core import CodeSymbol, extract_symbols, run_query


def list_symbols(path: Path, language: Optional[str] = None) -> List[CodeSymbol]:
    return extract_symbols(path, language)


def query_file(path: Path, query: str, language: Optional[str] = None):
    return run_query(path, query, language)


__all__ = ["list_symbols", "query_file", "CodeSymbol"]
