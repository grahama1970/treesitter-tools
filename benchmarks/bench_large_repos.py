#!/usr/bin/env python3
"""Benchmark script for measuring treesitter-tools throughput."""

import time
from pathlib import Path
from treesitter_tools import api

def benchmark_file(file_path: Path, max_chunk_size=None, iterations=10):
    """Benchmark symbol extraction on a single file."""
    file_size = file_path.stat().st_size
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        symbols = api.list_symbols(file_path, max_chunk_size=max_chunk_size)
        end = time.perf_counter()
        times.append(end - start)
    
    avg_time = sum(times) / len(times)
    throughput = file_size / avg_time / 1024 / 1024  # MB/s
    symbols_per_sec = len(symbols) / avg_time
    
    return {
        "file": file_path.name,
        "size_bytes": file_size,
        "avg_time_sec": avg_time,
        "throughput_mbps": throughput,
        "symbols_per_sec": symbols_per_sec,
        "total_symbols": len(symbols),
    }

def main():
    """Run benchmarks on test artifacts and report results."""
    test_files = list(Path("tests/artifacts").glob("*.py")) + \
                 list(Path("tests/artifacts").glob("*.go")) + \
                 list(Path("tests/artifacts").glob("*.rs")) + \
                 list(Path("tests/artifacts").glob("*.c"))
    
    if not test_files:
        print("No test files found. Using src/treesitter_tools/core.py")
        test_files = [Path("src/treesitter_tools/core.py")]
    
    print("=" * 80)
    print("treesitter-tools Benchmark")
    print("=" * 80)
    print()
    
    # Benchmark without chunking
    print("Without chunking:")
    print("-" * 80)
    for f in test_files:
        result = benchmark_file(f)
        print(f"{result['file']:30} | {result['size_bytes']:>8} bytes | "
              f"{result['avg_time_sec']*1000:>8.2f} ms | "
              f"{result['throughput_mbps']:>8.2f} MB/s | "
              f"{result['total_symbols']:>4} symbols")
    
    print()
    print("With chunking (max 500 chars):")
    print("-" * 80)
    for f in test_files:
        result = benchmark_file(f, max_chunk_size=500)
        print(f"{result['file']:30} | {result['size_bytes']:>8} bytes | "
              f"{result['avg_time_sec']*1000:>8.2f} ms | "
              f"{result['throughput_mbps']:>8.2f} MB/s | "
              f"{result['total_symbols']:>4} symbols (chunked)")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    main()
