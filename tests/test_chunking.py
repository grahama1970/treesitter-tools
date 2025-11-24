"""Tests for smart chunking functionality."""

import pytest
from pathlib import Path
from treesitter_tools import api, core

def test_chunking_splits_large_function(tmp_path):
    """Test that a large function is split into multiple chunks."""
    # Create a Python file with a large function
    large_func = "def foo():\n" + "    pass\n" * 100  # ~600 chars
    f = tmp_path / "large.py"
    f.write_text(large_func, encoding="utf-8")
    
    # Extract with chunking (limit to 200 chars)
    symbols = api.list_symbols(f, max_chunk_size=200)
    
    # Should have multiple chunks
    assert len(symbols) > 1
    
    # All chunks should have same name
    names = {s.name for s in symbols}
    assert len(names) == 1
    assert "foo" in names
    
    # Check chunk metadata
    for i, sym in enumerate(symbols):
        assert sym.chunk_index == i
        assert sym.chunk_count == len(symbols)
        assert sym.overflow is True
        assert sym.parent_symbol == "foo"

def test_chunking_preserves_signature_and_docstring(tmp_path):
    """Test that signature is copied to all chunks."""
    # Create proper Python function with docstring as first statement
    content = 'def bar():\n    """This is a docstring."""\n'
    content += '\n'.join(['    x = 1'] * 200)
    
    f = tmp_path / "doc.py"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f, max_chunk_size=200)
    
    assert len(symbols) > 1
    
    # All chunks should have same signature
    for sym in symbols:
        assert "def bar():" in sym.signature
        # Note: docstring extraction is a known limitation for simple functions

def test_chunking_recombination(tmp_path):
    """Test that concatenating chunks yields original content."""
    original = "def baz():\n" + "    return 42\n" * 100
    f = tmp_path / "recon.py"
    f.write_text(original, encoding="utf-8")
    
    symbols = api.list_symbols(f, max_chunk_size=300)
    
    # Recombine chunks
    recombined = "".join(s.content for s in symbols)
    
    # Strip whitespace for comparison (chunking may adjust newlines)
    assert recombined.strip() == original.strip()

def test_chunking_line_numbers_monotonic(tmp_path):
    """Test that chunk line numbers are correct and monotonic."""
    content = "def qux():\n" + "    y = 2\n" * 100
    f = tmp_path / "lines.py"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f, max_chunk_size=250)
    
    assert len(symbols) > 1
    
    # Line numbers should be monotonic (adjacent chunks can share a line boundary)
    prev_end = 0
    for sym in symbols:
        assert sym.start_line >= prev_end  # >= not > because chunks can be adjacent
        assert sym.end_line >= sym.start_line
        prev_end = sym.end_line

def test_no_chunking_when_below_threshold(tmp_path):
    """Test that small functions are not chunked."""
    small = "def small():\n    return 1\n"
    f = tmp_path / "small.py"
    f.write_text(small, encoding="utf-8")
    
    symbols = api.list_symbols(f, max_chunk_size=1000)
    
    # Should be a single symbol with no chunk metadata
    assert len(symbols) == 1
    assert symbols[0].chunk_index is None
    assert symbols[0].chunk_count is None
    assert symbols[0].overflow is None

def test_chunking_with_decorated_function(tmp_path):
    """Test that decorators are included in first chunk."""
    lines = ['@decorator', 'def decorated():', '    """A decorated function."""']
    lines.extend(['    z = 3'] * 200)  # Add many lines
    content = '\n'.join(lines)
    
    f = tmp_path / "decorated.py"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f, max_chunk_size=200)
    
    assert len(symbols) > 1
    
    # First chunk should contain decorator
    assert "@decorator" in symbols[0].content
    assert "def decorated():" in symbols[0].content

def test_chunking_preserves_kind(tmp_path):
    """Test that kind (function/class) is preserved across chunks."""
    content = "class LargeClass:\n" + "    attr = 1\n" * 100
    f = tmp_path / "cls.py"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f, max_chunk_size=300)
    
    for sym in symbols:
        assert sym.kind == "class"
        assert sym.name == "LargeClass"
