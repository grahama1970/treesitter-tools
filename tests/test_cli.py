"""Integration tests for CLI commands."""

import json
import subprocess
import sys
from pathlib import Path
import pytest


def run_cli(args, cwd=None):
    """Helper to run treesitter-tools CLI."""
    import os
    
    cmd = [sys.executable, "-m", "treesitter_tools.cli"] + args
    env = os.environ.copy()
    # Add src directory to PYTHONPATH
    src_dir = Path(__file__).parent.parent / "src"
    env["PYTHONPATH"] = str(src_dir) + os.pathsep + env.get("PYTHONPATH", "")
    
    result = subprocess.run(
        cmd,
        cwd=cwd or Path.cwd(),
        capture_output=True,
        text=True,
        env=env,
    )
    return result


def test_cli_symbols_basic(tmp_path):
    """Test symbols command with basic Python file."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo(): pass\nclass Bar: pass", encoding="utf-8")
    
    result = run_cli(["symbols", str(test_file)])
    
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert len(output) == 2
    names = {sym["name"] for sym in output}
    assert "foo" in names
    assert "Bar" in names


def test_cli_symbols_with_content(tmp_path):
    """Test symbols command with --content flag."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo():\n    return 42", encoding="utf-8")
    
    result = run_cli(["symbols", str(test_file), "--content"])
    
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert len(output) == 1
    assert output[0]["name"] == "foo"
    assert output[0]["content"] is not None
    assert "return 42" in output[0]["content"]


def test_cli_symbols_with_output(tmp_path):
    """Test symbols command with JSON output file."""
    test_file = tmp_path / "test.py"
    output_file = tmp_path / "output.json"
    test_file.write_text("def foo(): pass", encoding="utf-8")
    
    result = run_cli(["symbols", str(test_file), "--output", str(output_file)])
    
    assert result.returncode == 0
    assert output_file.exists()
    output = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(output) == 1
    assert output[0]["name"] == "foo"


def test_cli_symbols_language_override(tmp_path):
    """Test symbols command with --language override."""
    # Create .txt file with Python code
    test_file = tmp_path / "test.txt"
    test_file.write_text("def foo(): pass", encoding="utf-8")
    
    result = run_cli(["symbols", str(test_file), "--language", "python"])
    
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert len(output) == 1
    assert output[0]["name"] == "foo"


def test_cli_query_basic(tmp_path):
    """Test query command with basic Tree-sitter query."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo(): pass", encoding="utf-8")
    
    query = "(function_definition name: (identifier) @name)"
    result = run_cli(["query", str(test_file), query])
    
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert len(output) > 0
    # Should capture the identifier "foo"
    captures = [match for match in output if match["captures"]]
    assert len(captures) > 0


def test_cli_query_with_output(tmp_path):
    """Test query command with JSON output file."""
    test_file = tmp_path / "test.py"
    output_file = tmp_path / "query_output.json"
    test_file.write_text("def foo(): pass", encoding="utf-8")
    
    query = "(function_definition name: (identifier) @name)"
    result = run_cli(["query", str(test_file), query, "--output", str(output_file)])
    
    assert result.returncode == 0
    assert output_file.exists()
    output = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(output) > 0


def test_cli_scan_basic(tmp_path):
    """Test scan command on directory."""
    # Create test files
    (tmp_path / "file1.py").write_text("def foo(): pass", encoding="utf-8")
    (tmp_path / "file2.py").write_text("class Bar: pass", encoding="utf-8")
    
    result = run_cli(["scan", str(tmp_path)])
    
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert len(output) == 2
    filenames = {Path(report["path"]).name for report in output}
    assert "file1.py" in filenames
    assert "file2.py" in filenames


def test_cli_scan_with_include(tmp_path):
    """Test scan command with --include pattern."""
    # Create test files
    (tmp_path / "file1.py").write_text("def foo(): pass", encoding="utf-8")
    (tmp_path / "file2.txt").write_text("def bar(): pass", encoding="utf-8")
    
    result = run_cli(["scan", str(tmp_path), "--include", "**/*.py"])
    
    assert result.returncode == 0
    output = json.loads(result.stdout)
    # Should only find .py files
    assert len(output) == 1
    assert Path(output[0]["path"]).name == "file1.py"


def test_cli_scan_with_content(tmp_path):
    """Test scan command with --content flag."""
    (tmp_path / "file1.py").write_text("def foo():\n    return 42", encoding="utf-8")
    
    result = run_cli(["scan", str(tmp_path), "--content"])
    
    assert result.returncode == 0
    output = json.loads(result.stdout)
    assert len(output) == 1
    symbols = output[0]["symbols"]
    assert len(symbols) == 1
    assert symbols[0]["content"] is not None
    assert "return 42" in symbols[0]["content"]


def test_cli_scan_with_outline(tmp_path):
    """Test scan command with --outline markdown output."""
    (tmp_path / "file1.py").write_text("def foo(): pass", encoding="utf-8")
    outline_file = tmp_path / "outline.md"
    
    result = run_cli(["scan", str(tmp_path), "--outline", str(outline_file)])
    
    assert result.returncode == 0
    assert outline_file.exists()
    outline_content = outline_file.read_text(encoding="utf-8")
    assert "file1.py" in outline_content
    assert "foo" in outline_content


def test_cli_scan_with_output(tmp_path):
    """Test scan command with JSON output file."""
    (tmp_path / "file1.py").write_text("def foo(): pass", encoding="utf-8")
    output_file = tmp_path / "scan_output.json"
    
    result = run_cli(["scan", str(tmp_path), "--output", str(output_file)])
    
    assert result.returncode == 0
    assert output_file.exists()
    output = json.loads(output_file.read_text(encoding="utf-8"))
    assert len(output) == 1


def test_cli_error_handling_missing_file():
    """Test CLI error handling for missing file."""
    result = run_cli(["symbols", "/nonexistent/file.py"])
    
    assert result.returncode != 0
    # Should have error output
    assert len(result.stderr) > 0 or "Error" in result.stdout


def test_cli_error_handling_invalid_language(tmp_path):
    """Test CLI error handling for invalid language."""
    test_file = tmp_path / "test.py"
    test_file.write_text("def foo(): pass", encoding="utf-8")
    
    result = run_cli(["symbols", str(test_file), "--language", "invalid_lang"])
    
    # Should fail or handle gracefully
    assert result.returncode != 0 or "invalid_lang" not in result.stdout
