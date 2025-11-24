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
        try:
            output.write_text(payload, encoding="utf-8")
            typer.echo(f"Wrote {len(symbols)} symbols -> {output}")
        except OSError as e:
            typer.secho(f"I/O Error writing output: {e}", err=True, fg=typer.colors.RED)
            raise typer.Exit(1)
    else:
        typer.echo(payload)


def version_callback(value: bool):
    if value:
        typer.echo("treesitter-tools v0.1.0")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="Show version and exit"
    ),
):
    """
    Tree-sitter helpers for inspecting local code.
    """
    pass

@app.command()
def symbols(
    path: Path = typer.Argument(..., exists=True, readable=True, help="Path to the source file to inspect"),
    language: Optional[str] = typer.Option(None, help="Override detected language"),
    output: Optional[Path] = typer.Option(None, help="Optional path to JSON output"),
    content: bool = typer.Option(False, "--content", "-c", help="Include full source code of symbols"),
):
    """List functions/classes detected in the file."""
    try:
        items = extract_symbols(path, language)
        if not items:
            typer.secho(f"Warning: No symbols found in {path}", err=True, fg=typer.colors.YELLOW)
            
        _echo_symbols(items, output, content)
    except ValueError as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        typer.secho("Hint: Try using --language to manually specify the language.", err=True, fg=typer.colors.YELLOW)
        raise typer.Exit(1)
    except RuntimeError as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)
    except OSError as e:
        typer.secho(f"I/O Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def query(
    path: Path = typer.Argument(..., exists=True, readable=True, help="Path to the source file to inspect"),
    query: str = typer.Argument(..., help="Tree-sitter query to execute"),
    language: Optional[str] = typer.Option(None, help="Override detected language"),
    output: Optional[Path] = typer.Option(None, help="Optional path to JSON output"),
):
    """Execute a Tree-sitter query and return the captures."""
    try:
        matches = run_query(path, query, language)
        payload = json.dumps(matches, indent=2)
        if output:
            try:
                output.write_text(payload, encoding="utf-8")
                typer.echo(f"Wrote {len(matches)} matches -> {output}")
            except OSError as e:
                typer.secho(f"I/O Error writing output: {e}", err=True, fg=typer.colors.RED)
                raise typer.Exit(1)
        else:
            typer.echo(payload)
    except ValueError as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        typer.secho("Hint: Try using --language to manually specify the language.", err=True, fg=typer.colors.YELLOW)
        raise typer.Exit(1)
    except RuntimeError as e:
        typer.secho(f"Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)
    except OSError as e:
        typer.secho(f"I/O Error: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)


@app.command()
def scan(
    root: Path = typer.Argument(Path.cwd(), help="Directory to walk"),
    include: List[str] = typer.Option(["**/*"], help="Glob patterns to include"),
    exclude: List[str] = typer.Option([], help="Glob patterns to exclude"),
    output: Optional[Path] = typer.Option(None, help="Write JSON report to this path"),
    outline: Optional[Path] = typer.Option(None, help="Optional markdown outline destination"),
    content: bool = typer.Option(False, "--content", "-c", help="Include full source code of symbols"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Print errors and skipped files"),
):
    """Walk a directory and summarize symbols per file."""
    
    reports = scan_directory(root, include, exclude)
    
    # Strip content if not requested
    if not content:
        for report in reports:
            for sym in report.symbols:
                sym.content = None
    
    # Calculate stats
    total_files = len(reports)
    files_with_symbols = sum(1 for r in reports if r.symbols)
    total_symbols = sum(len(r.symbols) for r in reports)
    errors = [r for r in reports if r.error]
    
    # Print summary to stderr
    summary_color = typer.colors.GREEN if not errors else typer.colors.YELLOW
    typer.secho(
        f"Scanned {total_files} files. Found {total_symbols} symbols in {files_with_symbols} files.",
        err=True,
        fg=summary_color
    )
    
    if errors:
        typer.secho(f"Encountered {len(errors)} errors.", err=True, fg=typer.colors.YELLOW)
        if verbose:
            typer.secho("\nError details:", err=True, fg=typer.colors.YELLOW)
            for err in errors:
                typer.secho(f"  {err.path}: {err.error}", err=True, fg=typer.colors.YELLOW)
        else:
            typer.secho("Use --verbose to see error details.", err=True, fg=typer.colors.YELLOW)

    try:
        payload = json.dumps([report.to_dict() for report in reports], indent=2)
        if output:
            output.write_text(payload, encoding="utf-8")
            typer.echo(f"Wrote symbol report ({len(reports)} files) -> {output}")
        else:
            typer.echo(payload)
        if outline:
            outline.write_text(outline_markdown(reports), encoding="utf-8")
            typer.echo(f"Wrote outline -> {outline}")
    except OSError as e:
        typer.secho(f"I/O Error writing output: {e}", err=True, fg=typer.colors.RED)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
