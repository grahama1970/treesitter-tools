"""Tests for reliability and parity fixes."""

import pytest
from pathlib import Path
from treesitter_tools import api, core

def test_binary_file_detection(tmp_path):
    """Test that binary files are rejected with a clear error."""
    # Create a file with a NUL byte
    binary_file = tmp_path / "binary.py"
    with binary_file.open("wb") as f:
        f.write(b"import os\x00")
    
    with pytest.raises(ValueError, match="Refusing to parse binary file"):
        api.list_symbols(binary_file)

def test_python_decorator_extraction(tmp_path):
    """Test that Python decorators are included in content extraction."""
    content = """
@decorator
def foo():
    pass

@cls_decorator
class Bar:
    pass
"""
    f = tmp_path / "test.py"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f)
    
    # Check function
    foo = next(s for s in symbols if s.name == "foo")
    assert "@decorator" in foo.content
    assert "def foo():" in foo.content
    
    # Check class
    bar = next(s for s in symbols if s.name == "Bar")
    assert "@cls_decorator" in bar.content
    assert "class Bar:" in bar.content

def test_go_type_spec_filtering(tmp_path):
    """Test that only Go structs/interfaces are captured, not aliases."""
    content = """
package main

type MyStruct struct {}
type MyInterface interface {}
type MyAlias int
type MyAlias2 = string
"""
    f = tmp_path / "test.go"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f)
    names = {s.name for s in symbols}
    
    assert "MyStruct" in names
    assert "MyInterface" in names
    assert "MyAlias" not in names
    assert "MyAlias2" not in names

def test_c_struct_naming(tmp_path):
    """Test robust C struct naming."""
    content = """
struct Named { int x; };
typedef struct { int y; } Anonymous;
"""
    f = tmp_path / "test.c"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f)
    names = {s.name for s in symbols}
    
    assert "Named" in names
    # Anonymous struct might be skipped or named <anonymous> depending on implementation
    # Our implementation sets name to <anonymous> if no direct name child
    # But typedef might wrap it. For now, just ensure we don't crash or pick up "int"
    assert "int" not in names
    assert "y" not in names

def test_scan_error_capture(tmp_path):
    """Test that scan captures errors instead of swallowing them."""
    # Create a valid file
    (tmp_path / "valid.py").write_text("def foo(): pass", encoding="utf-8")
    
    # Create a binary file that looks like python
    binary = tmp_path / "binary.py"
    with binary.open("wb") as f:
        f.write(b"\x00\x00\x00")
        
    reports = core.scan_directory(tmp_path)
    
    assert len(reports) == 2
    
    valid = next(r for r in reports if r.path.name == "valid.py")
    assert not valid.error
    assert len(valid.symbols) == 1
    
    invalid = next(r for r in reports if r.path.name == "binary.py")
    assert invalid.error
    assert "Refusing to parse binary file" in invalid.error
