"""Tests for docstring/doc comment extraction across languages."""

import pytest
from pathlib import Path
from treesitter_tools import api

def test_python_docstring_function(tmp_path):
    """Test Python function docstring extraction."""
    content = '''
def foo():
    """This is a function docstring."""
    pass
'''
    f = tmp_path / "test.py"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f)
    assert len(symbols) == 1
    assert symbols[0].docstring == "This is a function docstring."

def test_python_docstring_class(tmp_path):
    """Test Python class docstring extraction."""
    content = '''
class MyClass:
    """This is a class docstring."""
    pass
'''
    f = tmp_path / "test.py"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f)
    assert len(symbols) == 1
    assert symbols[0].docstring == "This is a class docstring."

def test_python_docstring_method(tmp_path):
    """Test Python method docstring extraction."""
    content = '''
class MyClass:
    def method(self):
        """This is a method docstring."""
        pass
'''
    f = tmp_path / "test.py"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f)
    # Should get class and method
    method = next(s for s in symbols if s.name == "method")
    assert method.docstring == "This is a method docstring."

def test_javascript_jsdoc(tmp_path):
    """Test JavaScript JSDoc extraction."""
    content = '''
/**
 * This is a JSDoc comment.
 */
function foo() {
    return 42;
}
'''
    f = tmp_path / "test.js"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f)
    assert len(symbols) == 1
    assert symbols[0].docstring is not None
    assert "JSDoc comment" in symbols[0].docstring

def test_rust_doc_comment(tmp_path):
    """Test Rust doc comment extraction."""
    content = '''
/// This is a doc comment.
fn foo() -> i32 {
    42
}
'''
    f = tmp_path / "test.rs"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f)
    assert len(symbols) == 1
    assert symbols[0].docstring is not None
    assert "doc comment" in symbols[0].docstring

def test_go_doc_comment(tmp_path):
    """Test Go doc comment extraction."""
    content = '''
package main

// Foo does something.
func Foo() int {
    return 42
}
'''
    f = tmp_path / "test.go"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f)
    assert len(symbols) == 1
    assert symbols[0].docstring is not None
    assert "Foo does something" in symbols[0].docstring

def test_java_javadoc(tmp_path):
    """Test Java Javadoc extraction."""
    content = '''
/**
 * This is a Javadoc comment.
 */
public class Foo {
    public void bar() {}
}
'''
    f = tmp_path / "test.java"
    f.write_text(content, encoding="utf-8")
    
    symbols = api.list_symbols(f)
    foo_class = next(s for s in symbols if s.name == "Foo")
    assert foo_class.docstring is not None
    assert "Javadoc comment" in foo_class.docstring
