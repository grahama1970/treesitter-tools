from pathlib import Path

from treesitter_tools.core import extract_symbols, run_query, scan_directory


def test_extract_symbols_python(tmp_path: Path) -> None:
    src = tmp_path / "sample.py"
    src.write_text(
        """
class Greeter:
    def hi(self, name):
        'say hi'
        return f"hi {name}"
""",
        encoding="utf-8",
    )
    symbols = extract_symbols(src)
    kinds = {s.kind for s in symbols}
    assert "class" in kinds
    assert any(s for s in symbols if s.kind == "function")


def test_run_query(tmp_path: Path) -> None:
    src = tmp_path / "demo.py"
    src.write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    matches = run_query(src, "(function_definition name: (identifier) @name)")
    assert matches
    assert matches[0]["captures"][0]["text"] == "add"


def test_scan_directory(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    root.mkdir()
    (root / "a.py").write_text("def foo():\n    pass\n", encoding="utf-8")
    (root / "skip.txt").write_text("noop", encoding="utf-8")
    reports = scan_directory(root, include=["**/*.py"])
    assert len(reports) == 1
    assert reports[0].symbols
