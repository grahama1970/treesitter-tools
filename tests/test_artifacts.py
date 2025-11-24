"""Test against real artifact files with expected outputs."""

import pytest
import json
from pathlib import Path
from treesitter_tools import api

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"
EXPECTED_DIR = Path(__file__).parent / "expected"

def load_expected(artifact_path):
    """Load expected output JSON for an artifact."""
    # Just use the filename with .json extension
    expected_name = artifact_path.name + '.json'
    expected_path = EXPECTED_DIR / expected_name
    if not expected_path.exists():
        return None
    return json.loads(expected_path.read_text(encoding='utf-8'))

def normalize_symbols(symbols_list):
    """Normalize symbols to match expected format (strip content)."""
    result = []
    for s in symbols_list:
        d = s.to_dict() if hasattr(s, 'to_dict') else s
        d['content'] = None  # Strip content for comparison
        result.append(d)
    return result

def test_python_complex_artifact():
    """Test complex Python file with classes and functions."""
    artifact = ARTIFACTS_DIR / "sample_complex.py"
    expected = load_expected(artifact)
    
    symbols = api.list_symbols(artifact)
    actual = normalize_symbols(symbols)
    
    assert expected is not None, "Expected output file missing"
    assert len(actual) == len(expected)
    
    # Check we found the expected symbols
    actual_names = {s['name'] for s in actual}
    expected_names = {s['name'] for s in expected}
    assert actual_names == expected_names
    
    # Check kinds match
    for act, exp in zip(actual, expected):
        assert act['kind'] == exp['kind']
        assert act['name'] == exp['name']

def test_react_jsx_artifact():
    """Test React JSX component."""
    artifact = ARTIFACTS_DIR / "sample_react.jsx"
    expected = load_expected(artifact)
    
    symbols = api.list_symbols(artifact)
    actual = normalize_symbols(symbols)
    
    assert expected is not None
    assert len(actual) == len(expected)
    
    # Should find the component functions
    actual_names = {s['name'] for s in actual}
    assert "UserProfile" in actual_names or "fetchUser" in actual_names

def test_rust_complex_artifact():
    """Test Rust file with structs and functions."""
    artifact = ARTIFACTS_DIR / "sample_complex.rs"
    expected = load_expected(artifact)
    
    symbols = api.list_symbols(artifact)
    actual = normalize_symbols(symbols)
    
    assert expected is not None
    assert len(actual) == len(expected)
    
    actual_names = {s['name'] for s in actual}
    expected_names = {s['name'] for s in expected}
    assert actual_names == expected_names

def test_go_complex_artifact():
    """Test Go file with types and functions."""
    artifact = ARTIFACTS_DIR / "sample_complex.go"
    expected = load_expected(artifact)
    
    symbols = api.list_symbols(artifact)
    actual = normalize_symbols(symbols)
    
    assert expected is not None
    assert len(actual) == len(expected)
    
    actual_names = {s['name'] for s in actual}
    assert "NewCache" in actual_names
    assert "main" in actual_names

def test_c_complex_artifact():
    """Test C file with functions."""
    artifact = ARTIFACTS_DIR / "sample_complex.c"
    expected = load_expected(artifact)
    
    symbols = api.list_symbols(artifact)
    actual = normalize_symbols(symbols)
    
    assert expected is not None
    assert len(actual) == len(expected)
    
    actual_names = {s['name'] for s in actual}
    # C functions that should be found
    assert "cache_destroy" in actual_names
    assert "hash_string" in actual_names

def test_junk_file_artifact():
    """Test that junk file is handled gracefully."""
    artifact = ARTIFACTS_DIR / "junk.txt"
    expected = load_expected(artifact)
    
    assert expected is not None
    assert expected.get("error") == "ValueError"
    
    # Should raise ValueError for unknown extension
    with pytest.raises(ValueError, match="Cannot detect Tree-sitter language"):
        api.list_symbols(artifact)

def test_all_artifacts_have_expected():
    """Ensure all artifacts have expected outputs."""
    artifacts = [
        "sample_complex.py",
        "sample_react.jsx",
        "sample_complex.rs",
        "sample_complex.go",
        "sample_complex.c",
        "junk.txt",  # Even error cases have expected results
    ]
    
    for name in artifacts:
        artifact = ARTIFACTS_DIR / name
        assert artifact.exists(), f"Artifact {name} missing"
        
        expected_path = EXPECTED_DIR / (name + '.json')
        assert expected_path.exists(), f"Expected output for {name} missing"
