from pathlib import Path
from treesitter_tools.core import extract_symbols

def test_content_extraction(tmp_path):
    # Create a dummy python file
    f = tmp_path / "test.py"
    f.write_text("def foo():\n    return 1\n", encoding="utf-8")
    
    symbols = extract_symbols(f)
    assert len(symbols) == 1
    assert symbols[0].name == "foo"
    # Content should be populated by default in core logic now
    assert symbols[0].content == "def foo():\n    return 1"
