from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import typer

from .core import (
    CodeSymbol,
    extract_symbols,
    outline_markdown,
    run_query,
    scan_directory,
    symbols_to_json,
)

app = typer.Typer(add_completion=False, help="Tree-sitter helpers for inspecting local code.")


def _echo_symbols(symbols: list[CodeSymbol], output: Optional[Path], include_content: bool = False) -> None:
    if not include_content:
        # Strip content if not requested
        for sym in symbols:
            sym.content = None
    payload = symbols_to_json(symbols)
    if output:
        output.write_text(payload, encoding="utf-8")
        typer.echo(f"Wrote {len(symbols)} symbols -> {output}")
    else:
        typer.echo(payload)


@app.command()
def symbols(
    path: Path = typer.Argument(..., exists=True, readable=True, help="Path to the source file to inspect"),
    language: Optional[str] = typer.Option(None, help="Override detected language"),
    output: Optional[Path] = typer.Option(None, help="Optional path to JSON output"),
    content: bool = typer.Option(False, "--content", "-c", help="Include full source code of symbols"),
):
    """List functions/classes detected in the file."""

    items = extract_symbols(path, language)
    _echo_symbols(items, output, content)


@app.command()
def query(
    path: Path = typer.Argument(..., exists=True, readable=True, help="Path to the source file to inspect"),
    query: str = typer.Argument(..., help="Tree-sitter query to execute"),
    language: Optional[str] = typer.Option(None, help="Override detected language"),
    output: Optional[Path] = typer.Option(None, help="Optional path to JSON output"),
):
    """Execute a Tree-sitter query and return the captures."""

    matches = run_query(path, query, language)
    payload = json.dumps(matches, indent=2)
    if output:
        output.write_text(payload, encoding="utf-8")
        typer.echo(f"Wrote {len(matches)} matches -> {output}")
    else:
        typer.echo(payload)


@app.command()
def scan(
    root: Path = typer.Argument(Path.cwd(), help="Directory to walk"),
    include: List[str] = typer.Option(["**/*"], help="Glob patterns to include"),
    exclude: List[str] = typer.Option([], help="Glob patterns to exclude"),
    output: Optional[Path] = typer.Option(None, help="Write JSON report to this path"),
    outline: Optional[Path] = typer.Option(None, help="Optional markdown outline destination"),
):
    """Walk a directory and summarize symbols per file."""

    reports = scan_directory(root, include, exclude)
    payload = json.dumps([report.to_dict() for report in reports], indent=2)
    if output:
        output.write_text(payload, encoding="utf-8")
        typer.echo(f"Wrote symbol report ({len(reports)} files) -> {output}")
    else:
        typer.echo(payload)
    if outline:
        outline.write_text(outline_markdown(reports), encoding="utf-8")
        typer.echo(f"Wrote outline -> {outline}")


if __name__ == "__main__":
    app()
